import os
import sys
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".env"))
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, session, send_from_directory, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ── App Setup ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "skillbridge-dev-secret-2024")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    BASE_DIR, "instance", "skillbridge.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["GOOGLE_TRANSLATE_API_KEY"] = os.environ.get("GOOGLE_TRANSLATE_API_KEY", "")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
app.jinja_env.globals["enumerate"] = enumerate


@app.context_processor
def inject_lang():
    """Make current language and i18n helper available in every template."""
    from flask_login import current_user as cu
    lang = "en"
    if cu.is_authenticated and cu.language and cu.language in SUPPORTED_LANGUAGES:
        lang = cu.language
    def t(key):
        return I18N.get(key, {}).get(lang, I18N.get(key, {}).get("en", key))
    return {"lang": lang, "t": t, "SUPPORTED_LANGUAGES": SUPPORTED_LANGUAGES}

# ── Models ─────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    interest      = db.Column(db.String(80), default="Technology")
    location      = db.Column(db.String(120), default="")
    language      = db.Column(db.String(10), default="en")   # preferred language code
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
    modules      = db.Column(db.Text, default="[]")   # JSON list
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
    progress    = db.Column(db.Integer, default=0)        # 0-100
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    user        = db.relationship("User", back_populates="enrollments")
    course      = db.relationship("Course", back_populates="enrollments")


class CompletedModule(db.Model):
    """Tracks which modules a user has completed — one row per user+course+module."""
    __tablename__ = "completed_modules"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id  = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    module_idx = db.Column(db.Integer, nullable=False)   # 0-based index
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
    time_limit= db.Column(db.Integer, default=600)   # seconds
    pass_pct  = db.Column(db.Integer, default=60)    # % needed to pass
    course    = db.relationship("Course")
    questions = db.relationship("QuizQuestion", backref="quiz", lazy="dynamic", cascade="all,delete")


class QuizQuestion(db.Model):
    __tablename__ = "quiz_questions"
    id           = db.Column(db.Integer, primary_key=True)
    quiz_id      = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question     = db.Column(db.Text, nullable=False)
    option_a     = db.Column(db.String(300), nullable=False)
    option_b     = db.Column(db.String(300), nullable=False)
    option_c     = db.Column(db.String(300), nullable=False)
    option_d     = db.Column(db.String(300), nullable=False)
    correct      = db.Column(db.String(1), nullable=False)   # 'a','b','c','d'
    explanation  = db.Column(db.Text, default="")


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
    file_size   = db.Column(db.Integer, default=0)   # bytes
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
    skills      = db.Column(db.String(300), default="")   # comma-separated
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
    rating     = db.Column(db.Integer, nullable=False)   # 1-5
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
    status      = db.Column(db.String(20), default="pending")  # pending/answered/closed
    reply       = db.Column(db.Text, default="")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    user        = db.relationship("User")
    mentor      = db.relationship("MentorProfile")


class PathStepProgress(db.Model):
    """Tracks which steps a user has completed in a skill path."""
    __tablename__ = "path_step_progress"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    path_slug  = db.Column(db.String(80), nullable=False)
    step_index = db.Column(db.Integer, nullable=False)   # 0-based
    __table_args__ = (
        db.UniqueConstraint("user_id", "path_slug", "step_index", name="uq_user_path_step"),
    )


class LearningAnalytics(db.Model):
    """Tracks per-user learning events for analytics."""
    __tablename__ = "learning_analytics"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id    = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=True)
    event_type   = db.Column(db.String(40), nullable=False)  # watch, quiz_pass, quiz_fail, module_done
    watch_secs   = db.Column(db.Integer, default=0)          # seconds watched (for watch events)
    score        = db.Column(db.Integer, default=0)          # quiz score %
    category     = db.Column(db.String(80), default="")      # course category (for weak-skill calc)
    recorded_at  = db.Column(db.DateTime, default=datetime.utcnow)
    user         = db.relationship("User")


# ── Upload Config ──────────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "notes")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024   # 16 MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ── Seed Data ──────────────────────────────────────────────────────────────────
SEED_COURSES = [
    {
        "title": "Python for Data Science",
        "description": "Master Python fundamentals and data analysis with Pandas, NumPy, and Matplotlib. Build real-world projects from day one.",
        "category": "Technology",
        "level": "Beginner",
        "duration_hrs": 24.0,
        "instructor": "Shradha Khapra",
        "youtube_id": "t2ypzz6gJm0",
        "modules": json.dumps([
            {"title": "Introduction to Python", "duration": "1h 20m", "completed": True},
            {"title": "Variables & Data Types", "duration": "45m", "completed": True},
            {"title": "Control Flow & Loops", "duration": "1h 10m", "completed": False},
            {"title": "Functions & Modules", "duration": "1h 30m", "completed": False},
            {"title": "Data Analysis with Pandas", "duration": "2h 00m", "completed": False},
            {"title": "Visualization with Matplotlib", "duration": "1h 45m", "completed": False},
        ]),
    },
    {
        "title": "Digital Marketing Essentials",
        "description": "Learn SEO, social media marketing, Google Ads, and content strategy. Get certified and launch your first campaign.",
        "category": "Marketing",
        "level": "Beginner",
        "duration_hrs": 18.0,
        "instructor": "Rohit Verma",
        "youtube_id": "bixR-KIJKYM",
        "modules": json.dumps([
            {"title": "What is Digital Marketing?", "duration": "30m", "completed": True},
            {"title": "SEO Fundamentals", "duration": "1h 00m", "completed": False},
            {"title": "Social Media Strategy", "duration": "1h 20m", "completed": False},
            {"title": "Google Ads Basics", "duration": "1h 10m", "completed": False},
            {"title": "Email Marketing", "duration": "50m", "completed": False},
            {"title": "Analytics & Reporting", "duration": "45m", "completed": False},
        ]),
    },
    {
        "title": "Financial Literacy & Entrepreneurship",
        "description": "Understand budgeting, savings, micro-loans, and how to build a small business from scratch in rural India.",
        "category": "Finance",
        "level": "Beginner",
        "duration_hrs": 12.0,
        "instructor": "Meena Patel",
        "youtube_id": "ZoqgAy3h4OM",
        "modules": json.dumps([
            {"title": "Money Basics & Budgeting", "duration": "40m", "completed": False},
            {"title": "Savings & Investment 101", "duration": "50m", "completed": False},
            {"title": "Micro-loans & SHG Programs", "duration": "45m", "completed": False},
            {"title": "Starting Your Business", "duration": "1h 00m", "completed": False},
            {"title": "Record Keeping & GST Basics", "duration": "55m", "completed": False},
        ]),
    },
    {
        "title": "Spoken English & Communication",
        "description": "Build confidence in English communication. Master professional writing, interviews, and public speaking.",
        "category": "Language",
        "level": "Beginner",
        "duration_hrs": 20.0,
        "instructor": "Rachel's English",
        "youtube_id": "9RCuRUKSRt8",
        "modules": json.dumps([
            {"title": "English Pronunciation Basics", "duration": "35m", "completed": False},
            {"title": "Everyday Conversations", "duration": "1h 00m", "completed": False},
            {"title": "Grammar in Context", "duration": "50m", "completed": False},
            {"title": "Professional Email Writing", "duration": "40m", "completed": False},
            {"title": "Interview Skills", "duration": "1h 10m", "completed": False},
        ]),
    },
    {
        "title": "Web Development Bootcamp",
        "description": "Build modern, responsive websites with HTML, CSS, and JavaScript. No prior experience required.",
        "category": "Technology",
        "level": "Intermediate",
        "duration_hrs": 32.0,
        "instructor": "Karan Mehta",
        "youtube_id": "ysEN5RaKOlA",
        "modules": json.dumps([
            {"title": "HTML5 Structure", "duration": "1h 00m", "completed": False},
            {"title": "CSS3 & Flexbox", "duration": "1h 30m", "completed": False},
            {"title": "JavaScript Essentials", "duration": "2h 00m", "completed": False},
            {"title": "Responsive Design", "duration": "1h 20m", "completed": False},
            {"title": "Building Your Portfolio", "duration": "1h 45m", "completed": False},
        ]),
    },
    {
        "title": "Sustainable Agriculture & AgriTech",
        "description": "Modern farming techniques, soil health, drip irrigation, and using mobile apps for smarter agriculture.",
        "category": "Agriculture",
        "level": "Beginner",
        "duration_hrs": 15.0,
        "instructor": "Dr. Suresh Naik",
        "youtube_id": "iloAQmroRK0",
        "modules": json.dumps([
            {"title": "Soil Health & Testing", "duration": "50m", "completed": False},
            {"title": "Drip Irrigation Setup", "duration": "1h 10m", "completed": False},
            {"title": "Organic Farming Basics", "duration": "45m", "completed": False},
            {"title": "AgriTech Apps & Tools", "duration": "40m", "completed": False},
            {"title": "Market Linkage & MSP", "duration": "35m", "completed": False},
        ]),
    },
]

SKILL_RECOMMENDATIONS = {
    "Technology":    ["Python for Data Science", "Web Development Bootcamp", "Cybersecurity Basics"],
    "Marketing":     ["Digital Marketing Essentials", "Content Creation", "E-Commerce Strategy"],
    "Finance":       ["Financial Literacy & Entrepreneurship", "Stock Market Basics", "GST & Accounting"],
    "Language":      ["Spoken English & Communication", "Business Writing", "Hindi for Professionals"],
    "Agriculture":   ["Sustainable Agriculture & AgriTech", "Horticulture 101", "Dairy Farming Basics"],
    "Healthcare":    ["Community Health Worker Training", "First Aid & Nutrition", "Mental Health Awareness"],
}

# ── Skill Paths ────────────────────────────────────────────────────────────────
SKILL_PATHS = [
    {
        "slug": "frontend-developer", "title": "Frontend Developer",
        "icon": "🌐", "color": "#3b82f6",
        "description": "Go from zero to job-ready frontend developer. Master HTML, CSS, JavaScript and modern frameworks.",
        "duration": "6 months", "level": "Beginner → Intermediate",
        "jobs": ["Frontend Developer", "UI Developer", "Web Designer"],
        "steps": [
            {
                "title": "HTML5 Fundamentals", "desc": "Structure web pages with semantic HTML5.",
                "duration": "2 weeks", "course": "Web Development Bootcamp", "milestone": False,
                "lessons": ["What is HTML?", "Tags & Attributes", "Headings, Paragraphs & Links",
                            "Lists & Tables", "Forms & Inputs", "Semantic HTML5 Elements"],
                "quiz": [
                    {"q": "Which tag defines the largest heading?", "options": ["<h6>","<h1>","<head>","<title>"], "answer": 1},
                    {"q": "Which attribute makes a link open in a new tab?", "options": ["href","src","target='_blank'","rel"], "answer": 2},
                    {"q": "Which tag is used for an unordered list?", "options": ["<ol>","<li>","<ul>","<list>"], "answer": 2},
                ],
            },
            {
                "title": "CSS3 & Responsive Design", "desc": "Style and layout with CSS3, Flexbox, Grid.",
                "duration": "3 weeks", "course": "Web Development Bootcamp", "milestone": False,
                "lessons": ["Selectors & Specificity", "Box Model", "Flexbox Layout",
                            "CSS Grid", "Media Queries", "CSS Variables & Animations"],
                "quiz": [
                    {"q": "Which CSS property controls text colour?", "options": ["font-color","text-color","color","foreground"], "answer": 2},
                    {"q": "What does 'display: flex' do?", "options": ["Hides element","Creates flex container","Adds border","Centres text"], "answer": 1},
                    {"q": "Which unit is relative to the viewport width?", "options": ["px","em","vw","rem"], "answer": 2},
                ],
            },
            {
                "title": "JavaScript Essentials", "desc": "Add interactivity with modern JavaScript (ES6+).",
                "duration": "4 weeks", "course": "Web Development Bootcamp", "milestone": True,
                "lessons": ["Variables & Data Types", "Functions & Scope", "DOM Manipulation",
                            "Events & Listeners", "Fetch API & Promises", "ES6+ Features"],
                "quiz": [
                    {"q": "Which method adds an event listener?", "options": ["element.on()","element.listen()","element.addEventListener()","element.bind()"], "answer": 2},
                    {"q": "What does 'const' do?", "options": ["Declares a variable","Declares a constant","Creates a function","Imports a module"], "answer": 1},
                    {"q": "Which method fetches data from an API?", "options": ["get()","fetch()","request()","load()"], "answer": 1},
                ],
            },
            {
                "title": "Version Control with Git", "desc": "Track changes and collaborate using Git & GitHub.",
                "duration": "1 week", "course": None, "milestone": False,
                "lessons": ["Git Init & Commit", "Branching & Merging", "Push to GitHub", "Pull Requests"],
                "quiz": [
                    {"q": "Which command stages all changes?", "options": ["git commit","git add .","git push","git pull"], "answer": 1},
                    {"q": "Which command creates a new branch?", "options": ["git branch new","git checkout -b new","git new branch","git create new"], "answer": 1},
                ],
            },
            {
                "title": "React Basics", "desc": "Build component-based UIs with React.",
                "duration": "4 weeks", "course": None, "milestone": True,
                "lessons": ["JSX & Components", "Props & State", "useEffect Hook",
                            "Event Handling", "Conditional Rendering", "Fetching Data in React"],
                "quiz": [
                    {"q": "What is JSX?", "options": ["A database","JavaScript XML syntax","A CSS framework","A testing tool"], "answer": 1},
                    {"q": "Which hook manages component state?", "options": ["useEffect","useRef","useState","useContext"], "answer": 2},
                    {"q": "How do you pass data to a child component?", "options": ["state","props","context only","localStorage"], "answer": 1},
                ],
            },
            {
                "title": "Portfolio Project", "desc": "Build and deploy a real-world portfolio site.",
                "duration": "2 weeks", "course": None, "milestone": True,
                "lessons": ["Plan Your Portfolio", "Build with HTML/CSS/JS", "Add React Components",
                            "Deploy on Netlify/Vercel", "Write a README", "Share on LinkedIn"],
                "quiz": [
                    {"q": "Which platform offers free static site hosting?", "options": ["AWS EC2","Netlify","Heroku paid","DigitalOcean"], "answer": 1},
                    {"q": "What should a portfolio README include?", "options": ["Only screenshots","Project description, setup steps, live link","Your salary","Nothing"], "answer": 1},
                ],
            },
        ],
    },
    {
        "slug": "data-analyst", "title": "Data Analyst",
        "icon": "📊", "color": "#22c55e",
        "description": "Learn to collect, clean, analyse and visualise data to drive business decisions.",
        "duration": "5 months", "level": "Beginner → Intermediate",
        "jobs": ["Data Analyst", "Business Analyst", "BI Developer"],
        "steps": [
            {
                "title": "Python Basics", "desc": "Learn Python syntax, data types and control flow.",
                "duration": "3 weeks", "course": "Python for Data Science", "milestone": False,
                "lessons": ["Variables & Types", "Lists & Dicts", "Loops & Conditionals",
                            "Functions", "File I/O", "Error Handling"],
                "quiz": [
                    {"q": "Which function prints output in Python?", "options": ["echo()","print()","console.log()","write()"], "answer": 1},
                    {"q": "What does len([1,2,3]) return?", "options": ["2","4","3","0"], "answer": 2},
                    {"q": "How do you create a dictionary?", "options": ["[]","()","{}","<>"], "answer": 2},
                ],
            },
            {
                "title": "Data Wrangling with Pandas", "desc": "Clean and transform datasets using Pandas.",
                "duration": "3 weeks", "course": "Python for Data Science", "milestone": True,
                "lessons": ["DataFrames & Series", "Reading CSV/Excel", "Filtering & Sorting",
                            "Handling Missing Data", "GroupBy & Aggregation", "Merging DataFrames"],
                "quiz": [
                    {"q": "Which method reads a CSV in Pandas?", "options": ["pd.open_csv()","pd.load()","pd.read_csv()","pd.import()"], "answer": 2},
                    {"q": "Which method drops rows with NaN?", "options": ["df.remove()","df.dropna()","df.clean()","df.fillna()"], "answer": 1},
                    {"q": "Which method groups data?", "options": ["df.sort()","df.filter()","df.groupby()","df.merge()"], "answer": 2},
                ],
            },
            {
                "title": "Data Visualisation", "desc": "Create charts with Matplotlib and Seaborn.",
                "duration": "2 weeks", "course": "Python for Data Science", "milestone": False,
                "lessons": ["Line & Bar Charts", "Scatter Plots", "Histograms",
                            "Heatmaps with Seaborn", "Subplots", "Saving Figures"],
                "quiz": [
                    {"q": "Which library creates statistical plots easily?", "options": ["NumPy","Seaborn","Requests","Flask"], "answer": 1},
                    {"q": "Which function shows a plot in Matplotlib?", "options": ["plt.draw()","plt.render()","plt.show()","plt.display()"], "answer": 2},
                ],
            },
            {
                "title": "SQL for Data Analysis", "desc": "Query databases with SQL — SELECT, JOIN, GROUP BY.",
                "duration": "3 weeks", "course": None, "milestone": True,
                "lessons": ["SELECT & WHERE", "ORDER BY & LIMIT", "Aggregate Functions",
                            "GROUP BY & HAVING", "JOINs", "Subqueries"],
                "quiz": [
                    {"q": "Which clause filters rows?", "options": ["GROUP BY","ORDER BY","WHERE","HAVING"], "answer": 2},
                    {"q": "Which JOIN returns all rows from both tables?", "options": ["INNER JOIN","LEFT JOIN","RIGHT JOIN","FULL OUTER JOIN"], "answer": 3},
                    {"q": "Which function counts rows?", "options": ["SUM()","AVG()","COUNT()","MAX()"], "answer": 2},
                ],
            },
            {
                "title": "Excel & Google Sheets", "desc": "Pivot tables, VLOOKUP, and dashboards.",
                "duration": "2 weeks", "course": None, "milestone": False,
                "lessons": ["Formulas & Functions", "VLOOKUP & HLOOKUP", "Pivot Tables",
                            "Charts & Dashboards", "Data Validation", "Conditional Formatting"],
                "quiz": [
                    {"q": "Which function looks up a value in a table?", "options": ["SUMIF","COUNTIF","VLOOKUP","INDEX"], "answer": 2},
                    {"q": "What does a Pivot Table do?", "options": ["Sorts data","Summarises data by category","Deletes duplicates","Formats cells"], "answer": 1},
                ],
            },
            {
                "title": "Capstone Project", "desc": "Analyse a real dataset and present findings.",
                "duration": "3 weeks", "course": None, "milestone": True,
                "lessons": ["Choose a Dataset", "Clean & Explore Data", "Analyse with Python/SQL",
                            "Visualise Insights", "Write a Report", "Present to Stakeholders"],
                "quiz": [
                    {"q": "What is EDA?", "options": ["Error Detection Algorithm","Exploratory Data Analysis","External Data Access","Encoded Data Array"], "answer": 1},
                    {"q": "Which chart best shows distribution?", "options": ["Pie chart","Line chart","Histogram","Scatter plot"], "answer": 2},
                ],
            },
        ],
    },
    {
        "slug": "ai-beginner", "title": "AI Beginner",
        "icon": "🤖", "color": "#a855f7",
        "description": "Understand AI and Machine Learning from scratch. No maths degree required.",
        "duration": "4 months", "level": "Beginner",
        "jobs": ["AI Prompt Engineer", "ML Intern", "Data Science Trainee"],
        "steps": [
            {
                "title": "Python for AI", "desc": "Python fundamentals needed for AI/ML.",
                "duration": "3 weeks", "course": "Python for Data Science", "milestone": False,
                "lessons": ["Python Basics Recap", "NumPy Arrays", "Pandas DataFrames",
                            "Matplotlib Plots", "List Comprehensions", "Lambda Functions"],
                "quiz": [
                    {"q": "Which library handles numerical arrays in Python?", "options": ["Pandas","NumPy","Matplotlib","Seaborn"], "answer": 1},
                    {"q": "What is a NumPy array?", "options": ["A Python list","A multi-dimensional array","A dictionary","A string"], "answer": 1},
                ],
            },
            {
                "title": "Maths for ML", "desc": "Linear algebra, statistics and probability basics.",
                "duration": "2 weeks", "course": None, "milestone": False,
                "lessons": ["Vectors & Matrices", "Dot Products", "Mean, Median, Std Dev",
                            "Probability Basics", "Normal Distribution", "Gradient Intuition"],
                "quiz": [
                    {"q": "What is the mean of [2, 4, 6]?", "options": ["3","4","5","6"], "answer": 1},
                    {"q": "What does a gradient tell us in ML?", "options": ["Data size","Direction of steepest increase","Number of features","Loss value"], "answer": 1},
                ],
            },
            {
                "title": "Intro to Machine Learning", "desc": "Supervised vs unsupervised learning, scikit-learn.",
                "duration": "4 weeks", "course": None, "milestone": True,
                "lessons": ["What is ML?", "Supervised Learning", "Unsupervised Learning",
                            "Train/Test Split", "Linear Regression", "Classification with scikit-learn"],
                "quiz": [
                    {"q": "Which type of ML uses labelled data?", "options": ["Unsupervised","Reinforcement","Supervised","Generative"], "answer": 2},
                    {"q": "What does overfitting mean?", "options": ["Model is too simple","Model memorises training data","Model has no data","Model is fast"], "answer": 1},
                    {"q": "Which library is used for ML in Python?", "options": ["Flask","Django","scikit-learn","NumPy"], "answer": 2},
                ],
            },
            {
                "title": "Neural Networks Basics", "desc": "How deep learning and neural networks work.",
                "duration": "3 weeks", "course": None, "milestone": False,
                "lessons": ["Neurons & Layers", "Activation Functions", "Forward Propagation",
                            "Backpropagation", "Intro to Keras/TensorFlow", "Training a Simple NN"],
                "quiz": [
                    {"q": "What is an activation function?", "options": ["A loss metric","Introduces non-linearity","A dataset","A layer type"], "answer": 1},
                    {"q": "Which framework is used for deep learning?", "options": ["Pandas","scikit-learn","TensorFlow","Matplotlib"], "answer": 2},
                ],
            },
            {
                "title": "AI Tools & Prompt Engineering", "desc": "Use ChatGPT, Gemini and prompt engineering.",
                "duration": "2 weeks", "course": None, "milestone": False,
                "lessons": ["What are LLMs?", "Prompt Engineering Basics", "Zero-shot vs Few-shot",
                            "Chain-of-Thought Prompting", "Using APIs (OpenAI)", "AI Ethics & Bias"],
                "quiz": [
                    {"q": "What is prompt engineering?", "options": ["Writing Python code","Crafting inputs to guide AI output","Training a model","Building a dataset"], "answer": 1},
                    {"q": "What is a zero-shot prompt?", "options": ["Prompt with examples","Prompt with no examples","Empty prompt","Code prompt"], "answer": 1},
                ],
            },
            {
                "title": "Mini AI Project", "desc": "Build a simple classifier or chatbot.",
                "duration": "2 weeks", "course": None, "milestone": True,
                "lessons": ["Choose Your Project", "Prepare Dataset", "Train Model",
                            "Evaluate Results", "Build Simple UI", "Deploy & Share"],
                "quiz": [
                    {"q": "Which metric measures classification accuracy?", "options": ["MSE","R²","Accuracy Score","RMSE"], "answer": 2},
                    {"q": "What is a confusion matrix?", "options": ["A type of neural network","Table showing prediction vs actual","A loss function","A dataset format"], "answer": 1},
                ],
            },
        ],
    },
    {
        "slug": "digital-marketing", "title": "Digital Marketing",
        "icon": "📣", "color": "#f59e0b",
        "description": "Master SEO, social media, paid ads and analytics to grow any business online.",
        "duration": "3 months", "level": "Beginner",
        "jobs": ["Digital Marketer", "SEO Specialist", "Social Media Manager"],
        "steps": [
            {
                "title": "Digital Marketing Overview", "desc": "Channels, funnels and the marketing mix.",
                "duration": "1 week", "course": "Digital Marketing Essentials", "milestone": False,
                "lessons": ["What is Digital Marketing?", "Marketing Funnel", "Owned/Earned/Paid Media",
                            "Setting SMART Goals", "Competitor Analysis"],
                "quiz": [
                    {"q": "What does the marketing funnel top represent?", "options": ["Purchase","Loyalty","Awareness","Conversion"], "answer": 2},
                    {"q": "What is 'owned media'?", "options": ["Paid ads","Your website & social profiles","Press coverage","Influencer posts"], "answer": 1},
                ],
            },
            {
                "title": "SEO & Content Marketing", "desc": "Rank on Google with on-page and off-page SEO.",
                "duration": "3 weeks", "course": "Digital Marketing Essentials", "milestone": True,
                "lessons": ["Keyword Research", "On-Page SEO", "Technical SEO Basics",
                            "Link Building", "Content Strategy", "Blogging for SEO"],
                "quiz": [
                    {"q": "What does SEO stand for?", "options": ["Social Engagement Optimisation","Search Engine Optimisation","Site Engagement Overview","Search Engagement Operations"], "answer": 1},
                    {"q": "Which tool shows keyword search volume?", "options": ["Google Analytics","Google Search Console","Google Keyword Planner","Google Ads Editor"], "answer": 2},
                    {"q": "What is a backlink?", "options": ["Internal link","Link from another site to yours","Broken link","Redirect"], "answer": 1},
                ],
            },
            {
                "title": "Social Media Marketing", "desc": "Grow audiences on Instagram, LinkedIn, YouTube.",
                "duration": "2 weeks", "course": "Digital Marketing Essentials", "milestone": False,
                "lessons": ["Platform Selection", "Content Calendar", "Instagram Growth",
                            "LinkedIn for B2B", "YouTube SEO", "Engagement Strategies"],
                "quiz": [
                    {"q": "Which platform is best for B2B marketing?", "options": ["Instagram","TikTok","LinkedIn","Snapchat"], "answer": 2},
                    {"q": "What is engagement rate?", "options": ["Follower count","Interactions ÷ reach × 100","Ad spend","Click-through rate"], "answer": 1},
                ],
            },
            {
                "title": "Google Ads & Meta Ads", "desc": "Run paid campaigns with measurable ROI.",
                "duration": "3 weeks", "course": "Digital Marketing Essentials", "milestone": True,
                "lessons": ["Google Ads Structure", "Keyword Match Types", "Ad Copywriting",
                            "Meta Ads Manager", "Audience Targeting", "A/B Testing Ads"],
                "quiz": [
                    {"q": "What does PPC stand for?", "options": ["Page Per Click","Pay Per Conversion","Pay Per Click","Paid Promotion Campaign"], "answer": 2},
                    {"q": "What is CTR?", "options": ["Cost to Reach","Click-Through Rate","Conversion Tracking Rate","Campaign Total Revenue"], "answer": 1},
                    {"q": "What is retargeting?", "options": ["Emailing past customers","Showing ads to previous visitors","Organic SEO","Influencer marketing"], "answer": 1},
                ],
            },
            {
                "title": "Email Marketing", "desc": "Build lists and automate email campaigns.",
                "duration": "2 weeks", "course": "Digital Marketing Essentials", "milestone": False,
                "lessons": ["Building an Email List", "Email Copywriting", "Subject Line Optimisation",
                            "Automation Sequences", "A/B Testing Emails", "Measuring Open & Click Rates"],
                "quiz": [
                    {"q": "What is a good email open rate?", "options": ["1–5%","15–25%","50–60%","80–90%"], "answer": 1},
                    {"q": "What is an email drip campaign?", "options": ["One-time blast","Automated sequence of emails","Newsletter","Cold email"], "answer": 1},
                ],
            },
            {
                "title": "Analytics & Reporting", "desc": "Measure results with Google Analytics 4.",
                "duration": "1 week", "course": "Digital Marketing Essentials", "milestone": True,
                "lessons": ["GA4 Setup", "Key Metrics & Dimensions", "Traffic Sources",
                            "Conversion Tracking", "Building Reports", "Data-Driven Decisions"],
                "quiz": [
                    {"q": "Which tool tracks website traffic for free?", "options": ["Ahrefs","SEMrush","Google Analytics","Moz"], "answer": 2},
                    {"q": "What does bounce rate measure?", "options": ["Page load speed","% visitors who leave after one page","Ad clicks","Email opens"], "answer": 1},
                ],
            },
        ],
    },
]


