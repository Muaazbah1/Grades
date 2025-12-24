import logging
import asyncio
from telethon import TelegramClient, events, errors
from config import API_ID, API_HASH, BOT_TOKEN
from modules.database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot client for notifications
bot = None
if API_ID and API_HASH and BOT_TOKEN:
    try:
        bot = TelegramClient('bot_session', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)
        logger.info("Notification Bot initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Notification Bot: {e}")

async def notify_student(student_id, subject, grade, rank, percentile, chart_path):
    if not bot:
        logger.error("Bot not initialized. Cannot send notification.")
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

if bot:
    # Bot handlers for registration
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        welcome = db.get_setting('welcome_message') or "Welcome! Please use /register <student_id> to receive your grades."
        await event.respond(welcome)

    @bot.on(events.NewMessage(pattern='/register (.+)'))
    async def register_handler(event):
        student_id = event.pattern_match.group(1).strip()
        tg_id = event.sender_id
        
        # Update or insert user in DB
        try:
            db.supabase.table('users').upsert({
                'student_id': student_id,
                'tg_id': tg_id,
                'full_name': f"{event.sender.first_name} {event.sender.last_name or ''}".strip()
            }).execute()
            await event.respond(f"Successfully registered Student ID: {student_id}")
        except Exception as e:
            logger.error(f"Registration failed for {tg_id}: {e}")
            await event.respond(f"Registration failed. Please try again later.")

if __name__ == "__main__":
    if bot:
        logger.info("Starting Notification Bot...")
        bot.run_until_disconnected()
    else:
        logger.error("Bot not initialized. Exiting.")
