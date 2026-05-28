"""init_db.py — Bootstrap DB and run Flask-Migrate for the first time."""
import eventlet
eventlet.monkey_patch()

from app import create_app
from skillbridge.extensions import db

app = create_app()

with app.app_context():
    # flask db init  (run once to create migrations/ folder)
    # flask db migrate -m "initial"
    # flask db upgrade
    db.create_all()
    print("✅ Database tables created.")
