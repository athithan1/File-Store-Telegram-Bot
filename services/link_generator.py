from base64 import urlsafe_b64encode, urlsafe_b64decode

def encode_file_id(message_id: int) -> str:
    """Encode message ID to safe string"""
    return urlsafe_b64encode(str(message_id).encode()).decode().strip('=')

def decode_file_id(encoded_id: str) -> int:
    """Decode message ID from encoded string"""
    try:
        # Add padding back
        padding = 4 - (len(encoded_id) % 4)
        if padding != 4:
            encoded_id += '=' * padding
            
        decoded = urlsafe_b64decode(encoded_id).decode()
        return int(decoded)
    except:
        raise ValueError("Invalid file ID")

def generate_share_link(bot_username: str, message_id: int) -> str:
    encoded_id = encode_file_id(message_id)
    return f"https://t.me/{bot_username}?start={encoded_id}"
