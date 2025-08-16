
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import router as auth_router
from routes.student_routes import router as student_router
from routes.recruiter_routes import router as recruiter_router
from routes.job_routes import router as job_router
from routes.chat_routes import router as chat_router
import socketio
from auth.jwt_handler import decode_token as decode_access_token
from services.chat_service import ChatService
from models.message import MessageCreate
import os
from datetime import datetime
from typing import Optional

# Create the base FastAPI app (mounted under Socket.IO ASGI wrapper)
api = FastAPI()

# Get allowed origins from environment variable for production CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

api.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Render
@api.get("/healthz")
async def healthz():
    return {"status": "healthy", "message": "ResuMatch API is running"}

# Include all routers
api.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api.include_router(student_router, prefix="/student", tags=["Student"])
api.include_router(recruiter_router, prefix="/recruiter", tags=["Recruiter"])
api.include_router(job_router, prefix="/jobs", tags=["Jobs"])
api.include_router(chat_router, prefix="/chat", tags=["Chat"])

# Initialize Socket.IO Server with authentication
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=ALLOWED_ORIGINS,
    logger=True,
    engineio_logger=True
)

# Build the main ASGI application.
# We want the Socket.IO endpoint to be available at /ws/socket.io, so we mount
# the Socket.IO ASGI app under the /ws prefix (leaving the socketio_path as default "socket.io").
app = api
sio_app = socketio.ASGIApp(sio, socketio_path="socket.io")
app.mount("/ws", sio_app)

# Initialize chat service
chat_service = ChatService()

# Dictionary to store active user sessions
active_users = {}

@sio.event
async def connect(sid, environ):
    """Handle new client connections with JWT auth."""
    # Try multiple ways to get the token
    token = None
    
    # Check for token in query parameters
    query_string = environ.get('QUERY_STRING', '')
    if 'token=' in query_string:
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
    
    # Check for token in auth header
    if not token:
        auth_header = environ.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    if not token:
        print("❌ Connection rejected: No token provided")
        raise socketio.exceptions.ConnectionRefusedError('Authentication required')
    
    try:
        payload = decode_access_token(token)
        if not payload:
            print("❌ Connection rejected: Invalid token")
            raise socketio.exceptions.ConnectionRefusedError('Invalid token')
            
        active_users[sid] = {
            "user_id": payload["sub"],
            "role": payload.get("role", "student"),
            "username": payload.get("username", payload["sub"]),
            "email": payload.get("email", ""),
            "rooms": set()
        }
        print(f"✅ User {payload['sub']} ({payload.get('role', 'student')}) connected with SID: {sid}")
    except Exception as e:
        print(f"❌ Connection rejected: {str(e)}")
        raise socketio.exceptions.ConnectionRefusedError(str(e))

@sio.event
async def disconnect(sid):
    """Handle client disconnections."""
    if sid in active_users:
        user = active_users[sid]
        # Leave all rooms
        for room_id in user["rooms"]:
            await sio.leave_room(sid, room_id)
        del active_users[sid]
        print(f"❌ User {user.get('user_id', 'unknown')} disconnected")

@sio.event
async def join_room(sid, data):
    """Join a chat room with proper authorization."""
    if sid not in active_users:
        return await sio.emit("error", {"msg": "Not authenticated"}, room=sid)
        
    user = active_users[sid]
    room_id = data.get("room_id")
    job_id = data.get("job_id")
    
    if not room_id and not job_id:
        return await sio.emit("error", {"msg": "Room ID or Job ID required"}, room=sid)
    
    try:
        if not room_id:
            # Create/get room for job application chat
            if user["role"] == "student":
                student_id = user["user_id"]
                recruiter_id = data["recruiter_id"]
            else:
                student_id = data["student_id"]
                recruiter_id = user["user_id"]
                
            room_id = await chat_service.create_or_get_room(job_id, student_id, recruiter_id)
        
        # Join the room
        await sio.enter_room(sid, room_id)
        user["rooms"].add(room_id)
        
        # Mark messages as read
        await chat_service.mark_messages_as_read(room_id, user["user_id"])
        
        # Get recent messages
        messages = await chat_service.get_messages(room_id, limit=50)
        
        # Send chat history to the user
        await sio.emit("chat_history", {
            "room_id": room_id,
            "messages": [msg.dict() for msg in messages]
        }, room=sid)
        
        print(f"➡️ User {user['user_id']} joined room: {room_id}")
        
    except Exception as e:
        await sio.emit("error", {"msg": f"Failed to join room: {str(e)}"}, room=sid)

