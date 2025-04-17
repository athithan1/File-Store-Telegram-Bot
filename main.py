from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    API_ID, API_HASH, BOT_TOKEN, 
    STORAGE_CHANNEL, POST_CHANNEL
)
from handlers.file_handler import handle_file
from handlers.auth import check_subscription, get_subscribe_markup
from handlers.admin_handler import (
    load_admin_config, 
    set_welcome_image, 
    set_welcome_caption,
    set_force_channel,
    add_admin,
    get_random_reaction
)
from services.link_generator import decode_file_id
import os

print(f"Initializing bot with API_ID: {API_ID}")
app = Client(
    "mybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Store user's requested files
user_requests = {}

# Load admin config
config = load_admin_config()
FORCE_CHANNEL = config["force_sub_channel"]
START_IMAGE = config["welcome_image"]

async def check_subscription(client, user_id):
    try:
        print(f"Checking subscription for user {user_id} in channel {FORCE_CHANNEL}")
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        print(f"Member status: {member.status}")
        
        if str(member.status) in ["member", "administrator", "creator", 
                                 "ChatMemberStatus.MEMBER", 
                                 "ChatMemberStatus.ADMINISTRATOR", 
                                 "ChatMemberStatus.OWNER"]:
            print(f"User {user_id} is subscribed")
            return True
        else:
            print(f"User {user_id} is not subscribed (status: {member.status})")
            return False
            
    except Exception as e:
        print(f"Error checking subscription for user {user_id}: {str(e)}")
        return False

async def send_requested_file(client, chat_id, file_id):
    try:
        sent_msg = await client.copy_message(
            chat_id=chat_id,
            from_chat_id=STORAGE_CHANNEL,
            message_id=file_id
        )
        # Add random reaction
        if sent_msg:
            await sent_msg.react(get_random_reaction())
        return True
    except Exception as e:
        print(f"Error sending file: {str(e)}")
        return False

# Admin Commands
app.on_message(filters.command("setimage"))(set_welcome_image)
app.on_message(filters.command("setcaption"))(set_welcome_caption)
app.on_message(filters.command("setchannel"))(set_force_channel)
app.on_message(filters.command("addadmin"))(add_admin)

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    try:
        user_id = message.from_user.id
        user_mention = message.from_user.mention
        print(f"Start command received from user {user_id}")
        
        # Reload config in case it was updated
        config = load_admin_config()
        
        is_subscribed = await check_subscription(client, user_id)
        print(f"Subscription check result for user {user_id}: {is_subscribed}")
        
        # Check if there's a deep link parameter
        command_parts = message.text.split()
        has_file_request = len(command_parts) > 1
        
        if has_file_request:
            file_id = decode_file_id(command_parts[1])
            user_requests[user_id] = file_id
        
        if not is_subscribed:
            buttons = [[
                InlineKeyboardButton("Join Channel 🔔", url=f"https://t.me/{FORCE_CHANNEL.replace('@', '')}"),
                InlineKeyboardButton("Try Again 🔄", callback_data="check_sub")
            ]]
            caption = config["welcome_caption"].format(user_mention=user_mention)
        else:
            if has_file_request:
                success = await send_requested_file(client, message.chat.id, file_id)
                if success:
                    user_requests.pop(user_id, None)
                    return
                else:
                    await message.reply("❌ Sorry, couldn't find the requested file.")
                    return
            
            buttons = [[InlineKeyboardButton("✅ Already Joined", callback_data="already_joined")]]
            caption = config["welcome_caption"].format(user_mention=user_mention)
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        if os.path.exists(config["welcome_image"]):
            await client.send_photo(
                chat_id=message.chat.id,
                photo=config["welcome_image"],
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            await message.reply(caption, reply_markup=reply_markup)

    except Exception as e:
        print(f"Error in start command: {e}")
        await message.reply("❌ An error occurred")

@app.on_callback_query(filters.regex("check_sub|already_joined"))
async def callback_check_sub(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        print(f"Callback received from user {user_id}: {callback_query.data}")
        
        if callback_query.data == "already_joined":
            await callback_query.answer("You're already subscribed! ✅", show_alert=True)
            return
            
        is_subscribed = await check_subscription(client, user_id)
        print(f"Subscription check in callback for user {user_id}: {is_subscribed}")
        
        if is_subscribed:
            buttons = [[InlineKeyboardButton("✅ Already Joined", callback_data="already_joined")]]
            await callback_query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            await callback_query.answer("✅ Thank you for joining! You can use the bot now.", show_alert=True)
            
            if user_id in user_requests:
                file_id = user_requests[user_id]
                success = await send_requested_file(client, callback_query.message.chat.id, file_id)
                if success:
                    user_requests.pop(user_id)
        else:
            await callback_query.answer("⚠️ Please join the channel first!", show_alert=True)
    except Exception as e:
        print(f"Callback error: {e}")
        await callback_query.answer("❌ Error checking subscription", show_alert=True)

@app.on_message(filters.document | filters.video | filters.audio)
async def file_receive(client, message):
    # Check subscription before handling file
    user_id = message.from_user.id
    if not await check_subscription(client, user_id):
        buttons = [[
            InlineKeyboardButton("Join Channel 🔔", url=f"https://t.me/{FORCE_CHANNEL.replace('@', '')}"),
            InlineKeyboardButton("Try Again 🔄", callback_data="check_sub")
        ]]
        await message.reply(
            "❌ You need to join our channel to use this bot.\n"
            f"👉 {FORCE_CHANNEL}\n\n"
            "Join and click Try Again.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
        
    sent_msg = await handle_file(client, message)
    if sent_msg:
        await sent_msg.react(get_random_reaction())

async def main():
    async with app:
        print("Bot is starting...")
        try:
            print("Bot started successfully!")
            print("Bot is running... Press Ctrl+C to stop")
            await idle()
        except Exception as e:
            print(f"Error during startup: {str(e)}")
            raise e

if __name__ == "__main__":
    app.run(main())
