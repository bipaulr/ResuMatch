from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from database.mongo import get_database
from models.message import Message, MessageCreate

class ChatService:
    def __init__(self):
        self.db = get_database()
        self.messages_collection = self.db.messages
        self.chat_rooms_collection = self.db.chat_rooms
    
    async def create_or_get_room(self, job_id: str, student_id: str, recruiter_id: str) -> str:
        """
        Create a new chat room or get existing one for a job application.
        
        Args:
            job_id: ID of the job posting
            student_id: ID of the student
            recruiter_id: ID of the recruiter
            
        Returns:
            str: The room ID
        """
        # Check for existing room
        room = await self.chat_rooms_collection.find_one({
            "job_id": job_id,
            "student_id": student_id,
            "recruiter_id": recruiter_id
        })
        
        if room:
            return str(room["_id"])
            
        # Create new room
        room_data = {
            "job_id": job_id,
            "student_id": student_id,
            "recruiter_id": recruiter_id,
            "created_at": datetime.utcnow(),
            "last_message_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await self.chat_rooms_collection.insert_one(room_data)
        return str(result.inserted_id)
    
    async def save_message(self, message: MessageCreate) -> str:
        """
        Save a new message to the database.
        
        Args:
            message: The message to save
            
        Returns:
            str: The ID of the saved message
        """
        message_dict = message.dict()
        message_dict["timestamp"] = datetime.utcnow()
        
        # Save message
        result = await self.messages_collection.insert_one(message_dict)
        
        # Update room's last message timestamp
        await self.chat_rooms_collection.update_one(
            {"_id": ObjectId(message.room_id)},
            {"$set": {"last_message_at": message_dict["timestamp"]}}
        )
        
        return str(result.inserted_id)
    
    async def get_messages(
        self,
        room_id: str,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> List[Message]:
        """
        Retrieve messages from a chat room with pagination.
        
        Args:
            room_id: The ID of the chat room
            limit: Maximum number of messages to return
            before: Optional timestamp for pagination
            
        Returns:
            List[Message]: List of messages
        """
        query = {"room_id": room_id}
        if before:
            query["timestamp"] = {"$lt": before}
            
        cursor = self.messages_collection.find(query) \
            .sort("timestamp", -1) \
            .limit(limit)
            
        messages = []
        async for msg in cursor:
            msg["id"] = str(msg.pop("_id"))
            messages.append(Message(**msg))
            
        return messages[::-1]  # Reverse to get chronological order
    
    async def mark_messages_as_read(self, room_id: str, user_id: str):
        """
        Mark all messages in a room as read for a user.
        
        Args:
            room_id: The ID of the chat room
            user_id: The ID of the user marking messages as read
        """
        await self.messages_collection.update_many(
            {
                "room_id": room_id,
                "receiver_id": user_id,
                "read": False
            },
            {"$set": {"read": True}}
        )
    
    async def get_user_rooms(self, user_id: str) -> List[dict]:
        """
        Get all chat rooms for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[dict]: List of rooms with basic info
        """
        rooms = await self.chat_rooms_collection.find({
            "$or": [
                {"student_id": user_id},
                {"recruiter_id": user_id}
            ]
        }).to_list(None)
        
        for room in rooms:
            room["id"] = str(room.pop("_id"))
            # Get last message preview
            last_message = await self.messages_collection.find_one(
                {"room_id": room["id"]},
                sort=[("timestamp", -1)]
            )
            if last_message:
                room["last_message"] = {
                    "content": last_message["content"],
                    "sender_id": last_message["sender_id"],
                    "timestamp": last_message["timestamp"]
                }
                
        return rooms
