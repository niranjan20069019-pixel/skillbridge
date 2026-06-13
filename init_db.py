"""init_db.py — Bootstrap DB and seed data."""
import eventlet
eventlet.monkey_patch()

from app import create_app, init_database

app = create_app()
init_database(app)
print("Done")
