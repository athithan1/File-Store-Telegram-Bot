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
        "storage_channel": -1001986592737,  # Match with config.py (numeric format)
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
        bulk_mode_status = "ON ✅" if config.get("bulk_mode", False) else "OFF ❌"
        auto_accept_status = "ON ✅" if config.get("auto_accept", True) else "OFF ❌"
        maintenance_status = "ON 🛠" if config.get("maintenance_mode", False) else "OFF ✅"
        
        buttons = [
            [InlineKeyboardButton("📂 File Settings", callback_data="file_settings")],
            [InlineKeyboardButton("📢 Channel Settings", callback_data="channel_settings")],
            [InlineKeyboardButton("⚙️ Bot Settings", callback_data="bot_settings")],
            [InlineKeyboardButton("👥 Admin Management", callback_data="admin_management")],
            [InlineKeyboardButton(f"📦 Bulk Mode: {bulk_mode_status}", callback_data="toggle_bulk")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")],
            [InlineKeyboardButton("❌ Close", callback_data="close_settings")]
        ]
        
        # If this message is a callback query result, edit the message
        if hasattr(message, 'edit_text'):
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
        else:
            await message.reply_text(
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
            if admin_user.username:
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
    
    storage_channel = config.get('storage_channel', 'Not set')
    
    # Format the channel display
    storage_display = str(storage_channel)
    
    await message.edit_text(
        "📢 **Channel Settings**\n\n"
        f"Storage Channel: `{storage_display}`\n"
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
                "Note: Make sure the bot is admin in the channel with post permission.\n"
                "Channel ID format must be: -100xxxxxxxxxx (numeric integer format)"
            )
            return
            
        channel_id = message.text.strip()
        
        # Verify channel and bot's admin status
        try:
            # First try to get the chat with the exact ID
            chat = None
            try:
                chat = await client.get_chat(channel_id)
            except Exception as e:
                # If that fails, try to parse the ID in different ways
                try:
                    # Try to convert username to ID
                    if channel_id.startswith('@'):
                        try:
                            chat = await client.get_chat(channel_id)
                        except Exception:
                            await message.reply(
                                "❌ Cannot get channel by username. For private channels, please use the numeric ID.\n"
                                "To get a channel ID, forward a message from the channel to @username_to_id_bot"
                            )
                            return
                    # Try different numeric formats
                    else:
                        # Try standard formatting
                        numeric_formats = [
                            channel_id,  # as provided
                            channel_id.replace('-100', '-1001'),  # -1001 format
                            channel_id.replace('-1001', '-100'),  # -100 format
                            f"-100{channel_id.lstrip('-')}"  # Add -100 prefix
                        ]
                        
                        for fmt in numeric_formats:
                            try:
                                chat = await client.get_chat(fmt)
                                if chat:
                                    channel_id = fmt
                                    break
                            except Exception:
                                continue
                                
                        if not chat:
                            raise Exception("Could not find channel with any ID format")
                except Exception as parse_error:
                    await message.reply(
                        f"❌ Failed to parse channel ID: {str(parse_error)}\n\n"
                        "Make sure the ID is in the correct format (usually -100xxxxxxxxxx)"
                    )
                    return
            
            if not chat:
                await message.reply("❌ Could not find the channel with the provided ID")
                return
                
            # Now check bot's permissions in the channel
            bot_member = await client.get_chat_member(chat.id, "me")
            
            # Verify the bot has proper admin status
            if bot_member.status != "administrator":
                await message.reply(
                    "❌ Bot is not an administrator in this channel!\n\n"
                    "Please add the bot as an admin with these permissions:\n"
                    "- Post Messages\n"
                    "- Edit Messages\n"
                    "- Delete Messages"
                )
                return
            
            # Check specific permissions
            can_post = False
            if hasattr(bot_member, 'privileges'):
                privileges = bot_member.privileges
                can_post = getattr(privileges, 'can_post_messages', False)
            else:
                can_post = getattr(bot_member, 'can_post_messages', False)
                
            if not can_post:
                await message.reply(
                    "❌ Bot doesn't have 'Post Messages' permission in this channel!\n\n"
                    "Please edit the bot's admin rights in the channel and enable 'Post Messages'."
                )
                return
                
            # Test posting a message to verify permissions
            try:
                test_msg = await client.send_message(
                    chat.id,
                    "✅ Test message - Bot permissions are working correctly! You can delete this message."
                )
                
                # Try to delete the message to verify delete permission
                try:
                    await test_msg.delete()
                except Exception:
                    await message.reply(
                        "⚠️ Warning: Bot can post messages but cannot delete them.\n"
                        "For full functionality, please enable 'Delete Messages' permission."
                    )
            except Exception as e:
                await message.reply(
                    f"❌ Bot has admin rights but cannot post messages: {str(e)}\n\n"
                    "Please check the channel settings and make sure:\n"
                    "1. The channel allows admin posts\n"
                    "2. The bot's 'Post Messages' permission is enabled\n"
                    "3. Try removing and re-adding the bot as admin"
                )
                return
                
            # Get the actual numeric ID and save it
            numeric_id = chat.id
            
            # Save the ID as an integer (not string)
            config = load_admin_config()
            config["storage_channel"] = numeric_id  # Store as integer
            
            if save_admin_config(config):
                # Update the global config
                import sys
                import os
                
                try:
                    # Try to update config.py for permanent storage
                    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.py")
                    
                    if os.path.exists(config_path):
                        with open(config_path, "r") as f:
                            config_content = f.read()
                            
                        # Replace the STORAGE_CHANNEL value
                        import re
                        new_content = re.sub(
                            r'STORAGE_CHANNEL\s*=\s*-?\d+',
                            f'STORAGE_CHANNEL = {numeric_id}',
                            config_content
                        )
                        
                        # Also replace POST_CHANNEL and DUMP_CHANNEL
                        new_content = re.sub(
                            r'POST_CHANNEL\s*=\s*-?\d+',
                            f'POST_CHANNEL = {numeric_id}',
                            new_content
                        )
                        
                        new_content = re.sub(
                            r'DUMP_CHANNEL\s*=\s*-?\d+',
                            f'DUMP_CHANNEL = {numeric_id}',
                            new_content
                        )
                        
                        # Write the updated content
                        with open(config_path, "w") as f:
                            f.write(new_content)
                            
                except Exception as e:
                    print(f"Warning: Couldn't update config.py: {e}")
                
                await message.reply(
                    f"✅ Storage channel updated successfully!\n\n"
                    f"Channel: {chat.title}\n"
                    f"ID: {numeric_id}\n\n"
                    f"✅ Bot has proper admin rights in this channel.\n"
                    f"✅ Test message was sent and deleted successfully.\n\n"
                    "You may need to restart the bot for changes to take effect."
                )
            else:
                await message.reply("❌ Failed to save configuration!")
                
        except Exception as e:
            error_message = str(e)
            await message.reply(
                f"❌ Invalid channel ID or bot is not a member!\n\n"
                f"Error: {error_message}\n\n"
                f"Make sure:\n"
                f"1. Channel ID is in correct format: -100xxxxxxxxxx (numeric integer)\n"
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
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        # Handle common callbacks first
        if data == "back_to_settings":
            if is_admin(user_id):
                await show_settings(client, callback_query.message)
            else:
                await callback_query.answer("❌ Only admin can access!", show_alert=True)
            await callback_query.answer()
            return
            
        elif data == "close_settings":
            await callback_query.message.delete()
            await callback_query.answer()
            return
            
        elif data == "contact_info":
            await show_contact_info(client, callback_query.message)
            await callback_query.answer()
            return
            
        # Handle admin-only callbacks
        elif data in ["admin_settings", "file_settings", "channel_settings", "bot_settings", 
                     "toggle_bulk", "toggle_auto", "toggle_maintenance", "admin_management"]:
            if is_admin(user_id):
                if data == "admin_settings":
                    await show_admin_settings(client, callback_query.message)
                elif data == "file_settings":
                    await show_file_settings(client, callback_query.message)
                elif data == "channel_settings":
                    await show_channel_settings(client, callback_query.message)
                elif data == "bot_settings":
                    await show_bot_settings(client, callback_query.message)
                elif data == "toggle_bulk":
                    await toggle_bulk_mode(client, callback_query)
                elif data == "toggle_auto":
                    await toggle_auto_accept(client, callback_query)
                elif data == "toggle_maintenance":
                    await toggle_maintenance(client, callback_query)
                elif data == "admin_management":
                    await show_admin_management(client, callback_query.message)
                await callback_query.answer()
            else:
                await callback_query.answer("❌ Only admin can access!", show_alert=True)
            return
            
        # Handle other settings-related callbacks
        elif data in ["set_image", "set_caption", "set_storage", "set_force_sub", "set_file_size", "set_admin"]:
            if is_admin(user_id):
                if data == "set_admin":
                    await callback_query.message.reply(
                        "👥 **Add New Admin**\n\n"
                        "Reply to a message from the user you want to make admin.\n\n"
                        "⚠️ **Warning**: The current admin will be replaced!"
                    )
                    await callback_query.answer()
                else:
                    instructions = {
                        "set_image": "📸 Please send the new welcome image (send as photo)",
                        "set_caption": "✏️ Please send the new welcome caption text",
                        "set_storage": "📦 Please send the storage channel ID",
                        "set_force_sub": "🔔 Please send the force subscribe channel username (with @) or ID",
                        "set_file_size": "📊 Please send the maximum file size in MB (1-2048)"
                    }
                    await callback_query.message.reply(instructions[data])
                    await callback_query.answer()
            else:
                await callback_query.answer("❌ Only admin can access!", show_alert=True)
            return
            
    except Exception as e:
        print(f"Error in callback handler: {e}")
        await callback_query.answer("❌ Error processing request", show_alert=True) 