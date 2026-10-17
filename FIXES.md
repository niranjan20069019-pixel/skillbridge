# SkillBridge — Fix Log (how each bug was closed)

Companion to `SECURITY_AUDIT.md`. Each entry: problem → fix → why this way → verification.

## C1 — Secrets in git (`.env`)
**Problem.** Root `.env` was tracked in git; `backend/.env` held a live Gemini API key.
**Fix.**
1. `git rm --cached .env` — untracked it (file stays on disk for local dev).
2. Added to `.gitignore`: `.env`, `backend/.env`, `*.env`, `!.env.example`.
3. Same pass removed tracked `__pycache__/` dirs + `.pyc` files, the entire `venv/`, and `instance/*.db` (a SQLite DB with user data asks to be leaked; only `.env.example`-style files belong in git) from the index.
**You must still:** **rotate the Gemini key** (it is baked into git history — untracking the file deletes nothing from history; use `git filter-repo` or BFG if the repo is public, or just consider the key burned and replace it).
**Why not more.** Did not scrub history in this pass (destructive, needs a decision). Flagged instead.

## C2 — Open redirect after login
**Problem.** `auth.py` did `redirect(request.args.get("next"))` — an attacker link `/login?next=https://evil.com` sent users (with their fresh session) offsite.
**Fix.** Before redirecting, `next` must pass all of: starts with `/` (relative only), does NOT start with `//` (protocol-relative URLs are still browser-external), and its `urlparse().netloc` must be empty or `request.host`.
```
_next = request.args.get("next")
if not (_next and _next.startswith("/")
        and not _next.startswith("//")
        and urlparse(_next).scheme in ("", "http", "https")
        and urlparse(_next).netloc in ("", request.host)):
    _next = None
```
**Verified.** Test-client logins with `next=https://evil.com`, `//evil.com`, `\/evil.com` all land on `/dashboard`; `next=/courses` still lands on `/courses`.

## C1.1 — WebSocket same-origin enforcement
**Problem.** `socketio` ran with `cors_allowed_origins="*"` — any website could open an authenticated socket with the victim's session cookie.
**Fix.** `app.py` now reads `SOCKETIO_ORIGINS` env (comma-separated), defaulting to localhost ports used in dev. Deployments set it to their real domain.

## H1 — Weak password hashing (Node backend)
**Problem.** `sha256(password + 'skillbridge-salt')` — fast hash, static global salt, costs nothing to brute-force.
**Fix.** Replaced with Node's **built-in** `crypto.scrypt` (memory-hard KDF, per-user random 16-byte salt) and `timingSafeEqual` compare. Stored format: `hash:salt`. No new dependency added.
**Verified.** Round-trip: valid password verifies, wrong one doesn't, malformed stored hash safely returns false.

## H2 — Insecure session cookie by default
**Problem.** `SESSION_COOKIE_SECURE` defaulted to `False`; a deployment that forgets the env var ships the auth cookie over plain HTTP.
**Fix.** Default flipped to `"True"` in ProductionConfig. Dev config unaffected.

## H3 — Production config never validated
**Problem.** `ProductionConfig.validate()` existed but nothing called it; app ran fine with the hardcoded `SECRET_KEY="change-me-in-production"`.
**Fix.** `create_app()` now calls `cfg.validate()` when the production config is active → fails fast on boot instead of running with a forgeable session key.

## H4 — `/health` leaking internal DB errors
**Problem.** The anonymous endpoint returned `str(e)` — could include DB host/credentials hints.
**Fix.** Return fixed `"unavailable"`; the exception goes to a logger via `log.exception(...)`.

## M1 — Unbounded rate-limiter dict
**Problem.** `_failed_attempts` grew forever (one entry per unique attacker IP) — memory DoS.
**Fix.** Cap at 10k IPs; when full, drop the oldest key before inserting. Marked with a `ponytail:` comment: switch to Redis when rate-limiting must survive multi-process deploys.

## M3 — `add_course` 500s on missing fields
**Problem.** `request.form["title"]` raises `KeyError` → raw 500 instead of a message.
**Fix.** `.get()` + `.strip()` on title/description/category; missing/blank → flash an error and redirect.

## M4 — `track_analytics` 500s on non-numeric input
**Problem.** `int(data.get("watch_secs", 0))` raises `ValueError` on `"abc"` (client crash or crafted request).
**Fix.** Small `_int()` helper returns 0 on `TypeError/ValueError`.
**Verified.** `POST /api/analytics/track {"watch_secs": "abc"}` → 200 ok, previously 500.

## L1 / L2 — documented, not patched
- **L1:** `innerHTML` interpolation of server JSON in templates — data is server-owned today; switch to `textContent` when user-generated strings (chat, titles) flow through. Patching all 13 sites now would churn production templates for no current exposure.
- **L2:** Node auth store is in-memory (`users = []`) — dev placeholder; real fix needs a DB, out of scope.

