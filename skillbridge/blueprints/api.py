"""blueprints/api.py — JSON API, analytics, skill-path, quiz, and leaderboard routes."""
import os
import random
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from ..extensions import db
from ..models import (Enrollment, CompletedModule, Course, UserProfile, UserBadge,
                      PathStepProgress, SkillPathEnrollment, QuizAttempt,
                      LearningAnalytics)
from ..data import (SKILL_RECOMMENDATIONS, SUPPORTED_LANGUAGES, SKILL_PATHS,
                    PATH_NOTES, SUBTITLE_LANGS, NEXT_STEP_MSG, I18N,
                    get_videos_for_course)

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/progress/<int:course_id>", methods=["POST"])
@login_required
def update_progress(course_id):
    data       = request.get_json()
    progress   = int(data.get("progress", 0))
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if enrollment:
        enrollment.progress = max(enrollment.progress, min(100, progress))
        db.session.commit()
        return jsonify({"status": "ok", "progress": enrollment.progress})
    return jsonify({"status": "error"}), 404


@bp.route("/recommend")
@login_required
def recommend():
    interest = current_user.interest
    recs     = SKILL_RECOMMENDATIONS.get(interest, SKILL_RECOMMENDATIONS["Technology"])
    random.shuffle(recs)
    matched  = Course.query.filter_by(category=interest).all()
    return jsonify({
        "interest":        interest,
        "recommendations": recs[:3],
        "matched_courses": [{"id": c.id, "title": c.title, "level": c.level} for c in matched],
        "message":         f"Based on your interest in {interest}, we recommend these paths.",
    })


@bp.route("/set-language", methods=["POST"])
@login_required
def set_language():
    lang = (request.get_json() or {}).get("language", "en")
    if lang not in SUPPORTED_LANGUAGES:
        return jsonify({"status": "error", "message": "Unsupported language"}), 400
    current_user.language = lang
    db.session.commit()
    return jsonify({"status": "ok", "language": lang, "label": SUPPORTED_LANGUAGES[lang]})


@bp.route("/youtube-videos/<int:course_id>")
@login_required
def youtube_videos(course_id):
    course = Course.query.get_or_404(course_id)
    lang   = request.args.get("lang") or current_user.language or "en"
    return jsonify({
        "course_id": course_id,
        "language":  lang,
        "language_label": SUPPORTED_LANGUAGES.get(lang, "English"),
        "videos":    get_videos_for_course(course, lang),
        "using_api": bool(os.environ.get("YOUTUBE_API_KEY")),
    })


@bp.route("/mark-complete/<int:course_id>/<int:module_idx>", methods=["POST"])
@login_required
def mark_complete(course_id, module_idx):
    course = Course.query.get_or_404(course_id)
    total  = len(course.get_modules())
    if module_idx < 0 or module_idx >= total:
        return jsonify({"status": "error", "message": "Invalid module index"}), 400
    if CompletedModule.query.filter_by(
        user_id=current_user.id, course_id=course_id, module_idx=module_idx
    ).first():
        return jsonify({"status": "already_done"}), 200
    db.session.add(CompletedModule(
        user_id=current_user.id, course_id=course_id, module_idx=module_idx
    ))
    done_count   = CompletedModule.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).count() + 1
    new_progress = min(100, round(done_count / total * 100))
    enrollment   = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if enrollment:
        enrollment.progress = max(enrollment.progress, new_progress)
    db.session.commit()
    return jsonify({"status": "ok", "progress": enrollment.progress if enrollment else new_progress})


@bp.route("/completed-modules/<int:course_id>")
@login_required
def completed_modules(course_id):
    rows = CompletedModule.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).all()
    return jsonify({"completed": [r.module_idx for r in rows]})


