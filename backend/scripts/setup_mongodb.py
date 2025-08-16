import asyncio
from database.mongo import get_database

async def setup_mongodb():
    """Set up MongoDB collections, indexes, and validation rules"""
    
    db = get_database()
    
    # Users Collection
    await db.command({
        "collMod": "users",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["username", "email", "password", "role"],
                "properties": {
                    "username": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "email": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                        "description": "must be a valid email address"
                    },
                    "password": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "role": {
                        "enum": ["student", "recruiter", "admin"],
                        "description": "must be one of: student, recruiter, admin"
                    }
                }
            }
        }
    })
    
    # Jobs Collection
    await db.command({
        "collMod": "jobs",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["title", "description", "company_name", "skills_required", "location", "recruiter_id"],
                "properties": {
                    "title": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "description": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "company_name": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "skills_required": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        },
                        "description": "must be an array of strings and is required"
                    },
                    "location": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "recruiter_id": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "status": {
                        "enum": ["active", "filled", "closed"],
                        "description": "must be one of: active, filled, closed"
                    }
                }
            }
        }
    })
    
    # Messages Collection
    await db.command({
        "collMod": "messages",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["room_id", "sender_id", "content", "timestamp"],
                "properties": {
                    "room_id": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "sender_id": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "receiver_id": {
                        "bsonType": "string",
                        "description": "must be a string"
                    },
                    "content": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "timestamp": {
                        "bsonType": "date",
                        "description": "must be a date and is required"
                    },
                    "read": {
                        "bsonType": "bool",
                        "description": "must be a boolean"
                    }
                }
            }
        }
    })
    
    # Chat Rooms Collection
    await db.command({
        "collMod": "chat_rooms",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["job_id", "student_id", "recruiter_id", "created_at"],
                "properties": {
                    "job_id": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "student_id": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "recruiter_id": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "created_at": {
                        "bsonType": "date",
                        "description": "must be a date and is required"
                    },
                    "last_message_at": {
                        "bsonType": "date",
                        "description": "must be a date"
                    },
                    "is_active": {
                        "bsonType": "bool",
                        "description": "must be a boolean"
                    }
                }
            }
        }
    })
    
    # Create indexes
    print("Creating indexes...")
    
    # Users indexes
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    
    # Jobs indexes
    await db.jobs.create_index("recruiter_id")
    await db.jobs.create_index("skills_required")
    await db.jobs.create_index("status")
    await db.jobs.create_index([("title", "text"), ("description", "text")])
    
    # Messages indexes
    await db.messages.create_index([("room_id", 1), ("timestamp", -1)])
    await db.messages.create_index("sender_id")
    await db.messages.create_index("receiver_id")
    await db.messages.create_index("timestamp")
    
    # Chat rooms indexes
    await db.chat_rooms.create_index([("job_id", 1), ("student_id", 1), ("recruiter_id", 1)], unique=True)
    await db.chat_rooms.create_index("student_id")
    await db.chat_rooms.create_index("recruiter_id")
    await db.chat_rooms.create_index("last_message_at")
    
    print("MongoDB setup completed successfully!")

if __name__ == "__main__":
    asyncio.run(setup_mongodb())
