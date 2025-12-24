from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.warning("Supabase credentials not found in environment variables.")
            self.supabase = None
            return
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Successfully connected to Supabase.")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self.supabase = None

    def get_user_by_student_id(self, student_id):
        if not self.supabase: return None
        try:
            response = self.supabase.table('users').select('*').eq('student_id', student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user {student_id}: {e}")
            return None

    def get_all_users(self):
        if not self.supabase: return []
        try:
            response = self.supabase.table('users').select('*').execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            return []

    def add_grade(self, student_id, subject, grade, rank, percentile, source):
        if not self.supabase: return None
        data = {
            'student_id': student_id,
            'subject_name': subject,
            'grade': grade,
            'rank': rank,
            'percentile': percentile,
            'file_source': source
        }
        try:
            return self.supabase.table('grades').insert(data).execute()
        except Exception as e:
            logger.error(f"Error adding grade for {student_id}: {e}")
            return None

    def get_monitored_channels(self):
        if not self.supabase: return []
        try:
            response = self.supabase.table('channels').select('*').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching monitored channels: {e}")
            return []

    def get_setting(self, key):
        if not self.supabase: return None
        try:
            response = self.supabase.table('settings').select('value').eq('key', key).execute()
            return response.data[0]['value'] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching setting {key}: {e}")
            return None

    def update_setting(self, key, value):
        if not self.supabase: return None
        try:
            return self.supabase.table('settings').update({'value': value}).eq('key', key).execute()
        except Exception as e:
            logger.error(f"Error updating setting {key}: {e}")
            return None

db = Database()
