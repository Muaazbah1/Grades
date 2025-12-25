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
from http.server import BaseHTTPRequestHandler, HTTPServer
from telethon import errors
from modules.listener import GradeListener
from modules.notifier import bot
from config import BOT_TOKEN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("TelegramOrchestrator")

# --- DUMMY HEALTH CHECK SERVER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return # Silent logs for health checks

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Health check server started on port {port}")
    server.serve_forever()
# ---------------------------------

async def start_services():
    """Orchestrates the startup of all Telegram services within the same loop."""
    logger.info("Initializing Telegram services...")
    
    # 1. Initialize the listener (Userbot)
    listener = GradeListener()
    
    try:
        tasks = []
        
        # Add Userbot task
        # We wrap it in a task to ensure it's awaited properly by asyncio.gather
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
    # 1. Start the dummy health check server in a separate thread
    health_thread = threading.Thread(target=run_health_check, daemon=True)
    health_thread.start()

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
