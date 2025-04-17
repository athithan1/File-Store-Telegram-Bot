from pyrogram.types import Message
from pyrogram.errors import ChannelInvalid, PeerIdInvalid, ChatAdminRequired, RPCError
from config import STORAGE_CHANNEL, POST_CHANNEL, DEBUG, FILE_UPLOAD_TEXT
from services.link_generator import encode_file_id

async def handle_file(client, message: Message):
    try:
        # Verify channel access first
        try:
            chat = await client.get_chat(STORAGE_CHANNEL)
            print(f"Storage channel access OK: {chat.title}")
            
            # Check bot permissions
            bot_member = await client.get_chat_member(STORAGE_CHANNEL, "me")
            print(f"Bot permissions in storage channel: {bot_member.privileges}")
        except Exception as e:
            print(f"Channel verification failed: {str(e)}")
            raise Exception(f"Bot needs admin access to channels: {str(e)}")

        if DEBUG:
            print(f"Processing file from user {message.from_user.id}")
        
        # Forward to storage channel
        stored_msg = await client.forward_messages(
            chat_id=STORAGE_CHANNEL,
            from_chat_id=message.chat.id,
            message_ids=message.id
        )
        
        if not stored_msg:
            raise Exception("Failed to store file")

        # Generate encoded file ID
        encoded_id = encode_file_id(stored_msg.id)
        
        # Create share link
        bot_info = await client.get_me()
        share_link = f"https://t.me/{bot_info.username}?start={encoded_id}"
        
        # Send success message with link
        await message.reply(
            f"{FILE_UPLOAD_TEXT}\n\n"
            f"📎 Share Link: {share_link}"
        )
        
    except ChatAdminRequired:
        error_msg = "Bot needs admin rights in channels"
        print(f"Admin rights missing: {error_msg}")
        await message.reply(error_msg)
    except Exception as e:
        detailed_error = f"Error: {str(e)}"
        print(detailed_error)
        await message.reply(f"❌ Failed to process file\n{detailed_error}")
