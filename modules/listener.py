import os
import asyncio
import logging
from telethon import TelegramClient, events, errors
from config import API_ID, API_HASH, DOWNLOAD_DIR
from modules.database import db

# Configure logging
logger = logging.getLogger(__name__)

class GradeListener:
    def __init__(self):
        self.api_id = API_ID
        self.api_hash = API_HASH
        self.client = None
        self.monitored_channels = []

    async def start(self):
        """Starts the Telegram Userbot client within the current event loop."""
        if not self.api_id or not self.api_hash:
            logger.error("TELEGRAM_API_ID or TELEGRAM_API_HASH not found.")
            return

        # Initialize client inside the running loop to avoid loop mismatch
        logger.info("Initializing Userbot Client...")
        self.client = TelegramClient('userbot_session', int(self.api_id), self.api_hash)
            
        logger.info("Connecting Userbot...")
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
        try:
            channels_data = db.get_monitored_channels()
            self.monitored_channels = [int(c['channel_id']) for c in channels_data]
        except Exception as e:
            logger.error(f"Failed to load monitored channels: {e}")
            self.monitored_channels = []
        
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

        logger.info(f"Userbot is now monitoring {len(self.monitored_channels)} channels.")
        try:
            await self.client.run_until_disconnected()
        except Exception as e:
            logger.error(f"Userbot disconnected with error: {e}")
