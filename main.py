import asyncio
import threading
import logging
import sys
import os
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
logger = logging.getLogger("MainOrchestrator")

def run_flask():
    """Runs the Flask dashboard in a separate thread."""
    logger.info("Starting Admin Dashboard on port 5000...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
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
        logger.info("Starting Userbot...")
        tasks.append(listener.start())
        
        # Add Notifier Bot task if initialized
        if bot:
            logger.info("Starting Notifier Bot...")
            # Start the bot client with the token inside the running loop
            await bot.start(bot_token=BOT_TOKEN)
            tasks.append(bot.run_until_disconnected())
        else:
            logger.error("Notifier Bot instance is None. Check API_ID/API_HASH.")
        
        # Run both concurrently in the same loop
        logger.info("Launching all Telegram services...")
        await asyncio.gather(*tasks)
        
    except errors.FloodWaitError as e:
        logger.error(f"CRITICAL: Telegram FloodWait detected. Must wait for {e.seconds} seconds.")
        logger.info("Exiting gracefully to prevent rapid restart loop on Koyeb.")
        # Exit with code 0 so Koyeb doesn't treat it as a crash and restart immediately
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
    # 1. Start Flask in a separate daemon thread
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
