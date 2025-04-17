from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os
import json

# Admin settings file
ADMIN_CONFIG_FILE = "config/admin_config.json"
DEFAULT_ADMIN = 7424730333  # Admin ID

# Ensure config directory exists
os.makedirs("config", exist_ok=True)

# Load or create admin config
def load_admin_config():
    try:
        if os.path.exists(ADMIN_CONFIG_FILE):
            with open(ADMIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading admin config: {e}")
    
    # Default config
    default_config = {
        "admins": DEFAULT_ADMIN,
        "force_sub_channel": "@athithan_220",
        "storage_channel": "-1002397387402",  # Updated to match the correct ID format
        "welcome_image": "welcome_image.jpg",
        "welcome_caption": "👋 Hello {user_mention}!\n\nWelcome to Ragnar File Store Bot 📁\nJust send me any media or file, and I'll give you a permanent download link 🔗\n\n⚠️ Note: You must join our channel to use this bot!\n👉 @athithan_220\n\nAll Rights Reserved © @ragnarlothbrockV",
        "bulk_mode": False,
        "auto_accept": True,  # Auto accept new files
        "maintenance_mode": False,  # Maintenance mode
        "max_file_size": 4096  # Max file size in MB (4GB)
    }
    
    # Save default config
    save_admin_config(default_config)
    return default_config

def save_admin_config(config):
    try:
        with open(ADMIN_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving admin config: {e}")
        return False

def is_admin(user_id):
    try:
        config = load_admin_config()
        # Force user_id to be an integer
        user_id = int(user_id) if user_id else 0
        admin_id = int(config["admins"]) if config.get("admins") else DEFAULT_ADMIN
        
        # Debug print
        print(f"Checking admin: user_id={user_id}, admin_id={admin_id}, result={user_id == admin_id}")
        
        return user_id == admin_id
    except Exception as e:
        print(f"Error checking admin status: {e}")
        # Fallback to default admin
        return int(user_id) == DEFAULT_ADMIN

# Settings menu for regular users
async def show_settings(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("📞 Contact Us", callback_data="contact_info")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("❌ Close", callback_data="close_settings")]
    ]
    
    # Add admin settings button if user is admin
    if is_admin(message.from_user.id):
        buttons.insert(0, [InlineKeyboardButton("⚙️ Admin Settings", callback_data="admin_settings")])
    
    await message.reply(
        "⚙️ **Bot Settings & Information**\n\n"
        "Welcome to the settings panel. Choose an option:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Admin Settings Menu
async def show_admin_settings(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Only admins can access admin settings!")
        return

    config = load_admin_config()
    bulk_mode_status = "ON ✅" if config.get("bulk_mode", False) else "OFF ❌"
    auto_accept_status = "ON ✅" if config.get("auto_accept", True) else "OFF ❌"
    maintenance_status = "ON 🛠" if config.get("maintenance_mode", False) else "OFF ✅"

    buttons = [
        # File Settings
        [InlineKeyboardButton("📂 File Settings", callback_data="file_settings")],
        
        # Channel Settings
        [InlineKeyboardButton("📢 Channel Settings", callback_data="channel_settings")],
        
        # Bot Settings
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data="bot_settings")],

        # Admin Management
        [InlineKeyboardButton("👥 Admin Management", callback_data="admin_management")],
        
        # Quick toggles
        [
            InlineKeyboardButton(f"📦 Bulk: {bulk_mode_status}", callback_data="toggle_bulk"),
            InlineKeyboardButton(f"🔄 Auto: {auto_accept_status}", callback_data="toggle_auto")
        ],
        [InlineKeyboardButton(f"🛠 Maintenance: {maintenance_status}", callback_data="toggle_maintenance")],
        
        # Back and Close buttons
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_to_settings"),
            InlineKeyboardButton("❌ Close", callback_data="close_settings")
        ]
    ]
    
    try:
        if isinstance(message, Message):
            await message.reply(
                "⚙️ **Admin Settings Panel**\n\n"
                "**Current Settings:**\n"
                f"• Bulk Mode: {bulk_mode_status}\n"
                f"• Auto Accept: {auto_accept_status}\n"
                f"• Maintenance: {maintenance_status}\n"
                f"• Max File Size: {config.get('max_file_size', 4096)}MB\n\n"
                "Choose a category to modify settings:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await message.edit_text(
                "⚙️ **Admin Settings Panel**\n\n"
                "**Current Settings:**\n"
                f"• Bulk Mode: {bulk_mode_status}\n"
                f"• Auto Accept: {auto_accept_status}\n"
                f"• Maintenance: {maintenance_status}\n"
                f"• Max File Size: {config.get('max_file_size', 4096)}MB\n\n"
                "Choose a category to modify settings:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        print(f"Error in show_admin_settings: {e}")
        if isinstance(message, Message):
            await message.reply("❌ Error showing admin settings")
        else:
            await message.edit_text("❌ Error showing admin settings")

async def show_admin_management(client: Client, message: Message):
    try:
        user_id = message.from_user.id if hasattr(message, 'from_user') else 0
        
        # Only allow admin to access this
        if not is_admin(user_id):
            try:
                # Try to answer callback query if it exists
                if hasattr(message, 'callback_query'):
                    await message.callback_query.answer("❌ Only admin can access!", show_alert=True)
                    return
            except:
                pass
            
            # Otherwise send a reply
            await message.reply("❌ Only admin can access!")
            return
                
        config = load_admin_config()
        current_admin = config["admins"]
        
        buttons = [
            [InlineKeyboardButton("➕ Set New Admin", callback_data="set_admin")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_settings")],
            [InlineKeyboardButton("❌ Close", callback_data="close_settings")]
        ]
        
        admin_info = "👥 **Admin Management**\n\n"
        admin_info += "**Current Admin:**\n"
        try:
            admin_user = await client.get_users(current_admin)
            admin_info += f"• ID: `{admin_user.id}`\n"
            admin_info += f"• Name: {admin_user.first_name}\n"
            admin_info += f"• Username: @{admin_user.username}\n"
        except:
            admin_info += f"• ID: `{current_admin}`\n"
        
        admin_info += "\nClick 'Set New Admin' to change the admin."
        
        # Check if message has edit_text method
        if hasattr(message, 'edit_text'):
            await message.edit_text(admin_info, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            # Send a new message
            await message.reply(admin_info, reply_markup=InlineKeyboardMarkup(buttons))
            
    except Exception as e:
        print(f"Error in show_admin_management: {str(e)}")
        if hasattr(message, 'edit_text'):
            await message.edit_text(f"❌ Error showing admin management: {str(e)}")
        else:
            await message.reply(f"❌ Error showing admin management: {str(e)}")

async def handle_set_admin(client: Client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply("❌ Only current admin can set new admin!")
            return
            
        if not message.reply_to_message:
            await message.reply(
                "❌ Please reply to the user's message to make them admin!\n\n"
                "Note: The current admin will be replaced with the new admin."
            )
            return
            
        new_admin_id = message.reply_to_message.from_user.id
        new_admin_name = message.reply_to_message.from_user.first_name
        
        config = load_admin_config()
        if new_admin_id == config["admins"]:
            await message.reply("⚠️ This user is already the admin!")
            return
            
        # Update admin
        config["admins"] = new_admin_id
        if save_admin_config(config):
            await message.reply(
                f"✅ New admin set successfully!\n\n"
                f"New Admin: {new_admin_name}\n"
                f"ID: `{new_admin_id}`\n\n"
                "⚠️ Note: The bot will now only respond to the new admin's commands.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Settings", callback_data="admin_management")
                ]])
            )
        else:
            await message.reply("❌ Failed to save configuration!")
            
    except Exception as e:
        print(f"Error in handle_set_admin: {str(e)}")
        await message.reply(f"❌ Error: {str(e)}")