@bp.route("/leaderboard")
@login_required
def leaderboard():
    top = (db.session.query(UserProfile, db.session.query(db.Model.metadata.tables["users"])
                            .filter_by(id=UserProfile.user_id).subquery())
           .order_by(UserProfile.xp.desc()).limit(10).all())
    # Simpler query using join
    from ..models import User
    top = (db.session.query(UserProfile, User)
           .join(User, User.id == UserProfile.user_id)
           .order_by(UserProfile.xp.desc()).limit(10).all())
    return jsonify([
        {"name": u.name, "xp": p.xp, "streak": p.streak,
         "badges": UserBadge.query.filter_by(user_id=u.id).count()}
        for p, u in top
    ])


@bp.route("/skill-paths/<slug>/complete-step", methods=["POST"])
@login_required
def complete_path_step(slug):
    from ..gamification import award_xp
    path = next((p for p in SKILL_PATHS if p["slug"] == slug), None)
    if not path:
        return jsonify({"error": "not found"}), 404
    step_index = (request.get_json() or {}).get("step_index")
    if step_index is None or not (0 <= step_index < len(path["steps"])):
        return jsonify({"error": "invalid step"}), 400
    if not PathStepProgress.query.filter_by(
        user_id=current_user.id, path_slug=slug, step_index=step_index
    ).first():
        db.session.add(PathStepProgress(
            user_id=current_user.id, path_slug=slug, step_index=step_index
        ))
        db.session.commit()
        total_done = PathStepProgress.query.filter_by(user_id=current_user.id).count()
        badge      = "first_step" if total_done == 1 else None
        path_done  = PathStepProgress.query.filter_by(
            user_id=current_user.id, path_slug=slug
        ).count()
        if path_done == len(path["steps"]):
            badge = "path_complete"
        award_xp(current_user.id, 30, badge)
    done = PathStepProgress.query.filter_by(user_id=current_user.id, path_slug=slug).count()
    return jsonify({"progress_pct": round(done / len(path["steps"]) * 100), "done": done})


@bp.route("/skill-paths/<slug>/next-step")
@login_required
def skill_path_next_step(slug):
    path = next((p for p in SKILL_PATHS if p["slug"] == slug), None)
    if not path:
        return jsonify({"error": "not found"}), 404
    lang      = current_user.language if current_user.language in NEXT_STEP_MSG else "en"
    completed = {r.step_index for r in PathStepProgress.query.filter_by(
        user_id=current_user.id, path_slug=slug).all()}
    next_idx  = next((i for i in range(len(path["steps"])) if i not in completed), None)
    if next_idx is None:
        return jsonify({"done": True, "message": I18N["step_done"][lang]})
    step = path["steps"][next_idx]
    return jsonify({
        "done": False, "step_index": next_idx,
        "title": step["title"], "desc": step["desc"],
        "message": NEXT_STEP_MSG[lang].format(title=step["title"], desc=step["desc"]),
        "label": I18N["next_step"][lang],
    })


@bp.route("/quiz-analytics/<int:course_id>")
@login_required
def quiz_analytics(course_id):
    attempts = QuizAttempt.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).order_by(QuizAttempt.attempted_at).all()
    return jsonify({
        "attempts": [
            {"score": a.score, "correct": a.correct_q, "total": a.total_q,
             "passed": a.passed, "date": a.attempted_at.strftime("%b %d")}
            for a in attempts
        ],
        "best_score":     max((a.score for a in attempts), default=0),
        "total_attempts": len(attempts),
    })


@bp.route("/analytics/track", methods=["POST"])
@login_required
def track_analytics():
    data       = request.get_json(silent=True) or {}
    event_type = data.get("event_type")
    course_id  = data.get("course_id")
    if not event_type:
        return jsonify({"error": "event_type required"}), 400
    course = db.session.get(Course, course_id) if course_id else None
    db.session.add(LearningAnalytics(
        user_id    = current_user.id,
        course_id  = course_id,
        event_type = event_type,
        watch_secs = int(data.get("watch_secs", 0)),
        score      = int(data.get("score", 0)),
        category   = course.category if course else data.get("category", ""),
    ))
    db.session.commit()
    return jsonify({"ok": True})
