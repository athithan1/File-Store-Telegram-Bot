from pyrogram import Client, filters
from pyrogram.types import Message
import os
import json

# Admin settings file
ADMIN_CONFIG_FILE = "config/admin_config.json"
DEFAULT_ADMIN_ID = 144590326  # Your admin ID

# Ensure config directory exists
os.makedirs("config", exist_ok=True)

# Load or create admin config
def load_admin_config():
    try:
        if os.path.exists(ADMIN_CONFIG_FILE):
            with open(ADMIN_CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading admin config: {e}")
    
    # Default config
    default_config = {
        "admins": [DEFAULT_ADMIN_ID],
        "force_sub_channel": "@athithan_220",
        "welcome_image": "photo_2025-04-17_14-20-26.jpg",
        "welcome_caption": """
👋 Hello {user_mention}!

Welcome to **Ragnar File Store Bot** 📁  
Just send me any media or file, and I'll give you a permanent download link 🔗

⚠️ Note: You must join our channel to use this bot!
👉 @athithan_220

All Rights Reserved © @ragnarlothbrockV
"""
    }
    
    # Save default config
    save_admin_config(default_config)
    return default_config

def save_admin_config(config):
    try:
        with open(ADMIN_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving admin config: {e}")
        return False

# Admin command handler
def admin_command(func):
    async def wrapper(client: Client, message: Message):
        config = load_admin_config()
        if message.from_user.id not in config["admins"]:
            await message.reply("❌ This command is only for admins!")
            return
        return await func(client, message, config)
    return wrapper

# Admin Commands
@admin_command
async def set_welcome_image(client: Client, message: Message, config):
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply("❌ Please reply to an image to set as welcome image!")
            return
            
        # Download and save the image
        photo = message.reply_to_message.photo.file_id
        path = await client.download_media(photo, file_name="welcome_image.jpg")
        
        # Update config
        config["welcome_image"] = path
        if save_admin_config(config):
            await message.reply("✅ Welcome image updated successfully!")
        else:
            await message.reply("❌ Failed to save configuration!")
            
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@admin_command
async def set_welcome_caption(client: Client, message: Message, config):
    try:
        # Get caption from reply or command args
        if message.reply_to_message and message.reply_to_message.text:
            new_caption = message.reply_to_message.text
        else:
            # Remove command from text
            command = message.text.split(None, 1)
            if len(command) < 2:
                await message.reply("❌ Please provide the welcome caption text!")
                return
            new_caption = command[1]
            
        # Update config
        config["welcome_caption"] = new_caption
        if save_admin_config(config):
            await message.reply("✅ Welcome caption updated successfully!")
        else:
            await message.reply("❌ Failed to save configuration!")
            
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@admin_command
async def set_force_channel(client: Client, message: Message, config):
    try:
        # Get channel username from command
        command = message.text.split(None, 1)
        if len(command) < 2:
            await message.reply("❌ Please provide the channel username (with @)!")
            return
            
        channel = command[1]
        if not channel.startswith("@"):
            channel = "@" + channel
            
        # Try to get channel info to verify it exists
        try:
            chat = await client.get_chat(channel)
            # Update config
            config["force_sub_channel"] = channel
            if save_admin_config(config):
                await message.reply(f"✅ Force subscribe channel updated to {channel}")
            else:
                await message.reply("❌ Failed to save configuration!")
        except Exception:
            await message.reply("❌ Invalid channel or bot is not admin in the channel!")
            
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@admin_command
async def add_admin(client: Client, message: Message, config):
    try:
        # Get user ID from command or reply
        user_id = None
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            command = message.text.split(None, 1)
            if len(command) < 2:
                await message.reply("❌ Please provide user ID or reply to a user!")
                return
            try:
                user_id = int(command[1])
            except ValueError:
                await message.reply("❌ Invalid user ID!")
                return
                
        # Add to admins list if not already there
        if user_id not in config["admins"]:
            config["admins"].append(user_id)
            if save_admin_config(config):
                await message.reply(f"✅ User {user_id} added as admin!")
            else:
                await message.reply("❌ Failed to save configuration!")
        else:
            await message.reply("⚠️ User is already an admin!")
            
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# Random emoji reactions for files
FILE_REACTIONS = ["👍", "🔥", "💫", "⭐️", "💎", "🎯", "🎬", "📁", "✨", "💝"]

def get_random_reaction():
    import random
    return random.choice(FILE_REACTIONS) 