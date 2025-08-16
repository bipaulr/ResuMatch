from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    """Schema for creating a new chat message"""
    content: str = Field(..., min_length=1)
    room_id: str
    sender_id: str
    receiver_id: Optional[str] = None
    message_type: str = Field(default="text", description="text, file, or system")

class Message(MessageCreate):
    """Schema for a message in the database"""
    id: Optional[str] = Field(None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read: bool = Field(default=False)
    
    def dict(self, **kwargs):
        """Override dict method to ensure datetime serialization"""
        data = super().dict(**kwargs)
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }