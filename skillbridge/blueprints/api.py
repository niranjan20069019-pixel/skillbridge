"""blueprints/api.py — JSON API: analytics, skill-path, quiz, leaderboard, translate, dashboard-stats."""
import os
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, abort, send_file
from flask_login import login_required, current_user
from sqlalchemy import func
from ..extensions import db
from ..models import (Enrollment, CompletedModule, Course, UserProfile, UserBadge,
                      PathStepProgress, SkillPathEnrollment, QuizAttempt,
                      LearningAnalytics, Certificate)
from ..data import (SKILL_RECOMMENDATIONS, SUPPORTED_LANGUAGES, SKILL_PATHS,
                    PATH_NOTES, SUBTITLE_LANGS, NEXT_STEP_MSG, I18N,
                    get_videos_for_course)
from ml_services import get_ai_recommendations, get_ai_chat_response

bp = Blueprint("api", __name__, url_prefix="/api")


# ── Progress ──────────────────────────────────────────────────────────────────

@bp.route("/progress/<int:course_id>", methods=["POST"])
@login_required
def update_progress(course_id):
    data       = request.get_json() or {}
    progress   = min(100, max(0, int(data.get("progress", 0))))
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if enrollment:
        enrollment.progress = max(enrollment.progress, progress)
        db.session.commit()
        return jsonify({"status": "ok", "progress": enrollment.progress})
    return jsonify({"status": "error"}), 404


# ── Recommendations ───────────────────────────────────────────────────────────

@bp.route("/recommend")
@login_required
def recommend():
    recs = get_ai_recommendations(current_user.id, 5)
    matched = Course.query.filter_by(category=current_user.interest).all()
    return jsonify({
        "interest": current_user.interest,
        "recommendations": recs,
        "matched_courses": [{"id": c.id, "title": c.title, "level": c.level} for c in matched[:3]],
        "message": "Based on your learning patterns and interests.",
    })


# ── AI Chat ───────────────────────────────────────────────────────────────────

@bp.route("/chat", methods=["POST"])
@login_required
def chat():
    data    = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400
    response = get_ai_chat_response(current_user.id, message)
    return jsonify({"reply": response, "timestamp": datetime.utcnow().isoformat()})


# ── Page Translation ──────────────────────────────────────────────────────────

@bp.route("/translate-page", methods=["POST"])
@login_required
def translate_page():
    """Batch-translate UI strings using OpenAI or a simple fallback."""
    data    = request.get_json(silent=True) or {}
    strings = data.get("strings", [])
    lang    = data.get("lang", "en")

    if not strings or lang == "en":
        return jsonify({"translated": strings})

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            joined = "\n".join(f"{i+1}. {s}" for i, s in enumerate(strings))
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": (
                        f"Translate the following numbered UI strings to {lang}. "
                        "Return ONLY the numbered list, same format, no extra text."
                    )},
                    {"role": "user", "content": joined},
                ],
                max_tokens=1000,
                temperature=0.2,
            )
            lines = resp.choices[0].message.content.strip().split("\n")
            translated = []
            for line in lines:
                # Strip leading "1. " etc.
                parts = line.split(". ", 1)
                translated.append(parts[1] if len(parts) == 2 else line)
            # Pad/trim to match input length
            while len(translated) < len(strings):
                translated.append(strings[len(translated)])
            return jsonify({"translated": translated[:len(strings)]})
        except Exception as e:
            print(f"[Translate] OpenAI error: {e}")

    # Fallback: return originals unchanged
    return jsonify({"translated": strings})


# ── Language ──────────────────────────────────────────────────────────────────

@bp.route("/set-language", methods=["POST"])
@login_required
def set_language():
    lang = (request.get_json() or {}).get("language", "en")
    if lang not in SUPPORTED_LANGUAGES:
        return jsonify({"status": "error", "message": "Unsupported language"}), 400
    current_user.language = lang
    db.session.commit()
    return jsonify({"status": "ok", "language": lang, "label": SUPPORTED_LANGUAGES[lang]})


# ── YouTube Videos ────────────────────────────────────────────────────────────

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


# ── Module Completion ─────────────────────────────────────────────────────────

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


# ── Leaderboard ───────────────────────────────────────────────────────────────

@bp.route("/leaderboard")
@login_required
def leaderboard():
    from ..models import User
    top = (db.session.query(UserProfile, User)
           .join(User, User.id == UserProfile.user_id)
           .order_by(UserProfile.xp.desc()).limit(10).all())
    return jsonify([
        {"name": u.name, "xp": p.xp, "streak": p.streak,
         "badges": UserBadge.query.filter_by(user_id=u.id).count()}
        for p, u in top
    ])


