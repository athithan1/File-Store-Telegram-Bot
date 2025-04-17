import os
from dotenv import load_dotenv

load_dotenv()

# Get environment variables with fallback to hardcoded values
API_ID = int(os.getenv("API_ID", "28794909"))
API_HASH = os.getenv("API_HASH", "b876f43d34fb6213728b30225e4f9005")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7150003784:AAEWiVw70N0DFNUgyM-B-b-mjCZrNwN-tAk")

# Validate credentials
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("Missing required API credentials")

# Channel IDs from JSON dump
STORAGE_CHANNEL = -1002397387402  # Storage channel ID from JSON
POST_CHANNEL = -1002176704916     # Post channel
DUMP_CHANNEL = -1002397387402     # Using storage channel as dump

# Force Subscribe Channel
FORCE_SUB_CHANNEL = "@athithan_220"

# Welcome Image and Messages
WELCOME_IMAGE = "photo_2025-04-17_14-20-26.jpg"  # Updated to your image path
WELCOME_TEXT = """
Welcome to FileStore Bot🌟
Made by @athithan_220

Please join our channel to use this bot!
"""

# Debug mode
DEBUG = True

print("Bot Configuration:")
print(f"API_ID: {API_ID}")
print(f"Channels: Storage={STORAGE_CHANNEL}, Post={POST_CHANNEL}")