# Show specific settings menus
async def show_file_settings(client: Client, message: Message):
    config = load_admin_config()
    buttons = [
        [InlineKeyboardButton("📸 Set Welcome Image", callback_data="set_image")],
        [InlineKeyboardButton("✏️ Set Welcome Caption", callback_data="set_caption")],
        [InlineKeyboardButton("📊 Set Max File Size", callback_data="set_file_size")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_settings")],
        [InlineKeyboardButton("❌ Close", callback_data="close_settings")]
    ]
    
    # Show current settings
    settings_text = "📂 **File Settings**\n\n"
    settings_text += f"**Current Settings:**\n"
    settings_text += f"• Max File Size: {config.get('max_file_size', 4096)}MB\n"
    settings_text += f"• Welcome Image: {'✅ Set' if os.path.exists(config['welcome_image']) else '❌ Not Set'}\n"
    settings_text += f"\n**Current Caption:**\n{config['welcome_caption']}\n\n"
    settings_text += "Choose an option to modify:"
    
    # If welcome image exists, send it with settings
    if os.path.exists(config['welcome_image']):
        try:
            await message.reply_photo(
                photo=config['welcome_image'],
                caption=settings_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            # Delete the original message
            try:
                await message.delete()
            except:
                pass
        except Exception as e:
            print(f"Error sending welcome image: {e}")
            await message.edit_text(settings_text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.edit_text(settings_text, reply_markup=InlineKeyboardMarkup(buttons))

async def show_channel_settings(client: Client, message: Message):
    config = load_admin_config()
    buttons = [
        [InlineKeyboardButton("📦 Set Storage Channel", callback_data="set_storage")],
        [InlineKeyboardButton("🔔 Set Force Sub Channel", callback_data="set_force_sub")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_settings")],
        [InlineKeyboardButton("❌ Close", callback_data="close_settings")]
    ]
    
    await message.edit_text(
        "📢 **Channel Settings**\n\n"
        f"Storage Channel: {config.get('storage_channel', 'Not set')}\n"
        f"Force Sub Channel: {config.get('force_sub_channel', 'Not set')}\n\n"
        "Choose a channel to modify:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_bot_settings(client: Client, message: Message):
    config = load_admin_config()
    auto_accept = "ON ✅" if config.get("auto_accept", True) else "OFF ❌"
    maintenance = "ON 🛠" if config.get("maintenance_mode", False) else "OFF ✅"
    
    buttons = [
        [InlineKeyboardButton(f"🔄 Auto Accept: {auto_accept}", callback_data="toggle_auto")],
        [InlineKeyboardButton(f"🛠 Maintenance: {maintenance}", callback_data="toggle_maintenance")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_settings")],
        [InlineKeyboardButton("❌ Close", callback_data="close_settings")]
    ]
    
    await message.edit_text(
        "⚙️ **Bot Settings**\n\n"
        f"• Auto Accept: {auto_accept}\n"
        f"• Maintenance Mode: {maintenance}\n\n"
        "Choose an option to toggle:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Settings handlers
async def handle_set_image(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.reply("❌ Only admins can change the welcome image!")
            return
            
        if not message.photo:
            await message.reply(
                "❌ Please send an image to set as welcome image!\n\n"
                "Note: Just send the image directly, no need to reply."
            )
            return
            
        # Set path for the new image
        path = "welcome_image.jpg"
        
        # First make sure we can access the file
        file_id = message.photo.file_id if hasattr(message.photo, 'file_id') else None
        
        if not file_id and isinstance(message.photo, list) and len(message.photo) > 0:
            # Get the largest photo (last in the list)
            file_id = message.photo[-1].file_id
            
        if not file_id:
            await message.reply("❌ Could not get photo file ID. Please try again.")
            return
            
        # Download the image using file_id
        try:
            file_path = await message.download()
            if file_path and os.path.exists(file_path):
                # Copy to our destination
                import shutil
                shutil.copy(file_path, path)
                os.remove(file_path)  # Remove the temp file
            else:
                await message.reply("❌ Failed to download image. Please try again.")
                return
        except Exception as e:
            print(f"Download error: {str(e)}")
            await message.reply(f"❌ Download error: {str(e)}")
            return
            
        # Update config
        config = load_admin_config()
        old_image = config["welcome_image"]
        config["welcome_image"] = path
        
        if save_admin_config(config):
            # Delete old image if different
            if old_image != path and os.path.exists(old_image) and old_image != "welcome_image.jpg":
                try:
                    os.remove(old_image)
                except Exception as e:
                    print(f"Error removing old image: {e}")
            
            # Show success message with the new image
            try:
                with open(path, "rb") as photo_file:
                    await message.reply_photo(
                        photo=photo_file,
                        caption="✅ Welcome image updated successfully!\n\nThis is how it will look when users start the bot.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back to Settings", callback_data="file_settings")
                        ]])
                    )
            except Exception as e:
                print(f"Reply error: {str(e)}")
                await message.reply(
                    "✅ Welcome image updated successfully!\n\n"
                    "⚠️ Note: Preview couldn't be sent, but the image has been saved.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Settings", callback_data="file_settings")
                    ]])
                )
        else:
            await message.reply("❌ Failed to save configuration!")
            
    except Exception as e:
        print(f"Error in handle_set_image: {str(e)}")
        await message.reply(f"❌ Error: {str(e)}")