# ── Language Config ────────────────────────────────────────────────────────────

SUPPORTED_LANGUAGES = {
    "en":    "English",
    "hi":    "Hindi",
    "ta":    "Tamil",
    "te":    "Telugu",
    "bn":    "Bengali",
    "mr":    "Marathi",
    "gu":    "Gujarati",
    "kn":    "Kannada",
    "ml":    "Malayalam",
    "pa":    "Punjabi",
}

# ── i18n UI strings (EN / HI / KN / TA / TE) ─────────────────────────────────
I18N = {
    "skill_paths":        {"en": "Skill Paths",          "hi": "कौशल पथ",          "kn": "ಕೌಶಲ್ ಮಾರ್ಗಗಳು",    "ta": "திறன் பாதைகள்",      "te": "నైపుణ్య మార్గాలు"},
    "enrolled":           {"en": "Enrolled",             "hi": "नामांकित",          "kn": "ನೋಂದಾಯಿಸಲಾಗಿದೆ",   "ta": "சேர்க்கப்பட்டது",    "te": "నమోదైంది"},
    "start_path":         {"en": "Start This Path",      "hi": "यह पथ शुरू करें",   "kn": "ಈ ಮಾರ್ಗ ಪ್ರಾರಂಭಿಸಿ","ta": "இந்த பாதையை தொடங்கு","te": "ఈ మార్గం ప్రారంభించు"},
    "progress":           {"en": "Progress",             "hi": "प्रगति",            "kn": "ಪ್ರಗತಿ",             "ta": "முன்னேற்றம்",         "te": "పురోగతి"},
    "steps_completed":    {"en": "steps completed",      "hi": "चरण पूर्ण",         "kn": "ಹಂತಗಳು ಪೂರ್ಣ",      "ta": "படிகள் முடிந்தன",     "te": "దశలు పూర్తయ్యాయి"},
    "career_outcomes":    {"en": "Career outcomes",      "hi": "करियर परिणाम",      "kn": "ವೃತ್ತಿ ಫಲಿತಾಂಶಗಳು", "ta": "தொழில் வாய்ப்புகள்", "te": "కెరీర్ ఫలితాలు"},
    "learning_roadmap":   {"en": "Learning Roadmap",     "hi": "सीखने का रोडमैप",   "kn": "ಕಲಿಕೆಯ ರೋಡ್‌ಮ್ಯಾಪ್", "ta": "கற்றல் வரைபடம்",     "te": "నేర్చుకునే రోడ్‌మ్యాప్"},
    "lessons":            {"en": "LESSONS",              "hi": "पाठ",               "kn": "ಪಾಠಗಳು",            "ta": "பாடங்கள்",            "te": "పాఠాలు"},
    "quick_quiz":         {"en": "QUICK QUIZ",           "hi": "त्वरित प्रश्नोत्तरी","kn": "ತ್ವರಿತ ರಸಪ್ರಶ್ನೆ",  "ta": "விரைவு வினாடி வினா", "te": "శీఘ్ర క్విజ్"},
    "mark_complete":      {"en": "Mark Step Complete",   "hi": "चरण पूर्ण करें",    "kn": "ಹಂತ ಪೂರ್ಣಗೊಳಿಸಿ",  "ta": "படி முடிந்தது",       "te": "దశ పూర్తి చేయి"},
    "step_done":          {"en": "Step completed!",      "hi": "चरण पूर्ण!",        "kn": "ಹಂತ ಪೂರ್ಣ!",        "ta": "படி முடிந்தது!",      "te": "దశ పూర్తైంది!"},
    "locked":             {"en": "Complete previous step first", "hi": "पहले पिछला चरण पूरा करें", "kn": "ಮೊದಲು ಹಿಂದಿನ ಹಂತ ಪೂರ್ಣಗೊಳಿಸಿ", "ta": "முதல் முந்தைய படியை முடிக்கவும்", "te": "ముందు మునుపటి దశ పూర్తి చేయండి"},
    "view_course":        {"en": "View Course →",        "hi": "कोर्स देखें →",     "kn": "ಕೋರ್ಸ್ ನೋಡಿ →",     "ta": "பாடத்தை பார்க்க →",  "te": "కోర్సు చూడండి →"},
    "next_step":          {"en": "Next Step",            "hi": "अगला चरण",          "kn": "ಮುಂದಿನ ಹಂತ",        "ta": "அடுத்த படி",         "te": "తదుపరి దశ"},
    "notes":              {"en": "Notes",                "hi": "नोट्स",             "kn": "ಟಿಪ್ಪಣಿಗಳು",        "ta": "குறிப்புகள்",         "te": "నోట్స్"},
    "subtitles":          {"en": "Subtitles",            "hi": "उपशीर्षक",          "kn": "ಉಪಶೀರ್ಷಿಕೆಗಳು",     "ta": "வசன வரிகள்",         "te": "సబ్‌టైటిల్స్"},
    "milestone":          {"en": "Milestone",            "hi": "मील का पत्थर",      "kn": "ಮೈಲಿಗಲ್ಲು",         "ta": "மைல்கல்",            "te": "మైలురాయి"},
    "back":               {"en": "← Back to Skill Paths","hi": "← कौशल पथ पर वापस","kn": "← ಕೌಶಲ್ ಮಾರ್ಗಗಳಿಗೆ ಹಿಂತಿರುಗಿ","ta": "← திறன் பாதைகளுக்கு திரும்பு","te": "← నైపుణ్య మార్గాలకు తిరిగి"},
    "correct":            {"en": "✓ Correct!",           "hi": "✓ सही!",            "kn": "✓ ಸರಿ!",             "ta": "✓ சரி!",              "te": "✓ సరైనది!"},
    "incorrect":          {"en": "✗ Incorrect — correct answer highlighted.", "hi": "✗ गलत — सही उत्तर हाइलाइट किया।", "kn": "✗ ತಪ್ಪು — ಸರಿಯಾದ ಉತ್ತರ ಹೈಲೈಟ್ ಆಗಿದೆ.", "ta": "✗ தவறு — சரியான பதில் குறிக்கப்பட்டது.", "te": "✗ తప్పు — సరైన సమాధానం హైలైట్ చేయబడింది."},
    "next_rec":           {"en": "Recommended Next",     "hi": "अनुशंसित अगला",     "kn": "ಶಿಫಾರಸು ಮಾಡಿದ ಮುಂದಿನದು","ta": "பரிந்துரைக்கப்பட்ட அடுத்தது","te": "సిఫార్సు చేయబడిన తదుపరిది"},
    "subtitle_hint":      {"en": "Enable subtitles in YouTube player for your language.", "hi": "अपनी भाषा के लिए YouTube में उपशीर्षक चालू करें।", "kn": "ನಿಮ್ಮ ಭಾಷೆಗಾಗಿ YouTube ನಲ್ಲಿ ಉಪಶೀರ್ಷಿಕೆಗಳನ್ನು ಆನ್ ಮಾಡಿ.", "ta": "உங்கள் மொழிக்கு YouTube இல் வசன வரிகளை இயக்கவும்.", "te": "మీ భాష కోసం YouTube లో సబ్‌టైటిల్స్ ఆన్ చేయండి."},
}

