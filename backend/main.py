
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
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:3000,https://resumatch-front.vercel.app,https://*.vercel.app,https://resumatch-front-git-main.vercel.app,https://resumatch-front-production.up.railway.app")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",")]

# For development, allow all localhost origins
if os.getenv("ENVIRONMENT") != "production":
    ALLOWED_ORIGINS.extend([
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175", 
        "http://127.0.0.1:5176",
        "http://127.0.0.1:3000"
    ])

# Print allowed origins for debugging
print(f"🌐 CORS Allowed Origins: {ALLOWED_ORIGINS}")

# Add wildcard for maximum compatibility in development
if os.getenv("ENVIRONMENT") != "production":
    ALLOWED_ORIGINS.append("*")

# Enhanced CORS middleware with redirect handling
api.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Add explicit handling for preflight OPTIONS requests
    expose_headers=["*"],
    max_age=86400,  # Cache preflight for 24 hours
)

# Custom middleware to handle trailing slash redirects with CORS
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
import asyncio

@api.middleware("http")
async def cors_redirect_middleware(request: Request, call_next):
    """
    Handle redirects while preserving CORS headers for preflight requests.
    """
    # Handle OPTIONS requests for CORS preflight
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
    # Check if this is a trailing slash redirect case
    path = str(request.url.path)
    if path.endswith("/") and path != "/" and len(path) > 1:
        # Remove trailing slash and check if route exists
        new_path = path.rstrip("/")
        if new_path in ["/jobs", "/auth", "/student", "/recruiter", "/chat"]:
            # Redirect but preserve CORS headers
            response = RedirectResponse(url=str(request.url).replace(path, new_path), status_code=307)
            # Add CORS headers to redirect response
            origin = request.headers.get("origin")
            if origin and origin in ALLOWED_ORIGINS:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "*"
            return response
    
    response = await call_next(request)
    return response

# Health check endpoint for Render
@api.get("/healthz")
async def healthz():
    return {"status": "healthy", "message": "ResuMatch API is running"}

# Socket.IO health check endpoint
@api.get("/socket.io/health")
async def socket_health():
    return {
        "status": "healthy", 
        "message": "Socket.IO server is running",
        "active_users": len(active_users),
        "cors_origins": ALLOWED_ORIGINS
    }

# Additional health checks for all possible Socket.IO paths
@api.get("/ws/socket.io/health")
async def ws_socket_health():
    return {"status": "healthy", "message": "WS Socket.IO path is accessible"}

@api.get("/socketio/health")
async def socketio_health():
    return {"status": "healthy", "message": "SocketIO path is accessible"}

@api.get("/ws/socketio/health")
async def ws_socketio_health():
    return {"status": "healthy", "message": "WS SocketIO path is accessible"}

@api.get("/api/socket.io/health")
async def api_socket_health():
    return {"status": "healthy", "message": "API Socket.IO path is accessible"}

# Include all routers
api.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api.include_router(student_router, prefix="/student", tags=["Student"])
api.include_router(recruiter_router, prefix="/recruiter", tags=["Recruiter"])
api.include_router(job_router, prefix="/jobs", tags=["Jobs"])
api.include_router(chat_router, prefix="/chat", tags=["Chat"])

# Additional health check endpoints
@api.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "ResuMatch API is running",
        "cors_origins": len(ALLOWED_ORIGINS),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Jobs health check
@api.get("/jobs/health")  
async def jobs_health():
    return {"status": "healthy", "message": "Jobs API is accessible"}

# Initialize Socket.IO Server with authentication and proper CORS for production
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=ALLOWED_ORIGINS,
    logger=True,  # Enable logging for debugging deployment issues
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
    # Add these for better production compatibility
    always_connect=True,
    namespaces='*'
)

# Create multiple ASGI apps for different Socket.IO paths
# Primary app with standard Socket.IO path
app = socketio.ASGIApp(sio, other_asgi_app=api, socketio_path="socket.io")

# Create alternative Socket.IO servers for different paths
sio_ws = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=ALLOWED_ORIGINS,
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
    always_connect=True,
    namespaces='*'
)

