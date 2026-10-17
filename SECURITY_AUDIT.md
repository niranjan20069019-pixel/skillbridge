# SkillBridge — Security Audit (2026-10-17)

Findings ranked CRITICAL → LOW. Fixes applied in order: see `FIXES.md`.

## CRITICAL

### C1. Secrets committed to git (`.env`)
- Root `.env` is **tracked in git** (`git ls-files` shows it) and contains `SECRET_KEY` and run instructions.
- `backend/.env` (untracked but present on disk) contains a **live Gemini API key** — real credentials.
- Anyone with repo access can forge Flask session cookies / steal the AI key.
- Fix: untrack `.env`, gitignore all `.env` files, rotate the leaked Gemini key, ship examples only.

### C2. Open redirect after login
- `skillbridge/blueprints/auth.py:133` — `next_page = request.args.get("next")` is redirected to with **no validation**.
- `/login?next=https://evil.example` sends authenticated users (and their session) to an attacker site.
- Fix: validate with `url_has_allowed_host_and_scheme(next, request.host)`.

### C3. WebSocket accepts connections from any origin
- `realtime_chat/__init__.py:9` and `app.py:43` — `cors_allowed_origins="*"`.
- A malicious page can open a socket to the server and ride the victim's session cookie (authenticated sockets, chat history leak).
- Fix: restrict origins to `FRONTEND_URL` env (default localhost:5000/5173).

## HIGH

### H1. Weak password hashing in Node backend
- `backend/src/routes/auth.js:16` — `sha256(password + 'skillbridge-salt')`: fast hash, static salt, per-user salt absent.
- Fix: Node's built-in `crypto.scrypt` with random per-user salt (no new dependency needed).

### H2. Session cookies not secure in production
- `config.py:56` — `SESSION_COOKIE_SECURE` defaults to `False` unless env is set; a typo/omission ships cookies over HTTP.
- Fix: default to `True` in ProductionConfig.

### H3. Production config never validated — `SECRET_KEY` can be missing or the hardcoded dev value
- `config.py` defines `ProductionConfig.validate()` but nothing calls it; app boots with `SECRET_KEY="change-me-in-production"` silently.
- Fix: call `validate()` in `create_app()` when `FLASK_ENV=production`.

### H4. `/health` leaks internal DB error to anonymous users
- `app.py:70-79` returns `str(e)` — includes connection strings / host names. Also leaves `db.session` in aborted state.
- Fix: return generic error, `logger.exception` the detail.

## MEDIUM

### M1. In-memory rate limiter leaks memory (unbounded dict)
- `auth.py:15` — `_failed_attempts` keeps every IP forever → attacker IPs inflate memory; also reset not thread-safe.
- Fix: cap entries (drop oldest when over threshold).

### M2. CSRF protection stripped for the entire `/api` blueprint
- `app.py:51` — `csrf.exempt(api_bp)` means state-changing JSON endpoints (`set-language`, `mark-complete`, `progress`, …) are CSRF-able if a future endpoint accepts cookies/forms. Browsers auto-send cookies with `fetch`.
- Fix: keep the JSON endpoints exempt only where fetch/XHR is used, but note the ceiling: JSON-only bodies are the mitigation; do NOT add form-accepting endpoints under `/api`.

### M3. `add_course` crashes with 500 on missing fields
- `admin.py:129` — `request.form["title"]` raises `KeyError` instead of a friendly flash (also unvalidated empty strings).
- Fix: use `.get()` + required-field check.

### M4. `track_analytics` 500s on non-integer values
- `api.py:281-282` — `int(data.get("watch_secs", 0))` raises `ValueError` on `"abc"`.
- Fix: safe int conversion helper.

## LOW

### L1. HTML injected via `innerHTML` from server data
- `templates/quiz_result.html:89`, `templates/dashboard.html:471`, `templates/learn.html:439` interpolate API data into `innerHTML`.
- Current data sources (own server JSON) are low-risk, but any future user-generated string (chat message, course title) becomes stored XSS.
- Fix: keep ceiling noted — server content is admin/trusted today; switch to `textContent` when user content flows in.

### L2. Node backend auth is fully in-memory (`users = []`)
- Registered users vanish on restart. Development placeholder, not a production auth system — documented, not "fixed" (would need a DB).

Verdict: CRITICAL C1–C3 + H2/H3/H4 + M1/M2/M3/M4 fixed in this pass; C2, C3, H1, M1, M3, M4 code changes applied; C1 repo hygiene applied; L1/L2 documented only.
