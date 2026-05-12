"""models.py — All SQLAlchemy models for SkillBridge."""
import json
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    interest      = db.Column(db.String(80), default="Technology")
    location      = db.Column(db.String(120), default="")
    language      = db.Column(db.String(10), default="en")
    joined_at     = db.Column(db.DateTime, default=datetime.utcnow)
    enrollments   = db.relationship("Enrollment", back_populates="user", lazy="dynamic")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Course(db.Model):
    __tablename__ = "courses"
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text, nullable=False)
    category     = db.Column(db.String(80), nullable=False)
    level        = db.Column(db.String(40), default="Beginner")
    duration_hrs = db.Column(db.Float, default=10.0)
    instructor   = db.Column(db.String(120), default="SkillBridge Faculty")
    thumbnail    = db.Column(db.String(300), default="")
    youtube_id   = db.Column(db.String(20), default="")
    modules      = db.Column(db.Text, default="[]")
    enrollments  = db.relationship("Enrollment", back_populates="course", lazy="dynamic")

    def get_modules(self):
        try:
            return json.loads(self.modules)
        except Exception:
            return []


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id   = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    progress    = db.Column(db.Integer, default=0)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    user        = db.relationship("User", back_populates="enrollments")
    course      = db.relationship("Course", back_populates="enrollments")


class CompletedModule(db.Model):
    __tablename__ = "completed_modules"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id  = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    module_idx = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", "module_idx", name="uq_user_course_module"),
    )


class Certificate(db.Model):
    __tablename__ = "certificates"
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    cert_id   = db.Column(db.String(36), unique=True, nullable=False)
    user      = db.relationship("User")
    course    = db.relationship("Course")
    __table_args__ = (db.UniqueConstraint("user_id", "course_id", name="uq_cert_user_course"),)


class JobPosting(db.Model):
    __tablename__ = "job_postings"
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    company     = db.Column(db.String(120), nullable=False)
    location    = db.Column(db.String(120), default="Remote")
    job_type    = db.Column(db.String(40), default="Full-time")
    category    = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default="")
    skills      = db.Column(db.String(300), default="")
    salary      = db.Column(db.String(80), default="")
    apply_url   = db.Column(db.String(300), default="#")
    posted_at   = db.Column(db.DateTime, default=datetime.utcnow)
    is_active   = db.Column(db.Boolean, default=True)


class Quiz(db.Model):
    __tablename__ = "quizzes"
    id        = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title     = db.Column(db.String(200), nullable=False)
    time_limit= db.Column(db.Integer, default=600)
    pass_pct  = db.Column(db.Integer, default=60)
    course    = db.relationship("Course")
    questions = db.relationship("QuizQuestion", backref="quiz", lazy="dynamic", cascade="all,delete")


class QuizQuestion(db.Model):
    __tablename__ = "quiz_questions"
    id          = db.Column(db.Integer, primary_key=True)
    quiz_id     = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question    = db.Column(db.Text, nullable=False)
    option_a    = db.Column(db.String(300), nullable=False)
    option_b    = db.Column(db.String(300), nullable=False)
    option_c    = db.Column(db.String(300), nullable=False)
    option_d    = db.Column(db.String(300), nullable=False)
    correct     = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text, default="")


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id    = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    quiz_id      = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=True)
    score        = db.Column(db.Integer, default=0)
    total_q      = db.Column(db.Integer, default=0)
    correct_q    = db.Column(db.Integer, default=0)
    passed       = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    user         = db.relationship("User")
    course       = db.relationship("Course")


class UserProfile(db.Model):
    __tablename__ = "user_profiles"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    bio          = db.Column(db.Text, default="")
    skills       = db.Column(db.String(500), default="")
    linkedin     = db.Column(db.String(200), default="")
    github       = db.Column(db.String(200), default="")
    avatar_color = db.Column(db.String(20), default="#22c55e")
    xp           = db.Column(db.Integer, default=0)
    streak       = db.Column(db.Integer, default=0)
    last_active  = db.Column(db.DateTime, default=datetime.utcnow)
    user         = db.relationship("User")


class CourseNote(db.Model):
    __tablename__ = "course_notes_files"
    id          = db.Column(db.Integer, primary_key=True)
    course_id   = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title       = db.Column(db.String(200), nullable=False)
    filename    = db.Column(db.String(200), nullable=False, unique=True)
    language    = db.Column(db.String(10), default="en")
    file_size   = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    downloads   = db.Column(db.Integer, default=0)
    course      = db.relationship("Course")


class SkillPathEnrollment(db.Model):
    __tablename__ = "skill_path_enrollments"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    path_slug    = db.Column(db.String(80), nullable=False)
    enrolled_at  = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("user_id", "path_slug", name="uq_user_path"),)


class Badge(db.Model):
    __tablename__ = "badges"
    id          = db.Column(db.Integer, primary_key=True)
    slug        = db.Column(db.String(60), unique=True, nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), default="")
    icon        = db.Column(db.String(10), default="🏅")
    xp_reward   = db.Column(db.Integer, default=0)


class UserBadge(db.Model):
    __tablename__ = "user_badges"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge_id   = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    earned_at  = db.Column(db.DateTime, default=datetime.utcnow)
    badge      = db.relationship("Badge")
    __table_args__ = (db.UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)


class MentorProfile(db.Model):
    __tablename__ = "mentor_profiles"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    bio         = db.Column(db.Text, default="")
    skills      = db.Column(db.String(300), default="")
    experience  = db.Column(db.String(100), default="")
    linkedin    = db.Column(db.String(200), default="")
    approved    = db.Column(db.Boolean, default=False)
    avg_rating  = db.Column(db.Float, default=0.0)
    user        = db.relationship("User")


class MentorRating(db.Model):
    __tablename__ = "mentor_ratings"
    id         = db.Column(db.Integer, primary_key=True)
    mentor_id  = db.Column(db.Integer, db.ForeignKey("mentor_profiles.id"), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating     = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.Text, default="")
    rated_at   = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("mentor_id", "user_id", name="uq_mentor_rating"),)


class DoubtRequest(db.Model):
    __tablename__ = "doubt_requests"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mentor_id   = db.Column(db.Integer, db.ForeignKey("mentor_profiles.id"), nullable=False)
    subject     = db.Column(db.String(200), nullable=False)
    message     = db.Column(db.Text, nullable=False)
    status      = db.Column(db.String(20), default="pending")
    reply       = db.Column(db.Text, default="")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    user        = db.relationship("User")
    mentor      = db.relationship("MentorProfile")


class PathStepProgress(db.Model):
    __tablename__ = "path_step_progress"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    path_slug  = db.Column(db.String(80), nullable=False)
    step_index = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.UniqueConstraint("user_id", "path_slug", "step_index", name="uq_user_path_step"),
    )


class LearningAnalytics(db.Model):
    __tablename__ = "learning_analytics"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id    = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=True)
    event_type   = db.Column(db.String(40), nullable=False)
    watch_secs   = db.Column(db.Integer, default=0)
    score        = db.Column(db.Integer, default=0)
    category     = db.Column(db.String(80), default="")
    recorded_at  = db.Column(db.DateTime, default=datetime.utcnow)
    user         = db.relationship("User")