# Copy all Socket.IO event handlers to the alternative server
def copy_handlers_to_server(source_sio, target_sio):
    """Copy all event handlers from source to target Socket.IO server"""
    # We'll define all handlers for both servers after this

# Initialize chat service
chat_service = ChatService()

# Create WebSocket route handlers for all possible paths
from fastapi import WebSocket
from fastapi.responses import JSONResponse

@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for /ws path"""
    await websocket.accept()
    await websocket.send_text("Socket.IO server available at /socket.io")
    await websocket.close()

@api.get("/ws")
async def ws_get():
    """GET endpoint for /ws path - redirect to Socket.IO"""
    return JSONResponse({"message": "Socket.IO server available", "path": "/socket.io"})

@api.get("/socketio")
async def socketio_redirect():
    """Redirect /socketio to /socket.io"""
    return JSONResponse({"message": "Socket.IO server available", "path": "/socket.io"})

@api.get("/ws/socketio")
async def ws_socketio_redirect():
    """Redirect /ws/socketio to /socket.io"""
    return JSONResponse({"message": "Socket.IO server available", "path": "/socket.io"})

# Mount additional Socket.IO apps for different paths using sub-applications
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create sub-app for /ws path
ws_app = FastAPI()
ws_app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO ASGI app for /ws path
ws_socketio_app = socketio.ASGIApp(sio_ws, other_asgi_app=ws_app, socketio_path="socket.io")

# Mount the /ws Socket.IO app
api.mount("/ws", ws_socketio_app)

# Add startup event for any async initialization
@api.on_event("startup")
async def startup_event():
    """Initialize any async resources on startup."""
    print("🚀 ResuMatch backend starting up...")
    print(f"🔌 Socket.IO server mounted at: /socket.io")
    print(f"🔌 Additional Socket.IO server mounted at: /ws/socket.io")
    print(f"🌐 CORS origins: {len(ALLOWED_ORIGINS)} configured")
    print("✅ Backend startup complete")

@api.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    print("🔄 ResuMatch backend shutting down...")
    # Disconnect all active Socket.IO sessions
    if active_users:
        print(f"📤 Disconnecting {len(active_users)} active users...")
        for sid in list(active_users.keys()):
            await sio.disconnect(sid)
    print("✅ Backend shutdown complete")

# Dictionary to store active user sessions
active_users = {}

# Function to register Socket.IO event handlers for any server
def register_socketio_handlers(socketio_server):
    """Register all Socket.IO event handlers for a given server"""
    
    @socketio_server.event
    async def connect(sid, environ):
        """Handle new client connections with JWT auth."""
        print(f"🔄 New connection attempt from SID: {sid}")
        print(f"🌐 Origin: {environ.get('HTTP_ORIGIN', 'Unknown')}")
        print(f"🔗 User-Agent: {environ.get('HTTP_USER_AGENT', 'Unknown')}")
        
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
            print(f"❌ Connection rejected: No token provided for SID: {sid}")
            raise socketio.exceptions.ConnectionRefusedError('Authentication required')
        
        try:
            payload = decode_access_token(token)
            if not payload:
                print(f"❌ Connection rejected: Invalid token for SID: {sid}")
                raise socketio.exceptions.ConnectionRefusedError('Invalid token')
                
            active_users[sid] = {
                "user_id": payload["sub"],
                "role": payload.get("role", "student"),
                "username": payload.get("username", payload["sub"]),
                "email": payload.get("email", ""),
                "rooms": set()
            }
            print(f"✅ User {payload['sub']} ({payload.get('role', 'student')}) connected with SID: {sid}")
            print(f"📊 Total active users: {len(active_users)}")
        except Exception as e:
            print(f"❌ Connection rejected: {str(e)} for SID: {sid}")
            raise socketio.exceptions.ConnectionRefusedError(str(e))

    @socketio_server.event
    async def disconnect(sid):
        """Handle client disconnections."""
        if sid in active_users:
            user = active_users[sid]
            # Leave all rooms
            for room_id in user["rooms"]:
                await socketio_server.leave_room(sid, room_id)
            del active_users[sid]
            print(f"❌ User {user.get('user_id', 'unknown')} disconnected")

    @socketio_server.event
    async def join_room(sid, data):
        """Join a chat room with proper authorization."""
        if sid not in active_users:
            return await socketio_server.emit("error", {"msg": "Not authenticated"}, room=sid)
            
        user = active_users[sid]
        room_id = data.get("room_id")
        job_id = data.get("job_id")
        
        if not room_id and not job_id:
            return await socketio_server.emit("error", {"msg": "Room ID or Job ID required"}, room=sid)
        
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
            await socketio_server.enter_room(sid, room_id)
            user["rooms"].add(room_id)
            
            # Mark messages as read
            await chat_service.mark_messages_as_read(room_id, user["user_id"])
            
            # Get recent messages
            messages = await chat_service.get_messages(room_id, limit=50)
            
            # Send chat history to the user
            await socketio_server.emit("chat_history", {
                "room_id": room_id,
                "messages": [msg.dict() for msg in messages]
            }, room=sid)
            
            print(f"➡️ User {user['user_id']} joined room: {room_id}")
            
        except Exception as e:
            await socketio_server.emit("error", {"msg": f"Failed to join room: {str(e)}"}, room=sid)

    @socketio_server.event
    async def send_message(sid, data):
        """Send and persist a new message."""
        if sid not in active_users:
            return await socketio_server.emit("error", {"msg": "Not authenticated"}, room=sid)
            
        user = active_users[sid]
        room_id = data.get("room_id")
        content = data.get("content")
        receiver_id = data.get("receiver_id")
        
        if not room_id or not content:
            return await socketio_server.emit("error", {"msg": "Room ID and content required"}, room=sid)
            
        if room_id not in user["rooms"]:
            return await socketio_server.emit("error", {"msg": "Not in this room"}, room=sid)
        
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
            await socketio_server.emit("new_message", {
                "id": message_id,
                **message.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }, room=room_id)
            
        except Exception as e:
            await socketio_server.emit("error", {"msg": f"Failed to send message: {str(e)}"}, room=sid)

    # Add all other event handlers (typing, etc.)
    @socketio_server.event
    async def start_typing(sid, data):
        if sid not in active_users:
            return await socketio_server.emit("error", {"msg": "Not authenticated"}, room=sid)
        user = active_users[sid]
        room_id = data.get("room_id")
        if room_id and room_id in user["rooms"]:
            await socketio_server.emit("user_typing", {"userId": user["user_id"], "roomId": room_id}, room=room_id, skip_sid=sid)

    @socketio_server.event
    async def stop_typing(sid, data):
        if sid not in active_users:
            return await socketio_server.emit("error", {"msg": "Not authenticated"}, room=sid)
        user = active_users[sid]
        room_id = data.get("room_id")
        if room_id and room_id in user["rooms"]:
            await socketio_server.emit("user_stopped_typing", {"userId": user["user_id"], "roomId": room_id}, room=room_id, skip_sid=sid)

    @socketio_server.event
    async def mark_as_read(sid, data):
        if sid not in active_users:
            return await socketio_server.emit("error", {"msg": "Not authenticated"}, room=sid)
        user = active_users[sid]
        room_id = data.get("room_id")
        if room_id:
            try:
                await chat_service.mark_messages_as_read(room_id, user["user_id"])
                print(f"📖 User {user['user_id']} marked messages as read in room: {room_id}")
            except Exception as e:
                await socketio_server.emit("error", {"msg": f"Failed to mark as read: {str(e)}"}, room=sid)

    @socketio_server.event
    async def leave_room(sid, data):
        if sid not in active_users:
            return await socketio_server.emit("error", {"msg": "Not authenticated"}, room=sid)
        user = active_users[sid]
        room_id = data.get("room_id")
        if room_id and room_id in user["rooms"]:
            await socketio_server.leave_room(sid, room_id)
            user["rooms"].remove(room_id)
            print(f"🚪 User {user['user_id']} left room: {room_id}")
            await socketio_server.emit("room_left", {"roomId": room_id}, room=sid)

# Register handlers for both Socket.IO servers
register_socketio_handlers(sio)
register_socketio_handlers(sio_ws)

if __name__ == "__main__":
    import uvicorn
    # Run the Socket.IO ASGI wrapper by default
    uvicorn.run("resume_api.main:app", host="127.0.0.1", port=8000, reload=True)


