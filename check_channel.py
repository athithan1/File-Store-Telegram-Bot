from pyrogram import Client
import asyncio
from config import API_ID, API_HASH, BOT_TOKEN

async def check_specific_channel():
    # The channel ID directly from your forwarded message
    channel_id = -1002605972463
    
    print(f"Checking channel with ID: {channel_id}")
    
    app = Client("channel_checker", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    
    try:
        await app.start()
        print("Bot started")
        
        try:
            # Try getting the chat info
            chat = await app.get_chat(channel_id)
            print(f"✅ Channel found: {chat.title} (ID: {chat.id})")
            
            # Check membership
            member = await app.get_chat_member(chat.id, "me")
            print(f"Bot status in channel: {member.status}")
            
            # Try to send a message
            try:
                msg = await app.send_message(chat.id, "Test message from permission checker")
                print("✅ Successfully sent a message to the channel")
                await msg.delete()
                print("✅ Successfully deleted the message")
            except Exception as e:
                print(f"❌ Failed to send message: {str(e)}")
                
        except Exception as e:
            print(f"❌ Error accessing channel: {str(e)}")
    except Exception as e:
        print(f"❌ Error starting bot: {str(e)}")
    finally:
        await app.stop()
        print("Bot stopped")

asyncio.run(check_specific_channel()) 