"""gamification.py — XP, badges, streaks."""
from datetime import datetime
from .extensions import db
from .models import UserProfile, Badge, UserBadge

BADGE_DEFS = [
    {"slug": "first_step",    "name": "First Step",      "icon": "👣", "desc": "Complete your first path step",    "xp": 50},
    {"slug": "quiz_master",   "name": "Quiz Passer",      "icon": "🧠", "desc": "Pass your first quiz",             "xp": 100},
    {"slug": "streak_3",      "name": "3-Day Streak",     "icon": "🔥", "desc": "Learn 3 days in a row",            "xp": 75},
    {"slug": "streak_7",      "name": "Week Warrior",     "icon": "⚡", "desc": "Learn 7 days in a row",            "xp": 200},
    {"slug": "path_complete", "name": "Path Master",      "icon": "🗺️", "desc": "Complete an entire skill path",   "xp": 500},
    {"slug": "course_done",   "name": "Course Graduate",  "icon": "🎓", "desc": "Reach 100% on any course",         "xp": 150},
    {"slug": "first_enroll",  "name": "Enrolled",         "icon": "📚", "desc": "Enroll in your first course",      "xp": 20},
    {"slug": "top10",         "name": "Top 10",           "icon": "🏆", "desc": "Reach top 10 on the leaderboard",  "xp": 300},
]


def get_or_create_profile(user_id):
    p = UserProfile.query.filter_by(user_id=user_id).first()
    if not p:
        p = UserProfile(user_id=user_id)
        db.session.add(p)
        db.session.flush()
    return p


def award_xp(user_id, points, badge_slug=None):
    profile = get_or_create_profile(user_id)
    profile.xp += points
    today = datetime.utcnow().date()
    last  = profile.last_active.date() if profile.last_active else None
    if last and (today - last).days == 1:
        profile.streak += 1
    elif last != today:
        profile.streak = 1
    profile.last_active = datetime.utcnow()
    new_badges = []
    if badge_slug:
        badge = Badge.query.filter_by(slug=badge_slug).first()
        if badge and not UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
            db.session.add(UserBadge(user_id=user_id, badge_id=badge.id))
            profile.xp += badge.xp_reward
            new_badges.append(badge.name)
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