@sio.event
async def send_message(sid, data):
    """Send and persist a new message."""
    if sid not in active_users:
        return await sio.emit("error", {"msg": "Not authenticated"}, room=sid)
        
    user = active_users[sid]
    room_id = data.get("room_id")
    content = data.get("content")
    receiver_id = data.get("receiver_id")
    
    if not room_id or not content:
        return await sio.emit("error", {"msg": "Room ID and content required"}, room=sid)
        
    if room_id not in user["rooms"]:
        return await sio.emit("error", {"msg": "Not in this room"}, room=sid)
    
    try:
        # Create and save message
        message = MessageCreate(
            content=content,
            room_id=room_id,
            sender_id=user["user_id"],
            receiver_id=receiver_id,
            message_type="text"
        )
        
        message_id = await chat_service.save_message(message)
        
        # Broadcast to room
        await sio.emit("new_message", {
            "id": message_id,
            **message.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }, room=room_id)
        
    except Exception as e:
        await sio.emit("error", {"msg": f"Failed to send message: {str(e)}"}, room=sid)

@sio.event
async def start_typing(sid, data):
    """Handle typing indicator start."""
    if sid not in active_users:
        return await sio.emit("error", {"msg": "Not authenticated"}, room=sid)
        
    user = active_users[sid]
    room_id = data.get("room_id")
    
    if not room_id or room_id not in user["rooms"]:
        return await sio.emit("error", {"msg": "Invalid room"}, room=sid)
    
    # Broadcast typing indicator to room (except sender)
    await sio.emit("user_typing", {
        "userId": user["user_id"],
        "roomId": room_id
    }, room=room_id, skip_sid=sid)

@sio.event
async def stop_typing(sid, data):
    """Handle typing indicator stop."""
    if sid not in active_users:
        return await sio.emit("error", {"msg": "Not authenticated"}, room=sid)
        
    user = active_users[sid]
    room_id = data.get("room_id")
    
    if not room_id or room_id not in user["rooms"]:
        return await sio.emit("error", {"msg": "Invalid room"}, room=sid)
    
    # Broadcast stop typing to room (except sender)
    await sio.emit("user_stopped_typing", {
        "userId": user["user_id"],
        "roomId": room_id
    }, room=room_id, skip_sid=sid)

@sio.event
async def mark_as_read(sid, data):
    """Mark messages as read."""
    if sid not in active_users:
        return await sio.emit("error", {"msg": "Not authenticated"}, room=sid)
        
    user = active_users[sid]
    room_id = data.get("room_id")
    
    if not room_id:
        return await sio.emit("error", {"msg": "Room ID required"}, room=sid)
    
    try:
        await chat_service.mark_messages_as_read(room_id, user["user_id"])
        print(f"📖 User {user['user_id']} marked messages as read in room: {room_id}")
    except Exception as e:
        await sio.emit("error", {"msg": f"Failed to mark as read: {str(e)}"}, room=sid)

@sio.event
async def room_joined(sid, data):
    """Confirm room join."""
    if sid not in active_users:
        return
    
    await sio.emit("room_joined", {"roomId": data.get("room_id")}, room=sid)

@sio.event
async def room_left(sid, data):
    """Confirm room leave."""
    if sid not in active_users:
        return
    
    await sio.emit("room_left", {"roomId": data.get("room_id")}, room=sid)

@sio.event
async def leave_room(sid, data):
    """Leave a chat room."""
    if sid not in active_users:
        return await sio.emit("error", {"msg": "Not authenticated"}, room=sid)
        
    user = active_users[sid]
    room_id = data.get("room_id")
    
    if not room_id or room_id not in user["rooms"]:
        return await sio.emit("error", {"msg": "Invalid room"}, room=sid)
    
    await sio.leave_room(sid, room_id)
    user["rooms"].remove(room_id)
    print(f"🚪 User {user['user_id']} left room: {room_id}")
    await sio.emit("room_left", {"roomId": room_id}, room=sid)

if __name__ == "__main__":
    import uvicorn
    # Run the Socket.IO ASGI wrapper by default
    uvicorn.run("resume_api.main:app", host="127.0.0.1", port=8000, reload=True)


