import asyncio
import threading
from modules.listener import GradeListener
from modules.notifier import bot
from modules.dashboard import app
import os

def run_flask():
    print("Starting Admin Dashboard on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

async def main():
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start the Userbot Listener
    listener = GradeListener()
    
    # Run both the listener and the notification bot
    print("Starting Telegram services...")
    await asyncio.gather(
        listener.start(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("System shutting down...")
