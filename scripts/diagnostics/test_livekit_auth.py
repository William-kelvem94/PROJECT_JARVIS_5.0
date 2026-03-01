import os
import asyncio
from dotenv import load_dotenv
from livekit import api

load_dotenv("env/.env")

async def main():
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    print(f"URL: {url}")
    print(f"Key: {api_key}")
    
    # Initialize the LiveKit API client
    lkapi = api.LiveKitAPI(url, api_key, api_secret)
    
    try:
        # Try to list active rooms
        rooms = await lkapi.room.list_rooms(api.ListRoomsRequest())
        print(f"Success! Rooms active: {len(rooms.rooms)}")
    except Exception as e:
        print(f"Error connecting to LiveKit: {e}")
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(main())
