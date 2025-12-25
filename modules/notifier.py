import logging
import asyncio
from telethon import TelegramClient, events, errors
from config import API_ID, API_HASH, BOT_TOKEN
from modules.database import db

# Configure logging
logger = logging.getLogger("NotifierBot")

# Initialize the bot client instance without starting it
bot = None
if API_ID and API_HASH:
    bot = TelegramClient('bot_session', int(API_ID), API_HASH)
    logger.info("Notifier Bot instance initialized.")

# State management for registration (in-memory for simplicity)
registration_state = {}

def register_handlers(client):
    """Registers command handlers for the bot."""
    
    @client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        if not event.is_private:
            return
        registration_state[event.sender_id] = 'AWAITING_ID'
        await event.respond("Welcome! Please enter your University ID number to register for grade notifications.")

    @client.on(events.NewMessage)
    async def message_handler(event):
        if not event.is_private or event.text.startswith('/'):
            return
        
        sender_id = event.sender_id
        if registration_state.get(sender_id) == 'AWAITING_ID':
            university_id = event.text.strip()
            
            # Basic validation: check if it's a number
            if not university_id.isdigit():
                await event.respond("Invalid ID. Please enter a numeric University ID.")
                return
            
            try:
                sender = await event.get_sender()
                full_name = f"{sender.first_name} {sender.last_name or ''}".strip()
                
                # Save to Supabase
                db.supabase.table('users').upsert({
                    'student_id': university_id,
                    'tg_id': str(sender_id),
                    'full_name': full_name
                }).execute()
                
                registration_state.pop(sender_id, None)
                await event.respond(f"Success! I have registered your ID: {university_id}. I will notify you as soon as a new grade file is posted.")
                logger.info(f"User {sender_id} registered with ID {university_id}")
            except Exception as e:
                logger.error(f"Registration failed for {sender_id}: {e}")
                await event.respond("Registration failed due to a database error. Please try again later.")

# Register handlers immediately on the instance
if bot:
    register_handlers(bot)

async def notify_student(student_id, subject, grade, rank, percentile, chart_path):
    global bot
    if not bot or not bot.is_connected():
        logger.error("Bot not connected. Cannot send notification.")
        return

    user = db.get_user_by_student_id(student_id)
    if not user:
        return

    tg_id = int(user['tg_id'])
    template = db.get_setting('result_message_template') or "Subject: {subject}\nGrade: {grade}\nRank: {rank}\nPercentile: {percentile}%"
    
    message = template.format(
        subject=subject,
        grade=grade,
        rank=rank,
        percentile=percentile
    )

    try:
        if chart_path and os.path.exists(chart_path):
            await bot.send_message(tg_id, message, file=chart_path)
        else:
            await bot.send_message(tg_id, message)
        logger.info(f"Notification sent to student {student_id} (TG: {tg_id})")
    except errors.FloodWaitError as e:
        logger.warning(f"FloodWait during notification: waiting {e.seconds}s")
        await asyncio.sleep(e.seconds)
        await bot.send_message(tg_id, message, file=chart_path)
    except Exception as e:
        logger.error(f"Failed to send notification to {tg_id}: {e}")
