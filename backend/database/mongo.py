from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qs
import logging

# Load environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
client = None
db = None
users_collection = None
jobs_collection = None
messages_collection = None
chat_rooms_collection = None
resumes_collection = None

def initialize_database():
    """Initialize database connection"""
    global client, db, users_collection, jobs_collection, messages_collection, chat_rooms_collection, resumes_collection
    
    # Get the MongoDB URI from the environment variables
    mongo_uri = os.getenv("MONGODB_URI")
    
    if not mongo_uri:
        logger.warning("MONGODB_URI environment variable not set. Using default local connection.")
        mongo_uri = "mongodb://localhost:27017/resumatch"
    
    logger.info(f"Connecting to MongoDB...")
    
    try:
        # Create an asynchronous MongoDB client
        client = AsyncIOMotorClient(mongo_uri)
        
        # Access your database
        db_name = os.getenv("MONGODB_DB_NAME", "resumatch")
        db = client[db_name]
        
        # Access collections
        users_collection = db["users"]
        jobs_collection = db["jobs"]
        messages_collection = db["messages"]
        chat_rooms_collection = db["chat_rooms"]
        resumes_collection = db["resumes"]
        
        logger.info("Database connection initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Create mock collections for testing
        client = None
        db = None
        users_collection = None
        jobs_collection = None
        messages_collection = None
        chat_rooms_collection = None
        resumes_collection = None

# Initialize database connection on import
initialize_database()

def get_database():
    """Get the database instance"""
    if db is None:
        initialize_database()
    return db

def get_users_collection():
    """Get the users collection"""
    if users_collection is None:
        initialize_database()
    return users_collection

def get_job_collection():
    """Get the jobs collection"""
    if jobs_collection is None:
        initialize_database()
    return jobs_collection

def get_messages_collection():
    """Get the messages collection"""
    if messages_collection is None:
        initialize_database()
    return messages_collection

def get_chat_rooms_collection():
    """Get the chat rooms collection"""
    if chat_rooms_collection is None:
        initialize_database()
    return chat_rooms_collection

def get_resumes_collection():
    """Get the resumes collection"""
    if resumes_collection is None:
        initialize_database()
    return resumes_collection
