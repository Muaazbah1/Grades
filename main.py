import asyncio
import threading
import logging
import sys
from modules.listener import GradeListener
from modules.notifier import init_bot, BOT_TOKEN
from modules.dashboard import app

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
    
    # 2. Initialize the notification bot
    bot_client = init_bot()
    
    try:
        tasks = []
        
        # Add Userbot task
        logger.info("Preparing Userbot task...")
        tasks.append(listener.start())
        
        # Add Notifier Bot task if initialized
        if bot_client:
            logger.info("Preparing Notifier Bot task...")
            # Start the bot client with the token
            await bot_client.start(bot_token=BOT_TOKEN)
            tasks.append(bot_client.run_until_disconnected())
        
        # Run both concurrently in the same loop
        logger.info("Launching all Telegram services...")
        await asyncio.gather(*tasks)
        
    except Exception as e:
        logger.error(f"Telegram services encountered an error: {e}")
    finally:
        logger.info("Disconnecting clients...")
        if listener.client:
            await listener.client.disconnect()
        if bot_client:
            await bot_client.disconnect()

def main():
    # 1. Start Flask in a separate daemon thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Run the main asyncio event loop for Telegram services
    try:
        # This creates the loop and runs the services inside it
        asyncio.run(start_services())
    except KeyboardInterrupt:
        logger.info("System received shutdown signal (KeyboardInterrupt).")
    except Exception as e:
        logger.error(f"System crash: {e}")
    finally:
        logger.info("System shutdown complete.")

if __name__ == "__main__":
    main()
