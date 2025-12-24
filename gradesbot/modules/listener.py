import os
import asyncio
import logging
from telethon import TelegramClient, events, errors
from config import API_ID, API_HASH, DOWNLOAD_DIR
from modules.database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradeListener:
    def __init__(self):
        if not API_ID or not API_HASH:
            logger.error("TELEGRAM_API_ID or TELEGRAM_API_HASH not found.")
            self.client = None
            return
        self.client = TelegramClient('userbot_session', int(API_ID), API_HASH)
        self.monitored_channels = []

    async def start(self):
        if not self.client:
            return
            
        logger.info("Starting Userbot Listener...")
        try:
            await self.client.start()
        except errors.FloodWaitError as e:
            logger.warning(f"FloodWaitError: Must wait for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            await self.client.start()
        except Exception as e:
            logger.error(f"Failed to start userbot: {e}")
            return
        
        # Load channels from DB
        channels_data = db.get_monitored_channels()
        self.monitored_channels = [int(c['channel_id']) for c in channels_data]
        
        @self.client.on(events.NewMessage(chats=self.monitored_channels))
        async def handler(event):
            if event.message.document:
                file_ext = event.message.file.ext.lower()
                if file_ext in ['.pdf', '.xlsx', '.csv']:
                    logger.info(f"Detected document: {event.message.file.name}")
                    try:
                        path = await event.download_media(file=DOWNLOAD_DIR)
                        logger.info(f"Downloaded to: {path}")
                        
                        # Trigger analysis engine
                        from modules.engine import process_file
                        await process_file(path, event.chat_id)
                    except errors.FloodWaitError as e:
                        logger.warning(f"FloodWait during download: waiting {e.seconds}s")
                        await asyncio.sleep(e.seconds)
                    except Exception as e:
                        logger.error(f"Error processing file: {e}")

        logger.info(f"Monitoring {len(self.monitored_channels)} channels.")
        try:
            await self.client.run_until_disconnected()
        except Exception as e:
            logger.error(f"Userbot disconnected with error: {e}")

if __name__ == "__main__":
    listener = GradeListener()
    asyncio.run(listener.start())