async def handle_set_caption(client: Client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply("❌ Only admins can change the welcome caption!")
            return
            
        if not message.text:
            await message.reply("❌ Please send the new welcome caption text!")
            return
            
        config = load_admin_config()
        # Remove the command if it's part of the message
        new_caption = message.text
        if new_caption.startswith('/'):
            new_caption = ' '.join(message.text.split()[1:])
            
        if not new_caption:
            await message.reply("❌ Please provide the new caption text!")
            return
            
        config["welcome_caption"] = new_caption
        if save_admin_config(config):
            # Show preview of new caption
            preview_text = "✅ Welcome caption updated successfully!\n\n"
            preview_text += "**Preview of new welcome message:**\n"
            preview_text += f"{new_caption}"
            
            # If we have a welcome image, show it with the new caption
            if os.path.exists(config["welcome_image"]):
                await message.reply_photo(
                    photo=config["welcome_image"],
                    caption=preview_text,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Settings", callback_data="file_settings")
                    ]])
                )
            else:
                await message.reply(
                    preview_text,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Settings", callback_data="file_settings")
                    ]])
                )
        else:
            await message.reply("❌ Failed to save configuration!")
            
    except Exception as e:
        print(f"Error in handle_set_caption: {str(e)}")
        await message.reply(f"❌ Error: {str(e)}")

