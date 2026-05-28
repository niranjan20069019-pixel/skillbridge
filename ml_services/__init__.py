"""
ML Services for SkillBridge — real OpenAI + TF-IDF recommendations.
"""
import os as _os
import pickle
from typing import List, Dict

_BASE = _os.path.dirname(_os.path.abspath(__file__))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ── Recommendation Engine ─────────────────────────────────────────────────────

class RecommendationEngine:
    _MODEL_PATH  = _os.path.join(_BASE, "recommendation_model.pkl")
    _COURSES_PATH = _os.path.join(_BASE, "courses_data.pkl")

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.course_vectors = None
        self.courses: list = []
        self._load_or_train()

    def _load_or_train(self):
        if _os.path.exists(self._MODEL_PATH) and _os.path.exists(self._COURSES_PATH):
            try:
                with open(self._MODEL_PATH, "rb") as f:
                    self.vectorizer = pickle.load(f)
                with open(self._COURSES_PATH, "rb") as f:
                    self.course_vectors, self.courses = pickle.load(f)
                return
            except Exception:
                pass
        self._train()

    def _train(self):
        try:
            from skillbridge.models import Course
            courses = Course.query.all()
            if not courses:
                return
            self.courses = courses
            texts = [f"{c.title} {c.description} {c.category}" for c in courses]
            self.course_vectors = self.vectorizer.fit_transform(texts)
            _os.makedirs(_BASE, exist_ok=True)
            with open(self._MODEL_PATH, "wb") as f:
                pickle.dump(self.vectorizer, f)
            with open(self._COURSES_PATH, "wb") as f:
                pickle.dump((self.course_vectors, self.courses), f)
        except Exception as e:
            print(f"[ML] Training failed: {e}")

    def get_recommendations(self, user_id: int, limit: int = 5) -> List[Dict]:
        from skillbridge.models import User, Enrollment, QuizAttempt, LearningAnalytics
        user = User.query.get(user_id)
        if not user or self.course_vectors is None:
            return self._popular(limit)

        enrolled_ids = {e.course_id for e in Enrollment.query.filter_by(user_id=user_id).all()}
        topics = [user.interest or "Technology"]
        topics += [e.course.title for e in Enrollment.query.filter_by(user_id=user_id).all() if e.course]
        topics += [a.category for a in LearningAnalytics.query.filter_by(user_id=user_id).all() if a.category]

        user_text = " ".join(set(topics))
        try:
            vec = self.vectorizer.transform([user_text])
            sims = cosine_similarity(vec, self.course_vectors)[0]
            scored = sorted(
                [(i, sims[i]) for i in range(len(self.courses)) if self.courses[i].id not in enrolled_ids],
                key=lambda x: x[1], reverse=True
            )
            return [
                {
                    "id": self.courses[i].id,
                    "title": self.courses[i].title,
                    "description": self.courses[i].description,
                    "category": self.courses[i].category,
                    "level": self.courses[i].level,
                    "duration_hrs": self.courses[i].duration_hrs,
                    "similarity_score": round(float(s), 3),
                    "reason": f"Based on your interest in {user.interest or 'Technology'}",
                }
                for i, s in scored[:limit]
            ]
        except Exception as e:
            print(f"[ML] Recommendation error: {e}")
            return self._popular(limit)

    def _popular(self, limit: int) -> List[Dict]:
        from skillbridge.models import Course, Enrollment
        from skillbridge.extensions import db
        rows = (
            db.session.query(Course, db.func.count(Enrollment.id).label("cnt"))
            .outerjoin(Enrollment)
            .group_by(Course.id)
            .order_by(db.text("cnt DESC"))
            .limit(limit)
            .all()
        )
        return [
            {"id": c.id, "title": c.title, "description": c.description,
             "category": c.category, "level": c.level, "duration_hrs": c.duration_hrs,
             "similarity_score": 1.0, "reason": "Popular course"}
            for c, _ in rows
        ]


# ── Chatbot Service ───────────────────────────────────────────────────────────

