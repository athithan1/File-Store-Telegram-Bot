from pyrogram import Client, filters, idle
from config import API_ID, API_HASH, BOT_TOKEN, STORAGE_CHANNEL, POST_CHANNEL
from handlers.file_handler import handle_file
from services.link_generator import decode_file_id

print(f"Initializing bot with API_ID: {API_ID}")
app = Client(
    "mybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    try:
        # Check if there's a file ID parameter
        command_parts = message.text.split()
        if len(command_parts) > 1:
            # Decode file ID
            encoded_id = command_parts[1]
            file_id = decode_file_id(encoded_id)
            
            # Forward the file from storage to user
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=STORAGE_CHANNEL,
                message_id=file_id
            )
        else:
            await message.reply("👋 Send me any file to get a shareable link!")
    except Exception as e:
        print(f"Error in start command: {e}")
        await message.reply("❌ Failed to retrieve file")

@app.on_message(filters.document | filters.video | filters.audio)
async def file_receive(client, message):
    await handle_file(client, message)

async def main():
    async with app:
        print("Bot is starting...")
        try:
            # Verify channel access
            storage = await app.get_chat(STORAGE_CHANNEL)
            post = await app.get_chat(POST_CHANNEL)
            print(f"Bot started successfully!")
            print(f"Storage channel: {storage.title}")
            print(f"Post channel: {post.title}")
            print("Bot is running... Press Ctrl+C to stop")
            
            # Keep the bot running
            await idle()
            
        except Exception as e:
            print(f"Error during startup: {str(e)}")
            raise e

if __name__ == "__main__":
    app.run(main())
