from pyrogram.types import Message
from pyrogram.errors import ChannelInvalid, PeerIdInvalid, ChatAdminRequired, RPCError
from config import STORAGE_CHANNEL, POST_CHANNEL, DEBUG, FILE_UPLOAD_TEXT
from services.link_generator import encode_file_id

async def handle_file(client, message: Message, bulk_mode=False):
    try:
        # Verify channel access first
        try:
            # Channel must be numeric - ensure it's treated as an integer
            storage_channel_id = int(STORAGE_CHANNEL)
            
            # Log the channel ID for debugging
            print(f"Attempting to access storage channel with ID: {storage_channel_id}")
            
            # Try to get chat info
            chat = None
            try:
                chat = await client.get_chat(storage_channel_id)
                print(f"✅ Storage channel access OK: {chat.title} (ID: {chat.id})")
            except (PeerIdInvalid, ChannelInvalid) as e:
                # Try alternative channel ID formats if the original doesn't work
                alternative_ids = [
                    int(str(storage_channel_id).replace('-100', '-1001')),  # Try -1001 format
                    int(f"-100{str(abs(storage_channel_id))[3:]}"),  # Different -100 format
                    int(str(abs(storage_channel_id))[3:])  # Just the numeric part
                ]
                
                for alt_id in alternative_ids:
                    try:
                        print(f"Trying alternative channel ID: {alt_id}")
                        chat = await client.get_chat(alt_id)
                        if chat:
                            print(f"✅ Found channel with alternative ID: {chat.title} (ID: {chat.id})")
                            storage_channel_id = alt_id
                            break
                    except Exception:
                        continue
                        
                if not chat:
                    raise PeerIdInvalid(f"Storage channel not found with any ID format. Original error: {str(e)}")
            
            # Check bot permissions
            bot_member = await client.get_chat_member(chat.id, "me")
            print(f"Bot permissions in storage channel: {bot_member.status}")
            
            # Verify posting permission - improved check that works with different Pyrogram versions
            can_post = False
            if hasattr(bot_member, 'privileges'):
                # New Pyrogram version
                can_post = getattr(bot_member.privileges, 'can_post_messages', False)
            else:
                # Old Pyrogram version
                can_post = getattr(bot_member, 'can_post_messages', False)
                
            if not can_post:
                print("Bot does not have permission to post messages in the storage channel!")
                raise ChatAdminRequired("Bot needs to be an admin in the storage channel with 'Post Messages' permission. Please check your channel settings.")
                
        except PeerIdInvalid as e:
            print(f"Invalid channel ID: {storage_channel_id}")
            raise Exception(f"Storage channel ID is invalid. Use the /setchannel command to set a valid channel ID where the bot is an admin. Error: {str(e)}")
        except ChannelInvalid as e:
            print(f"Channel not found: {storage_channel_id}")
            raise Exception(f"Storage channel not found. Make sure the bot is a member of the channel. Error: {str(e)}")
        except ChatAdminRequired as e:
            print(f"Bot is not admin in channel: {storage_channel_id}")
            raise Exception(f"Bot needs to be an admin in the storage channel with 'Post Messages' permission. Error: {str(e)}")
        except Exception as e:
            print(f"Channel verification failed: {str(e)}")
            raise Exception(f"Bot needs admin access to channel. Error: {str(e)}")

        if DEBUG:
            print(f"Processing file from user {message.from_user.id}")
        
        # Forward to storage channel
        try:
            stored_msg = await client.forward_messages(
                chat_id=storage_channel_id,
                from_chat_id=message.chat.id,
                message_ids=message.id
            )
            
            if not stored_msg:
                raise Exception("Failed to forward message to storage channel")
                
            print(f"Message successfully forwarded to storage channel, ID: {stored_msg.id}")
        except Exception as e:
            print(f"Failed to forward message: {str(e)}")
            raise Exception(f"Failed to forward message to storage channel: {str(e)}")

        # Generate encoded file ID
        encoded_id = encode_file_id(stored_msg.id)
        
        # Create share link
        bot_info = await client.get_me()
        share_link = f"https://t.me/{bot_info.username}?start={encoded_id}"
        
        # Send success message with link
        return await message.reply(
            f"{FILE_UPLOAD_TEXT}\n\n"
            f"📎 Share Link: {share_link}"
        )
        
    except ChatAdminRequired:
        error_msg = "Bot needs admin rights with post messages permission in the storage channel"
        print(f"Admin rights missing: {error_msg}")
        await message.reply(error_msg)
        return None
    except PeerIdInvalid:
        error_msg = "Storage channel ID is invalid. Ask admin to use /setchannel to set a valid channel"
        print(f"Invalid channel ID: {error_msg}")
        await message.reply(error_msg)
        return None
    except Exception as e:
        detailed_error = f"Error: {str(e)}"
        print(detailed_error)
        await message.reply(f"❌ Failed to process file\n{detailed_error}")
        return None