class ChatbotService:
    def __init__(self):
        self.api_key = _os.environ.get("OPENAI_API_KEY", "")
        self._history: Dict[int, list] = {}

    def get_response(self, user_id: int, message: str) -> str:
        if self.api_key:
            return self._openai_response(user_id, message)
        return self._rule_based(user_id, message)

    def _openai_response(self, user_id: int, message: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            if user_id not in self._history:
                self._history[user_id] = [
                    {"role": "system", "content": (
                        "You are SkillBridge AI Assistant — a helpful, encouraging educational mentor. "
                        "Help users with course recommendations, study tips, career advice, and platform guidance. "
                        "Be concise (under 120 words per reply)."
                    )}
                ]

            self._history[user_id].append({"role": "user", "content": message})
            # Keep last 10 turns + system prompt
            if len(self._history[user_id]) > 11:
                self._history[user_id] = [self._history[user_id][0]] + self._history[user_id][-10:]

            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self._history[user_id],
                max_tokens=150,
                temperature=0.7,
            )
            reply = resp.choices[0].message.content.strip()
            self._history[user_id].append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            print(f"[ChatBot] OpenAI error: {e}")
            return self._rule_based(user_id, message)

    def _rule_based(self, user_id: int, message: str) -> str:
        from skillbridge.models import User, Enrollment, QuizAttempt, Certificate, UserBadge
        user = User.query.get(user_id)
        name = user.name.split()[0] if user else "there"
        interest = user.interest if user else "Technology"
        m = message.lower().strip()

        if any(w in m for w in ["hi", "hello", "hey"]):
            return f"Hey {name}! 👋 I'm your SkillBridge AI assistant. Ask me about courses, progress, or career tips!"

        if any(w in m for w in ["recommend", "suggest", "what should", "next course"]):
            engine = RecommendationEngine()
            recs = engine.get_recommendations(user_id, 3)
            if recs:
                lines = "\n".join(f"{i+1}. **{r['title']}** ({r['category']})" for i, r in enumerate(recs))
                return f"Based on your interest in {interest}, I recommend:\n\n{lines}"
            return f"Explore our {interest} courses — they're a great fit for you!"

        if any(w in m for w in ["progress", "status", "how am i"]):
            enrollments = Enrollment.query.filter_by(user_id=user_id).all()
            if not enrollments:
                return f"You haven't enrolled yet, {name}. Want course recommendations?"
            done = [e for e in enrollments if e.progress >= 100]
            wip  = [e for e in enrollments if 0 < e.progress < 100]
            msg  = f"📊 Progress for {name}:\n✅ Completed: {len(done)}\n📚 In Progress: {len(wip)}"
            if wip:
                best = max(wip, key=lambda e: e.progress)
                msg += f"\n🎯 Closest: **{best.course.title}** ({best.progress}%)"
            return msg

        if any(w in m for w in ["certificate", "cert", "badge"]):
            certs  = Certificate.query.filter_by(user_id=user_id).count()
            badges = UserBadge.query.filter_by(user_id=user_id).count()
            return f"🏆 You have {certs} certificate(s) and {badges} badge(s). Complete courses + pass quizzes to earn more!"

        if any(w in m for w in ["study", "tip", "focus", "advice"]):
            return (
                "📚 Top study tips:\n"
                "1. Pomodoro: 25 min focus, 5 min break\n"
                "2. Take active notes\n"
                "3. Build small projects immediately\n"
                "4. Review with spaced repetition\n"
                "5. Teach concepts to others"
            )

        if any(w in m for w in ["career", "job", "salary"]):
            return (
                f"💼 Career path for {interest}:\n"
                "1. Complete 2-3 core courses\n"
                "2. Build a portfolio project\n"
                "3. Update LinkedIn & GitHub\n"
                "4. Network in online communities\n"
                "5. Apply for internships or freelance work"
            )

        return (
            f"Hi {name}! I can help with:\n"
            "🎯 Course recommendations\n"
            "📊 Progress tracking\n"
            "💡 Study tips\n"
            "💼 Career guidance\n"
            "🏆 Certificates & badges\n\n"
            "What would you like to know?"
        )


# ── Singletons ────────────────────────────────────────────────────────────────
_rec_engine: RecommendationEngine | None = None
_chatbot: ChatbotService | None = None


def _get_engine() -> RecommendationEngine:
    global _rec_engine
    if _rec_engine is None:
        _rec_engine = RecommendationEngine()
    return _rec_engine


def _get_chatbot() -> ChatbotService:
    global _chatbot
    if _chatbot is None:
        _chatbot = ChatbotService()
    return _chatbot


def get_ai_recommendations(user_id: int, limit: int = 5) -> list:
    return _get_engine().get_recommendations(user_id, limit)


def get_ai_chat_response(user_id: int, message: str) -> str:
    return _get_chatbot().get_response(user_id, message)


def retrain_recommendation_model():
    global _rec_engine
    _rec_engine = RecommendationEngine()
