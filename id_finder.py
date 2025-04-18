from pyrogram import Client
import asyncio
from config import API_ID, API_HASH, BOT_TOKEN

# List of potential channel ID formats to try
CHANNEL_IDS = [
    -1002605972463,  # Original from forwarded message
    -100605972463,   # Removing extra '2'
    -1001605972463,  # Standard format with shorter ID
    2605972463,      # Just the numeric part
    -100 + 2605972463,  # Computed standard format
    -1001002605972463,  # Extra long format
    -1002605972,      # Shorter variant
    1002605972463,    # Positive variant
]

async def find_working_channel_id():
    print("=== CHANNEL ID FINDER ===")
    print("Trying multiple channel ID formats to find the working one...")
    
    app = Client("id_finder", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    
    try:
        await app.start()
        print("Bot started successfully")
        
        for i, channel_id in enumerate(CHANNEL_IDS):
            print(f"\nTrying format #{i+1}: {channel_id}")
            
            try:
                # Try to get chat info
                chat = await app.get_chat(channel_id)
                print(f"✓ SUCCESS! Channel found: {chat.title}")
                print(f"Channel ID: {chat.id}")
                
                # Check membership
                try:
                    member = await app.get_chat_member(chat.id, "me")
                    print(f"Bot status: {member.status}")
                    
                    # Try to send a message
                    try:
                        msg = await app.send_message(chat.id, "Test message - please ignore")
                        print("✓ Successfully sent a message!")
                        await msg.delete()
                        print("✓ Successfully deleted the message!")
                        
                        print("\n=== SOLUTION FOUND ===")
                        print(f"The correct channel ID format is: {chat.id}")
                        print("Please update your config.py and admin_config.json with this ID")
                        break
                    except Exception as e:
                        print(f"✗ Failed to send message: {str(e)}")
                except Exception as e:
                    print(f"✗ Failed to check membership: {str(e)}")
            except Exception as e:
                print(f"✗ Failed with this format: {str(e)}")
                
    except Exception as e:
        print(f"Error starting bot: {str(e)}")
    finally:
        await app.stop()
        print("\nBot stopped")
        print("If no working ID was found, please ensure:")
        print("1. The bot is actually added to the channel")
        print("2. The channel exists and hasn't been deleted")
        print("3. Try forwarding a message from the channel again to get the correct ID")

if __name__ == "__main__":
    asyncio.run(find_working_channel_id()) 