# ── Translated path notes (per slug, per lang) ────────────────────────────────
PATH_NOTES = {
    "frontend-developer": {
        "en": "🌐 Frontend Developer Path\n\nFocus on building real projects at every step. Use browser DevTools daily. The best way to learn HTML/CSS/JS is to build — don't just watch tutorials.\n\n💡 Tips:\n• Inspect websites you admire using DevTools\n• Commit code to GitHub from Day 1\n• Build a portfolio with at least 3 projects before applying for jobs",
        "hi": "🌐 फ्रंटएंड डेवलपर पथ\n\nहर चरण में वास्तविक प्रोजेक्ट बनाने पर ध्यान दें। DevTools का उपयोग करें। HTML/CSS/JS सीखने का सबसे अच्छा तरीका बनाना है।\n\n💡 सुझाव:\n• DevTools से वेबसाइट्स का निरीक्षण करें\n• Day 1 से GitHub पर कोड डालें\n• नौकरी के लिए कम से कम 3 प्रोजेक्ट बनाएं",
        "kn": "🌐 ಫ್ರಂಟೆಂಡ್ ಡೆವಲಪರ್ ಮಾರ್ಗ\n\nಪ್ರತಿ ಹಂತದಲ್ಲಿ ನಿಜವಾದ ಪ್ರಾಜೆಕ್ಟ್‌ಗಳನ್ನು ನಿರ್ಮಿಸಿ. DevTools ಬಳಸಿ.\n\n💡 ಸಲಹೆಗಳು:\n• DevTools ಮೂಲಕ ವೆಬ್‌ಸೈಟ್‌ಗಳನ್ನು ಪರಿಶೀಲಿಸಿ\n• Day 1 ರಿಂದ GitHub ಗೆ ಕೋಡ್ ಹಾಕಿ\n• ಕೆಲಸಕ್ಕೆ ಅರ್ಜಿ ಹಾಕುವ ಮೊದಲು 3 ಪ್ರಾಜೆಕ್ಟ್ ಮಾಡಿ",
        "ta": "🌐 ஃப்ரண்டெண்ட் டெவலப்பர் பாதை\n\nஒவ்வொரு படியிலும் உண்மையான திட்டங்களை உருவாக்குங்கள். DevTools பயன்படுத்துங்கள்.\n\n💡 குறிப்புகள்:\n• DevTools மூலம் வலைத்தளங்களை ஆய்வு செய்யுங்கள்\n• Day 1 முதல் GitHub இல் கோட் போடுங்கள்\n• வேலைக்கு விண்ணப்பிக்கும் முன் 3 திட்டங்கள் உருவாக்குங்கள்",
        "te": "🌐 ఫ్రంటెండ్ డెవలపర్ మార్గం\n\nప్రతి దశలో నిజమైన ప్రాజెక్టులు నిర్మించండి. DevTools ఉపయోగించండి.\n\n💡 చిట్కాలు:\n• DevTools తో వెబ్‌సైట్లు పరిశీలించండి\n• Day 1 నుండి GitHub కు కోడ్ పంపండి\n• ఉద్యోగానికి దరఖాస్తు చేయడానికి ముందు 3 ప్రాజెక్టులు చేయండి",
    },
    "data-analyst": {
        "en": "📊 Data Analyst Path\n\nData analysis is about asking the right questions. Learn to think in data — every business decision can be improved with data.\n\n💡 Tips:\n• Practice on Kaggle datasets (free)\n• Learn SQL before advanced Python\n• Document your analysis clearly — communication is half the job",
        "hi": "📊 डेटा एनालिस्ट पथ\n\nडेटा विश्लेषण सही प्रश्न पूछने के बारे में है। Kaggle पर अभ्यास करें।\n\n💡 सुझाव:\n• Kaggle डेटासेट पर अभ्यास करें (मुफ्त)\n• Python से पहले SQL सीखें\n• अपना विश्लेषण स्पष्ट रूप से दस्तावेज़ करें",
        "kn": "📊 ಡೇಟಾ ಅನಾಲಿಸ್ಟ್ ಮಾರ್ಗ\n\nಡೇಟಾ ವಿಶ್ಲೇಷಣೆ ಸರಿಯಾದ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುವ ಬಗ್ಗೆ. Kaggle ನಲ್ಲಿ ಅಭ್ಯಾಸ ಮಾಡಿ.\n\n💡 ಸಲಹೆಗಳು:\n• Kaggle ಡೇಟಾಸೆಟ್‌ಗಳಲ್ಲಿ ಅಭ್ಯಾಸ ಮಾಡಿ\n• Python ಮೊದಲು SQL ಕಲಿಯಿರಿ\n• ನಿಮ್ಮ ವಿಶ್ಲೇಷಣೆಯನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ದಾಖಲಿಸಿ",
        "ta": "📊 டேட்டா அனலிஸ்ட் பாதை\n\nதரவு பகுப்பாய்வு சரியான கேள்விகளை கேட்பது பற்றியது. Kaggle இல் பயிற்சி செய்யுங்கள்.\n\n💡 குறிப்புகள்:\n• Kaggle தரவுத்தொகுப்புகளில் பயிற்சி செய்யுங்கள்\n• Python க்கு முன் SQL கற்றுக்கொள்ளுங்கள்\n• உங்கள் பகுப்பாய்வை தெளிவாக ஆவணப்படுத்துங்கள்",
        "te": "📊 డేటా అనలిస్ట్ మార్గం\n\nడేటా విశ్లేషణ సరైన ప్రశ్నలు అడగడం గురించి. Kaggle లో సాధన చేయండి.\n\n💡 చిట్కాలు:\n• Kaggle డేటాసెట్లపై సాధన చేయండి\n• Python కంటే ముందు SQL నేర్చుకోండి\n• మీ విశ్లేషణను స్పష్టంగా డాక్యుమెంట్ చేయండి",
    },
    "ai-beginner": {
        "en": "🤖 AI Beginner Path\n\nAI is not magic — it's maths + data + code. Start with the intuition before the equations.\n\n💡 Tips:\n• Use Google Colab (free GPU) for all ML experiments\n• Read 'Hands-On ML' by Aurélien Géron\n• Follow fast.ai for practical deep learning",
        "hi": "🤖 AI बिगिनर पथ\n\nAI जादू नहीं है — यह गणित + डेटा + कोड है। Google Colab (मुफ्त GPU) का उपयोग करें।\n\n💡 सुझाव:\n• सभी ML प्रयोगों के लिए Google Colab उपयोग करें\n• 'Hands-On ML' पुस्तक पढ़ें\n• fast.ai फॉलो करें",
        "kn": "🤖 AI ಆರಂಭಿಕ ಮಾರ್ಗ\n\nAI ಮ್ಯಾಜಿಕ್ ಅಲ್ಲ — ಇದು ಗಣಿತ + ಡೇಟಾ + ಕೋಡ್. Google Colab ಬಳಸಿ.\n\n💡 ಸಲಹೆಗಳು:\n• ಎಲ್ಲಾ ML ಪ್ರಯೋಗಗಳಿಗೆ Google Colab ಬಳಸಿ\n• 'Hands-On ML' ಪುಸ್ತಕ ಓದಿ\n• fast.ai ಅನುಸರಿಸಿ",
        "ta": "🤖 AI தொடக்கநிலை பாதை\n\nAI மாயம் இல்லை — இது கணிதம் + தரவு + குறியீடு. Google Colab பயன்படுத்துங்கள்.\n\n💡 குறிப்புகள்:\n• அனைத்து ML சோதனைகளுக்கும் Google Colab பயன்படுத்துங்கள்\n• 'Hands-On ML' புத்தகம் படியுங்கள்\n• fast.ai பின்தொடருங்கள்",
        "te": "🤖 AI బిగినర్ మార్గం\n\nAI మాయ కాదు — ఇది గణితం + డేటా + కోడ్. Google Colab ఉపయోగించండి.\n\n💡 చిట్కాలు:\n• అన్ని ML ప్రయోగాలకు Google Colab ఉపయోగించండి\n• 'Hands-On ML' పుస్తకం చదవండి\n• fast.ai అనుసరించండి",
    },
    "digital-marketing": {
        "en": "📣 Digital Marketing Path\n\nMarketing is about understanding people, not just tools. Master one channel deeply before spreading thin.\n\n💡 Tips:\n• Get Google Digital Garage certification (free)\n• Run a real campaign with even ₹500 budget to learn\n• Study successful brand campaigns and reverse-engineer them",
        "hi": "📣 डिजिटल मार्केटिंग पथ\n\nमार्केटिंग लोगों को समझने के बारे में है। Google Digital Garage सर्टिफिकेशन लें (मुफ्त)।\n\n💡 सुझाव:\n• Google Digital Garage सर्टिफिकेशन लें\n• ₹500 बजट से असली कैंपेन चलाएं\n• सफल ब्रांड कैंपेन का अध्ययन करें",
        "kn": "📣 ಡಿಜಿಟಲ್ ಮಾರ್ಕೆಟಿಂಗ್ ಮಾರ್ಗ\n\nಮಾರ್ಕೆಟಿಂಗ್ ಜನರನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವ ಬಗ್ಗೆ. Google Digital Garage ಸರ್ಟಿಫಿಕೇಶನ್ ಪಡೆಯಿರಿ.\n\n💡 ಸಲಹೆಗಳು:\n• Google Digital Garage ಸರ್ಟಿಫಿಕೇಶನ್ ಪಡೆಯಿರಿ\n• ₹500 ಬಜೆಟ್‌ನಲ್ಲಿ ನಿಜವಾದ ಕ್ಯಾಂಪೇನ್ ನಡೆಸಿ\n• ಯಶಸ್ವಿ ಬ್ರ್ಯಾಂಡ್ ಕ್ಯಾಂಪೇನ್‌ಗಳನ್ನು ಅಧ್ಯಯನ ಮಾಡಿ",
        "ta": "📣 டிஜிட்டல் மார்க்கெட்டிங் பாதை\n\nமார்க்கெட்டிங் மக்களை புரிந்துகொள்வது பற்றியது. Google Digital Garage சான்றிதழ் பெறுங்கள்.\n\n💡 குறிப்புகள்:\n• Google Digital Garage சான்றிதழ் பெறுங்கள்\n• ₹500 பட்ஜெட்டில் உண்மையான பிரச்சாரம் நடத்துங்கள்\n• வெற்றிகரமான பிராண்ட் பிரச்சாரங்களை ஆய்வு செய்யுங்கள்",
        "te": "📣 డిజిటల్ మార్కెటింగ్ మార్గం\n\nమార్కెటింగ్ అంటే మనుషులను అర్థం చేసుకోవడం. Google Digital Garage సర్టిఫికేషన్ పొందండి.\n\n💡 చిట్కాలు:\n• Google Digital Garage సర్టిఫికేషన్ పొందండి\n• ₹500 బడ్జెట్‌తో నిజమైన క్యాంపెయిన్ నడపండి\n• విజయవంతమైన బ్రాండ్ క్యాంపెయిన్లు అధ్యయనం చేయండి",
    },
}

# YouTube subtitle language codes for the 5 supported languages
SUBTITLE_LANGS = {"en": "en", "hi": "hi", "kn": "kn", "ta": "ta", "te": "te"}

# ── Next-step recommendation messages (per lang) ──────────────────────────────
NEXT_STEP_MSG = {
    "en": "Your next step is: **{title}** — {desc}",
    "hi": "आपका अगला चरण है: **{title}** — {desc}",
    "kn": "ನಿಮ್ಮ ಮುಂದಿನ ಹಂತ: **{title}** — {desc}",
    "ta": "உங்கள் அடுத்த படி: **{title}** — {desc}",
    "te": "మీ తదుపరి దశ: **{title}** — {desc}",
}

# Pre-written course notes shown in the Notes tab
COURSE_NOTES = {
    "Python for Data Science": """📘 PYTHON FOR DATA SCIENCE — Course Notes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODULE 1 — Introduction to Python
• Python is a high-level, interpreted language. Easy to read and write.
• print("Hello World")  ← your first program
• Use Python 3.x (not 2.x). Install from python.org or use Google Colab (free, no install).
• IDEs: VS Code, PyCharm, Jupyter Notebook

MODULE 2 — Variables & Data Types
• Variables store data: name = "Rahul", age = 20, price = 99.5, is_student = True
• Data types: int, float, str, bool, list, tuple, dict, set
• type(x) tells you the type. int("5") converts string to int.
• f-strings: f"Hello {name}, you are {age} years old"

MODULE 3 — Control Flow & Loops
• if / elif / else — decision making
• for loop: for i in range(5): print(i)   → prints 0 to 4
• while loop: runs as long as condition is True
• break exits a loop; continue skips to next iteration
• Indentation is MANDATORY in Python (use 4 spaces)

MODULE 4 — Functions & Modules
• def greet(name): return f"Hello {name}"
• *args = variable positional args; **kwargs = variable keyword args
• import math, import random — built-in modules
• Create your own module: save as mymodule.py, then import mymodule

MODULE 5 — Data Analysis with Pandas
• import pandas as pd
• DataFrame = table of data. Series = single column.
• df = pd.read_csv("file.csv")  ← load data
• df.head(), df.info(), df.describe() — explore data
• df["column"].mean() / .sum() / .value_counts()
• df.dropna() removes missing values; df.fillna(0) fills them

MODULE 6 — Visualization with Matplotlib
• import matplotlib.pyplot as plt
• plt.plot(x, y) — line chart
• plt.bar(x, y) — bar chart
• plt.hist(data) — histogram
• plt.xlabel("X"), plt.ylabel("Y"), plt.title("My Chart")
• plt.show() — display the chart

⭐ KEY TIPS
• Practice daily on HackerRank / LeetCode
• Use Jupyter Notebook for data science work
• Shradha Khapra's playlist on Apna College YouTube is excellent for revision
""",

    "Digital Marketing Essentials": """📘 DIGITAL MARKETING ESSENTIALS — Course Notes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODULE 1 — What is Digital Marketing?
• Marketing products/services using digital channels: social media, email, search engines, websites
• Key channels: SEO, SEM, SMM, Email Marketing, Content Marketing, Affiliate Marketing
• Digital marketing is measurable, targeted, and cost-effective vs traditional marketing

MODULE 2 — SEO Fundamentals
• SEO = Search Engine Optimisation — getting free (organic) traffic from Google
• On-page SEO: title tags, meta descriptions, keywords, headings (H1/H2), image alt text
• Off-page SEO: backlinks from other websites (quality > quantity)
• Technical SEO: site speed, mobile-friendly, HTTPS, sitemap.xml
• Tools: Google Search Console, Ahrefs, SEMrush, Ubersuggest (free)

MODULE 3 — Social Media Strategy
• Choose platforms based on audience: Instagram/YouTube (youth), LinkedIn (professionals), Facebook (all ages)
• Content pillars: Educational, Entertaining, Inspirational, Promotional (80/20 rule)
• Posting consistency > posting frequency. Use a content calendar.
• Hashtags: 5–10 relevant hashtags per post. Research with tools like Hashtagify.

MODULE 4 — Google Ads Basics
• PPC = Pay Per Click. You pay only when someone clicks your ad.
• Campaign types: Search, Display, Shopping, Video (YouTube)
• Keywords: broad match, phrase match, exact match
• Quality Score = relevance of ad + landing page + expected CTR
• Set daily budget. Monitor CTR (Click-Through Rate) and CPC (Cost Per Click).

MODULE 5 — Email Marketing
• Build an email list — it's YOUR asset (unlike social media followers)
• Tools: Mailchimp (free up to 500 contacts), ConvertKit, Sendinblue
• Subject line is everything — A/B test it
• Metrics: Open Rate (20–25% is good), CTR, Unsubscribe Rate

MODULE 6 — Analytics & Reporting
• Google Analytics 4 (GA4) — free, tracks website visitors, behaviour, conversions
• Key metrics: Sessions, Bounce Rate, Avg. Session Duration, Conversion Rate
• UTM parameters track which campaign brought traffic: ?utm_source=instagram&utm_medium=social
• Monthly report: traffic, leads, conversions, ROI

⭐ KEY TIPS
• Start with one channel and master it before expanding
• Content is king — solve real problems for your audience
• Always track ROI. If it doesn't convert, change the strategy.
""",

    "Financial Literacy & Entrepreneurship": """📘 FINANCIAL LITERACY & ENTREPRENEURSHIP — Course Notes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODULE 1 — Money Basics & Budgeting
• Income - Expenses = Savings. Simple but powerful.
• 50/30/20 Rule: 50% needs, 30% wants, 20% savings/investments
• Track every rupee using apps: Walnut, Money Manager, or a simple notebook
• Emergency Fund = 3–6 months of expenses kept in a savings account

MODULE 2 — Savings & Investment 101
• Savings Account: safe, liquid, low interest (~3–4%)
• Fixed Deposit (FD): higher interest (~6–7%), locked for a period
• Mutual Funds: pool of stocks/bonds managed by experts. Start with SIP ₹500/month.
• PPF (Public Provident Fund): tax-free, 15-year lock-in, ~7.1% interest
• Rule of 72: divide 72 by interest rate = years to double money. At 8% → 9 years.

MODULE 3 — Micro-loans & SHG Programs
• SHG = Self Help Group — women pool savings and give each other loans
• MUDRA Loan: govt scheme for small businesses. Shishu (up to ₹50K), Kishore (up to ₹5L), Tarun (up to ₹10L)
• PM SVANidhi: street vendor loans starting ₹10,000
• NABARD supports rural agriculture and cottage industry loans
• Repay on time — builds credit score (CIBIL score, target 750+)

MODULE 4 — Starting Your Business
• Idea → Validate → Plan → Register → Launch → Scale
• Business Plan: problem, solution, target market, revenue model, costs
• Registration: Sole Proprietorship (easiest), Partnership, Pvt Ltd (for scaling)
• GST registration needed if turnover > ₹20 lakhs (services) / ₹40 lakhs (goods)
• Start lean — test with minimum investment before scaling

MODULE 5 — Record Keeping & GST Basics
• Maintain: sales register, purchase register, expense register, bank statements
• GST = Goods and Services Tax. Rates: 0%, 5%, 12%, 18%, 28%
• File GSTR-1 (sales) and GSTR-3B (summary) monthly/quarterly
• Input Tax Credit (ITC): claim back GST paid on purchases
• Use free tools: Zoho Books, ClearTax, Vyapar app

⭐ KEY TIPS
• Pay yourself first — automate savings on salary day
• Avoid high-interest debt (credit cards charge 36–42% p.a.)
• Network actively — most business comes through relationships
""",

    "Spoken English & Communication": """📘 SPOKEN ENGLISH & COMMUNICATION — Course Notes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODULE 1 — English Pronunciation Basics
• Vowel sounds: short (cat, bed, sit) vs long (cake, bead, site)
• Stress the right syllable: PHOtograph vs phoTOgraphy
• Schwa sound /ə/ is the most common in English: "about", "the", "a"
• Minimal pairs practice: ship/sheep, live/leave, bit/beat
• Listen to BBC Learning English, VOA Learning English daily

MODULE 2 — Everyday Conversations
• Greetings: "How are you?" → "I'm doing well, thank you. And you?"
• Asking for help: "Could you please help me with…?" (polite)
• Disagreeing politely: "I see your point, however…" / "That's interesting, but…"
• Filler words to avoid: "um", "uh", "like" — replace with a pause
• Practice with mirror, record yourself, listen back

MODULE 3 — Grammar in Context
• Tenses: Simple Present (I work), Present Continuous (I am working), Simple Past (I worked)
• Articles: "a" (first mention), "the" (specific/known), no article (general/plural)
• Prepositions: in (enclosed space), on (surface), at (specific point)
• Common mistakes: "I am having a car" ✗ → "I have a car" ✓
• Active vs Passive: "The manager approved the plan" vs "The plan was approved"

MODULE 4 — Professional Email Writing
• Subject line: clear and specific. "Meeting Request – Thursday 3 PM" not "Hi"
• Structure: Greeting → Purpose → Details → Action Required → Closing
• Formal: "Dear Mr. Sharma," / Informal: "Hi Rahul,"
• Closing: "Best regards," / "Warm regards," / "Sincerely,"
• Proofread before sending. Use Grammarly (free) to check errors.

MODULE 5 — Interview Skills
• STAR method: Situation, Task, Action, Result — for behavioural questions
• "Tell me about yourself" = 1 min pitch: background + skills + why this role
• Research the company before the interview (website, LinkedIn, news)
• Questions to ask: "What does success look like in this role?"
• Body language: firm handshake, eye contact, sit straight, smile

⭐ KEY TIPS
• Fluency comes from speaking, not studying grammar rules
• Think in English — translate less, speak more
• Watch English movies/shows with English subtitles
""",

    "Web Development Bootcamp": """📘 WEB DEVELOPMENT BOOTCAMP — Course Notes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODULE 1 — HTML5 Structure
• HTML = HyperText Markup Language. Skeleton of every webpage.
• Basic structure: <!DOCTYPE html> → <html> → <head> + <body>
• Key tags: <h1>–<h6> headings, <p> paragraph, <a href=""> link, <img src=""> image
• Semantic tags: <header>, <nav>, <main>, <section>, <article>, <footer>
• Forms: <form>, <input type="text/email/password">, <button>, <select>

MODULE 2 — CSS3 & Flexbox
• CSS = Cascading Style Sheets. Styles the HTML.
• Selectors: element (p), class (.card), id (#header), pseudo (:hover)
• Box model: content → padding → border → margin
• Flexbox: display:flex; justify-content:center; align-items:center; gap:1rem;
• Colors: hex (#ff5733), rgb(255,87,51), hsl(11,100%,60%)
• Google Fonts: @import url('...') then font-family: 'Roboto', sans-serif;

MODULE 3 — JavaScript Essentials
• JS makes pages interactive. Runs in the browser.
• Variables: let (block scope), const (constant), var (avoid)
• Functions: function greet(name) { return "Hello " + name; }
• DOM manipulation: document.getElementById("id").textContent = "Hello"
• Events: btn.addEventListener("click", function() { alert("Clicked!"); })
• Fetch API: fetch(url).then(res => res.json()).then(data => console.log(data))

MODULE 4 — Responsive Design
• Mobile-first approach: design for small screens first, then scale up
• Media queries: @media (min-width: 768px) { .container { width: 750px; } }
• Viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1">
• CSS Grid: display:grid; grid-template-columns: repeat(3, 1fr); gap:1rem;
• Use relative units: %, em, rem, vw, vh instead of fixed px

MODULE 5 — Building Your Portfolio
• Host for free: GitHub Pages, Netlify, Vercel
• Must-have pages: Home, About, Projects, Contact
• Add 3–5 real projects with live links and GitHub source code
• Use a clean, fast-loading design. Performance matters.
• Tools: Figma (design), VS Code (code), Chrome DevTools (debug)

⭐ KEY TIPS
• Build projects from day 1 — don't just watch tutorials
• Learn Git/GitHub — essential for every developer
• Roadmap: HTML → CSS → JS → React → Node.js → Databases
""",

    "Sustainable Agriculture & AgriTech": """📘 SUSTAINABLE AGRICULTURE & AGRITECH — Course Notes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODULE 1 — Soil Health & Testing
• Healthy soil = healthy crops. Soil has physical, chemical, biological properties.
• Soil pH: 6.0–7.0 is ideal for most crops. Test with soil pH kit (₹200–500).
• Macronutrients: N (nitrogen) = leaf growth, P (phosphorus) = roots, K (potassium) = fruit
• Organic matter improves water retention, aeration, and microbial activity
• Soil testing labs: ICAR, KVK (Krishi Vigyan Kendra) — often free or subsidised

MODULE 2 — Drip Irrigation Setup
• Drip irrigation delivers water directly to roots — saves 40–60% water vs flood irrigation
• Components: water source → filter → pressure regulator → main line → sub-main → drip tape/emitters
• Suitable for: vegetables, fruits, sugarcane, cotton
• PM Krishi Sinchayee Yojana: 55% subsidy for small/marginal farmers
• Maintenance: flush lines weekly, check emitters monthly for clogging

MODULE 3 — Organic Farming Basics
• No synthetic pesticides or fertilisers. Uses natural inputs.
• Compost: kitchen waste + dry leaves + cow dung → ready in 45–60 days
• Vermicompost: earthworms break down organic matter → rich fertiliser
• Neem-based pesticide: soak neem leaves/seeds, spray on crops — safe and effective
• Certification: NPOP (National Programme for Organic Production) for export markets

MODULE 4 — AgriTech Apps & Tools
• Kisan Suvidha (Govt): weather, market prices, plant protection advice — free
• mKisan: SMS-based advisory from ICAR experts
• eNAM (National Agriculture Market): sell crops online at better prices
• Fasal: AI-based crop advisory, pest alerts, weather forecasts
• Drone spraying: reduces pesticide use by 30%, covers 1 acre in 10 minutes

MODULE 5 — Market Linkage & MSP
• MSP = Minimum Support Price — govt guaranteed price for 23 crops
• APMC Mandi: regulated market. Know your nearest mandi and its prices.
• FPO (Farmer Producer Organisation): group of farmers for collective bargaining
• Direct selling: Farmer's markets, WhatsApp groups, tie-ups with restaurants/hotels
• Value addition: processing (pickle, flour, juice) increases income 3–5x

⭐ KEY TIPS
• Keep a farm diary — record inputs, costs, yields, weather
• Join your local KVK for free training and demonstrations
• Water conservation is the #1 priority for sustainable farming
""",
}

