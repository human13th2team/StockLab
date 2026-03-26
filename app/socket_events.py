from flask import request
from flask_socketio import join_room, leave_room
from flask_jwt_extended import decode_token
from .extensions import socketio

@socketio.on('connect')
def handle_connect():
    print(f"🔌 [SocketIO] Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"🔌 [SocketIO] Client disconnected: {request.sid}")

@socketio.on('join')
def on_join(data):
    """
    사용자가 접속 시 JWT 토큰을 보내면 해당 유저의 전용 Room에 입장시킵니다.
    data: { "token": "JWT_ACCESS_TOKEN" }
    """
    token = data.get('token')
    if not token:
        print("⚠️ [SocketIO] Join failed: No token provided")
        return
    
    try:
        # 토큰 디코딩하여 user_id 추출
        decoded = decode_token(token)
        user_id = decoded.get('sub')
        
        if user_id:
            room = f"user_{user_id}"
            join_room(room)
            print(f"✅ [SocketIO] User {user_id} joined room {room} (sid: {request.sid})")
            socketio.emit('join_response', {'status': 'success', 'room': room}, room=request.sid)
        else:
            print("⚠️ [SocketIO] Join failed: Invalid user_id in token")
    except Exception as e:
        print(f"❌ [SocketIO] Join error: {str(e)}")

@socketio.on('leave')
def on_leave(data):
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        leave_room(room)
        print(f"🏃 [SocketIO] User {user_id} left room {room}")
