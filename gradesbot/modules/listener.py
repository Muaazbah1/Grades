import os
import asyncio
from telethon import TelegramClient, events
from config import API_ID, API_HASH, DOWNLOAD_DIR
from modules.database import db
# Note: process_file will be imported from engine once implemented

class GradeListener:
    def __init__(self):
        self.client = TelegramClient('userbot_session', API_ID, API_HASH)
        self.monitored_channels = []

    async def start(self):
        print("Starting Userbot Listener...")
        await self.client.start()
        
        # Load channels from DB
        channels_data = db.get_monitored_channels()
        self.monitored_channels = [c['channel_id'] for c in channels_data]
        
        @self.client.on(events.NewMessage(chats=self.monitored_channels))
        async def handler(event):
            if event.message.document:
                file_ext = event.message.file.ext.lower()
                if file_ext in ['.pdf', '.xlsx', '.csv']:
                    print(f"Detected document: {event.message.file.name}")
                    path = await event.download_media(file=DOWNLOAD_DIR)
                    print(f"Downloaded to: {path}")
                    
                    # Trigger analysis engine (to be implemented)
                    from modules.engine import process_file
                    try:
                        await process_file(path, event.chat_id)
                    except Exception as e:
                        print(f"Error processing file: {e}")

        print(f"Monitoring {len(self.monitored_channels)} channels.")
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    listener = GradeListener()
    asyncio.run(listener.start())
