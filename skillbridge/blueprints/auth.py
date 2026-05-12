"""blueprints/auth.py — Authentication routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db
from ..models import User, Course, Enrollment
from ..data import SUPPORTED_LANGUAGES

bp = Blueprint("auth", __name__)


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
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.login"))
        user = User(name=name, email=email, interest=interest,
                    location=location, language=language)
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


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user     = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(next_page or url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
