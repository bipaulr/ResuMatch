import socketio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
from services.chat_service import ChatService
from models.message import MessageCreate
from auth.jwt_handler import decode_token as decode_access_token

# --- Main Setup ---
# Initialize FastAPI for standard HTTP routes
app = FastAPI()

# Initialize Socket.IO Server with authentication
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

# Create the ASGI application (without other_asgi_app to avoid circular import)
socket_app = socketio.ASGIApp(sio)

# Initialize chat service
chat_service = ChatService()


# --- Add FastAPI Middleware & Routes to the 'app' object ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint for the FastAPI server."""
    return {"message": "Welcome to the Chat Server! Connect via Socket.IO."}

@app.get("/rooms")
async def get_user_rooms(user_id: str):
    """Get all chat rooms for a user."""
    try:
        rooms = await chat_service.get_user_rooms(user_id)
        return {"rooms": rooms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rooms/{room_id}/messages")
async def get_room_messages(
    room_id: str,
    limit: int = Query(50, ge=1, le=100),
    before: Optional[str] = None
):
    """Get messages from a chat room with pagination."""
    try:
        before_dt = datetime.fromisoformat(before) if before else None
        messages = await chat_service.get_messages(room_id, limit, before_dt)
        return {
            "room_id": room_id,
            "messages": [msg.dict() for msg in messages]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    
    # Check for token in environ (from Socket.IO client auth)
    if not token and 'HTTP_AUTHORIZATION' in environ:
        token = environ['HTTP_AUTHORIZATION']
    
    if not token:
        print("❌ Connection rejected: No token provided")
        raise ConnectionRefusedError('Authentication required')
    
    try:
        payload = decode_access_token(token)
        if not payload:
            print("❌ Connection rejected: Invalid token")
            raise ConnectionRefusedError('Invalid token')
            
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
        raise ConnectionRefusedError(str(e))

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
        
        # Send chat history to the user - use model's json() method for proper serialization
        messages_dict = []
        for msg in messages:
            messages_dict.append(msg.dict())
        
        await sio.emit("chat_history", {
            "room_id": room_id,
            "messages": messages_dict
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
    await sio.emit("left_room", {"room_id": room_id}, room=sid)
app.mount("/ws", socket_app)