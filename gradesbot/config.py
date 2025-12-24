import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API Credentials
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Supabase Credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Admin Dashboard Settings
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key')

# Storage Settings
DATA_DIR = 'data'
DOWNLOAD_DIR = os.path.join(DATA_DIR, 'downloads')
CHART_DIR = os.path.join(DATA_DIR, 'charts')

# Ensure directories exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)