# ── Skill Paths ───────────────────────────────────────────────────────────────

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


# ── Quiz Analytics ────────────────────────────────────────────────────────────

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


# ── Analytics Tracking ────────────────────────────────────────────────────────

@bp.route("/analytics/track", methods=["POST"])
@login_required
def track_analytics():
    data       = request.get_json(silent=True) or {}
    event_type = data.get("event_type")
    course_id  = data.get("course_id")
    if not event_type:
        return jsonify({"error": "event_type required"}), 400
    course = db.session.get(Course, course_id) if course_id else None

    def _int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0
    db.session.add(LearningAnalytics(
        user_id    = current_user.id,
        course_id  = course_id,
        event_type = event_type,
        watch_secs = _int(data.get("watch_secs", 0)),
        score      = _int(data.get("score", 0)),
        category   = course.category if course else data.get("category", ""),
    ))
    db.session.commit()
    return jsonify({"ok": True})


# ── Dashboard Stats ───────────────────────────────────────────────────────────

@bp.route("/dashboard-stats")
@login_required
def dashboard_stats():
    """Return chart-ready data for the dashboard."""
    uid = current_user.id

    # Enrollment progress per course
    enrollments = Enrollment.query.filter_by(user_id=uid).all()
    course_progress = [
        {"title": e.course.title[:25], "progress": e.progress}
        for e in enrollments if e.course
    ]

    # Quiz scores over time
    attempts = (QuizAttempt.query.filter_by(user_id=uid)
                .order_by(QuizAttempt.attempted_at).limit(20).all())
    quiz_scores = [
        {"date": a.attempted_at.strftime("%b %d"), "score": a.score,
         "passed": a.passed, "course": (a.course.title[:20] if a.course else "?")}
        for a in attempts
    ]

    # Watch time by day of week
    thirty_ago = datetime.utcnow() - timedelta(days=30)
    watch_rows = LearningAnalytics.query.filter(
        LearningAnalytics.user_id == uid,
        LearningAnalytics.event_type == "watch",
        LearningAnalytics.recorded_at >= thirty_ago,
    ).all()
    day_map = {d: 0 for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
    for r in watch_rows:
        day = r.recorded_at.strftime("%a")
        day_map[day] = day_map.get(day, 0) + round(r.watch_secs / 60)
    watch_by_day = [{"day": d, "mins": m} for d, m in day_map.items()]

    # Category skill scores
    cat_scores = (
        db.session.query(
            LearningAnalytics.category,
            func.avg(LearningAnalytics.score).label("avg"),
        )
        .filter(
            LearningAnalytics.user_id == uid,
            LearningAnalytics.event_type.in_(["quiz_pass", "quiz_fail"]),
        )
        .group_by(LearningAnalytics.category)
        .all()
    )
    skill_scores = [
        {"category": c, "score": round(float(avg), 1)}
        for c, avg in cat_scores if avg is not None
    ]

    # Summary
    from ..gamification import get_or_create_profile
    profile = get_or_create_profile(uid)
    certs   = Certificate.query.filter_by(user_id=uid).count()

    return jsonify({
        "course_progress": course_progress,
        "quiz_scores":     quiz_scores,
        "watch_by_day":    watch_by_day,
        "skill_scores":    skill_scores,
        "summary": {
            "enrolled":   len(enrollments),
            "completed":  sum(1 for e in enrollments if e.progress >= 100),
            "xp":         profile.xp,
            "streak":     profile.streak,
            "certificates": certs,
        },
    })


# ── Quiz Translation ────────────────────────────────────────────────────────────

@bp.route("/translate-quiz/<int:course_id>")
@login_required
def translate_quiz(course_id):
    """Translate quiz questions for a course into the user's language."""
    from ..models import Quiz, QuizQuestion
    lang = request.args.get("lang", "en")
    if lang == "en":
        quiz = Quiz.query.filter_by(course_id=course_id).first()
        if not quiz:
            return jsonify({"translated": False, "questions": []})
        questions = quiz.questions.all()
        return jsonify({
            "translated": True,
            "questions": [
                {"id": q.id, "question": q.question,
                 "option_a": q.option_a, "option_b": q.option_b,
                 "option_c": q.option_c, "option_d": q.option_d}
                for q in questions
            ]
        })
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return jsonify({"translated": False, "questions": []})
    quiz = Quiz.query.filter_by(course_id=course_id).first()
    if not quiz:
        return jsonify({"translated": False, "questions": []})
    questions = quiz.questions.all()
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        texts = []
        for q in questions:
            texts.append(f"Q: {q.question}")
            texts.append(f"A: {q.option_a}")
            texts.append(f"B: {q.option_b}")
            texts.append(f"C: {q.option_c}")
            texts.append(f"D: {q.option_d}")
        joined = "\n".join(f"{i+1}. {s}" for i, s in enumerate(texts))
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    f"Translate the following quiz questions and options to {lang}. "
                    "Return ONLY the numbered list, same format, preserving the Q:/A:/B:/C:/D: prefixes."
                )},
                {"role": "user", "content": joined},
            ],
            max_tokens=2000,
            temperature=0.2,
        )
        lines = resp.choices[0].message.content.strip().split("\n")
        translated_texts = []
        for line in lines:
            parts = line.split(". ", 1)
            translated_texts.append(parts[1] if len(parts) == 2 else line)
        result = []
        per_q = 5
        for i, q in enumerate(questions):
            offset = i * per_q
            if offset + per_q <= len(translated_texts):
                result.append({
                    "id": q.id,
                    "question": translated_texts[offset].replace("Q: ", "", 1) if translated_texts[offset].startswith("Q:") else translated_texts[offset],
                    "option_a": translated_texts[offset+1].replace("A: ", "", 1) if translated_texts[offset+1].startswith("A:") else translated_texts[offset+1],
                    "option_b": translated_texts[offset+2].replace("B: ", "", 1) if translated_texts[offset+2].startswith("B:") else translated_texts[offset+2],
                    "option_c": translated_texts[offset+3].replace("C: ", "", 1) if translated_texts[offset+3].startswith("C:") else translated_texts[offset+3],
                    "option_d": translated_texts[offset+4].replace("D: ", "", 1) if translated_texts[offset+4].startswith("D:") else translated_texts[offset+4],
                })
            else:
                result.append({
                    "id": q.id, "question": q.question,
                    "option_a": q.option_a, "option_b": q.option_b,
                    "option_c": q.option_c, "option_d": q.option_d,
                })
        return jsonify({"translated": True, "questions": result})
    except Exception:
        return jsonify({"translated": False, "questions": []})


