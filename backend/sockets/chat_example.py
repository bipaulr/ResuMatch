import asyncio
from datetime import datetime
from chat_client import ChatClient

async def example_message_handler(message):
    """Example handler for new messages."""
    sender = message.get("sender_id", "Unknown")
    content = message.get("content", "")
    timestamp = datetime.fromisoformat(message.get("timestamp", datetime.utcnow().isoformat()))
    print(f"[{timestamp:%H:%M:%S}] {sender}: {content}")

async def example_history_handler(data):
    """Example handler for chat history."""
    room_id = data.get("room_id")
    messages = data.get("messages", [])
    print(f"\nChat history for room {room_id}:")
    for msg in messages:
        sender = msg.get("sender_id", "Unknown")
        content = msg.get("content", "")
        timestamp = datetime.fromisoformat(msg.get("timestamp", datetime.utcnow().isoformat()))
        print(f"[{timestamp:%H:%M:%S}] {sender}: {content}")
    print("")

async def main():
    # Initialize client (replace with your server URL and JWT token)
    client = ChatClient(
        server_url="http://localhost:8000",
        token="your_jwt_token_here"
    )
    
    # Register message handlers
    client.on_message(example_message_handler)
    client.on_history(example_history_handler)
    
    try:
        # Connect to the server
        await client.connect()
        
        # Join a room (as a student)
        await client.join_room(
            job_id="job123",
            recruiter_id="recruiter456"  # The recruiter we want to chat with
        )
        
        # Send some messages
        await client.send_message(
            room_id="room123",
            content="Hello! I'm interested in the position."
        )
        
        # Keep the connection alive
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        # Leave room and disconnect on Ctrl+C
        await client.leave_room("room123")
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