# Search query templates per language for each category
CATEGORY_SEARCH_TERMS = {
    "Technology":  {
        "en": "programming tutorial for beginners",
        "hi": "programming tutorial Hindi",
        "ta": "programming tutorial Tamil",
        "te": "programming tutorial Telugu",
        "bn": "programming tutorial Bengali",
        "mr": "programming tutorial Marathi",
        "gu": "programming tutorial Gujarati",
        "kn": "programming tutorial Kannada",
        "ml": "programming tutorial Malayalam",
        "pa": "programming tutorial Punjabi",
    },
    "Marketing":   {
        "en": "digital marketing tutorial",
        "hi": "digital marketing Hindi tutorial",
        "ta": "digital marketing Tamil",
        "te": "digital marketing Telugu",
        "bn": "digital marketing Bengali",
        "mr": "digital marketing Marathi",
        "gu": "digital marketing Gujarati",
        "kn": "digital marketing Kannada",
        "ml": "digital marketing Malayalam",
        "pa": "digital marketing Punjabi",
    },
    "Finance":     {
        "en": "personal finance investing basics",
        "hi": "personal finance Hindi",
        "ta": "personal finance Tamil",
        "te": "personal finance Telugu",
        "bn": "personal finance Bengali",
        "mr": "personal finance Marathi",
        "gu": "personal finance Gujarati",
        "kn": "personal finance Kannada",
        "ml": "personal finance Malayalam",
        "pa": "personal finance Punjabi",
    },
    "Language":    {
        "en": "spoken English communication skills",
        "hi": "spoken English Hindi medium",
        "ta": "spoken English Tamil medium",
        "te": "spoken English Telugu medium",
        "bn": "spoken English Bengali medium",
        "mr": "spoken English Marathi medium",
        "gu": "spoken English Gujarati medium",
        "kn": "spoken English Kannada medium",
        "ml": "spoken English Malayalam medium",
        "pa": "spoken English Punjabi medium",
    },
    "Agriculture": {
        "en": "modern farming techniques tutorial",
        "hi": "kheti farming tutorial Hindi",
        "ta": "farming tutorial Tamil",
        "te": "farming tutorial Telugu",
        "bn": "farming tutorial Bengali",
        "mr": "farming tutorial Marathi",
        "gu": "farming tutorial Gujarati",
        "kn": "farming tutorial Kannada",
        "ml": "farming tutorial Malayalam",
        "pa": "farming tutorial Punjabi",
    },
    "Healthcare":  {
        "en": "community health worker training",
        "hi": "health training Hindi",
        "ta": "health training Tamil",
        "te": "health training Telugu",
        "bn": "health training Bengali",
        "mr": "health training Marathi",
        "gu": "health training Gujarati",
        "kn": "health training Kannada",
        "ml": "health training Malayalam",
        "pa": "health training Punjabi",
    },
}

# Curated fallback videos per category + language (used when no API key is set)
# Each entry: {id, title, channel, views, duration}
# Per-video metadata: description (from video page) + notes (from description/pinned comment)
# Keyed by YouTube video ID
VIDEO_META = {
    # ── Technology ──────────────────────────────────────────────────────────
    "rfscVS0vtbw": {
        "description": "Learn Python in this full tutorial course for beginners. This course covers the fundamentals of Python programming including variables, data types, loops, functions, and more.",
        "notes": "📌 Chapters:\n0:00 Introduction\n2:14 Installing Python & PyCharm\n8:05 Setup & Hello World\n13:12 Variables\n20:45 Strings\n30:22 Numbers\n38:32 Getting Input from Users\n43:28 Building a Calculator\n50:45 Lists\n1:01:32 Tuples\n1:07:42 Functions\n1:18:51 Return Statement\n1:23:37 If Statements\n1:34:11 Dictionaries\n1:48:55 While Loops\n1:57:44 For Loops\n2:05:11 Exponent Function\n2:10:58 2D Lists & Nested Loops\n2:20:18 Comments\n2:23:45 Try / Except\n2:30:37 Reading Files\n2:40:07 Writing to Files\n2:47:30 Modules & Pip\n2:52:58 Classes & Objects\n3:01:44 Building a Multiple Choice Quiz\n3:20:43 Object Functions\n3:30:21 Inheritance\n3:42:40 Python Interpreter",
    },
    "t2ypzz6gJm0": {
        "description": "Complete Python course by Shradha Khapra (Apna College). Covers Python from scratch — perfect for beginners. Includes OOP, file handling, and projects.",
        "notes": "📌 Topics Covered:\n• Variables, Data Types, Operators\n• Strings, Lists, Tuples, Sets, Dictionaries\n• Conditional Statements & Loops\n• Functions, Recursion, Lambda\n• OOP: Classes, Objects, Inheritance, Polymorphism\n• File Handling\n• Exception Handling\n• Modules & Libraries\n\n💡 Practice: After each topic, solve 5 problems on LeetCode or HackerRank.\n📎 Code: github.com/apna-college/Python",
    },
    "gfDE2a7MKjA": {
        "description": "Python tutorial in Hindi — complete course by CodeWithHarry. Covers all Python basics to advanced topics in simple Hindi language.",
        "notes": "📌 Chapters (Hindi):\n• Python क्या है और Install कैसे करें\n• Variables और Data Types\n• Operators\n• Strings\n• Lists, Tuples, Sets, Dictionaries\n• Conditional Statements\n• Loops (for, while)\n• Functions\n• OOP Concepts\n• File Handling\n• Exception Handling\n\n📎 Source Code: github.com/CodeWithHarry/Python-Tutorial-Hindi",
    },
    "PkZNo7MFNFg": {
        "description": "JavaScript full course for beginners by freeCodeCamp. Learn JS from scratch — variables, functions, DOM manipulation, events, and ES6+ features.",
        "notes": "📌 Chapters:\n0:00 Introduction\n3:11 Variables\n7:15 Data Types\n12:30 Functions\n20:00 Arrays\n28:00 Objects\n35:00 Loops\n42:00 DOM Manipulation\n55:00 Events\n1:05:00 ES6 Arrow Functions\n1:15:00 Promises & Async/Await\n1:30:00 Fetch API\n\n💡 Tip: Open browser console (F12) and practice every example live.",
    },
    "qw--VYLpxG4": {
        "description": "Python for Everybody — full university-level course by Dr. Chuck (University of Michigan). Covers Python 3, data structures, web scraping, databases, and data visualisation.",
        "notes": "📌 Course Sections:\n• Chapter 1: Why Program?\n• Chapter 2: Variables & Expressions\n• Chapter 3: Conditional Code\n• Chapter 4: Functions\n• Chapter 5: Loops & Iterations\n• Chapter 6: Strings\n• Chapter 7: Files\n• Chapter 8: Lists\n• Chapter 9: Dictionaries\n• Chapter 10: Tuples\n• Chapter 11: Regular Expressions\n• Chapter 12: Network Programming\n• Chapter 13: Web Services\n• Chapter 14: OOP\n• Chapter 15: Databases & SQL\n\n📎 Free textbook: py4e.com",
    },
    "ysEN5RaKOlA": {
        "description": "Web development full course — HTML, CSS, JavaScript, React, Node.js, and more. Build real projects from scratch.",
        "notes": "📌 What You'll Build:\n• Personal Portfolio Website\n• Responsive Landing Page\n• JavaScript Calculator\n• Weather App (API)\n• Full-Stack Todo App\n\n📌 Tools Needed:\n• VS Code (free)\n• Chrome Browser\n• Git & GitHub\n\n💡 Tip: Code along — don't just watch.",
    },
    # ── Marketing ───────────────────────────────────────────────────────────
    "bixR-KIJKYM": {
        "description": "Digital Marketing full course by Simplilearn. Covers SEO, SEM, social media, email marketing, content marketing, and web analytics.",
        "notes": "📌 Modules:\n1. Introduction to Digital Marketing\n2. Website Planning & Creation\n3. Search Engine Optimisation (SEO)\n4. Search Engine Marketing (Google Ads)\n5. Social Media Marketing\n6. Email Marketing\n7. Content Marketing\n8. Mobile Marketing\n9. Web Analytics (Google Analytics)\n10. Digital Marketing Strategy\n\n💡 Get Google Digital Garage certification (free) after this course.",
    },
    "nU-IIXBWlS4": {
        "description": "SEO tutorial for beginners by Ahrefs. Learn how search engines work, keyword research, on-page SEO, link building, and technical SEO.",
        "notes": "📌 Key Takeaways:\n• Keyword Research: use Ahrefs, Google Keyword Planner, Ubersuggest\n• On-Page: title tag (60 chars), meta description (160 chars), H1 tag\n• Content: answer search intent, use LSI keywords\n• Backlinks: guest posts, HARO, broken link building\n• Technical: page speed, mobile-friendly, HTTPS, Core Web Vitals\n\n📎 Free SEO tools: Google Search Console, Google Analytics, Ahrefs Webmaster Tools",
    },
    "1uEquiEe1GU": {
        "description": "Social media marketing full course. Learn to grow on Instagram, Facebook, YouTube, LinkedIn, and Twitter with proven strategies.",
        "notes": "📌 Platform Strategies:\n• Instagram: Reels > Stories > Posts. Post 3–5x/week.\n• Facebook: Groups + Ads. Organic reach is low — boost posts.\n• YouTube: SEO titles, thumbnails, first 30 seconds hook.\n• LinkedIn: Thought leadership posts, connect with decision-makers.\n• Twitter/X: Threads perform best. Engage with trending topics.\n\n💡 Use Buffer or Hootsuite to schedule posts across platforms.",
    },
    # ── Finance ─────────────────────────────────────────────────────────────
    "ZoqgAy3h4OM": {
        "description": "TED Talk by John Mullins — 6 Tips on Being a Successful Entrepreneur. Professor at London Business School shares counter-conventional mindsets that drive entrepreneurial success.",
        "notes": "📌 John Mullins' 6 Tips:\n1. Get the cash — customer-funded business models beat VC dependency\n2. Think narrow, not broad — focus on one customer, one problem first\n3. Problem first, solution second — fall in love with the problem, not your idea\n4. Ask for the cash — don't wait, test willingness to pay early\n5. Beg, borrow, don't steal — use other people's resources creatively\n6. Persistence + adaptability — pivot when needed, never quit on the goal\n\n💡 Key insight: Successful entrepreneurs break conventional rules. The best businesses are built on real customer pain, not investor money.",
    },
    "GkDMCNLSV8k": {
        "description": "Personal finance and investing basics. Learn budgeting, saving, investing in stocks and index funds, and building wealth over time.",
        "notes": "📌 Key Concepts:\n• Pay yourself first: automate 20% savings\n• Emergency fund: 3–6 months expenses in liquid account\n• Index funds beat most active fund managers over 10+ years\n• Compound interest: ₹10,000 at 12% for 20 years = ₹96,000+\n• Avoid lifestyle inflation as income grows\n\n📌 India-specific:\n• PPF: 7.1% tax-free, ₹1.5L/year limit\n• ELSS Mutual Funds: tax saving + market returns\n• NPS: pension + tax benefit under 80CCD",
    },
    "p7HKvqRI_Bo": {
        "description": "Stock market for beginners — how to invest in stocks, understand market basics, read charts, and build a portfolio.",
        "notes": "📌 Basics:\n• BSE (Bombay Stock Exchange) & NSE (National Stock Exchange)\n• Demat Account: open with Zerodha, Groww, or Upstox (free)\n• Sensex = top 30 companies on BSE. Nifty 50 = top 50 on NSE.\n• P/E Ratio: price ÷ earnings. Lower = cheaper stock.\n• Diversify: don't put all money in one stock\n\n⚠️ Never invest money you can't afford to lose. Start with index funds.",
    },
    "PHe0bXAIuk0": {
        "description": "Investing for beginners — full course covering stocks, bonds, mutual funds, ETFs, real estate, and retirement planning.",
        "notes": "📌 Investment Ladder (safest to riskiest):\n1. Savings Account / FD\n2. Government Bonds / PPF\n3. Debt Mutual Funds\n4. Balanced/Hybrid Funds\n5. Equity Mutual Funds (Index)\n6. Direct Stocks\n7. Crypto / Derivatives (high risk)\n\n💡 Rule: Invest only what you understand. Start SIP with ₹500/month.",
    },
    # ── Language ────────────────────────────────────────────────────────────
    "9RCuRUKSRt8": {
        "description": "Rachel's English — Speak English Naturally: 2-Hour Vocabulary & Conversation Masterclass. Uses real American English conversations to teach vocabulary, pronunciation, linking, and natural speech patterns.",
        "notes": "📌 What You'll Learn:\n• Natural American English pronunciation & linking\n• Real-life vocabulary from everyday conversations\n• How Americans greet each other & small talk\n• Reductions: 'gonna', 'wanna', 'gotta', 'kinda'\n• Stress and intonation patterns\n• Listening comprehension with native speakers\n\n💡 Tips from Rachel:\n• Mimic native speakers — pause, repeat, record yourself\n• Focus on connected speech, not individual words\n• Watch with English subtitles, then without\n• Practice 15 min daily consistently beats 2 hours once a week",
    },
    "t2ypzz6gJm0": {
        "description": "Apna College — How to Improve English Speaking for Interviews. Covers pronunciation, confidence building, common interview questions, and professional communication tips.",
        "notes": "📌 Key Topics:\n• How to introduce yourself in English (1-minute pitch)\n• Common HR interview questions & model answers\n• Pronunciation tips: stress, intonation, clarity\n• Body language + eye contact during interviews\n• Vocabulary for professional settings\n• Practice: record yourself answering 5 questions daily\n\n💡 Tip: Watch this video 2–3 times and practice each section out loud.",
    },
    "lMb5UMFbMzQ": {
        "description": "Spoken English full course by Spoken English Guru (Awal). Complete English speaking course from basic to advanced — pronunciation, grammar, vocabulary, and fluency.",
        "notes": "📌 Course Structure:\n• Basic English sentences and structures\n• Tenses (all 12 tenses with examples)\n• Modal verbs: can, could, should, would, must\n• Prepositions in context\n• Vocabulary building techniques\n• Pronunciation and accent\n• Conversation practice scripts\n• Interview preparation\n\n📎 Free PDF notes available at: spokenenglishguru.com\n💡 Practice: speak 15 minutes daily, record yourself, listen back.",
    },
    "ByYKyiooqLo": {
        "description": "English grammar full course by English with Lucy. Covers all grammar rules with clear explanations and examples.",
        "notes": "📌 Grammar Topics:\n• Parts of Speech: noun, verb, adjective, adverb, pronoun, preposition, conjunction\n• Tenses: simple, continuous, perfect, perfect continuous\n• Active & Passive Voice\n• Direct & Indirect Speech\n• Conditionals: zero, first, second, third\n• Articles: a, an, the\n• Punctuation rules\n\n💡 Grammar tip: Learn rules in context (sentences), not in isolation.",
    },
    "4_MnFBBBFMg": {
        "description": "English speaking practice — real conversations, phrases, and expressions used in daily life. Improve fluency fast.",
        "notes": "📌 Useful Phrases:\n• Agreeing: 'Absolutely!', 'That's a great point.', 'I couldn't agree more.'\n• Disagreeing: 'I see it differently.', 'That's interesting, but...'\n• Asking for clarification: 'Could you elaborate on that?', 'What do you mean by...?'\n• Expressing opinion: 'In my view...', 'As far as I'm concerned...'\n• Transitions: 'Furthermore', 'However', 'On the other hand', 'In conclusion'\n\n💡 Watch 1 episode of an English show daily with English subtitles.",
    },
    # ── Agriculture ─────────────────────────────────────────────────────────
    "iloAQmroRK0": {
        "description": "SARE — What is Sustainable Agriculture? Episode 1. Covers the whole-farm approach: cover crops, conservation tillage, ecological pest management, grazing, and water conservation.",
        "notes": "📌 Key Principles of Sustainable Agriculture:\n• Soil health first — healthy soil = healthy crops = healthy people\n• Biodiversity: grow multiple crops, support pollinators\n• Water conservation: drip irrigation, rainwater harvesting, mulching\n• Reduce chemical inputs — use compost, bio-pesticides, crop rotation\n• Long-term thinking: farm for future generations, not just this season\n• Community: local food systems reduce transport emissions\n\n💡 Sustainable ≠ low yield. Modern sustainable farms can match or exceed conventional yields.",
    },
    "nGl_v5kf8q0": {
        "description": "AgriTech Revolution — How Technology is Transforming Agriculture. Covers drones, IoT sensors, AI crop advisory, precision farming, and digital market platforms for farmers.",
        "notes": "📌 AgriTech Tools for Indian Farmers:\n• Kisan Suvidha app: weather, market prices, expert advice (free, Govt)\n• eNAM: sell crops online at national market prices\n• Fasal: AI-based crop advisory, pest & disease alerts\n• Drone spraying: 1 acre in 10 min, 30% less pesticide\n• IoT soil sensors: real-time moisture, pH, nutrient data\n• Satellite imagery: crop health monitoring from space\n\n📌 Getting Started:\n1. Download Kisan Suvidha (free)\n2. Register on eNAM portal\n3. Contact local KVK for drone demo",
    },
    "Z0GFRcFm-aY": {
        "description": "Modern farming techniques — sustainable agriculture practices including soil health, crop rotation, water management, and organic methods for Indian farmers.",
        "notes": "📌 Key Techniques:\n• Crop Rotation: prevents soil depletion, breaks pest cycles\n• Intercropping: grow two crops together (e.g. maize + beans)\n• Mulching: cover soil with straw/leaves — retains moisture, suppresses weeds\n• Composting: kitchen waste + dry leaves → rich fertiliser in 45 days\n• Integrated Pest Management (IPM): use natural predators before pesticides\n\n📌 Govt Schemes:\n• PM-KISAN: ₹6,000/year direct to farmer bank account\n• Soil Health Card: free soil testing at KVK\n• PMFBY: crop insurance at subsidised premium",
    },
    "evPFe5KCXQ4": {
        "description": "Organic farming full guide — how to start organic farming in India, certification process, market linkage, and profitability.",
        "notes": "📌 Steps to Start Organic Farming:\n1. Stop chemical inputs — transition period 2–3 years\n2. Build soil health with compost, vermicompost, green manure\n3. Use bio-pesticides: neem oil, Trichoderma, Beauveria bassiana\n4. Get NPOP certification for export markets\n5. Sell through: organic stores, FPOs, online (BigBasket, Jiomart)\n\n💡 Organic premium: 20–50% higher price than conventional produce.",
    },
    "XqZsoesa55w": {
        "description": "Drip irrigation complete guide — installation, maintenance, and cost-benefit analysis for Indian farmers. Covers all types of drip systems.",
        "notes": "📌 Drip Irrigation Benefits:\n• Saves 40–60% water vs flood irrigation\n• Reduces fertiliser use by 30% (fertigation)\n• Increases yield by 20–50%\n• Reduces weed growth\n• Works on uneven terrain\n\n📌 Cost & Subsidy:\n• Cost: ₹40,000–80,000 per acre\n• Subsidy: 55–90% under PM Krishi Sinchayee Yojana\n• Payback period: 2–3 seasons\n\n📌 Maintenance:\n• Flush main lines weekly\n• Check emitters monthly\n• Clean filters every 2 weeks",
    },
    "Ks-_Mh1QhMc": {
        "description": "Content marketing strategy — how to create content that attracts, engages, and converts your target audience.",
        "notes": "📌 Content Marketing Framework:\n1. Define audience (buyer persona)\n2. Set goals (traffic, leads, sales)\n3. Choose content types (blog, video, podcast, infographic)\n4. Create content calendar\n5. Distribute (SEO, social, email)\n6. Measure (traffic, engagement, conversions)\n\n💡 80/20 rule: 80% educational/entertaining, 20% promotional.",
    },
    # ── Healthcare ───────────────────────────────────────────────────────────
    "bixR-KIJKYM_health": {
        "description": "Yoga and wellness full course — beginner to intermediate yoga practices for physical and mental health.",
        "notes": "📌 Daily Practice (30 min):\n• 5 min: Pranayama (breathing)\n• 10 min: Sun Salutation (Surya Namaskar)\n• 10 min: Standing poses\n• 5 min: Savasana (relaxation)\n\n💡 Benefits: reduces stress, improves flexibility, better sleep, boosts immunity.",
    },
}