# ── Certificate PDF Download ──────────────────────────────────────────────────

@bp.route("/certificate/<int:course_id>/pdf")
@login_required
def certificate_pdf(course_id):
    from ..models import Certificate as Cert
    import io
    cert = Cert.query.filter_by(user_id=current_user.id, course_id=course_id).first_or_404()

    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                                 leftMargin=2*cm, rightMargin=2*cm,
                                 topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        center = ParagraphStyle("center", parent=styles["Normal"],
                                alignment=TA_CENTER, spaceAfter=10)
        title_style = ParagraphStyle("title", parent=styles["Title"],
                                     alignment=TA_CENTER, fontSize=32,
                                     textColor=colors.HexColor("#1e40af"),
                                     spaceAfter=6)
        sub_style = ParagraphStyle("sub", parent=styles["Normal"],
                                   alignment=TA_CENTER, fontSize=14,
                                   textColor=colors.HexColor("#374151"),
                                   spaceAfter=4)
        name_style = ParagraphStyle("name", parent=styles["Normal"],
                                    alignment=TA_CENTER, fontSize=26,
                                    textColor=colors.HexColor("#111827"),
                                    fontName="Helvetica-Bold", spaceAfter=6)

        story = [
            Spacer(1, 1*cm),
            Paragraph("SkillBridge", title_style),
            Paragraph("Certificate of Completion", sub_style),
            HRFlowable(width="80%", thickness=1, color=colors.HexColor("#2563eb")),
            Spacer(1, 0.5*cm),
            Paragraph("This is to certify that", center),
            Paragraph(cert.user.name, name_style),
            Paragraph("has successfully completed the course", center),
            Paragraph(f"<b>{cert.course.title}</b>", sub_style),
            Spacer(1, 0.4*cm),
            Paragraph(f"Issued on {cert.issued_at.strftime('%B %d, %Y')}", center),
            Paragraph(f"Certificate ID: {cert.cert_id}", center),
            Spacer(1, 0.5*cm),
            HRFlowable(width="80%", thickness=0.5, color=colors.HexColor("#d1d5db")),
            Spacer(1, 0.3*cm),
            Paragraph("SkillBridge Learning Platform · skillbridge.app", center),
        ]
        doc.build(story)
        buf.seek(0)
        return send_file(
            buf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"certificate_{cert.cert_id[:8]}.pdf",
        )
    except ImportError:
        return jsonify({"error": "reportlab not installed"}), 500