async def handle_set_storage(client: Client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply("❌ Only admins can change the storage channel!")
            return
            
        if not message.text:
            await message.reply(
                "❌ Please send the storage channel ID!\n\n"
                "Note: Make sure the bot is admin in the channel with post permission."
            )
            return
            
        channel_id = message.text.strip()
        
        # Verify channel and bot's admin status
        try:
            chat = await client.get_chat(channel_id)
            bot_member = await client.get_chat_member(chat.id, "me")
            
            # Check permissions
            if not bot_member.can_post_messages:
                await message.reply("❌ Bot needs to be admin in the channel with post permission!")
                return
                
            # Get the actual numeric ID
            numeric_id = chat.id
            
            # Save the ID as a string
            config = load_admin_config()
            config["storage_channel"] = str(numeric_id)
            
            if save_admin_config(config):
                await message.reply(
                    f"✅ Storage channel updated successfully!\n\n"
                    f"Channel: {chat.title}\n"
                    f"ID: {numeric_id}\n\n"
                    f"The bot has proper admin rights in this channel."
                )
            else:
                await message.reply("❌ Failed to save configuration!")
                
        except Exception as e:
            error_message = str(e)
            await message.reply(
                f"❌ Invalid channel ID or bot is not a member!\n\n"
                f"Error: {error_message}\n\n"
                f"Make sure:\n"
                f"1. Channel ID is correct format: -100xxxxxxxxxx\n"
                f"2. Bot is added to channel\n"
                f"3. Bot is admin in channel with post permission"
            )
            return
            
    except Exception as e:
        print(f"Error in handle_set_storage: {str(e)}")
        await message.reply(f"❌ Error: {str(e)}")

async def handle_set_force_sub(client: Client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply("❌ Only admins can change the force subscribe channel!")
            return
            
        if not message.text:
            await message.reply(
                "❌ Please send the channel username (with @) or ID!\n\n"
                "Note: Make sure the bot is admin in the channel."
            )
            return
            
        channel = message.text.strip()
        
        # Verify channel
        try:
            chat = await client.get_chat(channel)
            bot_member = await client.get_chat_member(chat.id, "me")
            if not bot_member.can_post_messages:
                await message.reply("❌ Bot needs to be admin in the channel!")
                return
        except Exception as e:
            await message.reply(
                f"❌ Invalid channel or bot is not a member!\n\n"
                f"Error: {str(e)}\n\n"
                f"Make sure:\n"
                f"1. Channel username/ID is correct\n"
                f"2. Bot is added to channel\n"
                f"3. Bot is admin in channel"
            )
            return
            
        config = load_admin_config()
        # Always save ID as string to prevent issues
        config["force_sub_channel"] = f"@{chat.username}" if chat.username else str(chat.id)
        if save_admin_config(config):
            await message.reply(
                f"✅ Force subscribe channel updated successfully!\n\n"
                f"Channel: {chat.title}\n"
                f"Username: {f'@{chat.username}' if chat.username else 'Private'}\n"
                f"ID: {chat.id}"
            )
        else:
            await message.reply("❌ Failed to save configuration!")
            
    except Exception as e:
        print(f"Error in handle_set_force_sub: {str(e)}")
        await message.reply(f"❌ Error: {str(e)}")

async def handle_set_file_size(client: Client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply("❌ Only admins can change the max file size!")
            return
            
        if not message.text:
            await message.reply(
                "❌ Please send the maximum file size in MB!\n\n"
                "Example: 4096 for 4GB"
            )
            return
            
        try:
            size = int(message.text.strip())
            if size < 1 or size > 4096:
                await message.reply("❌ File size must be between 1MB and 4096MB (4GB)!")
                return
        except ValueError:
            await message.reply("❌ Please send a valid number!")
            return
            
        config = load_admin_config()
        config["max_file_size"] = size
        if save_admin_config(config):
            await message.reply(f"✅ Maximum file size updated to {size}MB!")
        else:
            await message.reply("❌ Failed to save configuration!")
            
    except Exception as e:
        print(f"Error in handle_set_file_size: {str(e)}")
        await message.reply(f"❌ Error: {str(e)}")

# Toggle functions
async def toggle_bulk_mode(client: Client, callback_query):
    try:
        user_id = callback_query.from_user.id
        if not is_admin(user_id):
            await callback_query.answer("❌ Only admin can access!", show_alert=True)
            return False
            
        config = load_admin_config()
        config["bulk_mode"] = not config.get("bulk_mode", False)
        
        if save_admin_config(config):
            # Update the UI
            message = callback_query.message
            bulk_status = "ON ✅" if config["bulk_mode"] else "OFF ❌"
            
            # Update the button text directly
            buttons = message.reply_markup.inline_keyboard
            for row in buttons:
                for button in row:
                    if "Bulk:" in button.text:
                        button.text = f"📦 Bulk: {bulk_status}"
                        break
            
            await message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            await callback_query.answer(f"Bulk mode {'enabled' if config['bulk_mode'] else 'disabled'}")
            return True
        else:
            await callback_query.answer("❌ Failed to save config", show_alert=True)
            return False
    except Exception as e:
        print(f"Error in toggle_bulk_mode: {e}")
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)
        return False

async def toggle_auto_accept(client: Client, callback_query):
    try:
        user_id = callback_query.from_user.id
        if not is_admin(user_id):
            await callback_query.answer("❌ Only admin can access!", show_alert=True)
            return
            
        config = load_admin_config()
        config["auto_accept"] = not config.get("auto_accept", True)
        save_admin_config(config)
        
        # Show updated bot settings
        await show_bot_settings(client, callback_query.message)
        await callback_query.answer(f"Auto accept {'enabled' if config['auto_accept'] else 'disabled'}")
    except Exception as e:
        print(f"Error in toggle_auto_accept: {e}")
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

async def toggle_maintenance(client: Client, callback_query):
    try:
        user_id = callback_query.from_user.id
        if not is_admin(user_id):
            await callback_query.answer("❌ Only admin can access!", show_alert=True)
            return
            
        config = load_admin_config()
        config["maintenance_mode"] = not config.get("maintenance_mode", False)
        save_admin_config(config)
        
        # Show updated bot settings
        await show_bot_settings(client, callback_query.message)
        await callback_query.answer(f"Maintenance mode {'enabled' if config['maintenance_mode'] else 'disabled'}")
    except Exception as e:
        print(f"Error in toggle_maintenance: {e}")
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

# Contact Us handler
async def show_contact_info(client: Client, message: Message):
    contact_text = """
📞 **Contact Information**

For any queries or support, contact:
👤 Admin: @ivartheboneles1
📢 Channel: @athithan_220

All Rights Reserved © @ragnarlothbrockV
"""
    await message.reply(contact_text)

# Random emoji reactions for files
FILE_REACTIONS = ["👍", "🔥", "💫", "⭐️", "💎", "🎯", "🎬", "📁", "✨", "💝"]

def get_random_reaction():
    import random
    return random.choice(FILE_REACTIONS)

# Get bulk mode status
def is_bulk_mode_enabled():
    config = load_admin_config()
    return config.get("bulk_mode", False)

# Get maintenance mode status
def is_maintenance_mode():
    config = load_admin_config()
    return config.get("maintenance_mode", False)

# Get auto accept status
def is_auto_accept_enabled():
    config = load_admin_config()
    return config.get("auto_accept", True)

# Completely rewritten callback handler
@Client.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    message = callback_query.message
    
    print(f"Callback received: {data} from user {user_id}")
    
    try:
        # Handle non-admin actions first (available to everyone)
        if data == "back_to_settings":
            print(f"Processing back button for user {user_id}")
            await show_settings(client, message)
            await callback_query.answer()
            return
            
        elif data == "close_settings":
            print(f"Processing close button for user {user_id}")
            await message.delete()
            await callback_query.answer()
            return
            
        elif data == "contact_info":
            print(f"Processing contact info for user {user_id}")
            await show_contact_info(client, message)
            await callback_query.answer()
            return
            
        # Now check admin status for admin-only actions
        user_is_admin = is_admin(user_id)
        print(f"User {user_id} is admin: {user_is_admin}")
        
        # If not admin, deny access to all other actions
        if not user_is_admin:
            print(f"Denying access to {data} for non-admin user {user_id}")
            await callback_query.answer("❌ Only admins can access this feature!", show_alert=True)
            return
        
        # Handle admin-only actions
        if data == "admin_settings":
            await show_admin_settings(client, message)
                
        elif data == "file_settings":
            await show_file_settings(client, message)
                
        elif data == "channel_settings":
            await show_channel_settings(client, message)
                
        elif data == "bot_settings":
            await show_bot_settings(client, message)
                
        elif data == "admin_management":
            await show_admin_management(client, message)
                
        elif data == "toggle_bulk":
            # Toggle bulk mode
            config = load_admin_config()
            config["bulk_mode"] = not config.get("bulk_mode", False)
            save_admin_config(config)
            # Refresh the admin settings
            await show_admin_settings(client, message)
            await callback_query.answer(f"Bulk mode {'enabled' if config['bulk_mode'] else 'disabled'}")
                
        elif data == "toggle_auto":
            # Toggle auto accept
            config = load_admin_config()
            config["auto_accept"] = not config.get("auto_accept", True)
            save_admin_config(config)
            # Refresh the bot settings
            await show_bot_settings(client, message)
            await callback_query.answer(f"Auto accept {'enabled' if config['auto_accept'] else 'disabled'}")
                
        elif data == "toggle_maintenance":
            # Toggle maintenance mode
            config = load_admin_config()
            config["maintenance_mode"] = not config.get("maintenance_mode", False)
            save_admin_config(config)
            # Refresh the bot settings
            await show_bot_settings(client, message)
            await callback_query.answer(f"Maintenance mode {'enabled' if config['maintenance_mode'] else 'disabled'}")
                
        elif data == "set_admin":
            await message.reply(
                "👥 To set a new admin:\n\n"
                "1. Forward a message from the user you want to make admin\n"
                "2. Reply to that forwarded message with /setadmin\n\n"
                "⚠️ Note: The current admin will be replaced with the new admin."
            )
        
        else:
            # Handle any other admin callbacks
            await callback_query.answer()
                
    except Exception as e:
        print(f"Error in callback handler: {str(e)}")
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True) 