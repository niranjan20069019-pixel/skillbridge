"""blueprints/main.py — Page routes: dashboard, courses, quiz, mentors, skill paths, analytics."""
import os
import uuid
from datetime import datetime, timedelta
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify, abort, current_app)
from flask_login import login_required, current_user
from sqlalchemy import func
from ..extensions import db
from ..models import (User, Course, Enrollment, CompletedModule, Certificate,
                      Quiz, QuizQuestion, QuizAttempt, UserProfile, UserBadge,
                      MentorProfile, MentorRating, DoubtRequest,
                      SkillPathEnrollment, PathStepProgress, LearningAnalytics,
                      CourseNote, Badge)
from ..data import (SKILL_RECOMMENDATIONS, SKILL_PATHS, PATH_NOTES,
                    SUBTITLE_LANGS, COURSE_NOTES, I18N)
from ..gamification import get_or_create_profile, award_xp

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    from ..app import app as _app  # avoid circular — use current_app instead
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    enrollments  = Enrollment.query.filter_by(user_id=current_user.id).all()
    profile      = get_or_create_profile(current_user.id)
    my_badges    = UserBadge.query.filter_by(user_id=current_user.id).all()
    skill_score  = min(100, profile.xp // 10)
    now          = datetime.utcnow()
    return render_template("dashboard.html",
        enrollments=enrollments, profile=profile,
        my_badges=my_badges, skill_score=skill_score, now=now,
    )


@bp.route("/courses")
def courses():
    category = request.args.get("category", "")
    q        = Course.query
    if category:
        q = q.filter_by(category=category)
    all_courses = q.all()
    categories  = db.session.query(Course.category).distinct().all()
    return render_template("courses.html", courses=all_courses,
                           categories=[c[0] for c in categories],
                           selected_category=category)


@bp.route("/learn/<int:course_id>")
@login_required
def learn(course_id):
    course     = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if not enrollment:
        flash("Please enroll in this course first.", "warning")
        return redirect(url_for("main.courses"))
    notes_files = CourseNote.query.filter_by(course_id=course_id).all()
    lang        = current_user.language if current_user.language in ("en","hi","kn","ta","te") else "en"
    course_notes = COURSE_NOTES.get(course.title, "")
    return render_template("learn.html", course=course, enrollment=enrollment,
                           notes_files=notes_files, course_notes=course_notes,
                           lang=lang, I18N=I18N)


@bp.route("/enroll/<int:course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    if not Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first():
        db.session.add(Enrollment(user_id=current_user.id, course_id=course_id))
        db.session.commit()
        award_xp(current_user.id, 10, "first_enroll")
        flash(f"Enrolled in {course.title}! 🎉", "success")
    return redirect(url_for("main.learn", course_id=course_id))


@bp.route("/skill-paths")
@login_required
def skill_paths():
    enrolled_slugs = {
        e.path_slug for e in SkillPathEnrollment.query.filter_by(user_id=current_user.id).all()
    }
    progress_map = {}
    for slug in enrolled_slugs:
        path = next((p for p in SKILL_PATHS if p["slug"] == slug), None)
        if path:
            done = PathStepProgress.query.filter_by(
                user_id=current_user.id, path_slug=slug
            ).count()
            progress_map[slug] = round(done / len(path["steps"]) * 100)
    return render_template("skill_paths.html", paths=SKILL_PATHS,
                           enrolled_slugs=enrolled_slugs, progress_map=progress_map)


@bp.route("/skill-paths/<slug>")
@login_required
def skill_path_detail(slug):
    path = next((p for p in SKILL_PATHS if p["slug"] == slug), None)
    if not path:
        abort(404)
    enrolled = SkillPathEnrollment.query.filter_by(
        user_id=current_user.id, path_slug=slug
    ).first()
    completed_steps = {
        r.step_index for r in PathStepProgress.query.filter_by(
            user_id=current_user.id, path_slug=slug
        ).all()
    }
    total        = len(path["steps"])
    progress_pct = round(len(completed_steps) / total * 100) if total else 0
    lang         = current_user.language if current_user.language in ("en","hi","kn","ta","te") else "en"
    path_notes   = PATH_NOTES.get(slug, {}).get(lang, PATH_NOTES.get(slug, {}).get("en", ""))
    subtitle_lang = SUBTITLE_LANGS.get(lang, "en")
    return render_template("skill_path_detail.html", path=path, enrolled=enrolled,
                           completed_steps=completed_steps, progress_pct=progress_pct,
                           path_notes=path_notes, subtitle_lang=subtitle_lang)


@bp.route("/skill-paths/<slug>/enroll", methods=["POST"])
@login_required
def enroll_skill_path(slug):
    if not any(p["slug"] == slug for p in SKILL_PATHS):
        abort(404)
    if not SkillPathEnrollment.query.filter_by(
        user_id=current_user.id, path_slug=slug
    ).first():
        db.session.add(SkillPathEnrollment(user_id=current_user.id, path_slug=slug))
        db.session.commit()
        flash("You've enrolled in this skill path! 🚀", "success")
    return redirect(url_for("main.skill_path_detail", slug=slug))


@bp.route("/mentors")
@login_required
def mentors():
    approved = MentorProfile.query.filter_by(approved=True).all()
    return render_template("mentors.html", mentors=approved)


@bp.route("/mentors/apply", methods=["GET", "POST"])
@login_required
def mentor_apply():
    if request.method == "POST":
        existing = MentorProfile.query.filter_by(user_id=current_user.id).first()
        if existing:
            flash("You have already applied.", "warning")
            return redirect(url_for("main.mentors"))
        db.session.add(MentorProfile(
            user_id=current_user.id,
            bio=request.form.get("bio", ""),
            skills=request.form.get("skills", ""),
            experience=request.form.get("experience", ""),
            linkedin=request.form.get("linkedin", ""),
        ))
        db.session.commit()
        flash("Application submitted! An admin will review it shortly.", "success")
        return redirect(url_for("main.mentors"))
    return render_template("mentor_apply.html")


@bp.route("/mentors/<int:mentor_id>/rate", methods=["POST"])
@login_required
def rate_mentor(mentor_id):
    mentor = MentorProfile.query.get_or_404(mentor_id)
    rating = int(request.form.get("rating", 5))
    existing = MentorRating.query.filter_by(
        mentor_id=mentor_id, user_id=current_user.id
    ).first()
    if existing:
        existing.rating  = rating
        existing.comment = request.form.get("comment", "")
    else:
        db.session.add(MentorRating(
            mentor_id=mentor_id, user_id=current_user.id,
            rating=rating, comment=request.form.get("comment", ""),
        ))
    db.session.commit()
    # Recalculate avg
    avg = db.session.query(func.avg(MentorRating.rating)).filter_by(
        mentor_id=mentor_id
    ).scalar() or 0
    mentor.avg_rating = round(float(avg), 1)
    db.session.commit()
    flash("Rating submitted!", "success")
    return redirect(url_for("main.mentors"))


@bp.route("/mentors/<int:mentor_id>/doubt", methods=["POST"])
@login_required
def submit_doubt(mentor_id):
    MentorProfile.query.get_or_404(mentor_id)
    db.session.add(DoubtRequest(
        user_id=current_user.id, mentor_id=mentor_id,
        subject=request.form.get("subject", ""),
        message=request.form.get("message", ""),
    ))
    db.session.commit()
    flash("Doubt submitted! Your mentor will respond soon.", "success")
    return redirect(url_for("main.mentors"))


@bp.route("/quiz/<int:course_id>")
@login_required
def take_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    quiz   = Quiz.query.filter_by(course_id=course_id).first()
    if not quiz:
        flash("No quiz available for this course yet.", "info")
        return redirect(url_for("main.learn", course_id=course_id))
    questions = quiz.questions.all()
    return render_template("quiz.html", course=course, quiz=quiz, questions=questions)


@bp.route("/quiz/<int:course_id>/submit", methods=["POST"])
@login_required
def submit_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    quiz   = Quiz.query.filter_by(course_id=course_id).first_or_404()
    questions = quiz.questions.all()
    correct_q = sum(
        1 for q in questions
        if request.form.get(f"q_{q.id}") == q.correct
    )
    total_q  = len(questions)
    score    = round(correct_q / total_q * 100) if total_q else 0
    passed   = score >= quiz.pass_pct
    attempt  = QuizAttempt(
        user_id=current_user.id, course_id=course_id, quiz_id=quiz.id,
        score=score, total_q=total_q, correct_q=correct_q, passed=passed,
    )
    db.session.add(attempt)
    # Track analytics
    db.session.add(LearningAnalytics(
        user_id=current_user.id, course_id=course_id,
        event_type="quiz_pass" if passed else "quiz_fail",
        score=score, category=course.category,
    ))
    if passed:
        award_xp(current_user.id, 50, "quiz_master")
        # Issue certificate if course complete
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id, course_id=course_id
        ).first()
        if enrollment and enrollment.progress >= 100:
            if not Certificate.query.filter_by(
                user_id=current_user.id, course_id=course_id
            ).first():
                db.session.add(Certificate(
                    user_id=current_user.id, course_id=course_id,
                    cert_id=str(uuid.uuid4()),
                ))
    db.session.commit()
    return render_template("quiz_result.html", course=course, quiz=quiz,
                           score=score, passed=passed, correct_q=correct_q,
                           total_q=total_q, questions=questions,
                           answers={f"q_{q.id}": request.form.get(f"q_{q.id}") for q in questions})


@bp.route("/certificate/<int:course_id>")
@login_required
def certificate(course_id):
    cert = Certificate.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first_or_404()
    return render_template("certificate.html", cert=cert)


@bp.route("/gamification")
@login_required
def gamification():
    from ..models import User as _User
    profile    = get_or_create_profile(current_user.id)
    my_badges  = UserBadge.query.filter_by(user_id=current_user.id).all()
    earned_ids = {ub.badge_id for ub in my_badges}
    all_badges = Badge.query.all()
    top = (db.session.query(UserProfile, _User)
           .join(_User, _User.id == UserProfile.user_id)
           .order_by(UserProfile.xp.desc()).limit(20).all())
    rank = next((i+1 for i, (p, _) in enumerate(top) if p.user_id == current_user.id), None)
    return render_template("gamification.html", profile=profile, my_badges=my_badges,
                           earned_ids=earned_ids, all_badges=all_badges,
                           leaderboard=top, my_rank=rank)


@bp.route("/analytics")
@login_required
def analytics():
    uid         = current_user.id
    watch_rows  = LearningAnalytics.query.filter_by(user_id=uid, event_type="watch").all()
    total_watch_min = round(sum(r.watch_secs for r in watch_rows) / 60)
    attempts    = QuizAttempt.query.filter_by(user_id=uid).order_by(QuizAttempt.attempted_at).all()
    quiz_data   = [{"course": a.course.title if a.course else "Unknown",
                    "score": a.score, "passed": a.passed,
                    "date": a.attempted_at.strftime("%d %b")} for a in attempts]
    cat_scores  = (db.session.query(LearningAnalytics.category,
                                    func.avg(LearningAnalytics.score).label("avg_score"))
                   .filter(LearningAnalytics.user_id == uid,
                           LearningAnalytics.event_type.in_(["quiz_pass","quiz_fail"]))
                   .group_by(LearningAnalytics.category).all())
    weak_skills = [c for c, avg in cat_scores if avg is not None and avg < 60]
    thirty_ago  = datetime.utcnow() - timedelta(days=30)
    active_days = (db.session.query(func.date(LearningAnalytics.recorded_at))
                   .filter(LearningAnalytics.user_id == uid,
                           LearningAnalytics.recorded_at >= thirty_ago)
                   .distinct().count())
    enrollments = Enrollment.query.filter_by(user_id=uid).all()
    interest    = current_user.interest or "Technology"
    recs        = SKILL_RECOMMENDATIONS.get(interest, [])
    if weak_skills:
        recs = SKILL_RECOMMENDATIONS.get(weak_skills[0], recs)
    watch_by_day = {}
    for r in watch_rows:
        day = r.recorded_at.strftime("%a")
        watch_by_day[day] = watch_by_day.get(day, 0) + round(r.watch_secs / 60)
    watch_chart = [{"day": d, "mins": watch_by_day.get(d, 0)}
                   for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]]
    return render_template("analytics.html",
        total_watch_min=total_watch_min, quiz_data=quiz_data,
        weak_skills=weak_skills, active_days=active_days,
        completed_courses=sum(1 for e in enrollments if e.progress >= 100),
        total_enrolled=len(enrollments), recommendations=recs[:3],
        watch_chart=watch_chart, enrollments=enrollments,
    )
