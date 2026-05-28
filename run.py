"""run.py — Development entry point with eventlet for SocketIO."""
import eventlet
eventlet.monkey_patch()

import os
from app import create_app
from realtime_chat import socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)
