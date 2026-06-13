import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from skillbridge.extensions import db, login_manager, csrf
from skillbridge.blueprints.admin import bp as admin_bp
from skillbridge.blueprints.auth import bp as auth_bp
from skillbridge.blueprints.api import bp as api_bp
from skillbridge.blueprints.main import bp as main_bp
from realtime_chat import socketio
from config import get_config


def create_app(config_class=None):
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), "static"),
    )

    # Instantiate config to resolve @property descriptors
    cfg = config_class or get_config()
    if isinstance(cfg, type):
        cfg = cfg()
    app.config.from_object(cfg)

    # Ensure DATABASE_URI is set (from property or fallback)
    uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not uri:
        uri = os.environ.get("DATABASE_URL")
        if uri:
            app.config["SQLALCHEMY_DATABASE_URI"] = uri

    # Fix postgres:// -> postgresql:// (Heroku/Render compat)
    if uri and uri.startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = uri.replace("postgres://", "postgresql://", 1)

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    csrf.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(main_bp)

    # Exempt API blueprint from CSRF (uses JSON, not form data)
    csrf.exempt(api_bp)

    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads/notes"), exist_ok=True)

    # Register Jinja globals for templates
    from skillbridge.data import I18N
    from flask_login import current_user
    
    def _translate(key):
        translations = I18N.get(key, {})
        if not translations:
            return key
        lang = getattr(current_user, 'language', 'en') or 'en'
        return translations.get(lang, translations.get('en', key))
    
    app.jinja_env.globals['t'] = _translate
    app.jinja_env.globals['enumerate'] = enumerate

    # Health-check endpoint — verifies MySQL connectivity
    @app.route("/health")
    def health():
        status = {"status": "ok", "database": "unknown"}
        try:
            db.engine.connect()
            status["database"] = "connected"
        except Exception as e:
            status["status"] = "error"
            status["database"] = str(e)
        return jsonify(status)

    return app


def init_database(app):
    """Create tables and seed data. Call this explicitly after create_app()."""
    with app.app_context():
        db.create_all()
        from skillbridge.models import seed_db, seed_quizzes, seed_badges
        seed_db()
        seed_quizzes()
        seed_badges()


if __name__ == "__main__":
    import eventlet
    eventlet.monkey_patch()
    app = create_app()
    init_database(app)
    from realtime_chat import socketio
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)
