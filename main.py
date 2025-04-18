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
    show_settings,
    show_contact_info,
    handle_set_image,
    handle_set_caption,
    show_admin_settings,
    toggle_bulk_mode,
    is_admin,
    is_bulk_mode_enabled,
    get_random_reaction,
    show_file_settings,
    show_channel_settings,
    show_bot_settings,
    toggle_auto_accept,
    toggle_maintenance,
    handle_set_storage,
    handle_set_force_sub,
    handle_set_file_size,
    is_maintenance_mode,
    save_admin_config
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

# Store user's requested files and states
user_requests = {}
user_states = {}

# Load admin config
config = load_admin_config()
FORCE_SUB_CHANNEL = config["force_sub_channel"]

async def check_subscription(client, user_id):
    try:
        print(f"Checking subscription for user {user_id} in channel {FORCE_SUB_CHANNEL}")
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
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

# Command handlers
@app.on_message(filters.command(["start"]))
async def start_command(client, message: Message):
    try:
        user_id = message.from_user.id
        user_mention = message.from_user.mention
        print(f"Start command received from user {user_id}")
        
        # Always reload config to get latest changes
        config = load_admin_config()
        print(f"Loaded config: {config}")  # Debug print
        
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
                InlineKeyboardButton("Join Channel 🔔", url=f"https://t.me/{config['force_sub_channel'].replace('@', '')}"),
                InlineKeyboardButton("Try Again 🔄", callback_data="check_sub")
            ]]
        else:
            if has_file_request:
                success = await send_requested_file(client, message.chat.id, file_id)
                if success:
                    user_requests.pop(user_id, None)
                    return
                else:
                    await message.reply("✅ Thanks For Using Me Bro!.")
                    return
            
            buttons = [[InlineKeyboardButton("✅ Already Joined", callback_data="already_joined")]]
        
        # Get the welcome caption from config and format it
        caption = config["welcome_caption"].format(user_mention=user_mention)
        print(f"Formatted caption: {caption}")  # Debug print
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        # Send welcome message with image if exists
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

@app.on_message(filters.command(["settings"]))
async def settings_command(client, message: Message):
    await show_settings(client, message)

@app.on_message(filters.command(["adminsettings"]))
async def admin_settings_command(client, message: Message):
    await show_admin_settings(client, message)

@app.on_message(filters.command(["contactus"]))
async def contact_command(client, message: Message):
    await show_contact_info(client, message)

@app.on_message(filters.command("setchannel") & filters.private)
async def set_channel_command(client, message: Message):
    user_id = message.from_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await message.reply("❌ Only admins can use this command!")
        return
        
    # Check if command has channel ID parameter
    command_parts = message.text.split()
    if len(command_parts) > 1:
        channel_id = command_parts[1].strip()
        
        # Try to process the channel ID
        try:
            # Try to convert to integer (should be a numeric ID)
            if channel_id.startswith('-100'):
                # Already in proper format
                pass
            elif channel_id.startswith('@'):
                await message.reply(
                    "⚠️ Please provide a channel ID, not a username.\n\n"
                    "To get a channel ID:\n"
                    "1. Forward a message from your channel to @username_to_id_bot\n"
                    "2. Use the channel ID that starts with -100..."
                )
                return
                
            # Verify the channel
            try:
                # Try to get the channel
                chat = await client.get_chat(channel_id)
                
                # Check if bot is member and admin
                bot_member = await client.get_chat_member(chat.id, "me")
                
                if not bot_member.can_post_messages:
                    await message.reply(
                        f"❌ Bot is not an admin in the channel '{chat.title}'!\n\n"
                        f"Please make the bot an admin with post messages permission."
                    )
                    return
                    
                # Channel verified, update config
                config = load_admin_config()
                config["storage_channel"] = int(chat.id)  # Save as integer
                
                if save_admin_config(config):
                    await message.reply(
                        f"✅ Storage channel updated successfully!\n\n"
                        f"Channel: {chat.title}\n"
                        f"ID: {chat.id}\n\n"
                        f"Bot has proper admin rights in this channel."
                    )
                else:
                    await message.reply("❌ Failed to save configuration!")
                
            except Exception as e:
                await message.reply(
                    f"❌ Failed to set channel: {str(e)}\n\n"
                    f"Make sure:\n"
                    f"1. The channel ID is correct\n"
                    f"2. The bot is a member of the channel\n"
                    f"3. The bot is an admin in the channel"
                )
                
        except Exception as e:
            await message.reply(
                f"❌ Invalid channel ID format: {str(e)}\n\n"
                f"Channel ID should be a numeric ID like: -100xxxxxxxxxx"
            )
    else:
        # No channel ID provided - show instructions
        current_config = load_admin_config()
        current_channel = current_config.get("storage_channel", "Not set")
        
        await message.reply(
            f"ℹ️ Current storage channel: `{current_channel}`\n\n"
            f"To set a new storage channel, use:\n"
            f"`/setchannel -100xxxxxxxxxx`\n\n"
            f"To get a channel ID:\n"
            f"1. Forward a message from your channel to @username_to_id_bot\n"
            f"2. Use the channel ID that starts with -100..."
        )