FALLBACK_VIDEOS = {
    "Technology": {
        "en": [
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course for Beginners", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course for Beginners", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
            {"id": "qw--VYLpxG4", "title": "Python for Everybody – Full Course", "channel": "freeCodeCamp.org", "views": "5.8M views", "duration": "13:39:57"},
            {"id": "ysEN5RaKOlA", "title": "Web Development Full Course – 10 Hours", "channel": "Traversy Media", "views": "3.2M views", "duration": "10:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Python Full Course for Beginners – Shradha Khapra", "channel": "Apna College", "views": "12M views", "duration": "12:00:00"},
        ],
        "hi": [
            {"id": "gfDE2a7MKjA", "title": "Python Tutorial in Hindi – Full Course", "channel": "CodeWithHarry", "views": "8.5M views", "duration": "5:30:00"},
            {"id": "7wnove7LsuE", "title": "JavaScript Tutorial in Hindi", "channel": "CodeWithHarry", "views": "4.2M views", "duration": "4:00:00"},
            {"id": "QH2-TGUlwu4", "title": "C++ Full Course Hindi", "channel": "CodeWithHarry", "views": "3.1M views", "duration": "6:00:00"},
            {"id": "WGJJIrtnfpk", "title": "Web Development Roadmap Hindi", "channel": "Apna College", "views": "2.8M views", "duration": "1:00:00"},
            {"id": "irqbmMNs2Bo", "title": "Data Structures in Hindi", "channel": "Apna College", "views": "2.3M views", "duration": "8:00:00"},
        ],
        "ta": [
            {"id": "kqtD5dpn9C8", "title": "Python Full Course Tamil", "channel": "Tamil Tutorials", "views": "1.2M views", "duration": "4:00:00"},
            {"id": "8ext9G7xspg", "title": "Web Development Tamil Tutorial", "channel": "Tamil Coding", "views": "800K views", "duration": "3:00:00"},
            {"id": "tPYj3fTB0WY", "title": "Java Programming Tamil Tutorial", "channel": "Tamil Coding School", "views": "600K views", "duration": "3:30:00"},
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
        ],
        "te": [
            {"id": "NhBmd_N9GkA", "title": "Python Tutorial in Telugu", "channel": "Telugu Tech Tuts", "views": "900K views", "duration": "4:00:00"},
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "gfDE2a7MKjA", "title": "Python Tutorial in Hindi", "channel": "CodeWithHarry", "views": "8.5M views", "duration": "5:30:00"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
            {"id": "ysEN5RaKOlA", "title": "Web Development Full Course", "channel": "Traversy Media", "views": "3.2M views", "duration": "10:00:00"},
        ],
        "bn": [
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "gfDE2a7MKjA", "title": "Python Tutorial in Hindi", "channel": "CodeWithHarry", "views": "8.5M views", "duration": "5:30:00"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
            {"id": "qw--VYLpxG4", "title": "Python for Everybody – Full Course", "channel": "freeCodeCamp.org", "views": "5.8M views", "duration": "13:39:57"},
            {"id": "ysEN5RaKOlA", "title": "Web Development Full Course", "channel": "Traversy Media", "views": "3.2M views", "duration": "10:00:00"},
        ],
        "mr": [
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "gfDE2a7MKjA", "title": "Python Tutorial in Hindi", "channel": "CodeWithHarry", "views": "8.5M views", "duration": "5:30:00"},
            {"id": "7wnove7LsuE", "title": "JavaScript Tutorial in Hindi", "channel": "CodeWithHarry", "views": "4.2M views", "duration": "4:00:00"},
            {"id": "WGJJIrtnfpk", "title": "Web Development Roadmap Hindi", "channel": "Apna College", "views": "2.8M views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
        ],
        "gu": [
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "gfDE2a7MKjA", "title": "Python Tutorial in Hindi", "channel": "CodeWithHarry", "views": "8.5M views", "duration": "5:30:00"},
            {"id": "7wnove7LsuE", "title": "JavaScript Tutorial in Hindi", "channel": "CodeWithHarry", "views": "4.2M views", "duration": "4:00:00"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
            {"id": "ysEN5RaKOlA", "title": "Web Development Full Course", "channel": "Traversy Media", "views": "3.2M views", "duration": "10:00:00"},
        ],
        "kn": [
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "gfDE2a7MKjA", "title": "Python Tutorial in Hindi", "channel": "CodeWithHarry", "views": "8.5M views", "duration": "5:30:00"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
            {"id": "qw--VYLpxG4", "title": "Python for Everybody – Full Course", "channel": "freeCodeCamp.org", "views": "5.8M views", "duration": "13:39:57"},
            {"id": "ysEN5RaKOlA", "title": "Web Development Full Course", "channel": "Traversy Media", "views": "3.2M views", "duration": "10:00:00"},
        ],
        "ml": [
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "gfDE2a7MKjA", "title": "Python Tutorial in Hindi", "channel": "CodeWithHarry", "views": "8.5M views", "duration": "5:30:00"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
            {"id": "kqtD5dpn9C8", "title": "Python Full Course Tamil", "channel": "Tamil Tutorials", "views": "1.2M views", "duration": "4:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Web Development Full Course", "channel": "Traversy Media", "views": "3.2M views", "duration": "10:00:00"},
        ],
        "pa": [
            {"id": "rfscVS0vtbw", "title": "Learn Python – Full Course", "channel": "freeCodeCamp.org", "views": "35M views", "duration": "4:26:52"},
            {"id": "gfDE2a7MKjA", "title": "Python Tutorial in Hindi", "channel": "CodeWithHarry", "views": "8.5M views", "duration": "5:30:00"},
            {"id": "7wnove7LsuE", "title": "JavaScript Tutorial in Hindi", "channel": "CodeWithHarry", "views": "4.2M views", "duration": "4:00:00"},
            {"id": "PkZNo7MFNFg", "title": "JavaScript Full Course", "channel": "freeCodeCamp.org", "views": "14M views", "duration": "3:26:42"},
            {"id": "ysEN5RaKOlA", "title": "Web Development Full Course", "channel": "Traversy Media", "views": "3.2M views", "duration": "10:00:00"},
        ],
    },
    "Marketing": {
        "en": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "hi": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "ta": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "te": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "bn": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "mr": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "gu": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "kn": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "ml": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
        "pa": [
            {"id": "bixR-KIJKYM", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "views": "4.5M views", "duration": "10:00:00"},
            {"id": "nU-IIXBWlS4", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "views": "2.1M views", "duration": "1:30:00"},
            {"id": "1uEquiEe1GU", "title": "Social Media Marketing Full Course", "channel": "Simplilearn", "views": "1.8M views", "duration": "8:00:00"},
            {"id": "o_MfF1j0MVo", "title": "Google Ads Tutorial 2024", "channel": "Surfside PPC", "views": "1.2M views", "duration": "2:00:00"},
            {"id": "Ks-_Mh1QhMc", "title": "Content Marketing Strategy", "channel": "HubSpot Marketing", "views": "900K views", "duration": "1:00:00"},
        ],
    },
    "Finance": {
        "en": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – John Mullins TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "hi": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "ta": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "te": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "bn": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "mr": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "gu": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "kn": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "ml": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
        "pa": [
            {"id": "ZoqgAy3h4OM", "title": "6 Tips on Being a Successful Entrepreneur – TED", "channel": "TED", "views": "1.8M views", "duration": "0:17:00"},
            {"id": "GkDMCNLSV8k", "title": "Personal Finance & Investing Basics", "channel": "Andrei Jikh", "views": "3.2M views", "duration": "1:00:00"},
            {"id": "p7HKvqRI_Bo", "title": "Stock Market for Beginners", "channel": "Investopedia", "views": "2.8M views", "duration": "1:30:00"},
            {"id": "PHe0bXAIuk0", "title": "Investing for Beginners – Full Course", "channel": "freeCodeCamp.org", "views": "1.5M views", "duration": "3:00:00"},
            {"id": "xdfeXqHFmPI", "title": "Financial Literacy – Full Video", "channel": "Practical Wisdom", "views": "1.2M views", "duration": "1:00:00"},
        ],
    },
    "Language": {
        "en": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – 2-Hour Masterclass", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Improve English Speaking for Interviews – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course – Beginner to Advanced", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice – Daily Conversations", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "hi": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview के लिए English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Hindi Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "ta": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Tamil Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "te": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Telugu Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "bn": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Bengali Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "mr": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Marathi Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "gu": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Gujarati Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "kn": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Kannada Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "ml": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Malayalam Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
        "pa": [
            {"id": "9RCuRUKSRt8", "title": "Speak English Naturally – Rachel's English", "channel": "Rachel's English", "views": "5M views", "duration": "2:00:00"},
            {"id": "t2ypzz6gJm0", "title": "Interview English Speaking – Apna College", "channel": "Apna College", "views": "8M views", "duration": "1:30:00"},
            {"id": "lMb5UMFbMzQ", "title": "Spoken English Full Course (Punjabi Medium)", "channel": "Spoken English Guru", "views": "12M views", "duration": "8:00:00"},
            {"id": "ByYKyiooqLo", "title": "English Grammar Full Course", "channel": "English with Lucy", "views": "4.1M views", "duration": "3:00:00"},
            {"id": "4_MnFBBBFMg", "title": "English Speaking Practice", "channel": "Learn English with TV Series", "views": "5.2M views", "duration": "1:00:00"},
        ],
    },
    "Agriculture": {
        "en": [
            {"id": "iloAQmroRK0", "title": "What is Sustainable Agriculture? – SARE", "channel": "SARE Outreach", "views": "1.5M views", "duration": "0:12:00"},
            {"id": "nGl_v5kf8q0", "title": "AgriTech Revolution – How Technology is Transforming Agriculture", "channel": "AgriTech World", "views": "900K views", "duration": "0:18:00"},
            {"id": "evPFe5KCXQ4", "title": "Organic Farming Full Guide – Start to Finish", "channel": "Organic India Farming", "views": "1.8M views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "Drip Irrigation Complete Guide for Farmers", "channel": "Krishi Jagran", "views": "1.2M views", "duration": "0:45:00"},
            {"id": "Z0GFRcFm-aY", "title": "Modern Farming Techniques – Sustainable Agriculture", "channel": "AgriTech India", "views": "2.5M views", "duration": "1:30:00"},
        ],
        "hi": [
            {"id": "iloAQmroRK0", "title": "Sustainable Agriculture क्या है – SARE", "channel": "SARE Outreach", "views": "1.5M views", "duration": "0:12:00"},
            {"id": "nGl_v5kf8q0", "title": "AgriTech – खेती में Technology का उपयोग", "channel": "AgriTech World", "views": "900K views", "duration": "0:18:00"},
            {"id": "Z0GFRcFm-aY", "title": "आधुनिक खेती की तकनीकें – Modern Farming Hindi", "channel": "Krishi Jagran Hindi", "views": "3.1M views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "जैविक खेती कैसे करें – Organic Farming Hindi", "channel": "Kisan Helpline", "views": "2.2M views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "ड्रिप सिंचाई – Drip Irrigation Setup Hindi", "channel": "Krishi Vigyan", "views": "1.5M views", "duration": "0:45:00"},
        ],
        "ta": [
            {"id": "Z0GFRcFm-aY", "title": "நவீன விவசாய நுட்பங்கள் – Modern Farming Tamil", "channel": "Tamil Vivasayam", "views": "1.2M views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "இயற்கை விவசாயம் – Organic Farming Tamil", "channel": "Uzhavar Ulagam", "views": "900K views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "சொட்டு நீர்ப்பாசனம் – Drip Irrigation Tamil", "channel": "Tamil Krishi", "views": "700K views", "duration": "0:45:00"},
            {"id": "rfscVS0vtbw", "title": "Soil Health & Testing Guide", "channel": "ICAR Agriculture", "views": "900K views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "AgriTech Apps for Farmers", "channel": "Digital Krishi", "views": "700K views", "duration": "0:30:00"},
        ],
        "te": [
            {"id": "Z0GFRcFm-aY", "title": "ఆధునిక వ్యవసాయ పద్ధతులు – Modern Farming Telugu", "channel": "Telugu Rythu", "views": "1.5M views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "సేంద్రీయ వ్యవసాయం – Organic Farming Telugu", "channel": "Rythu Nestam", "views": "1.1M views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "డ్రిప్ ఇరిగేషన్ – Drip Irrigation Telugu", "channel": "Krishi Telugu", "views": "800K views", "duration": "0:45:00"},
            {"id": "rfscVS0vtbw", "title": "Soil Health & Testing Guide", "channel": "ICAR Agriculture", "views": "900K views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "AgriTech Apps for Farmers", "channel": "Digital Krishi", "views": "700K views", "duration": "0:30:00"},
        ],
        "bn": [
            {"id": "Z0GFRcFm-aY", "title": "আধুনিক কৃষি পদ্ধতি – Modern Farming Bengali", "channel": "Krishi Bangla", "views": "1.0M views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "জৈব চাষ – Organic Farming Bengali", "channel": "Chashi Bondhu", "views": "800K views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "ড্রিপ সেচ – Drip Irrigation Bengali", "channel": "Krishi Bangla", "views": "600K views", "duration": "0:45:00"},
            {"id": "rfscVS0vtbw", "title": "Soil Health & Testing Guide", "channel": "ICAR Agriculture", "views": "900K views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "AgriTech Apps for Farmers", "channel": "Digital Krishi", "views": "700K views", "duration": "0:30:00"},
        ],
        "mr": [
            {"id": "Z0GFRcFm-aY", "title": "आधुनिक शेती तंत्र – Modern Farming Marathi", "channel": "Shetkari Mitra", "views": "1.3M views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "सेंद्रिय शेती – Organic Farming Marathi", "channel": "Krishi Marathi", "views": "1.0M views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "ठिबक सिंचन – Drip Irrigation Marathi", "channel": "Shetkari Marathi", "views": "800K views", "duration": "0:45:00"},
            {"id": "rfscVS0vtbw", "title": "Soil Health & Testing Guide", "channel": "ICAR Agriculture", "views": "900K views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "AgriTech Apps for Farmers", "channel": "Digital Krishi", "views": "700K views", "duration": "0:30:00"},
        ],
        "gu": [
            {"id": "Z0GFRcFm-aY", "title": "આધુનિક ખેતી – Modern Farming Gujarati", "channel": "Khedut Mitra", "views": "900K views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "જૈવિક ખેતી – Organic Farming Gujarati", "channel": "Krishi Gujarat", "views": "700K views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "ટપક સિંચાઈ – Drip Irrigation Gujarati", "channel": "Khedut Gujarat", "views": "500K views", "duration": "0:45:00"},
            {"id": "rfscVS0vtbw", "title": "Soil Health & Testing Guide", "channel": "ICAR Agriculture", "views": "900K views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "AgriTech Apps for Farmers", "channel": "Digital Krishi", "views": "700K views", "duration": "0:30:00"},
        ],
        "kn": [
            {"id": "Z0GFRcFm-aY", "title": "ಆಧುನಿಕ ಕೃಷಿ ತಂತ್ರಗಳು – Modern Farming Kannada", "channel": "Raitha Mitra", "views": "1.1M views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "ಸಾವಯವ ಕೃಷಿ – Organic Farming Kannada", "channel": "Krishi Kannada", "views": "800K views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "ಹನಿ ನೀರಾವರಿ – Drip Irrigation Kannada", "channel": "Raitha Kannada", "views": "600K views", "duration": "0:45:00"},
            {"id": "rfscVS0vtbw", "title": "Soil Health & Testing Guide", "channel": "ICAR Agriculture", "views": "900K views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "AgriTech Apps for Farmers", "channel": "Digital Krishi", "views": "700K views", "duration": "0:30:00"},
        ],
        "ml": [
            {"id": "Z0GFRcFm-aY", "title": "ആധുനിക കൃഷി – Modern Farming Malayalam", "channel": "Karshaka Mitra", "views": "900K views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "ജൈവ കൃഷി – Organic Farming Malayalam", "channel": "Krishi Kerala", "views": "700K views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "ഡ്രിപ്പ് ജലസേചനം – Drip Irrigation Malayalam", "channel": "Karshaka Kerala", "views": "500K views", "duration": "0:45:00"},
            {"id": "rfscVS0vtbw", "title": "Soil Health & Testing Guide", "channel": "ICAR Agriculture", "views": "900K views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "AgriTech Apps for Farmers", "channel": "Digital Krishi", "views": "700K views", "duration": "0:30:00"},
        ],
        "pa": [
            {"id": "Z0GFRcFm-aY", "title": "ਆਧੁਨਿਕ ਖੇਤੀ – Modern Farming Punjabi", "channel": "Kisan Punjab", "views": "1.0M views", "duration": "1:30:00"},
            {"id": "evPFe5KCXQ4", "title": "ਜੈਵਿਕ ਖੇਤੀ – Organic Farming Punjabi", "channel": "Krishi Punjab", "views": "800K views", "duration": "2:00:00"},
            {"id": "XqZsoesa55w", "title": "ਤੁਪਕਾ ਸਿੰਚਾਈ – Drip Irrigation Punjabi", "channel": "Kisan Mitra Punjab", "views": "600K views", "duration": "0:45:00"},
            {"id": "rfscVS0vtbw", "title": "Soil Health & Testing Guide", "channel": "ICAR Agriculture", "views": "900K views", "duration": "1:00:00"},
            {"id": "PkZNo7MFNFg", "title": "AgriTech Apps for Farmers", "channel": "Digital Krishi", "views": "700K views", "duration": "0:30:00"},
        ],
    },
    "Healthcare": {
        "en": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "hi": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "ta": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "te": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "bn": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "mr": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "gu": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "kn": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "ml": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
        "pa": [
            {"id": "rfscVS0vtbw", "title": "Community Health Worker Training", "channel": "WHO Health", "views": "1.5M views", "duration": "2:00:00"},
            {"id": "PkZNo7MFNFg", "title": "First Aid Full Course", "channel": "Red Cross", "views": "3.2M views", "duration": "1:30:00"},
            {"id": "LHBE6Q9oYEs", "title": "Mental Health Awareness", "channel": "Mind Channel", "views": "2.1M views", "duration": "1:00:00"},
            {"id": "ysEN5RaKOlA", "title": "Nutrition & Diet Basics", "channel": "Nutrition Academy", "views": "1.8M views", "duration": "1:30:00"},
            {"id": "bixR-KIJKYM", "title": "Yoga & Wellness Full Course", "channel": "Yoga with Adriene", "views": "5.5M views", "duration": "1:00:00"},
        ],
    },
}


def fetch_youtube_videos(query, language_code, max_results=5):
    """
    Fetch top YouTube videos for a query using the YouTube Data API v3.
    Falls back to curated list if YOUTUBE_API_KEY is not set.
    Returns list of dicts: {id, title, channel, views, duration, thumbnail}
    """
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        return None  # caller will use fallback

    try:
        # Step 1: Search for videos
        search_params = urllib.parse.urlencode({
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoCategoryId": "27",   # Education category
            "relevanceLanguage": language_code,
            "maxResults": max_results * 2,  # fetch extra to filter
            "order": "viewCount",
            "key": api_key,
        })
        search_url = f"https://www.googleapis.com/youtube/v3/search?{search_params}"
        with urllib.request.urlopen(search_url, timeout=5) as resp:
            search_data = json.loads(resp.read().decode())

        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])
                     if item.get("id", {}).get("kind") == "youtube#video"]
        if not video_ids:
            return None

        # Step 2: Get statistics + contentDetails for those videos
        stats_params = urllib.parse.urlencode({
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(video_ids),
            "key": api_key,
        })
        stats_url = f"https://www.googleapis.com/youtube/v3/videos?{stats_params}"
        with urllib.request.urlopen(stats_url, timeout=5) as resp:
            stats_data = json.loads(resp.read().decode())

        results = []
        for item in stats_data.get("items", []):
            vid_id    = item["id"]
            snippet   = item.get("snippet", {})
            stats     = item.get("statistics", {})
            details   = item.get("contentDetails", {})
            view_count = int(stats.get("viewCount", 0))
            # Format view count
            if view_count >= 1_000_000:
                views_str = f"{view_count/1_000_000:.1f}M views"
            elif view_count >= 1_000:
                views_str = f"{view_count//1_000}K views"
            else:
                views_str = f"{view_count} views"
            # Parse ISO 8601 duration (e.g. PT1H30M45S)
            dur_raw = details.get("duration", "PT0S")
            dur_str = _parse_duration(dur_raw)
            results.append({
                "id":        vid_id,
                "title":     snippet.get("title", ""),
                "channel":   snippet.get("channelTitle", ""),
                "views":     views_str,
                "duration":  dur_str,
                "thumbnail": f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
                "view_count": view_count,
            })

        # Sort by view count descending and return top N
        results.sort(key=lambda x: x["view_count"], reverse=True)
        for r in results:
            del r["view_count"]
        return results[:max_results]

    except Exception:
        return None


def _parse_duration(iso_duration):
    """Convert ISO 8601 duration (PT1H30M45S) to HH:MM:SS string."""
    import re
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    match = re.match(pattern, iso_duration)
    if not match:
        return "—"
    hours   = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def get_videos_for_course(course, language_code):
    """
    Return suggested YouTube videos for a course in the given language.
    Uses live API if YOUTUBE_API_KEY is set, otherwise returns curated fallback.
    """
    category = course.category
    lang = language_code if language_code in SUPPORTED_LANGUAGES else "en"
    lang_name = SUPPORTED_LANGUAGES.get(lang, "English")

    # Build search query: course title + language name for most relevant results
    title_words = " ".join(course.title.split()[:5])
    if lang == "en":
        query = f"{title_words} tutorial full course"
    else:
        query = f"{title_words} tutorial {lang_name}"

    # Try live API first
    live_results = fetch_youtube_videos(query, lang, max_results=5)
    if live_results:
        for r in live_results:
            if "thumbnail" not in r:
                r["thumbnail"] = f"https://img.youtube.com/vi/{r['id']}/hqdefault.jpg"
        return live_results

    # Fallback: curated list — try requested language, then English, then any category
    cat_fallback = FALLBACK_VIDEOS.get(category) or FALLBACK_VIDEOS.get("Technology", {})
    videos = cat_fallback.get(lang) or cat_fallback.get("en") or next(iter(cat_fallback.values()), [])
    result = []
    for v in videos:
        meta = VIDEO_META.get(v["id"], {})
        result.append({
            "id":          v["id"],
            "title":       v["title"],
            "channel":     v["channel"],
            "views":       v["views"],
            "duration":    v["duration"],
            "thumbnail":   f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg",
            "description": meta.get("description", ""),
            "notes":       meta.get("notes", ""),
        })
    return result


def seed_db():
    """Populate DB with sample courses if empty."""
    if Course.query.count() == 0:
        for c in SEED_COURSES:
            course = Course(**c)
            db.session.add(course)
        db.session.commit()


# ── Auth Routes ────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
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
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("login"))

        user = User(name=name, email=email, interest=interest, location=location, language=language)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Auto-enroll in first matching course
        course = Course.query.filter_by(category=interest).first()
        if course:
            enrollment = Enrollment(user_id=user.id, course_id=course.id, progress=0)
            db.session.add(enrollment)
            db.session.commit()

        login_user(user)
        flash(f"Welcome to SkillBridge, {name}! 🎉", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user     = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(next_page or url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ── Main Routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    courses = Course.query.all()
    categories = list({c.category for c in courses})
    return render_template("index.html", courses=courses, categories=categories)


@app.route("/dashboard")
@login_required
def dashboard():
    enrollments = current_user.enrollments.all()
    # Compute overall skill score
    skill_score = 0
    if enrollments:
        skill_score = int(sum(e.progress for e in enrollments) / len(enrollments))

    recommendations = SKILL_RECOMMENDATIONS.get(current_user.interest, [])
    all_courses = Course.query.all()

    return render_template(
        "dashboard.html",
        enrollments=enrollments,
        skill_score=skill_score,
        recommendations=recommendations,
        all_courses=all_courses,
        now=datetime.utcnow(),
    )


@app.route("/learn/<int:course_id>")
@login_required
def learn(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if not enrollment:
        enrollment = Enrollment(user_id=current_user.id, course_id=course_id, progress=5)
        db.session.add(enrollment)
        db.session.commit()

    modules      = course.get_modules()
    all_courses  = Course.query.all()
    course_notes = COURSE_NOTES.get(course.title, "")
    return render_template(
        "learn.html",
        course=course,
        enrollment=enrollment,
        modules=modules,
        all_courses=all_courses,
        supported_languages=SUPPORTED_LANGUAGES,
        user_language=current_user.language or "en",
        course_notes=course_notes,
    )


@app.route("/courses")
def courses():
    category = request.args.get("category", "")
    q        = request.args.get("q", "")
    query    = Course.query
    if category:
        query = query.filter_by(category=category)
    if q:
        query = query.filter(Course.title.ilike(f"%{q}%"))
    courses    = query.all()
    categories = list({c.category for c in Course.query.all()})
    return render_template("courses.html", courses=courses, categories=categories,
                           selected_category=category, search_q=q)


@app.route("/my-courses")
@login_required
def my_courses():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id)\
                    .order_by(Enrollment.enrolled_at.desc()).all()
    return render_template("my_courses.html", enrollments=enrollments)


@app.route("/progress")
@login_required
def progress():
    enrollments       = current_user.enrollments.all()
    profile           = get_or_create_profile(current_user.id)
    my_badges         = UserBadge.query.filter_by(user_id=current_user.id).all()
    completed_modules = CompletedModule.query.filter_by(user_id=current_user.id).count()
    level             = profile.xp // 500 + 1
    xp_in_level       = profile.xp % 500
    total_progress    = int(sum(e.progress for e in enrollments) / len(enrollments)) if enrollments else 0
    now               = datetime.utcnow()
    return render_template("progress.html",
        enrollments=enrollments, profile=profile,
        my_badges=my_badges, completed_modules=completed_modules,
        level=level, xp_in_level=xp_in_level,
        total_progress=total_progress, now=now,
        timedelta=timedelta,
    )


@app.route("/enroll/<int:course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    existing = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if not existing:
        enrollment = Enrollment(user_id=current_user.id, course_id=course_id, progress=0)
        db.session.add(enrollment)
        db.session.commit()
        flash(f"Enrolled in '{course.title}' successfully!", "success")
    else:
        flash("You are already enrolled in this course.", "info")
    return redirect(url_for("learn", course_id=course_id))


@app.route("/api/progress/<int:course_id>", methods=["POST"])
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


@app.route("/api/recommend")
@login_required
def recommend():
    """Simulate AI-driven skill recommendation."""
    interest = current_user.interest
    recs     = SKILL_RECOMMENDATIONS.get(interest, SKILL_RECOMMENDATIONS["Technology"])
    # Add a bit of 'AI-like' personalisation noise
    random.shuffle(recs)
    matched_courses = Course.query.filter_by(category=interest).all()
    course_data = [
        {"id": c.id, "title": c.title, "level": c.level, "duration_hrs": c.duration_hrs}
        for c in matched_courses
    ]
    return jsonify({
        "interest":        interest,
        "recommendations": recs[:3],
        "matched_courses": course_data,
        "message":         f"Based on your interest in {interest}, we recommend these paths.",
    })


@app.route("/api/set-language", methods=["POST"])
@login_required
def set_language():
    """Update the user's preferred language."""
    data = request.get_json()
    lang = data.get("language", "en")
    if lang not in SUPPORTED_LANGUAGES:
        return jsonify({"status": "error", "message": "Unsupported language"}), 400
    current_user.language = lang
    db.session.commit()
    return jsonify({"status": "ok", "language": lang, "label": SUPPORTED_LANGUAGES[lang]})


@app.route("/api/suggested-videos")
@login_required
def suggested_videos():
    """Return suggested videos for a course — used by the Videos tab in learn.html."""
    course_id = request.args.get("course_id", type=int)
    lang = request.args.get("lang") or current_user.language or "en"
    if not course_id:
        return jsonify({"videos": [], "error": "course_id required"}), 400
    course = Course.query.get_or_404(course_id)
    videos = get_videos_for_course(course, lang)
    # Rename 'id' → 'video_id' for the frontend
    for v in videos:
        v["video_id"] = v.pop("id", v.get("video_id", ""))
    return jsonify({"videos": videos, "course": course.title, "language": lang})


@app.route("/api/youtube-videos/<int:course_id>")
@login_required
def youtube_videos(course_id):
    """Return top YouTube video suggestions for a course in the user's preferred language."""
    course = Course.query.get_or_404(course_id)
    lang = request.args.get("lang") or current_user.language or "en"
    videos = get_videos_for_course(course, lang)
    return jsonify({
        "course_id": course_id,
        "language":  lang,
        "language_label": SUPPORTED_LANGUAGES.get(lang, "English"),
        "videos":    videos,
        "using_api": bool(os.environ.get("YOUTUBE_API_KEY")),
    })


@app.route("/api/mark-complete/<int:course_id>/<int:module_idx>", methods=["POST"])
@login_required
def mark_complete(course_id, module_idx):
    """Mark a specific module as complete for the current user. Idempotent — safe to call once."""
    course = Course.query.get_or_404(course_id)
    total  = len(course.get_modules())
    if module_idx < 0 or module_idx >= total:
        return jsonify({"status": "error", "message": "Invalid module index"}), 400

    # Check if already completed
    existing = CompletedModule.query.filter_by(
        user_id=current_user.id, course_id=course_id, module_idx=module_idx
    ).first()
    if existing:
        return jsonify({"status": "already_done"}), 200

    # Record completion
    db.session.add(CompletedModule(
        user_id=current_user.id, course_id=course_id, module_idx=module_idx
    ))

    # Update enrollment progress
    done_count = CompletedModule.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).count() + 1  # +1 for the one we just added (not yet committed)
    new_progress = min(100, round(done_count / total * 100))

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if enrollment:
        enrollment.progress = max(enrollment.progress, new_progress)

    db.session.commit()
    return jsonify({"status": "ok", "progress": enrollment.progress if enrollment else new_progress})


@app.route("/api/completed-modules/<int:course_id>")
@login_required
def completed_modules(course_id):
    """Return the set of completed module indices for the current user in a course."""
    rows = CompletedModule.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).all()
    return jsonify({"completed": [r.module_idx for r in rows]})


# ── Google Translate helper ────────────────────────────────────────────────────
def _google_translate(texts, target_lang):
    """
    Translate a list of strings to target_lang using Google Cloud Translation API v2.
    Returns list of translated strings (same order). Falls back to originals on error.
    Docs: https://cloud.google.com/translate/docs/reference/rest/v2/translate
    """
    api_key = app.config.get("GOOGLE_TRANSLATE_API_KEY", "")
    if not api_key or not texts or target_lang == "en":
        return texts
    try:
        body = json.dumps({"q": texts, "target": target_lang, "format": "text"}).encode()
        url  = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
        req  = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return [t["translatedText"] for t in data["data"]["translations"]]
    except Exception as exc:
        app.logger.warning("google_translate: failed target=%s: %s", target_lang, exc)
        return texts


@app.route("/api/translate-notes/<int:course_id>")
@login_required
def translate_notes(course_id):
    course = Course.query.get_or_404(course_id)
    notes  = COURSE_NOTES.get(course.title, "")
    lang   = request.args.get("lang") or current_user.language or "en"
    if lang == "en" or not notes:
        return jsonify({"notes": notes, "lang": lang, "translated": False})
    translated = _google_translate([notes], lang)
    return jsonify({"notes": translated[0], "lang": lang, "translated": translated[0] != notes})


@app.route("/api/translate", methods=["POST"])
@login_required
def translate_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    lang = data.get("target_lang", "en")
    if not text or lang == "en":
        return jsonify({"translated": text, "lang": lang})
    result = _google_translate([text], lang)
    return jsonify({"translated": result[0], "lang": lang})


@app.route("/api/translate-page", methods=["POST"])
@login_required
def translate_page():
    data    = request.get_json(silent=True) or {}
    strings = data.get("strings", [])
    lang    = data.get("lang") or current_user.language or "en"
    if lang == "en" or not strings or lang not in SUPPORTED_LANGUAGES:
        return jsonify({"translated": strings, "lang": lang})
    return jsonify({"translated": _google_translate(strings, lang), "lang": lang})


@app.route("/api/translate-quiz/<int:course_id>")
@login_required
def translate_quiz(course_id):
    quiz      = Quiz.query.filter_by(course_id=course_id).first_or_404()
    lang      = request.args.get("lang") or current_user.language or "en"
    questions = quiz.questions.all()

    field_order = ["question", "option_a", "option_b", "option_c", "option_d"]
    orig = [{"id": q.id, **{f: getattr(q, f) for f in field_order}} for q in questions]

    if lang == "en":
        return jsonify({"questions": orig, "translated": False})

    all_texts    = [getattr(q, f) or "" for q in questions for f in field_order]
    translations = _google_translate(all_texts, lang)

    if translations == all_texts:          # helper returned originals — API failed
        app.logger.warning("translate_quiz: no translation returned lang=%s course=%s", lang, course_id)
        return jsonify({"questions": orig, "translated": False, "error": "Translation service unavailable"})

    translated, idx = [], 0
    for q in questions:
        entry = {"id": q.id}
        for f in field_order:
            entry[f] = translations[idx]; idx += 1
        translated.append(entry)
    return jsonify({"questions": translated, "translated": True, "lang": lang})


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    """Peer-mentor chat: suggests courses based on user interest and progress."""
    data    = request.get_json(silent=True) or {}
    message = data.get("message", "").lower().strip()

    # Gather user context
    interest   = current_user.interest or "Technology"
    name       = current_user.name.split()[0]
    enrollments = current_user.enrollments.all()
    enrolled_ids = {e.course_id for e in enrollments}
    in_progress  = [e for e in enrollments if 0 < e.progress < 100]
    completed    = [e for e in enrollments if e.progress >= 100]

    # Courses not yet enrolled in, matching interest
    suggested = Course.query.filter(
        Course.category == interest,
        ~Course.id.in_(enrolled_ids)
    ).limit(3).all()
    # Fallback: any unenrolled courses
    if not suggested:
        suggested = Course.query.filter(~Course.id.in_(enrolled_ids)).limit(3).all()

    def course_list(courses):
        return "\n".join(f"• {c.title} ({c.level}, {c.duration_hrs}h) → /learn/{c.id}" for c in courses)

    # Intent matching
    if any(w in message for w in ("hi", "hello", "hey", "start", "begin")):
        reply = (f"Hey {name}! 👋 I'm your AI peer mentor.\n\n"
                 f"You're interested in **{interest}**. Here are courses I recommend:\n"
                 f"{course_list(suggested) if suggested else 'All courses enrolled!'}\n\n"
                 f"Ask me about study tips, career advice, or type 'progress' to see your status.")

    elif any(w in message for w in ("recommend", "suggest", "course", "learn", "what should", "next")):
        if suggested:
            reply = (f"Based on your interest in **{interest}**, here are your next courses:\n\n"
                     f"{course_list(suggested)}\n\n"
                     f"You have {len(in_progress)} course(s) in progress. "
                     f"{'Finish those first for best results! 💪' if in_progress else 'Start one today!'}")
        else:
            reply = f"You're enrolled in all {interest} courses! Try exploring other categories at /courses 🎉"

    elif any(w in message for w in ("progress", "status", "how am i", "doing")):
        if not enrollments:
            reply = f"You haven't enrolled in any courses yet, {name}. Start with: {suggested[0].title if suggested else 'Browse /courses'}"
        else:
            lines = [f"📊 Your learning progress, {name}:"]
            for e in enrollments[:4]:
                bar = "█" * (e.progress // 10) + "░" * (10 - e.progress // 10)
                lines.append(f"• {e.course.title}: {bar} {e.progress}%")
            if len(enrollments) > 4:
                lines.append(f"  …and {len(enrollments)-4} more courses")
            if completed:
                lines.append(f"\n✅ Completed: {len(completed)} course(s). Great work!")
            if in_progress:
                # Suggest the one closest to completion
                closest = max(in_progress, key=lambda e: e.progress)
                lines.append(f"\n🎯 Almost done: **{closest.course.title}** at {closest.progress}% — keep going!")
            reply = "\n".join(lines)

    elif any(w in message for w in ("study", "tip", "focus", "how to", "advice")):
        reply = (f"Top study tips for {interest}:\n\n"
                 "• Use 25-min Pomodoro sessions with 5-min breaks\n"
                 "• Take notes while watching — don't just passively view\n"
                 "• Build a small project after each module\n"
                 "• Review yesterday's notes before starting today\n"
                 "• Consistency beats intensity — 30 min/day > 4 hrs on weekends 🔥")

    elif any(w in message for w in ("career", "job", "employ", "salary", "work")):
        reply = (f"Career path for **{interest}**:\n\n"
                 "1. Complete 2–3 courses and earn certificates\n"
                 "2. Build a portfolio project (even a small one counts)\n"
                 "3. Add skills to LinkedIn and update your resume\n"
                 "4. Apply to internships or freelance gigs first\n"
                 "5. Check /skill-paths for a structured roadmap 🗺️")

    elif any(w in message for w in ("certificate", "cert", "badge")):
        reply = ("Certificates are issued when you:\n"
                 "✓ Reach 100% course progress\n"
                 "✓ Pass the quiz (≥60%)\n\n"
                 f"You've earned {len(completed)} certificate(s) so far. "
                 f"{'Keep going!' if len(completed) < len(enrollments) else 'Amazing — you completed everything! 🏆'}")

    elif any(w in message for w in ("quiz", "test", "exam")):
        reply = ("Quiz tips:\n\n"
                 "• Review the course notes before attempting\n"
                 "• You can retake quizzes — each attempt improves your score\n"
                 "• Read each question carefully — watch for 'NOT' and 'EXCEPT'\n"
                 "• Pass mark is 60%. You've got this! 🧠")

    else:
        # Generic helpful response with course suggestion
        reply = (f"I'm here to help, {name}! 😊\n\n"
                 f"Since you're into **{interest}**, you might like:\n"
                 f"{course_list(suggested[:2]) if suggested else 'All courses enrolled!'}\n\n"
                 "Ask me about: courses, progress, study tips, career, or certificates.")

    return jsonify({"reply": reply})


# ── Gamification ──────────────────────────────────────────────────────────────

BADGE_DEFS = [
    {"slug": "first_step",    "name": "First Step",       "icon": "👣", "desc": "Complete your first path step",      "xp": 50},
    {"slug": "quiz_pass",     "name": "Quiz Passer",       "icon": "🧠", "desc": "Pass your first quiz",               "xp": 100},
    {"slug": "streak_3",      "name": "3-Day Streak",      "icon": "🔥", "desc": "Learn 3 days in a row",              "xp": 75},
    {"slug": "streak_7",      "name": "Week Warrior",      "icon": "⚡", "desc": "Learn 7 days in a row",              "xp": 200},
    {"slug": "path_complete", "name": "Path Master",       "icon": "🗺️", "desc": "Complete an entire skill path",      "xp": 500},
    {"slug": "course_done",   "name": "Course Graduate",   "icon": "🎓", "desc": "Reach 100% on any course",           "xp": 150},
    {"slug": "top10",         "name": "Top 10",            "icon": "🏆", "desc": "Reach top 10 on the leaderboard",    "xp": 300},
    {"slug": "mentor_rated",  "name": "Helpful Mentor",    "icon": "🤝", "desc": "Receive 5 mentor ratings",           "xp": 200},
]


def get_or_create_profile(user_id):
    p = UserProfile.query.filter_by(user_id=user_id).first()
    if not p:
        p = UserProfile(user_id=user_id)
        db.session.add(p)
        db.session.flush()
    return p


def award_xp(user_id, points, badge_slug=None):
    """Add XP, update streak, optionally award a badge. Returns list of new badge names."""
    profile = get_or_create_profile(user_id)
    profile.xp += points
    today = datetime.utcnow().date()
    last  = profile.last_active.date() if profile.last_active else None
    if last == today:
        pass
    elif last and (today - last).days == 1:
        profile.streak += 1
    else:
        profile.streak = 1
    profile.last_active = datetime.utcnow()
    new_badges = []
    if badge_slug:
        badge = Badge.query.filter_by(slug=badge_slug).first()
        if badge and not UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
            db.session.add(UserBadge(user_id=user_id, badge_id=badge.id))
            profile.xp += badge.xp_reward
            new_badges.append(badge.name)
    # Auto-check streak badges
    for slug, threshold in [("streak_3", 3), ("streak_7", 7)]:
        if profile.streak >= threshold:
            b = Badge.query.filter_by(slug=slug).first()
            if b and not UserBadge.query.filter_by(user_id=user_id, badge_id=b.id).first():
                db.session.add(UserBadge(user_id=user_id, badge_id=b.id))
                profile.xp += b.xp_reward
                new_badges.append(b.name)
    db.session.commit()
    return new_badges


def seed_badges():
    for d in BADGE_DEFS:
        if not Badge.query.filter_by(slug=d["slug"]).first():
            db.session.add(Badge(slug=d["slug"], name=d["name"], icon=d["icon"],
                                 description=d["desc"], xp_reward=d["xp"]))
    db.session.commit()


@app.route("/gamification")
@login_required
def gamification():
    profile    = get_or_create_profile(current_user.id)
    my_badges  = UserBadge.query.filter_by(user_id=current_user.id).all()
    earned_ids = {ub.badge_id for ub in my_badges}
    all_badges = Badge.query.all()
    # Leaderboard: top 20 by XP
    top = (db.session.query(UserProfile, User)
           .join(User, User.id == UserProfile.user_id)
           .order_by(UserProfile.xp.desc()).limit(20).all())
    rank = next((i+1 for i, (p, _) in enumerate(top) if p.user_id == current_user.id), None)
    return render_template("gamification.html", profile=profile, my_badges=my_badges,
                           earned_ids=earned_ids, all_badges=all_badges,
                           leaderboard=top, my_rank=rank)


@app.route("/api/leaderboard")
@login_required
def api_leaderboard():
    top = (db.session.query(UserProfile, User)
           .join(User, User.id == UserProfile.user_id)
           .order_by(UserProfile.xp.desc()).limit(10).all())
    return jsonify([{"name": u.name, "xp": p.xp, "streak": p.streak,
                     "badges": UserBadge.query.filter_by(user_id=u.id).count()}
                    for p, u in top])


# ── Skill Path Routes ─────────────────────────────────────────────────────────

@app.route("/skill-paths")
@login_required
def skill_paths():
    enrolled_slugs = {
        e.path_slug for e in SkillPathEnrollment.query.filter_by(user_id=current_user.id).all()
    }
    # Build progress % per enrolled path
    progress_map = {}
    for slug in enrolled_slugs:
        path = next((p for p in SKILL_PATHS if p["slug"] == slug), None)
        if path:
            done = PathStepProgress.query.filter_by(user_id=current_user.id, path_slug=slug).count()
            progress_map[slug] = round(done / len(path["steps"]) * 100)
    return render_template("skill_paths.html", paths=SKILL_PATHS,
                           enrolled_slugs=enrolled_slugs, progress_map=progress_map)


@app.route("/skill-paths/<slug>")
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
    total = len(path["steps"])
    progress_pct = round(len(completed_steps) / total * 100) if total else 0
    lang = current_user.language if current_user.language in ("en","hi","kn","ta","te") else "en"
    path_notes = PATH_NOTES.get(slug, {}).get(lang, PATH_NOTES.get(slug, {}).get("en", ""))
    subtitle_lang = SUBTITLE_LANGS.get(lang, "en")
    return render_template("skill_path_detail.html", path=path, enrolled=enrolled,
                           completed_steps=completed_steps, progress_pct=progress_pct,
                           path_notes=path_notes, subtitle_lang=subtitle_lang)


@app.route("/skill-paths/<slug>/enroll", methods=["POST"])
@login_required
def enroll_skill_path(slug):
    if not any(p["slug"] == slug for p in SKILL_PATHS):
        abort(404)
    existing = SkillPathEnrollment.query.filter_by(user_id=current_user.id, path_slug=slug).first()
    if not existing:
        db.session.add(SkillPathEnrollment(user_id=current_user.id, path_slug=slug))
        db.session.commit()
        flash("You've enrolled in this skill path! 🚀", "success")
    return redirect(url_for("skill_path_detail", slug=slug))


@app.route("/api/skill-paths/<slug>/complete-step", methods=["POST"])
@login_required
def complete_path_step(slug):
    path = next((p for p in SKILL_PATHS if p["slug"] == slug), None)
    if not path:
        return jsonify({"error": "not found"}), 404
    step_index = request.get_json().get("step_index")
    if step_index is None or not (0 <= step_index < len(path["steps"])):
        return jsonify({"error": "invalid step"}), 400
    existing = PathStepProgress.query.filter_by(
        user_id=current_user.id, path_slug=slug, step_index=step_index
    ).first()
    if not existing:
        db.session.add(PathStepProgress(
            user_id=current_user.id, path_slug=slug, step_index=step_index
        ))
        db.session.commit()
        # Award XP; first-ever step gets badge
        total_done = PathStepProgress.query.filter_by(user_id=current_user.id).count()
        badge = "first_step" if total_done == 1 else None
        # Full path complete?
        path_done = PathStepProgress.query.filter_by(user_id=current_user.id, path_slug=slug).count()
        if path_done == len(path["steps"]):
            badge = "path_complete"
        award_xp(current_user.id, 30, badge)
    done = PathStepProgress.query.filter_by(user_id=current_user.id, path_slug=slug).count()
    return jsonify({"progress_pct": round(done / len(path["steps"]) * 100), "done": done})


@app.route("/api/skill-paths/<slug>/next-step")
@login_required
def skill_path_next_step(slug):
    path = next((p for p in SKILL_PATHS if p["slug"] == slug), None)
    if not path:
        return jsonify({"error": "not found"}), 404
    lang = current_user.language if current_user.language in NEXT_STEP_MSG else "en"
    completed = {r.step_index for r in PathStepProgress.query.filter_by(
        user_id=current_user.id, path_slug=slug).all()}
    # Find first incomplete step
    next_idx = next((i for i in range(len(path["steps"])) if i not in completed), None)
    if next_idx is None:
        return jsonify({"done": True, "message": I18N["step_done"][lang]})
    step = path["steps"][next_idx]
    msg = NEXT_STEP_MSG[lang].format(title=step["title"], desc=step["desc"])
    return jsonify({
        "done": False,
        "step_index": next_idx,
        "title": step["title"],
        "desc": step["desc"],
        "message": msg,
        "label": I18N["next_step"][lang],
    })


# ── Mentor Routes ─────────────────────────────────────────────────────────────

@app.route("/mentors")
@login_required
def mentors():
    skill_filter = request.args.get("skill", "").strip().lower()
    query = MentorProfile.query.filter_by(approved=True)
    if skill_filter:
        query = query.filter(MentorProfile.skills.ilike(f"%{skill_filter}%"))
    all_mentors = query.all()
    # Skill-based match: mentors whose skills overlap with user's interest
    interest = current_user.interest.lower()
    matched = [m for m in MentorProfile.query.filter_by(approved=True).all()
               if interest in m.skills.lower()]
    return render_template("mentors.html", mentors=all_mentors, matched=matched,
                           skill_filter=skill_filter)


@app.route("/mentors/apply", methods=["GET", "POST"])
@login_required
def mentor_apply():
    existing = MentorProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        bio  = request.form.get("bio", "").strip()
        skills = request.form.get("skills", "").strip()
        exp  = request.form.get("experience", "").strip()
        link = request.form.get("linkedin", "").strip()
        if existing:
            existing.bio = bio; existing.skills = skills
            existing.experience = exp; existing.linkedin = link
        else:
            db.session.add(MentorProfile(user_id=current_user.id, bio=bio,
                                         skills=skills, experience=exp, linkedin=link))
        db.session.commit()
        flash("Mentor application submitted! Awaiting admin approval.", "success")
        return redirect(url_for("mentors"))
    return render_template("mentor_apply.html", existing=existing)


@app.route("/mentors/<int:mentor_id>/rate", methods=["POST"])
@login_required
def rate_mentor(mentor_id):
    mentor = MentorProfile.query.get_or_404(mentor_id)
    rating = int(request.form.get("rating", 0))
    comment = request.form.get("comment", "").strip()
    if not 1 <= rating <= 5:
        flash("Rating must be 1–5.", "danger")
        return redirect(url_for("mentors"))
    existing = MentorRating.query.filter_by(mentor_id=mentor_id, user_id=current_user.id).first()
    if existing:
        existing.rating = rating; existing.comment = comment
    else:
        db.session.add(MentorRating(mentor_id=mentor_id, user_id=current_user.id,
                                    rating=rating, comment=comment))
    # Recalculate avg
    db.session.flush()
    ratings = MentorRating.query.filter_by(mentor_id=mentor_id).all()
    mentor.avg_rating = round(sum(r.rating for r in ratings) / len(ratings), 1)
    # Badge if mentor has 5+ ratings
    if len(ratings) >= 5:
        award_xp(mentor.user_id, 0, "mentor_rated")
    db.session.commit()
    flash("Rating submitted!", "success")
    return redirect(url_for("mentors"))


@app.route("/mentors/<int:mentor_id>/doubt", methods=["POST"])
@login_required
def submit_doubt(mentor_id):
    MentorProfile.query.get_or_404(mentor_id)
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()
    if not subject or not message:
        flash("Subject and message are required.", "danger")
        return redirect(url_for("mentors"))
    db.session.add(DoubtRequest(user_id=current_user.id, mentor_id=mentor_id,
                                subject=subject, message=message))
    db.session.commit()
    flash("Doubt request sent to mentor!", "success")
    return redirect(url_for("mentors"))


# ── Quiz Routes ───────────────────────────────────────────────────────────────

@app.route("/quiz/<int:course_id>")
@login_required
def take_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    quiz   = Quiz.query.filter_by(course_id=course_id).first()
    if not quiz:
        flash("No quiz available for this course yet.", "info")
        return redirect(url_for("learn", course_id=course_id))
    questions = quiz.questions.all()
    # Past attempts for this user
    attempts = QuizAttempt.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).order_by(QuizAttempt.attempted_at.desc()).all()
    return render_template("quiz.html", course=course, quiz=quiz,
                           questions=questions, attempts=attempts)


@app.route("/quiz/<int:course_id>/submit", methods=["POST"])
@login_required
def submit_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    quiz   = Quiz.query.filter_by(course_id=course_id).first_or_404()
    questions = quiz.questions.all()

    answers  = {}   # {question_id: chosen_option}
    correct  = 0
    results  = []   # per-question feedback

    for q in questions:
        chosen = request.form.get(f"q_{q.id}", "").lower()
        answers[q.id] = chosen
        is_correct = (chosen == q.correct)
        if is_correct:
            correct += 1
        results.append({
            "id":          q.id,
            "question":    q.question,
            "chosen":      chosen,
            "correct":     q.correct,
            "is_correct":  is_correct,
            "explanation": q.explanation,
            "options": {
                "a": q.option_a, "b": q.option_b,
                "c": q.option_c, "d": q.option_d,
            },
        })

    total   = len(questions)
    score   = round(correct / total * 100) if total else 0
    passed  = score >= quiz.pass_pct

    attempt = QuizAttempt(
        user_id=current_user.id, course_id=course_id, quiz_id=quiz.id,
        score=score, total_q=total, correct_q=correct, passed=passed,
    )
    db.session.add(attempt)
    db.session.commit()
    # Award XP for quiz attempt; badge on first pass
    xp_earned = score // 2  # up to 50 XP
    badge = "quiz_pass" if passed and QuizAttempt.query.filter_by(
        user_id=current_user.id, passed=True).count() == 1 else None
    award_xp(current_user.id, xp_earned, badge)

    # Auto-issue certificate if passed and enrollment is 100%
    cert = None
    if passed:
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id, course_id=course_id
        ).first()
        if enrollment and enrollment.progress >= 100:
            existing_cert = Certificate.query.filter_by(
                user_id=current_user.id, course_id=course_id
            ).first()
            if not existing_cert:
                import uuid
                cert = Certificate(
                    user_id=current_user.id, course_id=course_id,
                    cert_id=str(uuid.uuid4()),
                )
                db.session.add(cert)
                db.session.commit()
            else:
                cert = existing_cert

    return render_template("quiz_result.html",
                           course=course, quiz=quiz, attempt=attempt,
                           results=results, cert=cert)


@app.route("/certificate/<int:course_id>")
@login_required
def certificate(course_id):
    course = Course.query.get_or_404(course_id)
    cert   = Certificate.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if not cert:
        flash("Certificate not yet earned. Complete the course and pass the quiz.", "warning")
        return redirect(url_for("learn", course_id=course_id))
    return render_template("certificate.html", course=course, cert=cert, user=current_user)


@app.route("/api/quiz-analytics/<int:course_id>")
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
        "best_score": max((a.score for a in attempts), default=0),
        "total_attempts": len(attempts),
    })


# ── Quiz Seed Data ─────────────────────────────────────────────────────────────

QUIZ_SEED = {
    "Python for Data Science": {
        "title": "Python for Data Science Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"q": "Which function prints output in Python?",
             "a": "echo()", "b": "print()", "c": "console.log()", "d": "write()",
             "correct": "b", "exp": "print() is Python's built-in output function."},
            {"q": "What does len([1,2,3]) return?",
             "a": "2", "b": "4", "c": "3", "d": "0",
             "correct": "c", "exp": "len() returns the number of items in a list."},
            {"q": "Which library is used for data analysis in Python?",
             "a": "NumPy", "b": "Pandas", "c": "Matplotlib", "d": "Requests",
             "correct": "b", "exp": "Pandas provides DataFrame for data analysis."},
            {"q": "What is the correct way to create a list in Python?",
             "a": "{1,2,3}", "b": "(1,2,3)", "c": "[1,2,3]", "d": "<1,2,3>",
             "correct": "c", "exp": "Square brackets [] define a list in Python."},
            {"q": "Which method reads a CSV file in Pandas?",
             "a": "pd.open_csv()", "b": "pd.load()", "c": "pd.read_csv()", "d": "pd.import()",
             "correct": "c", "exp": "pd.read_csv() loads a CSV file into a DataFrame."},
        ],
    },
    "Digital Marketing Essentials": {
        "title": "Digital Marketing Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"q": "What does SEO stand for?",
             "a": "Social Engagement Optimisation", "b": "Search Engine Optimisation",
             "c": "Site Engagement Overview", "d": "Search Engagement Operations",
             "correct": "b", "exp": "SEO = Search Engine Optimisation — improving organic search rankings."},
            {"q": "What does PPC stand for in digital advertising?",
             "a": "Page Per Click", "b": "Pay Per Conversion", "c": "Pay Per Click", "d": "Paid Promotion Campaign",
             "correct": "c", "exp": "PPC = Pay Per Click — you pay only when someone clicks your ad."},
            {"q": "Which metric measures the percentage of visitors who leave after one page?",
             "a": "CTR", "b": "Bounce Rate", "c": "Conversion Rate", "d": "Impressions",
             "correct": "b", "exp": "Bounce Rate = % of single-page sessions with no interaction."},
            {"q": "Which tool is used to track website traffic for free?",
             "a": "Ahrefs", "b": "SEMrush", "c": "Google Analytics", "d": "Moz",
             "correct": "c", "exp": "Google Analytics 4 is free and tracks website visitors and behaviour."},
            {"q": "What is the 80/20 rule in content marketing?",
             "a": "80% ads, 20% organic", "b": "80% educational, 20% promotional",
             "c": "80% video, 20% text", "d": "80% paid, 20% free",
             "correct": "b", "exp": "80% of content should educate/entertain; only 20% should promote."},
        ],
    },
    "Financial Literacy & Entrepreneurship": {
        "title": "Financial Literacy Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"q": "What does the 50/30/20 budgeting rule suggest for savings?",
             "a": "50%", "b": "30%", "c": "20%", "d": "10%",
             "correct": "c", "exp": "The 50/30/20 rule: 50% needs, 30% wants, 20% savings/investments."},
            {"q": "What is the Rule of 72 used for?",
             "a": "Calculating tax", "b": "Estimating time to double money", "c": "Loan EMI", "d": "GST calculation",
             "correct": "b", "exp": "Divide 72 by interest rate to estimate years to double your money."},
            {"q": "What is the maximum annual investment limit for PPF?",
             "a": "₹50,000", "b": "₹1,00,000", "c": "₹1,50,000", "d": "₹2,00,000",
             "correct": "c", "exp": "PPF allows a maximum of ₹1.5 lakh per year with tax-free returns."},
            {"q": "What does MUDRA stand for?",
             "a": "Micro Units Development and Refinance Agency", "b": "Ministry of Urban Development Rural Areas",
             "c": "Micro Urban Development Refinance Authority", "d": "None of the above",
             "correct": "a", "exp": "MUDRA provides loans up to ₹10 lakh for small businesses."},
            {"q": "What is a good CIBIL credit score?",
             "a": "Above 500", "b": "Above 600", "c": "Above 750", "d": "Above 900",
             "correct": "c", "exp": "A CIBIL score above 750 is considered good for loan approvals."},
        ],
    },
    "Spoken English & Communication": {
        "title": "Spoken English Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"q": "Which is the correct sentence?",
             "a": "I am having a car.", "b": "I have a car.", "c": "I am have a car.", "d": "I has a car.",
             "correct": "b", "exp": "Stative verbs like 'have' are not used in continuous tense."},
            {"q": "What does the STAR method stand for in interviews?",
             "a": "Skill, Task, Action, Result", "b": "Situation, Task, Action, Result",
             "c": "Situation, Target, Approach, Result", "d": "Skill, Target, Action, Review",
             "correct": "b", "exp": "STAR = Situation, Task, Action, Result — used for behavioural interview answers."},
            {"q": "Which is the correct formal email closing?",
             "a": "Bye!", "b": "See ya", "c": "Best regards,", "d": "Cheers mate,",
             "correct": "c", "exp": "'Best regards,' is a standard professional email closing."},
            {"q": "What is the schwa sound?",
             "a": "The loudest vowel sound", "b": "The most common unstressed vowel in English",
             "c": "A consonant sound", "d": "A silent letter",
             "correct": "b", "exp": "The schwa /ə/ is the most common sound in English, heard in 'about', 'the'."},
            {"q": "Which article is used before a specific known noun?",
             "a": "a", "b": "an", "c": "the", "d": "no article",
             "correct": "c", "exp": "'The' is used when both speaker and listener know which specific thing is meant."},
        ],
    },
    "Web Development Bootcamp": {
        "title": "Web Development Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"q": "Which HTML tag defines the main heading?",
             "a": "<head>", "b": "<h1>", "c": "<title>", "d": "<header>",
             "correct": "b", "exp": "<h1> is the top-level heading tag in HTML."},
            {"q": "Which CSS property controls text colour?",
             "a": "font-color", "b": "text-color", "c": "color", "d": "foreground",
             "correct": "c", "exp": "The CSS 'color' property sets the text colour."},
            {"q": "What does CSS Flexbox's 'justify-content: center' do?",
             "a": "Centres items vertically", "b": "Centres items horizontally along the main axis",
             "c": "Adds padding", "d": "Aligns text",
             "correct": "b", "exp": "justify-content centres flex items along the main (horizontal) axis."},
            {"q": "Which JavaScript method adds an event listener?",
             "a": "element.on()", "b": "element.listen()", "c": "element.addEventListener()", "d": "element.bind()",
             "correct": "c", "exp": "addEventListener() attaches an event handler to an element."},
            {"q": "What does 'responsive design' mean?",
             "a": "Fast loading website", "b": "Website that adapts to different screen sizes",
             "c": "Website with animations", "d": "Website with a database",
             "correct": "b", "exp": "Responsive design uses CSS media queries to adapt layout to screen size."},
        ],
    },
    "Sustainable Agriculture & AgriTech": {
        "title": "Sustainable Agriculture Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"q": "What is the ideal soil pH range for most crops?",
             "a": "4.0–5.0", "b": "6.0–7.0", "c": "8.0–9.0", "d": "3.0–4.0",
             "correct": "b", "exp": "Most crops grow best in slightly acidic to neutral soil (pH 6.0–7.0)."},
            {"q": "How much water does drip irrigation save compared to flood irrigation?",
             "a": "10–20%", "b": "20–30%", "c": "40–60%", "d": "70–80%",
             "correct": "c", "exp": "Drip irrigation delivers water directly to roots, saving 40–60% water."},
            {"q": "What does MSP stand for in agriculture?",
             "a": "Market Support Price", "b": "Minimum Support Price", "c": "Maximum Selling Price", "d": "Marginal Subsidy Programme",
             "correct": "b", "exp": "MSP = Minimum Support Price — the government-guaranteed price for 23 crops."},
            {"q": "Which government app provides free weather and market price info to farmers?",
             "a": "eNAM", "b": "Fasal", "c": "Kisan Suvidha", "d": "mKisan",
             "correct": "c", "exp": "Kisan Suvidha is a free government app with weather, prices, and expert advice."},
            {"q": "What is vermicompost?",
             "a": "Chemical fertiliser", "b": "Compost made using earthworms", "c": "Drip irrigation system", "d": "Pesticide spray",
             "correct": "b", "exp": "Vermicompost is organic fertiliser produced by earthworms breaking down organic matter."},
        ],
    },
}


