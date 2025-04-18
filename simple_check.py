from pyrogram import Client
import asyncio
import sys

# Import settings from config
from config import API_ID, API_HASH, BOT_TOKEN

async def check_channel(channel_id):
    app = Client("simple_check", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    
    try:
        await app.start()
        print(f"Checking channel: {channel_id}")
        
        try:
            chat = await app.get_chat(channel_id)
            print(f"✅ Channel found: {chat.title}")
            print(f"Channel ID: {chat.id}")
            
            try:
                member = await app.get_chat_member(chat.id, "me")
                print(f"Bot status: {member.status}")
                
                if member.status == "administrator":
                    print("✅ Bot is an administrator")
                else:
                    print("❌ Bot is NOT an administrator")
            except Exception as e:
                print(f"❌ Error checking membership: {e}")
        except Exception as e:
            print(f"❌ Error getting chat: {e}")
    except Exception as e:
        print(f"❌ Error starting client: {e}")
    finally:
        await app.stop()

# List of IDs to try
channel_ids = [
    -1002605972463,  # Original from forwarded message
    -100605972463,   # Without the extra '2'
    -1001605972463,  # Standard format
    605972463,       # Just the numeric part
]

async def main():
    for channel_id in channel_ids:
        print(f"\n--- Testing channel ID: {channel_id} ---")
        await check_channel(channel_id)
        await asyncio.sleep(1)  # Add delay between checks

if __name__ == "__main__":
    asyncio.run(main()) 