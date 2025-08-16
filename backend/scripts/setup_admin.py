import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from database.mongo import get_database
from auth.auth_utils import hash_password
import secrets

async def setup_admin_user():
    """Create the first admin user and generate JWT secret"""
    
    # Load environment variables
    load_dotenv()
    
    # Generate JWT secret if not exists
    env_path = ".env"
    jwt_secret = secrets.token_hex(32)
    
    # Read existing .env content
    with open(env_path, "r") as f:
        env_content = f.read()
    
    # Update JWT_SECRET if not set
    if "JWT_SECRET=" not in env_content or not os.getenv("JWT_SECRET"):
        if "JWT_SECRET=" in env_content:
            # Replace empty JWT_SECRET
            env_content = env_content.replace("JWT_SECRET=\n", f"JWT_SECRET={jwt_secret}\n")
        else:
            # Add JWT_SECRET
            env_content += f"\nJWT_SECRET={jwt_secret}\n"
        
        # Write updated content back to .env
        with open(env_path, "w") as f:
            f.write(env_content)
        print(f"Generated and saved new JWT secret")
    
    # Connect to database
    db = await get_database()
    
    # Check if admin user exists
    existing_admin = await db.users.find_one({"role": "admin"})
    if existing_admin:
        print("Admin user already exists")
        return
    
    # Create admin user
    admin_password = secrets.token_urlsafe(12)  # Generate secure random password
    admin_user = {
        "username": "admin",
        "email": "admin@resumatch.com",
        "password": hash_password(admin_password),
        "role": "admin",
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(admin_user)
    if result.inserted_id:
        print("\n=== Admin User Created Successfully ===")
        print(f"Username: {admin_user['username']}")
        print(f"Email: {admin_user['email']}")
        print(f"Password: {admin_password}")
        print("\nPLEASE SAVE THESE CREDENTIALS SECURELY AND CHANGE THE PASSWORD ON FIRST LOGIN")
        print("===============================\n")
    else:
        print("Failed to create admin user")

if __name__ == "__main__":
    asyncio.run(setup_admin_user())