def seed_quizzes():
    """Seed quiz questions for each course if not already present."""
    for course_title, data in QUIZ_SEED.items():
        course = Course.query.filter_by(title=course_title).first()
        if not course:
            continue
        if Quiz.query.filter_by(course_id=course.id).first():
            continue
        quiz = Quiz(course_id=course.id, title=data["title"],
                    time_limit=data["time_limit"], pass_pct=data["pass_pct"])
        db.session.add(quiz)
        db.session.flush()
        for q in data["questions"]:
            db.session.add(QuizQuestion(
                quiz_id=quiz.id, question=q["q"],
                option_a=q["a"], option_b=q["b"],
                option_c=q["c"], option_d=q["d"],
                correct=q["correct"], explanation=q["exp"],
            ))
    db.session.commit()


# ── Admin Routes ──────────────────────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.email not in ADMIN_EMAILS:
            abort(403)
        return f(*args, **kwargs)
    return decorated

ADMIN_EMAILS = {"admin@skillbridge.com"}   # add real admin emails here


@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    stats = {
        "users":    User.query.count(),
        "courses":  Course.query.count(),
        "enrollments": Enrollment.query.count(),
        "quizzes":  Quiz.query.count(),
        "mentors":  MentorProfile.query.filter_by(approved=True).count(),
        "pending_mentors": MentorProfile.query.filter_by(approved=False).count(),
        "doubts":   DoubtRequest.query.count(),
        "notes":    CourseNote.query.count(),
        "certificates": Certificate.query.count(),
    }
    recent_users = User.query.order_by(User.joined_at.desc()).limit(10).all()
    top_courses  = (db.session.query(Course, db.func.count(Enrollment.id).label("cnt"))
                    .join(Enrollment).group_by(Course.id)
                    .order_by(db.text("cnt desc")).limit(5).all())
    pending_mentors = MentorProfile.query.filter_by(approved=False).all()
    recent_doubts   = DoubtRequest.query.order_by(DoubtRequest.created_at.desc()).limit(10).all()
    all_quizzes     = Quiz.query.all()
    all_notes       = CourseNote.query.order_by(CourseNote.uploaded_at.desc()).all()
    return render_template("admin.html", stats=stats, recent_users=recent_users,
                           top_courses=top_courses, pending_mentors=pending_mentors,
                           recent_doubts=recent_doubts, all_courses=Course.query.all(),
                           all_users=User.query.order_by(User.joined_at.desc()).all(),
                           all_quizzes=all_quizzes, all_notes=all_notes)


