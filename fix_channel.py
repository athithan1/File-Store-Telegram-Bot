from pyrogram import Client
from pyrogram.errors import ChannelInvalid, PeerIdInvalid, ChatAdminRequired
import asyncio
import os
import sys

# Import settings from config
from config import API_ID, API_HASH, BOT_TOKEN, STORAGE_CHANNEL
from handlers.admin_handler import load_admin_config, save_admin_config

async def fix_channel_permissions():
    try:
        print("\n=== CHANNEL PERMISSION FIXER ===\n")
        
        # Get channel ID from argument or use default
        channel_id = None
        if len(sys.argv) > 1:
            channel_id = sys.argv[1]
            print(f"Using channel ID from arguments: {channel_id}")
        else:
            channel_id = STORAGE_CHANNEL
            print(f"Using channel ID from config: {channel_id}")
        
        # Initialize the client with user credentials for full admin powers
        app = Client("permission_fixer", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
        
        # Start the client
        await app.start()
        print("✅ Bot started successfully")
        
        # Try to join channel if needed
        try:
            # Try to access channel
            print(f"\nTrying to access channel {channel_id}...")
            chat = await app.get_chat(channel_id)
            print(f"✅ Found channel: {chat.title} (ID: {chat.id})")
            
            # Try to get bot's info
            bot_info = await app.get_me()
            print(f"Bot username: @{bot_info.username}")
            
            # Check if bot is member of the channel
            print("\nChecking bot membership...")
            try:
                member = await app.get_chat_member(chat.id, "me")
                print(f"✅ Bot is a member with status: {member.status}")
                
                if member.status == "administrator":
                    print("✅ Bot is an administrator")
                    
                    # Check permissions
                    print("\nChecking bot permissions:")
                    
                    # Different attributes depending on Pyrogram version
                    if hasattr(member, 'privileges'):
                        privileges = member.privileges
                        can_post = getattr(privileges, 'can_post_messages', False)
                        can_edit = getattr(privileges, 'can_edit_messages', False)
                        can_delete = getattr(privileges, 'can_delete_messages', False)
                    else:
                        can_post = getattr(member, 'can_post_messages', False)
                        can_edit = getattr(member, 'can_edit_messages', False)
                        can_delete = getattr(member, 'can_delete_messages', False)
                    
                    print(f"Can post messages: {can_post}")
                    print(f"Can edit messages: {can_edit}")
                    print(f"Can delete messages: {can_delete}")
                    
                    if not can_post:
                        print("\n❌ Bot cannot post messages in the channel!")
                        print("You need to update bot permissions in the channel:")
                        print("1. Go to channel > Admin > Administrators")
                        print("2. Find your bot and edit its permissions")
                        print("3. Enable 'Post Messages' permission")
                        return
                    
                    # Try to post a test message
                    print("\nAttempting to post a test message...")
                    try:
                        test_msg = await app.send_message(
                            chat.id, 
                            "🛠 This is a test message from the fix script. If you see this, bot permissions are working correctly!"
                        )
                        print("✅ Successfully posted test message!")
                        
                        # Update config if needed
                        admin_config = load_admin_config()
                        if admin_config["storage_channel"] != chat.id:
                            admin_config["storage_channel"] = chat.id
                            if save_admin_config(admin_config):
                                print("✅ Admin config updated with correct channel ID!")
                            else:
                                print("❌ Failed to update admin config")
                        
                        # Try to delete the message
                        try:
                            await test_msg.delete()
                            print("✅ Successfully deleted test message!")
                        except Exception as e:
                            print(f"❌ Could not delete test message: {str(e)}")
                    except Exception as e:
                        print(f"❌ Failed to post message: {str(e)}")
                else:
                    print("❌ Bot is not an administrator!")
                    print("\nYou need to make the bot an administrator:")
                    print("1. Go to channel > Admin > Administrators")
                    print("2. Add your bot as administrator with these permissions:")
                    print("   - Post Messages")
                    print("   - Edit Messages") 
                    print("   - Delete Messages")
                    
            except Exception as e:
                print(f"❌ Failed to check membership: {str(e)}")
                
        except PeerIdInvalid:
            print(f"❌ Invalid channel ID: {channel_id}")
            print("Make sure you're using a proper channel ID format: -100xxxxxxxxxx")
            
        except ChannelInvalid:
            print(f"❌ Channel not found or bot is not a member: {channel_id}")
            print("Make sure the bot is a member of the channel")
            
    except Exception as e:
        print(f"❌ Error in script: {str(e)}")
    finally:
        # Stop the client
        await app.stop()
        print("\nScript completed!")
        
if __name__ == "__main__":
    asyncio.run(fix_channel_permissions())