# Callback handlers
@app.on_callback_query(filters.regex("^(check_sub|already_joined|set_image|set_caption|toggle_bulk|close_settings|contact_info|about|admin_settings|back_to_settings|file_settings|channel_settings|bot_settings|toggle_auto|toggle_maintenance|set_storage|set_force_sub|set_file_size)$"))
async def handle_callbacks(client, callback_query):
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        if data == "back_to_settings":
            if is_admin(user_id):
                await show_admin_settings(client, callback_query.message)
            else:
                await show_settings(client, callback_query.message)
            return
        
        if data in ["check_sub", "already_joined"]:
            if data == "already_joined":
                await callback_query.answer("You're already subscribed! ✅", show_alert=True)
                return
                
            is_subscribed = await check_subscription(client, user_id)
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
        
        elif data == "contact_info":
            await show_contact_info(client, callback_query.message)
            
        elif data == "about":
            about_text = """
🤖 **About Ragnar File Store Bot**

This bot helps you store and share files easily:
• Upload any file to get a permanent link
• Access files through deep links
• Random emoji reactions on files
• Force subscribe feature
• Bulk mode for multiple files

👨‍💻 Developer: @ivartheboneles1
📢 Channel: @athithan_220

All Rights Reserved © @ragnarlothbrockV
"""
            await callback_query.message.edit_text(
                about_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")
                ]])
            )
                
        elif data == "close_settings":
            await callback_query.message.delete()
            
        elif data == "admin_settings":
            if is_admin(user_id):
                await show_admin_settings(client, callback_query.message)
            else:
                await callback_query.answer("❌ Only admins can access these settings!", show_alert=True)
                
        # New settings menu handlers
        elif data == "file_settings":
            if is_admin(user_id):
                await show_file_settings(client, callback_query.message)
            else:
                await callback_query.answer("❌ Only admins can access these settings!", show_alert=True)
                
        elif data == "channel_settings":
            if is_admin(user_id):
                await show_channel_settings(client, callback_query.message)
            else:
                await callback_query.answer("❌ Only admins can access these settings!", show_alert=True)
                
        elif data == "bot_settings":
            if is_admin(user_id):
                await show_bot_settings(client, callback_query.message)
            else:
                await callback_query.answer("❌ Only admins can access these settings!", show_alert=True)
            
        # Toggle handlers
        elif data == "toggle_bulk":
            if is_admin(user_id):
                await toggle_bulk_mode(client, callback_query)
            else:
                await callback_query.answer("❌ Only admins can toggle bulk mode!", show_alert=True)
                
        elif data == "toggle_auto":
            if is_admin(user_id):
                await toggle_auto_accept(client, callback_query)
            else:
                await callback_query.answer("❌ Only admins can toggle auto accept!", show_alert=True)
                
        elif data == "toggle_maintenance":
            if is_admin(user_id):
                await toggle_maintenance(client, callback_query)
            else:
                await callback_query.answer("❌ Only admins can toggle maintenance mode!", show_alert=True)
            
        # Settings input handlers
        else:
            if is_admin(user_id):
                user_states[user_id] = data
                instructions = {
                    "set_image": "📸 Please send the new welcome image (send as photo)",
                    "set_caption": "✏️ Please send the new welcome caption text",
                    "set_storage": "📦 Please send the storage channel ID",
                    "set_force_sub": "🔔 Please send the force subscribe channel username (with @) or ID",
                    "set_file_size": "📊 Please send the maximum file size in MB (1-2048)"
                }
                if data in instructions:
                    await callback_query.message.reply(instructions[data])
                    await callback_query.answer()
            else:
                await callback_query.answer("❌ Only admins can access these settings!", show_alert=True)
            
    except Exception as e:
        print(f"Callback error: {e}")
        await callback_query.answer("❌ Error processing request", show_alert=True)