@app.route("/admin/mentor/<int:mentor_id>/approve", methods=["POST"])
@login_required
@admin_required
def admin_approve_mentor(mentor_id):
    m = MentorProfile.query.get_or_404(mentor_id)
    m.approved = True
    db.session.commit()
    flash(f"Mentor approved.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/mentor/<int:mentor_id>/reject", methods=["POST"])
@login_required
@admin_required
def admin_reject_mentor(mentor_id):
    m = MentorProfile.query.get_or_404(mentor_id)
    db.session.delete(m)
    db.session.commit()
    flash("Mentor application rejected.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash("User deleted.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/course/add", methods=["POST"])
@login_required
@admin_required
def admin_add_course():
    c = Course(
        title=request.form["title"], description=request.form["description"],
        category=request.form["category"], level=request.form.get("level","Beginner"),
        instructor=request.form.get("instructor","SkillBridge Faculty"),
        youtube_id=request.form.get("youtube_id",""), modules="[]",
    )
    db.session.add(c); db.session.commit()
    flash("Course added.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/course/<int:course_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_course(course_id):
    c = Course.query.get_or_404(course_id)
    db.session.delete(c); db.session.commit()
    flash("Course deleted.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/doubt/<int:doubt_id>/reply", methods=["POST"])
@login_required
@admin_required
def admin_reply_doubt(doubt_id):
    d = DoubtRequest.query.get_or_404(doubt_id)
    d.reply  = request.form.get("reply","").strip()
    d.status = "answered"
    db.session.commit()
    flash("Reply sent.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/quiz/<int:quiz_id>/question/add", methods=["POST"])
@login_required
@admin_required
def admin_add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    q = QuizQuestion(
        quiz_id=quiz.id,
        question=request.form["question"],
        option_a=request.form["option_a"],
        option_b=request.form["option_b"],
        option_c=request.form["option_c"],
        option_d=request.form["option_d"],
        correct=request.form["correct"],
        explanation=request.form.get("explanation",""),
    )
    db.session.add(q); db.session.commit()
    flash("Question added.", "success")
    return redirect(url_for("admin_dashboard") + "#quizzes")


@app.route("/admin/question/<int:q_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_question(q_id):
    q = QuizQuestion.query.get_or_404(q_id)
    db.session.delete(q); db.session.commit()
    flash("Question deleted.", "info")
    return redirect(url_for("admin_dashboard") + "#quizzes")


@app.route("/admin/notes/upload", methods=["POST"])
@login_required
@admin_required
def admin_upload_notes():
    course_id = request.form.get("course_id", type=int)
    title     = request.form.get("title","").strip()
    language  = request.form.get("language","en")
    file      = request.files.get("file")
    if not file or not title or not course_id:
        flash("All fields required.", "error")
        return redirect(url_for("admin_dashboard") + "#notes")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx", ".txt", ".pptx"):
        flash("Only PDF, DOCX, TXT, PPTX allowed.", "error")
        return redirect(url_for("admin_dashboard") + "#notes")
    fname = secure_filename(f"note_{course_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{ext}")
    path  = os.path.join(app.config["UPLOAD_FOLDER"], fname)
    file.save(path)
    note = CourseNote(course_id=course_id, title=title, filename=fname,
                      language=language, file_size=os.path.getsize(path))
    db.session.add(note); db.session.commit()
    flash("Notes uploaded.", "success")
    return redirect(url_for("admin_dashboard") + "#notes")


@app.route("/admin/notes/<int:note_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_note(note_id):
    note = CourseNote.query.get_or_404(note_id)
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], note.filename))
    except OSError:
        pass
    db.session.delete(note); db.session.commit()
    flash("Note deleted.", "info")
    return redirect(url_for("admin_dashboard") + "#notes")


# ── Learning Analytics Routes ─────────────────────────────────────────────────

@app.route("/api/analytics/track", methods=["POST"])
@login_required
def track_analytics():
    """Record a learning event (watch time, quiz result, module completion)."""
    data       = request.get_json(silent=True) or {}
    event_type = data.get("event_type")
    course_id  = data.get("course_id")
    if not event_type:
        return jsonify({"error": "event_type required"}), 400
    course = db.session.get(Course, course_id) if course_id else None
    ev = LearningAnalytics(
        user_id    = current_user.id,
        course_id  = course_id,
        event_type = event_type,
        watch_secs = int(data.get("watch_secs", 0)),
        score      = int(data.get("score", 0)),
        category   = course.category if course else data.get("category",""),
    )
    db.session.add(ev); db.session.commit()
    return jsonify({"ok": True})


@app.route("/analytics")
@login_required
def analytics():
    uid = current_user.id
    # Total watch time (minutes)
    watch_rows = LearningAnalytics.query.filter_by(user_id=uid, event_type="watch").all()
    total_watch_min = round(sum(r.watch_secs for r in watch_rows) / 60)

    # Quiz performance per course
    attempts = QuizAttempt.query.filter_by(user_id=uid).order_by(QuizAttempt.attempted_at).all()
    quiz_data = []
    for a in attempts:
        quiz_data.append({
            "course": a.course.title if a.course else "Unknown",
            "score": a.score,
            "passed": a.passed,
            "date": a.attempted_at.strftime("%d %b"),
        })

    # Weak skill areas: categories where avg quiz score < 60
    from sqlalchemy import func
    cat_scores = (db.session.query(LearningAnalytics.category,
                                   func.avg(LearningAnalytics.score).label("avg_score"))
                  .filter(LearningAnalytics.user_id == uid,
                          LearningAnalytics.event_type.in_(["quiz_pass","quiz_fail"]))
                  .group_by(LearningAnalytics.category).all())
    weak_skills = [c for c, avg in cat_scores if avg is not None and avg < 60]

    # Consistency: days active in last 30 days
    from datetime import timedelta
    thirty_ago = datetime.utcnow() - timedelta(days=30)
    active_days = (db.session.query(func.date(LearningAnalytics.recorded_at))
                   .filter(LearningAnalytics.user_id == uid,
                           LearningAnalytics.recorded_at >= thirty_ago)
                   .distinct().count())

    # Course completion
    enrollments = Enrollment.query.filter_by(user_id=uid).all()
    completed_courses = [e for e in enrollments if e.progress >= 100]

    # Recommendations based on weak skills + interest
    interest = current_user.interest or "Technology"
    recs = SKILL_RECOMMENDATIONS.get(interest, [])
    if weak_skills:
        for ws in weak_skills:
            recs = SKILL_RECOMMENDATIONS.get(ws, recs)
            break

    # Watch time per day (last 7 days) for chart
    watch_by_day = {}
    for r in watch_rows:
        day = r.recorded_at.strftime("%a")
        watch_by_day[day] = watch_by_day.get(day, 0) + round(r.watch_secs / 60)
    days_order = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    watch_chart = [{"day": d, "mins": watch_by_day.get(d, 0)} for d in days_order]

    return render_template("analytics.html",
        total_watch_min=total_watch_min,
        quiz_data=quiz_data,
        weak_skills=weak_skills,
        active_days=active_days,
        completed_courses=len(completed_courses),
        total_enrolled=len(enrollments),
        recommendations=recs[:3],
        watch_chart=watch_chart,
        enrollments=enrollments,
    )


# ── Init ───────────────────────────────────────────────────────────────────────

def create_app():
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    with app.app_context():
        db.create_all()
        # Add language column to existing users table if it doesn't exist yet
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(10) DEFAULT 'en'"))
                conn.commit()
        except Exception:
            pass  # Column already exists or table is new — no action needed
        # Add new quiz_attempts columns if upgrading from older schema
        for col_sql in [
            "ALTER TABLE quiz_attempts ADD COLUMN quiz_id INTEGER REFERENCES quizzes(id)",
            "ALTER TABLE quiz_attempts ADD COLUMN passed BOOLEAN DEFAULT 0",
        ]:
            try:
                from sqlalchemy import text
                with db.engine.connect() as conn:
                    conn.execute(text(col_sql))
                    conn.commit()
            except Exception:
                pass
        seed_db()
        seed_quizzes()
        seed_badges()
    return app


if __name__ == "__main__":
    create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
