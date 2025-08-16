from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.message import Message
from database.mongo import get_database
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/test")
def test_chat():
    """Health check for chat system."""
    return {"message": "Chat system is up and running!"}

@router.get("/history/{room_id}")
async def get_chat_history(room_id: str, limit: int = 50):
    """
    Returns the last messages for a given chat room from MongoDB.
    
    Args:
        room_id: The chat room identifier
        limit: Maximum number of messages to return (default: 50)
    """
    db = get_database()
    messages_collection = db.messages
    
    # Query messages for the room, sort by timestamp descending
    cursor = messages_collection.find(
        {"room_id": room_id},
        sort=[("timestamp", -1)],
        limit=limit
    )
    
    messages = []
    async for msg in cursor:
        msg["id"] = str(msg.pop("_id"))  # Convert ObjectId to string and rename
        messages.append(msg)
    
    return {
        "room_id": room_id,
        "message_count": len(messages),
        "messages": messages[::-1]  # Reverse to get chronological order
    }