# Handle responses to settings
@app.on_message(filters.private & ~filters.command(["settings", "adminsettings", "start"]))
async def handle_settings_input(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_states:
        # Check maintenance mode
        if is_maintenance_mode() and not is_admin(user_id):
            await message.reply(
                "🛠 Bot is currently under maintenance.\n"
                "Please try again later!"
            )
            return
            
        # Handle normal file uploads
        if message.document or message.video or message.audio:
            if not await check_subscription(client, user_id):
                config = load_admin_config()
                buttons = [[
                    InlineKeyboardButton("Join Channel 🔔", url=f"https://t.me/{config['force_sub_channel'].replace('@', '')}"),
                    InlineKeyboardButton("Try Again 🔄", callback_data="check_sub")
                ]]
                await message.reply(
                    "❌ You need to join our channel to use this bot.\n"
                    f"👉 {config['force_sub_channel']}\n\n"
                    "Join and click Try Again.",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
            
            # Check file size
            file_size = (
                message.document.file_size if message.document else
                message.video.file_size if message.video else
                message.audio.file_size if message.audio else 0
            ) / (1024 * 1024)  # Convert to MB
            
            config = load_admin_config()
            max_size = config.get("max_file_size", 2048)
            
            if file_size > max_size:
                await message.reply(f"❌ File too large! Maximum size allowed is {max_size}MB")
                return
            
            # Check if bulk mode is enabled for admins
            if is_admin(user_id) and is_bulk_mode_enabled():
                # Handle multiple files in bulk mode
                sent_msg = await handle_file(client, message, bulk_mode=True)
            else:
                # Handle single file normally
                sent_msg = await handle_file(client, message)
                
            if sent_msg:
                await sent_msg.react(get_random_reaction())
        return

    # Handle settings input
    if is_admin(user_id):
        state = user_states[user_id]
        handlers = {
            "set_image": handle_set_image,
            "set_caption": handle_set_caption,
            "set_storage": handle_set_storage,
            "set_force_sub": handle_set_force_sub,
            "set_file_size": handle_set_file_size
        }
        
        if state in handlers:
            await handlers[state](client, message)
            user_states.pop(user_id)  # Clear the state after handling

# Verify channel access at startup
async def verify_channels(app):
    try:
        # Verify storage channel
        print(f"Verifying storage channel: {STORAGE_CHANNEL}")
        try:
            storage_chat = await app.get_chat(STORAGE_CHANNEL)
            storage_member = await app.get_chat_member(STORAGE_CHANNEL, "me")
            
            print(f"✅ Storage channel confirmed: {storage_chat.title}")
            print(f"Bot permissions: {storage_member.status}")
            
            if not storage_member.can_post_messages:
                print(f"WARNING: Bot doesn't have post permission in storage channel: {storage_chat.title}")
            else:
                print(f"✅ Storage channel access OK: {storage_chat.title}")
        except Exception as e:
            print(f"❌ CRITICAL: Storage channel access failed: {str(e)}")
            print(f"Please make sure the bot is a member and admin of the storage channel ID: {STORAGE_CHANNEL}")
            print("Without storage channel access, file uploads will not work!")
        
        # Verify post channel if different
        if POST_CHANNEL != STORAGE_CHANNEL:
            try:
                post_chat = await app.get_chat(POST_CHANNEL)
                post_member = await app.get_chat_member(POST_CHANNEL, "me")
                
                if not post_member.can_post_messages:
                    print(f"WARNING: Bot doesn't have post permission in post channel: {post_chat.title}")
                else:
                    print(f"✅ Post channel access OK: {post_chat.title}")
            except Exception as e:
                print(f"❌ ERROR: Post channel access failed: {str(e)}")
    
        # Verify force subscribe channel
        if FORCE_SUB_CHANNEL:
            try:
                force_chat = await app.get_chat(FORCE_SUB_CHANNEL)
                force_member = await app.get_chat_member(FORCE_SUB_CHANNEL, "me")
                
                if not force_member.can_post_messages:
                    print(f"WARNING: Bot doesn't have post permission in force subscribe channel: {force_chat.title}")
                else:
                    print(f"✅ Force subscribe channel access OK: {force_chat.title}")
            except Exception as e:
                print(f"⚠️ Could not verify force subscribe channel: {e}")
                print("Users may not be able to subscribe to use the bot!")
        
    except Exception as e:
        print(f"ERROR verifying channels: {e}")
        print("Make sure the bot is an admin in all channels with post permission.")

# Main program
if __name__ == "__main__":
    # First check if bot token is valid
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ CRITICAL ERROR: Bot token not set!")
        print("Please update your bot token in config.py or set the BOT_TOKEN environment variable")
        print("To get a new bot token:")
        print("1. Go to @BotFather on Telegram")
        print("2. Send /newbot and follow the instructions")
        print("3. Copy the bot token and update config.py")
        exit(1)
        
    try:
        # Start bot
        print("Starting bot...")
        app.start()
        
        # Verify channels
        print("Verifying channel access...")
        app.loop.create_task(verify_channels(app))
        
        # Run bot until stopped
        print("Bot is running!")
        idle()
    except ValueError as e:
        if "bot token" in str(e).lower():
            print("❌ ERROR: Invalid bot token. Please get a new token from @BotFather")
            print(f"Details: {str(e)}")
        else:
            print(f"❌ ERROR: {str(e)}")
    except ConnectionError as e:
        print("❌ ERROR: Connection error - Failed to connect to Telegram servers")
        print(f"Details: {str(e)}")
        print("This may be due to an invalid bot token or network issues")
    except Exception as e:
        print(f"❌ ERROR starting bot: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        if "USER_DEACTIVATED" in str(e):
            print("\n❌ CRITICAL: Your bot has been deactivated!")
            print("You need to get a new bot token from @BotFather")
            print("1. Go to @BotFather on Telegram")
            print("2. Send /newbot and follow the instructions")
            print("3. Copy the new token and update config.py")
    finally:
        try:
            app.stop()
        except Exception as e:
            # This might fail if the app never started properly
            print(f"Note: Could not properly stop the bot: {str(e)}")
            pass
        print("Bot has been stopped.")
