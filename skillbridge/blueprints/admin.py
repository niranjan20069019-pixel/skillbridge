"""blueprints/admin.py — Admin dashboard with RBAC (admin + superadmin)."""
import os
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from sqlalchemy import text
from ..extensions import db
from ..models import (User, Course, Enrollment, Quiz, QuizQuestion, MentorProfile,
                      DoubtRequest, CourseNote, Certificate)
from ..uploads import save_upload

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Allow admin and superadmin roles."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("admin", "superadmin"):
            abort(403)
        return f(*args, **kwargs)
    return decorated


def superadmin_required(f):
    """Allow only superadmin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "superadmin":
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ─────────────────────────────────────────────────────────────────

@bp.route("")
@login_required
@admin_required
def dashboard():
    stats = {
        "users":           User.query.count(),
        "courses":         Course.query.count(),
        "enrollments":     Enrollment.query.count(),
        "quizzes":         Quiz.query.count(),
        "mentors":         MentorProfile.query.filter_by(approved=True).count(),
        "pending_mentors": MentorProfile.query.filter_by(approved=False).count(),
        "doubts":          DoubtRequest.query.count(),
        "notes":           CourseNote.query.count(),
        "certificates":    Certificate.query.count(),
    }
    top_courses = (
        db.session.query(Course, db.func.count(Enrollment.id).label("cnt"))
        .join(Enrollment).group_by(Course.id)
        .order_by(text("cnt desc")).limit(5).all()
    )
    return render_template(
        "admin.html",
        stats=stats,
        recent_users=User.query.order_by(User.joined_at.desc()).limit(10).all(),
        top_courses=top_courses,
        pending_mentors=MentorProfile.query.filter_by(approved=False).all(),
        recent_doubts=DoubtRequest.query.order_by(DoubtRequest.created_at.desc()).limit(10).all(),
        all_courses=Course.query.all(),
        all_users=User.query.order_by(User.joined_at.desc()).all(),
        all_quizzes=Quiz.query.all(),
        all_notes=CourseNote.query.order_by(CourseNote.uploaded_at.desc()).all(),
        is_superadmin=(current_user.role == "superadmin"),
    )


# ── User Management (superadmin only) ────────────────────────────────────────

@bp.route("/user/<int:user_id>/role", methods=["POST"])
@login_required
@superadmin_required
def set_user_role(user_id):
    u = User.query.get_or_404(user_id)
    new_role = request.form.get("role", "user")
    if new_role not in ("user", "mentor", "admin", "superadmin"):
        flash("Invalid role.", "danger")
        return redirect(url_for("admin.dashboard") + "#users")
    # Prevent demoting yourself
    if u.id == current_user.id and new_role != "superadmin":
        flash("Cannot change your own superadmin role.", "warning")
        return redirect(url_for("admin.dashboard") + "#users")
    u.role = new_role
    db.session.commit()
    flash(f"Role updated to '{new_role}' for {u.name}.", "success")
    return redirect(url_for("admin.dashboard") + "#users")


@bp.route("/user/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@superadmin_required
def toggle_user_active(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash("Cannot deactivate yourself.", "warning")
        return redirect(url_for("admin.dashboard") + "#users")
    u.is_active = not u.is_active
    db.session.commit()
    flash(f"User {'activated' if u.is_active else 'deactivated'}.", "success")
    return redirect(url_for("admin.dashboard") + "#users")


@bp.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required
@superadmin_required
def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash("Cannot delete yourself.", "warning")
        return redirect(url_for("admin.dashboard") + "#users")
    db.session.delete(u)
    db.session.commit()
    flash("User deleted.", "info")
    return redirect(url_for("admin.dashboard") + "#users")


# ── Course Management ─────────────────────────────────────────────────────────

@bp.route("/course/add", methods=["POST"])
@login_required
@admin_required
def add_course():
    c = Course(
        title=request.form["title"],
        description=request.form["description"],
        category=request.form["category"],
        level=request.form.get("level", "Beginner"),
        instructor=request.form.get("instructor", "SkillBridge Faculty"),
        youtube_id=request.form.get("youtube_id", ""),
        modules="[]",
    )
    db.session.add(c)
    db.session.commit()
    flash("Course added.", "success")
    return redirect(url_for("admin.dashboard") + "#courses")


@bp.route("/course/<int:course_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_course(course_id):
    c = Course.query.get_or_404(course_id)
    c.title       = request.form.get("title", c.title).strip()
    c.description = request.form.get("description", c.description).strip()
    c.category    = request.form.get("category", c.category).strip()
    c.level       = request.form.get("level", c.level)
    c.instructor  = request.form.get("instructor", c.instructor).strip()
    c.youtube_id  = request.form.get("youtube_id", c.youtube_id).strip()
    db.session.commit()
    flash("Course updated.", "success")
    return redirect(url_for("admin.dashboard") + "#courses")


@bp.route("/course/<int:course_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_course(course_id):
    c = Course.query.get_or_404(course_id)
    db.session.delete(c)
    db.session.commit()
    flash("Course deleted.", "info")
    return redirect(url_for("admin.dashboard") + "#courses")


# ── Mentor Management ─────────────────────────────────────────────────────────

@bp.route("/mentor/<int:mentor_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_mentor(mentor_id):
    m = MentorProfile.query.get_or_404(mentor_id)
    m.approved = True
    m.user.role = "mentor"
    db.session.commit()
    flash("Mentor approved.", "success")
    return redirect(url_for("admin.dashboard") + "#mentors")


@bp.route("/mentor/<int:mentor_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_mentor(mentor_id):
    m = MentorProfile.query.get_or_404(mentor_id)
    db.session.delete(m)
    db.session.commit()
    flash("Mentor application rejected.", "info")
    return redirect(url_for("admin.dashboard") + "#mentors")


# ── Doubt Management ──────────────────────────────────────────────────────────

@bp.route("/doubt/<int:doubt_id>/reply", methods=["POST"])
@login_required
@admin_required
def reply_doubt(doubt_id):
    d = DoubtRequest.query.get_or_404(doubt_id)
    d.reply  = request.form.get("reply", "").strip()
    d.status = "answered"
    db.session.commit()
    flash("Reply sent.", "success")
    return redirect(url_for("admin.dashboard") + "#doubts")


# ── Quiz Management ───────────────────────────────────────────────────────────

@bp.route("/quiz/<int:quiz_id>/question/add", methods=["POST"])
@login_required
@admin_required
def add_question(quiz_id):
    Quiz.query.get_or_404(quiz_id)
    q = QuizQuestion(
        quiz_id=quiz_id,
        question=request.form["question"],
        option_a=request.form["option_a"],
        option_b=request.form["option_b"],
        option_c=request.form["option_c"],
        option_d=request.form["option_d"],
        correct=request.form["correct"],
        explanation=request.form.get("explanation", ""),
    )
    db.session.add(q)
    db.session.commit()
    flash("Question added.", "success")
    return redirect(url_for("admin.dashboard") + "#quizzes")


@bp.route("/question/<int:q_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_question(q_id):
    q = QuizQuestion.query.get_or_404(q_id)
    db.session.delete(q)
    db.session.commit()
    flash("Question deleted.", "info")
    return redirect(url_for("admin.dashboard") + "#quizzes")


# ── Notes Management ──────────────────────────────────────────────────────────

@bp.route("/notes/upload", methods=["POST"])
@login_required
@admin_required
def upload_notes():
    course_id = request.form.get("course_id", type=int)
    title     = request.form.get("title", "").strip()
    language  = request.form.get("language", "en")
    file      = request.files.get("file")
    if not file or not title or not course_id:
        flash("All fields required.", "error")
        return redirect(url_for("admin.dashboard") + "#notes")
    try:
        prefix = f"note_{course_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        fname  = save_upload(file, prefix)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("admin.dashboard") + "#notes")
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], fname)
    note = CourseNote(course_id=course_id, title=title, filename=fname,
                      language=language, file_size=os.path.getsize(path))
    db.session.add(note)
    db.session.commit()
    flash("Notes uploaded.", "success")
    return redirect(url_for("admin.dashboard") + "#notes")


@bp.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_note(note_id):
    note = CourseNote.query.get_or_404(note_id)
    try:
        os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], note.filename))
    except OSError:
        pass
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted.", "info")
    return redirect(url_for("admin.dashboard") + "#notes")
