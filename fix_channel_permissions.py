from pyrogram import Client
from pyrogram.errors import ChannelInvalid, PeerIdInvalid, ChatAdminRequired
import asyncio
import os

# Import settings from config
from config import API_ID, API_HASH, BOT_TOKEN, STORAGE_CHANNEL

async def main():
    try:
        print("\n=== CHANNEL PERMISSION DIAGNOSTIC TOOL ===\n")
        print(f"Checking channel ID: {STORAGE_CHANNEL}")
        
        # Initialize the client
        app = Client("permission_diagnostics", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
        
        try:
            # Start the client
            print("Starting bot...")
            await app.start()
            print("Bot started successfully")
            
            # Get bot info
            me = await app.get_me()
            print(f"Bot: @{me.username}")
            
            # Try to access channel
            print("\nAttempting to access channel...")
            try:
                chat = await app.get_chat(STORAGE_CHANNEL)
                print(f"✅ Channel found: {chat.title}")
                print(f"Channel ID: {chat.id}")
                print(f"Channel type: {chat.type}")
                
                if chat.type != "channel":
                    print(f"⚠️ Warning: This chat type is '{chat.type}', not a channel")
                
                # Check bot membership
                print("\nChecking bot membership...")
                try:
                    member = await app.get_chat_member(chat.id, me.id)
                    print(f"Bot membership status: {member.status}")
                    
                    if member.status == "administrator":
                        print("✅ Bot is an administrator")
                        
                        # Check permissions
                        print("\nChecking permissions:")
                        
                        # Handle both old and new Pyrogram versions
                        can_post = False
                        
                        if hasattr(member, 'privileges'):
                            privileges = member.privileges
                            can_post = getattr(privileges, 'can_post_messages', False)
                            print(f"Can post messages: {can_post}")
                            print(f"Can edit messages: {getattr(privileges, 'can_edit_messages', False)}")
                            print(f"Can delete messages: {getattr(privileges, 'can_delete_messages', False)}")
                        else:
                            can_post = getattr(member, 'can_post_messages', False)
                            print(f"Can post messages: {can_post}")
                            print(f"Can edit messages: {getattr(member, 'can_edit_messages', False)}")
                            print(f"Can delete messages: {getattr(member, 'can_delete_messages', False)}")
                        
                        if not can_post:
                            print("\n❌ ISSUE FOUND: Bot cannot post messages in this channel")
                            print("This is the most common reason for storage channel failures")
                            print("\nTo fix this issue:")
                            print("1. Go to the channel > three dots menu > Administrators")
                            print("2. Find your bot and tap Edit")
                            print("3. Make sure 'Post Messages' permission is enabled")
                            print("4. Save changes and restart your bot")
                        else:
                            # Test sending a message
                            print("\nTesting message sending ability...")
                            try:
                                message = await app.send_message(
                                    chat.id,
                                    "🔍 This is a test message from the permission diagnostic tool.\n"
                                    "If you can see this, the bot permissions are working correctly!"
                                )
                                print("✅ Successfully sent a message to the channel!")
                                
                                # Test message deletion
                                try:
                                    await message.delete()
                                    print("✅ Successfully deleted the test message")
                                    print("\n✅ ALL TESTS PASSED: The bot has correct permissions in this channel")
                                except Exception as e:
                                    print(f"⚠️ Could not delete test message: {str(e)}")
                                    print("This is not critical but indicates limited permissions")
                            except Exception as e:
                                print(f"❌ Failed to send message despite having permissions: {str(e)}")
                                print("\nThis might indicate:")
                                print("1. There's a Telegram API limitation")
                                print("2. The bot has post messages permission but not enough other rights")
                                print("3. The channel has special restrictions enabled")
                    else:
                        print("❌ Bot is NOT an administrator")
                        print("\nTo fix this issue:")
                        print("1. Go to the channel > three dots menu > Administrators")
                        print("2. Add your bot as an administrator")
                        print("3. Enable these permissions:")
                        print("   - Post Messages")
                        print("   - Edit Messages")
                        print("   - Delete Messages")
                except Exception as e:
                    print(f"❌ Failed to check bot membership: {str(e)}")
                    print("This could mean the bot is not a member of the channel")
                    
            except PeerIdInvalid:
                print(f"❌ Invalid channel ID: {STORAGE_CHANNEL}")
                print("The ID format appears to be incorrect")
                print("\nTo fix this issue:")
                print("1. Forward a message from your channel to @username_to_id_bot")
                print("2. Get the correct channel ID and update it in config.py")
                print("3. Make sure the ID format starts with -100...")
                
            except ChannelInvalid:
                print(f"❌ Channel not found: {STORAGE_CHANNEL}")
                print("The bot cannot access this channel")
                print("\nTo fix this issue:")
                print("1. Make sure the bot is added to the channel")
                print("2. Make sure the channel hasn't been deleted")
                print("3. For private channels, the bot must be a member")
                
            except Exception as e:
                print(f"❌ Unexpected error accessing channel: {type(e).__name__}: {str(e)}")
                
            print("\n=== TESTING ALTERNATIVE CHANNEL IDS ===")
            # Try some alternative formats
            alt_ids = [
                int(str(STORAGE_CHANNEL).replace('-100', '-1001')),
                int(str(STORAGE_CHANNEL).replace('-100', '-100')),
                int(str(abs(STORAGE_CHANNEL))[3:])  # Just the numeric part without -100
            ]
            
            for alt_id in alt_ids:
                print(f"\nTrying alternative ID: {alt_id}")
                try:
                    alt_chat = await app.get_chat(alt_id)
                    print(f"✅ Alternative channel found: {alt_chat.title}")
                    print(f"This ID works: {alt_chat.id}")
                    print(f"Try updating your config to use this ID instead: {alt_chat.id}")
                    break
                except Exception as e:
                    print(f"❌ This alternative ID failed: {str(e)}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
        finally:
            # Close the client
            print("\nStopping bot...")
            await app.stop()
            print("Bot stopped")
            
        print("\n=== SUMMARY ===")
        print("If the diagnostic found issues:")
        print("1. Make sure the bot is a member and admin in the channel")
        print("2. Ensure the bot has 'Post Messages' permission")
        print("3. Check that the channel ID format is correct (-100xxxxxxxxxx)")
        print("4. Try removing and re-adding the bot to the channel")
        print("5. If a specific alternative ID worked, update your config files")
            
    except Exception as e:
        print(f"Script error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 