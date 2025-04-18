from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
import time

# Load FORCE_SUB_CHANNEL from config or admin_handler
try:
    # Try to import from config first
    from config import FORCE_SUB_CHANNEL
except ImportError:
    # If not in config, import from admin_handler
    try:
        from handlers.admin_handler import load_admin_config
        config = load_admin_config()
        FORCE_SUB_CHANNEL = config["force_sub_channel"]
    except Exception as e:
        print(f"Error loading FORCE_SUB_CHANNEL: {e}")
        FORCE_SUB_CHANNEL = "@athithan_220"  # Default fallback

async def check_subscription(client, user_id):
    try:
        print(f"Checking subscription for user {user_id} in channel {FORCE_SUB_CHANNEL}")
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        print(f"Member status: {member.status}")
        
        # Check if user is a member
        allowed_statuses = [
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER
        ]
        
        return member.status in allowed_statuses
    except Exception as e:
        print(f"Subscription check error: {e}")
        return False

def get_subscribe_markup():
    # Get channel username without @ if it starts with @
    channel = FORCE_SUB_CHANNEL
    if channel.startswith('@'):
        channel = channel[1:]
    
    # Create invite link based on username
    url = f"https://t.me/{channel}"
    
    buttons = [
        [InlineKeyboardButton("📢 Join Channel", url=url)],
        [InlineKeyboardButton("🔄 Refresh", callback_data="check_subscription")]
    ]
    
    return InlineKeyboardMarkup(buttons)
