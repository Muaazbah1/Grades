import os
import sys

# --- CRITICAL PATH FIX ---
# This must be at the very top before any other imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# -------------------------

import asyncio
import threading
import logging
from telethon import errors
from modules.listener import GradeListener
from modules.notifier import bot
from modules.dashboard import app
from config import BOT_TOKEN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("TelegramOrchestrator")

def run_flask():
    """Runs the full Flask Admin Dashboard."""
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Admin Dashboard on port {port}...")
    try:
        # We use debug=False and use_reloader=False to avoid issues in threads
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask Dashboard failed: {e}")

async def start_services():
    """Orchestrates the startup of all Telegram services within the same loop."""
    logger.info("Initializing Telegram services...")
    
    # 1. Initialize the listener (Userbot)
    listener = GradeListener()
    
    try:
        tasks = []
        
        # Add Userbot task
        logger.info("Starting Userbot Listener...")
        tasks.append(asyncio.create_task(listener.start()))
        
        # Add Notifier Bot task if initialized
        if bot:
            logger.info("Starting Notifier Bot...")
            # Start the bot client with the token inside the running loop
            await bot.start(bot_token=BOT_TOKEN)
            tasks.append(asyncio.create_task(bot.run_until_disconnected()))
        else:
            logger.error("Notifier Bot instance is None. Check API_ID/API_HASH.")
        
        # Run both concurrently in the same loop
        logger.info("Launching all Telegram services...")
        await asyncio.gather(*tasks)
        
    except errors.FloodWaitError as e:
        logger.error(f"CRITICAL: Telegram FloodWait detected. Must wait for {e.seconds} seconds.")
        logger.info(f"Please manually restart the Koyeb service after {e.seconds} seconds have passed.")
        logger.info("Exiting gracefully to prevent rapid restart loop on Koyeb.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Telegram services encountered an error: {e}")
        raise e
    finally:
        logger.info("Disconnecting clients...")
        if listener and listener.client:
            await listener.client.disconnect()
        if bot:
            await bot.disconnect()

def main():
    # 1. Start the full Flask dashboard in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Run the main asyncio event loop for Telegram services
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        logger.info("System received shutdown signal (KeyboardInterrupt).")
    except SystemExit:
        logger.info("System exiting gracefully due to FloodWait.")
    except Exception as e:
        logger.error(f"System crash: {e}")
    finally:
        logger.info("System shutdown complete.")

if __name__ == "__main__":
    main()