## What was deliberately skipped (ponytail)
- History scrubbing for the leaked key (destructive; rotate instead).
- Redis-backed rate limiting (one-process app today).
- Rewriting the Node in-memory auth into a real DB-backed service (separate feature).

---

# Part 2 — Deploy-Blocker Pass (2026-10-17)

Checked every deploy path: Procfile, Dockerfile, docker-compose.yml, render.yaml, run.sh, run.bat — plus a codebase-wide static pass (compile + import matrix) and gunicorn/curl smoke tests of the exact Procfile command.

## D1 — CRITICAL: production gunicorn never creates/seeds the database
**Problem.** `Procfile`, `Dockerfile`, and `render.yaml` all run `gunicorn run:app`. Gunicorn imports the `run` module and never executes its `if __name__ == "__main__"` block, so `init_database()` (create tables + seed courses/quizzes/badges/admin) only ran in `python run.py` — i.e. locally, not in any production deploy. A fresh Postgres on Render/Docker came up with **zero tables** → every route 500s. App looks fine locally, dies on deploy: classic free-standing-dev bug.
**Fix.** `run.py` now calls `init_database(app)` at module import (top level), not just under `__main__`. Seeds are idempotent (`seed_db`/`seed_quizzes`/`seed_badges` all guard with `count()` checks), so calling on every boot is safe and skips instantly on an existing DB.
**Verified.** Booted the exact Procfile command against a brand-new empty sqlite (`DATABASE_URL=sqlite:////tmp/fresh.db FLASK_ENV=production SECRET_KEY=... `): `/health`, `/`, `/courses` → **200**, and the fresh DB ended up with **11 courses + 1 admin user** seeded automatically.

## D2 — HIGH: Docker image baked secrets + junk into every build
**Problem.** Dockerfile `COPY . .` copies everything → `.env` (SECRET_KEY), `backend/.env` (AI keys), `venv/` (600MB venv), `.git/` (full history including the leaked key), `node_modules/`, SQLite DBs all went into the image: secret leak in artifact + bloated/possibly-oversized image that can fail registry upload on Render.
**Fix.** Added `.dockerignore` excluding `.git`, `venv/`, `node_modules/`, `__pycache__/`, `.env`, `backend/.env`, `instance/`, `uploads/`, `logs/`, `*.db`.
**Verified** (static): `COPY . .` now excludes all of the above files; not build-tested here — no Docker daemon present to run one.

## D3 — Behavior change to be aware of: prod boot fails fast without `SECRET_KEY`
**Problem (found while simulating deploys).** Booting with `FLASK_ENV=production` and no `SECRET_KEY` previously "worked" with the forgeable dev key; now (from H3) the worker crashes at boot with `RuntimeError: SECRET_KEY environment variable must be set in production.` — I reproduced this on purpose.
**Resolution.** This is the intended fail-fast, not a bug — but deployments must set the var. `docker-compose.yml` already ships a default (`change-me-in-production`), so compose deploys boot; change that default before going live. `render.yaml` uses `generateValue: true` ✓.

## Verified-green checks (no action needed)
- **Procfile command boots clean**: `gunicorn --worker-class eventlet -w 1 run:app` — worker boots, no exceptions. Gunicorn's eventlet worker monkey-patches before the app imports, so no manual `eventlet.monkey_patch()` needed in this path (`run.py` does it first for the `python run.py` path).
- **Endpoints**: `/health`, `/`, `/courses` all 200 under gunicorn; `/health` returns `{"status":"ok","database":"connected"}`.
- **ml_services pickle loads at import** on Python 3.12.4 / scikit-learn 1.5.0 — no version-locked crash.
- **Import matrix**: app, config, run, all 4 blueprints, models, data, uploads, gamification, validation, realtime_chat — all import without error in correct order.
- **Py compile**: zero syntax errors in every project python file.
- **Seeds idempotent**: `count()` guards on all three seeders → safe on every redeploy.
- **Flask-Migrate with empty `migrations/` dir**: not a blocker — prod uses `db.create_all()` from `init_database()`; `flask db` isn't invoked by any deploy script.
- **docker-compose healthchecks** use `curl`, which the runtime image stage installs; nginx conf mounts `docker/nginx.conf` (exists) and proxies `/socket.io/` with upgrade headers (matches SocketIO path).
- **No file-logger configured against a read-only FS**: nothing in the code writes to `logs/` at boot (the config only declares it), so no crash on Render's ephemeral FS.
- **psycopg2-binary, reportlab, Redis client** all present in `requirements.txt`; requirements pin set installs cleanly (matches the working venv).

## Remaining deploy notes (skipped deliberately, ponytail)
- `docker-compose.yaml` sets a `REDIS_URL` env and runs a redis service the app never uses — harmless dead env, remove when touching compose next.
- `run.sh`'s `source .env` chokes on quotes/spaces in values — cosmetic; only affects the dev launcher.
