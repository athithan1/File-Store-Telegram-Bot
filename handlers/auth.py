from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_SUB_CHANNEL

async def check_subscription(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return True
    except Exception:
        return False

def get_subscribe_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}")]
    ])
