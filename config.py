"""config.py — Environment-based configuration classes."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600          # 1 hour
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "notes")
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".pptx"}
    ALLOWED_MIMETYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    # Magic bytes for file type validation (first 8 bytes)
    MAGIC_BYTES = {
        b"%PDF":     ".pdf",
        b"PK\x03\x04": ".docx",   # also .pptx (both are ZIP-based)
    }
    LOG_LEVEL = "INFO"
    LOG_FILE  = os.path.join(BASE_DIR, "logs", "skillbridge.log")
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "skillbridge.db"),
    )
    WTF_CSRF_ENABLED = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")  # must be set
    SESSION_COOKIE_SECURE   = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PREFERRED_URL_SCHEME    = "https"
    LOG_LEVEL = "WARNING"

    @classmethod
    def validate(cls):
        if not os.environ.get("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY environment variable must be set in production.")
        if not os.environ.get("DATABASE_URL"):
            raise RuntimeError("DATABASE_URL environment variable must be set in production.")


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "ERROR"


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config_map.get(env, DevelopmentConfig)
