from pyrogram import Client
from pyrogram.errors import ChannelInvalid, PeerIdInvalid, ChatAdminRequired
import asyncio
import os

# Import settings from config
from config import API_ID, API_HASH, BOT_TOKEN, STORAGE_CHANNEL

async def main():
    try:
        print("\n=== CHANNEL PERMISSION DEBUGGER ===\n")
        print(f"Testing channel with ID: {STORAGE_CHANNEL}")
        
        # Initialize the client
        app = Client("permission_checker", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
        
        # Start the client
        print("Starting bot...")
        await app.start()
        print("Bot started successfully")
        
        try:
            # Try to get channel info
            print(f"\nAttempting to access channel {STORAGE_CHANNEL}...")
            chat = await app.get_chat(STORAGE_CHANNEL)
            print(f"✅ Channel found: {chat.title} (ID: {chat.id})")
            
            # Check bot membership
            print("\nChecking bot's membership status...")
            bot_member = await app.get_chat_member(chat.id, "me")
            print(f"Bot status in channel: {bot_member.status}")
            
            # Debug permissions in detail
            print("\n=== DETAILED PERMISSIONS ===")
            if hasattr(bot_member, 'privileges'):
                privileges = bot_member.privileges
                print(f"Can post messages: {getattr(privileges, 'can_post_messages', 'Unknown')}")
                print(f"Can edit messages: {getattr(privileges, 'can_edit_messages', 'Unknown')}")
                print(f"Can delete messages: {getattr(privileges, 'can_delete_messages', 'Unknown')}")
                print(f"Can restrict members: {getattr(privileges, 'can_restrict_members', 'Unknown')}")
                print(f"Can invite users: {getattr(privileges, 'can_invite_users', 'Unknown')}")
                print(f"Can pin messages: {getattr(privileges, 'can_pin_messages', 'Unknown')}")
            else:
                # For older Pyrogram versions
                print(f"Can post messages: {getattr(bot_member, 'can_post_messages', 'Unknown')}")
                print(f"Can edit messages: {getattr(bot_member, 'can_edit_messages', 'Unknown')}")
                print(f"Can delete messages: {getattr(bot_member, 'can_delete_messages', 'Unknown')}")
                print(f"Can restrict members: {getattr(bot_member, 'can_restrict_members', 'Unknown')}")
                print(f"Can invite users: {getattr(bot_member, 'can_invite_users', 'Unknown')}")
                print(f"Can pin messages: {getattr(bot_member, 'can_pin_messages', 'Unknown')}")
            
            # Try to post a test message
            print("\nAttempting to post a test message...")
            try:
                test_msg = await app.send_message(
                    chat.id,
                    "🛠 This is a test message to verify bot permissions. You can delete this."
                )
                print("✅ Successfully posted test message!")
                
                # Try to delete the test message
                try:
                    await test_msg.delete()
                    print("✅ Successfully deleted test message!")
                except Exception as e:
                    print(f"❌ Could not delete test message: {str(e)}")
            except Exception as e:
                print(f"❌ Could not post test message: {str(e)}")
                
        except ChatAdminRequired as e:
            print(f"\n❌ Error: Bot needs admin privileges - {str(e)}")
            print("\nTo fix this:")
            print("1. Go to the channel")
            print("2. Open channel settings > Administrators")
            print("3. Add your bot as an administrator")
            print("4. Make sure these permissions are enabled:")
            print("   - Post Messages")
            print("   - Edit Messages")
            print("   - Delete Messages")
            
        except PeerIdInvalid as e:
            print(f"\n❌ Error: Invalid channel ID - {str(e)}")
            print("\nDouble check that the ID format is correct: -100xxxxxxxxxx")
            print("Use /setchannel in the bot to update the channel ID")
            
        except ChannelInvalid as e:
            print(f"\n❌ Error: Channel not found - {str(e)}")
            print("\nMake sure:")
            print("1. The bot is a member of the channel")
            print("2. The channel ID is correct")
            print("3. The channel exists and hasn't been deleted")
            
        except Exception as e:
            print(f"\n❌ Unexpected error: {type(e).__name__} - {str(e)}")
            
    except Exception as e:
        print(f"\n❌ Script error: {str(e)}")
        
    finally:
        # Close the client
        try:
            print("\nStopping bot...")
            await app.stop()
            print("Bot stopped")
        except:
            pass
            
        print("\n=== TROUBLESHOOTING STEPS ===")
        print("1. Make sure the bot is a member of the channel")
        print("2. Make sure the bot is an admin with ALL permissions")
        print("3. Try removing and re-adding the bot to the channel")
        print("4. Make sure the channel hasn't been deleted or archived")
        print("\nFor force subscribe channel, make sure it's public or the bot has invite links permission")

if __name__ == "__main__":
    asyncio.run(main()) 