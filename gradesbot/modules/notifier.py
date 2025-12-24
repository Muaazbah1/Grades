from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN
from modules.database import db
import asyncio

# Bot client for notifications
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def notify_student(student_id, subject, grade, rank, percentile, chart_path):
    user = db.get_user_by_student_id(student_id)
    if not user:
        print(f"Student {student_id} not found in database. Skipping notification.")
        return

    tg_id = user['tg_id']
    template = db.get_setting('result_message_template') or "Subject: {subject}\nGrade: {grade}\nRank: {rank}\nPercentile: {percentile}%"
    
    message = template.format(
        subject=subject,
        grade=grade,
        rank=rank,
        percentile=percentile
    )

    try:
        await bot.send_message(tg_id, message, file=chart_path)
        print(f"Notification sent to student {student_id} (TG: {tg_id})")
    except Exception as e:
        print(f"Failed to send notification to {tg_id}: {e}")

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
        await event.respond(f"Registration failed: {e}")

if __name__ == "__main__":
    print("Starting Notification Bot...")
    bot.run_until_disconnected()
