from typing import Optional, Callable, Dict, List, Any
import socketio
import asyncio
from datetime import datetime
import json

class ChatClient:
    """
    A Socket.IO client for the chat system that handles connections,
    message sending/receiving, and room management.
    """
    
    def __init__(self, server_url: str, token: str):
        """
        Initialize the chat client.
        
        Args:
            server_url: The WebSocket server URL
            token: JWT token for authentication
        """
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.token = token
        self.connected = False
        self.active_rooms: set = set()
        self.message_handlers: Dict[str, List[Callable]] = {
            "new_message": [],
            "chat_history": [],
            "error": [],
            "left_room": []
        }
        
        # Set up event handlers
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Set up internal Socket.IO event handlers."""
        
        @self.sio.event
        async def connect():
            self.connected = True
            print("✅ Connected to chat server")
            
        @self.sio.event
        async def connect_error(error: str):
            print(f"❌ Connection failed: {error}")
            
        @self.sio.event
        async def disconnect():
            self.connected = False
            self.active_rooms.clear()
            print("❌ Disconnected from server")

        @self.sio.event
        async def new_message(data: Dict[str, Any]):
            """Handle new messages from the server."""
            for handler in self.message_handlers["new_message"]:
                await handler(data)
                
        @self.sio.event
        async def chat_history(data: Dict[str, Any]):
            """Handle chat history from the server."""
            for handler in self.message_handlers["chat_history"]:
                await handler(data)
                
        @self.sio.event
        async def error(data: Dict[str, Any]):
            """Handle error messages from the server."""
            print(f"🚫 Chat error: {data.get('msg', 'Unknown error')}")
            for handler in self.message_handlers["error"]:
                await handler(data)
                
        @self.sio.event
        async def left_room(data: Dict[str, Any]):
            """Handle room leave events."""
            room_id = data.get("room_id")
            if room_id in self.active_rooms:
                self.active_rooms.remove(room_id)
            for handler in self.message_handlers["left_room"]:
                await handler(data)
    
    async def connect(self):
        """Connect to the chat server with JWT authentication."""
        if not self.connected:
            try:
                await self.sio.connect(
                    self.server_url,
                    headers={"Authorization": f"Bearer {self.token}"},
                    wait_timeout=10
                )
            except Exception as e:
                print(f"Connection error: {e}")
                raise
    
    async def disconnect(self):
        """Disconnect from the chat server."""
        if self.connected:
            await self.sio.disconnect()
    
    async def join_room(self, job_id: str = None, room_id: str = None, 
                       student_id: str = None, recruiter_id: str = None):
        """
        Join a chat room. Either provide room_id for existing rooms,
        or job_id and student_id/recruiter_id for new rooms.
        
        Args:
            job_id: ID of the job posting (for new rooms)
            room_id: ID of existing room
            student_id: ID of the student (required for recruiters in new rooms)
            recruiter_id: ID of the recruiter (required for students in new rooms)
        """
        if not self.connected:
            raise RuntimeError("Not connected to chat server")
            
        data = {}
        if room_id:
            data["room_id"] = room_id
        elif job_id:
            data["job_id"] = job_id
            if student_id:
                data["student_id"] = student_id
            if recruiter_id:
                data["recruiter_id"] = recruiter_id
        else:
            raise ValueError("Either room_id or job_id with student_id/recruiter_id is required")
            
        await self.sio.emit("join_room", data)
    
    async def leave_room(self, room_id: str):
        """
        Leave a chat room.
        
        Args:
            room_id: ID of the room to leave
        """
        if not self.connected:
            raise RuntimeError("Not connected to chat server")
            
        await self.sio.emit("leave_room", {"room_id": room_id})
    
    async def send_message(self, room_id: str, content: str, receiver_id: Optional[str] = None):
        """
        Send a message to a chat room.
        
        Args:
            room_id: ID of the room to send the message to
            content: Message content
            receiver_id: Optional ID of the specific recipient
        """
        if not self.connected:
            raise RuntimeError("Not connected to chat server")
            
        await self.sio.emit("send_message", {
            "room_id": room_id,
            "content": content,
            "receiver_id": receiver_id
        })
    
    def on_message(self, handler: Callable):
        """
        Register a handler for new messages.
        
        Args:
            handler: Async function to handle new messages
        """
        self.message_handlers["new_message"].append(handler)
    
    def on_history(self, handler: Callable):
        """
        Register a handler for chat history.
        
        Args:
            handler: Async function to handle chat history
        """
        self.message_handlers["chat_history"].append(handler)
    
    def on_error(self, handler: Callable):
        """
        Register a handler for error messages.
        
        Args:
            handler: Async function to handle errors
        """
        self.message_handlers["error"].append(handler)
    
    def on_left_room(self, handler: Callable):
        """
        Register a handler for room leave events.
        
        Args:
            handler: Async function to handle room leave events
        """
        self.message_handlers["left_room"].append(handler)
        
    async def get_room_messages(self, room_id: str, limit: int = 50) -> List[Dict]:
        """
        Fetch message history for a room using HTTP API.
        
        Args:
            room_id: ID of the room
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        async with self.sio.eio._http as session:
            async with session.get(
                f"{self.server_url}/rooms/{room_id}/messages",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {self.token}"}
            ) as response:
                data = await response.json()
                return data.get("messages", [])
