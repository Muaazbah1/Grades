import logging
import asyncio
from telethon import TelegramClient, events, errors
from config import API_ID, API_HASH, BOT_TOKEN
from modules.database import db

# Configure logging
logger = logging.getLogger("NotifierBot")

# Initialize the bot client instance without starting it
# This prevents loop capture at the module level
bot = None
if API_ID and API_HASH:
    bot = TelegramClient('bot_session', int(API_ID), API_HASH)
    logger.info("Notifier Bot instance initialized (not started).")

def register_handlers(client):
    """Registers command handlers for the bot."""
    @client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        welcome = db.get_setting('welcome_message') or "Welcome! Please use /register <student_id> to receive your grades."
        await event.respond(welcome)

    @client.on(events.NewMessage(pattern='/register (.+)'))
    async def register_handler(event):
        student_id = event.pattern_match.group(1).strip()
        tg_id = event.sender_id
        
        try:
            sender = await event.get_sender()
            full_name = f"{sender.first_name} {sender.last_name or ''}".strip()
            
            db.supabase.table('users').upsert({
                'student_id': student_id,
                'tg_id': str(tg_id),
                'full_name': full_name
            }).execute()
            await event.respond(f"Successfully registered Student ID: {student_id}")
        except Exception as e:
            logger.error(f"Registration failed for {tg_id}: {e}")
            await event.respond(f"Registration failed. Please try again later.")

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
        logger.info(f"Student {student_id} not found in database. Skipping notification.")
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
        await bot.send_message(tg_id, message, file=chart_path)
        logger.info(f"Notification sent to student {student_id} (TG: {tg_id})")
    except errors.FloodWaitError as e:
        logger.warning(f"FloodWait during notification: waiting {e.seconds}s")
        await asyncio.sleep(e.seconds)
        await bot.send_message(tg_id, message, file=chart_path)
    except Exception as e:
        logger.error(f"Failed to send notification to {tg_id}: {e}")
