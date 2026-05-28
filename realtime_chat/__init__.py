"""
Real-time WebSocket chat service for SkillBridge.
"""
from datetime import datetime
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")

# sid → user_id mapping
_active: dict = {}


@socketio.on("connect")
def on_connect():
    if not current_user.is_authenticated:
        return False
    uid = current_user.id
    _active[request.sid] = uid
    join_room(f"user_{uid}")
    emit("connection_status", {"status": "connected", "user_id": uid})
    emit("user_status", {"user_id": uid, "name": current_user.name, "status": "online"},
         broadcast=True, include_self=False)

    # Send recent chat history for general room
    try:
        from skillbridge.models import ChatMessage
        from skillbridge.extensions import db
        recent = ChatMessage.query.filter_by(room_type="general", room_id="lobby")\
            .order_by(ChatMessage.sent_at.desc()).limit(50).all()
        history = [{"id": m.id, "user_id": m.user_id, "user_name": m.user.name,
                    "message": m.message, "timestamp": m.sent_at.isoformat(),
                    "room_type": "general", "room_id": "lobby"} for m in reversed(recent)]
        if history:
            emit("chat_history", {"messages": history})
    except Exception as e:
        print(f"[Chat] History load error: {e}")


@socketio.on("disconnect")
def on_disconnect():
    uid = _active.pop(request.sid, None)
    if uid:
        leave_room(f"user_{uid}")
        emit("user_status", {"user_id": uid, "status": "offline"},
             broadcast=True, include_self=False)


@socketio.on("join_room")
def on_join(data):
    if not current_user.is_authenticated:
        return
    room = data.get("room")
    if room:
        join_room(room)
        emit("room_joined", {"room": room})


@socketio.on("leave_room")
def on_leave(data):
    if not current_user.is_authenticated:
        return
    room = data.get("room")
    if room:
        leave_room(room)


@socketio.on("send_message")
def on_message(data):
    if not current_user.is_authenticated:
        return
    message   = (data.get("message") or "").strip()
    room_type = data.get("room_type", "general")
    room_id   = str(data.get("room_id", "lobby"))
    if not message:
        return

    room = f"{room_type}_{room_id}"
    payload = {
        "id":        f"{int(datetime.utcnow().timestamp())}_{current_user.id}",
        "user_id":   current_user.id,
        "user_name": current_user.name,
        "message":   message,
        "timestamp": datetime.utcnow().isoformat(),
        "room_type": room_type,
        "room_id":   room_id,
    }

    # Persist to DB
    try:
        from skillbridge.models import ChatMessage
        from skillbridge.extensions import db
        db.session.add(ChatMessage(
            user_id=current_user.id,
            room_type=room_type,
            room_id=room_id,
            message=message,
        ))
        db.session.commit()
    except Exception as e:
        print(f"[Chat] DB persist error: {e}")

    emit("new_message", payload, room=room, include_self=True)
    emit("message_sent", {"message_id": payload["id"], "timestamp": payload["timestamp"]})


@socketio.on("typing_start")
def on_typing_start(data):
    if not current_user.is_authenticated:
        return
    room = f"{data.get('room_type','general')}_{data.get('room_id','lobby')}"
    emit("user_typing", {"user_id": current_user.id, "user_name": current_user.name},
         room=room, include_self=False)


@socketio.on("typing_stop")
def on_typing_stop(data):
    if not current_user.is_authenticated:
        return
    room = f"{data.get('room_type','general')}_{data.get('room_id','lobby')}"
    emit("user_stopped_typing", {"user_id": current_user.id},
         room=room, include_self=False)


@socketio.on("request_mentor_help")
def on_mentor_help(data):
    if not current_user.is_authenticated:
        return
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()
    if not subject or not message:
        emit("error", {"message": "Subject and message required"})
        return

    try:
        from skillbridge.models import DoubtRequest, MentorProfile
        from skillbridge.extensions import db
        mentor = MentorProfile.query.filter_by(approved=True).first()
        if not mentor:
            emit("error", {"message": "No mentors available right now"})
            return
        doubt = DoubtRequest(
            user_id=current_user.id,
            mentor_id=mentor.id,
            subject=subject,
            message=message,
        )
        db.session.add(doubt)
        db.session.commit()
        emit("mentor_request_sent", {"doubt_id": doubt.id,
                                     "message": "Request sent to available mentors"})
        emit("new_doubt_request", {
            "doubt_id": doubt.id, "user_id": current_user.id,
            "user_name": current_user.name, "subject": subject,
            "timestamp": doubt.created_at.isoformat(),
        }, room="mentors_available", include_self=False)
    except Exception as e:
        emit("error", {"message": str(e)})
