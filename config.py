import os
from dotenv import load_dotenv

load_dotenv()

# Get environment variables with fallback to hardcoded values
API_ID = int(os.getenv("API_ID", "28794909"))
API_HASH = os.getenv("API_HASH", "b876f43d34fb6213728b30225e4f9005")

# Bot Token - Using the new token value
BOT_TOKEN = os.getenv("BOT_TOKEN", "7855865481:AAFjxBLS6w_ZixPrGuTMW784EyMSRcq_8rA")

# Validate credentials
if not all([API_ID, API_HASH, BOT_TOKEN]) or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("❌ ERROR: Please set a valid BOT_TOKEN in config.py or as an environment variable")
    print("Get a new token from @BotFather if your current one is deactivated")

# Channel IDs - Important: Telegram requires numeric IDs for channel access
# Using the exact ID from your forwarded message
STORAGE_CHANNEL = -1002605972463  # Storage channel ID (numeric format)
POST_CHANNEL = -1002605972463     # Post channel (same as storage)
DUMP_CHANNEL = -1002605972463     # Using storage channel as dump

# Force Subscribe Channel
FORCE_SUB_CHANNEL = "@athithan_220"

# Welcome Image and Messages
WELCOME_IMAGE = "photo_2025-04-17_14-20-26.jpg"
WELCOME_TEXT = """
👋 Hello {user_mention}!

Welcome to **Ragnar File Store Bot** 📁  
Just send me any media or file, and I'll give you a permanent download link 🔗

⚠️ Note: You must join our channel to use this bot!
👉 @athithan_220

All Rights Reserved © @ragnarlothbrockV
"""

# File upload success message
FILE_UPLOAD_TEXT = """
🎬 File Uploaded Successfully
📥 All Rights Reserved @ragnarlothbrockV
🔗 Join us 👉 @athithan_220
"""

# Debug mode
DEBUG = True

print("Bot Configuration:")
print(f"API_ID: {API_ID}")
print(f"BOT_TOKEN: {BOT_TOKEN}")
print(f"Channels: Storage={STORAGE_CHANNEL}, Post={POST_CHANNEL}")
