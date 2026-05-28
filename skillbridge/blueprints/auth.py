"""blueprints/auth.py — Authentication with rate limiting and brute-force protection."""
import re
import time
from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db
from ..models import User, Course, Enrollment
from ..data import SUPPORTED_LANGUAGES

bp = Blueprint("auth", __name__)

# ── Simple in-process rate limiter ───────────────────────────────────────────
# Tracks failed login attempts per IP: {ip: [timestamp, ...]}
_failed_attempts: dict = defaultdict(list)
_MAX_ATTEMPTS = 5
_WINDOW_SECS  = 300   # 5 minutes
_LOCKOUT_SECS = 600   # 10 minutes


def _check_rate_limit(ip: str) -> tuple[bool, int]:
    """Return (is_blocked, seconds_remaining)."""
    now = time.time()
    attempts = _failed_attempts[ip]
    # Remove attempts outside the window
    _failed_attempts[ip] = [t for t in attempts if now - t < _WINDOW_SECS]
    if len(_failed_attempts[ip]) >= _MAX_ATTEMPTS:
        oldest = _failed_attempts[ip][0]
        remaining = int(_LOCKOUT_SECS - (now - oldest))
        if remaining > 0:
            return True, remaining
        # Lockout expired — clear
        _failed_attempts[ip] = []
    return False, 0


def _record_failure(ip: str):
    _failed_attempts[ip].append(time.time())


def _clear_failures(ip: str):
    _failed_attempts.pop(ip, None)


# ── Register ──────────────────────────────────────────────────────────────────

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        interest = request.form.get("interest", "Technology")
        location = request.form.get("location", "").strip()
        language = request.form.get("language", "en")
        if language not in SUPPORTED_LANGUAGES:
            language = "en"

        errors = []
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters.")
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Valid email required.")
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        elif not re.search(r"[A-Z]", password):
            errors.append("Password needs an uppercase letter.")
        elif not re.search(r"[a-z]", password):
            errors.append("Password needs a lowercase letter.")
        elif not re.search(r"\d", password):
            errors.append("Password needs a digit.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        user = User(name=name, email=email, interest=interest,
                    location=location, language=language, role="user")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        course = Course.query.filter_by(category=interest).first()
        if course:
            db.session.add(Enrollment(user_id=user.id, course_id=course.id))
            db.session.commit()

        login_user(user)
        flash(f"Welcome to SkillBridge, {name}! 🎉", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("register.html")


# ── Login ─────────────────────────────────────────────────────────────────────

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        ip = request.remote_addr or "unknown"
        blocked, remaining = _check_rate_limit(ip)
        if blocked:
            mins = remaining // 60
            secs = remaining % 60
            flash(f"Too many failed attempts. Try again in {mins}m {secs}s.", "danger")
            return redirect(url_for("auth.login"))

        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for("auth.login"))
        if not password:
            flash("Password is required.", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account has been deactivated. Contact support.", "danger")
                return redirect(url_for("auth.login"))
            _clear_failures(ip)
            login_user(user, remember=True)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(next_page or url_for("main.dashboard"))

        _record_failure(ip)
        remaining_attempts = _MAX_ATTEMPTS - len(_failed_attempts[ip])
        if remaining_attempts > 0:
            flash(f"Invalid email or password. {remaining_attempts} attempt(s) remaining.", "danger")
        else:
            flash("Too many failed attempts. Account temporarily locked.", "danger")
    return render_template("login.html")


# ── Logout ────────────────────────────────────────────────────────────────────

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
