from pyrogram.types import Message
from pyrogram.errors import ChannelInvalid, PeerIdInvalid, ChatAdminRequired, RPCError
from config import STORAGE_CHANNEL, POST_CHANNEL, DEBUG
from services.link_generator import encode_file_id

async def handle_file(client, message: Message):
    try:
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
        
        # Send link to user
        await message.reply(
            f"✅ File stored successfully!\n\n"
            f"📎 Share Link: {share_link}\n\n"
            f"📩 Click the link to receive the file"
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        await message.reply("❌ Failed to process file")
