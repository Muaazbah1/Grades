from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseLayer")

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
            response = self.supabase.table('users').select('*').eq('student_id', str(student_id)).execute()
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
            'student_id': str(student_id),
            'subject_name': str(subject),
            'grade': float(grade),
            'rank': int(rank),
            'percentile': float(percentile),
            'file_source': str(source)
        }
        try:
            logger.info(f"DEBUG: Sending grade payload: {json.dumps(data)}")
            return self.supabase.table('grades').insert(data).execute()
        except Exception as e:
            logger.error(f"Error adding grade for {student_id}: {e}")
            return None

    def get_monitored_channels(self):
        if not self.supabase: return []
        try:
            # Table name is 'channels' (plural)
            response = self.supabase.table('channels').select('*').execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching monitored channels: {e}")
            return []

    def get_setting(self, key):
        if not self.supabase: return None
        try:
            response = self.supabase.table('settings').select('value').eq('key', str(key)).execute()
            return response.data[0]['value'] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching setting {key}: {e}")
            return None

    def update_setting(self, key, value):
        if not self.supabase: return None
        data = {'key': str(key), 'value': str(value)}
        try:
            logger.info(f"DEBUG: Sending settings payload: {json.dumps(data)}")
            # Using upsert to handle both new and existing settings
            return self.supabase.table('settings').upsert(data).execute()
        except Exception as e:
            logger.error(f"Error updating setting {key}: {e}")
            return None

    def add_channel(self, channel_id, channel_name, channel_link):
        if not self.supabase: return None
        data = {
            'channel_id': int(channel_id), # schema.sql says BIGINT
            'channel_name': str(channel_name),
            'channel_link': str(channel_link),
            'is_active': True
        }
        try:
            logger.info(f"DEBUG: Sending channel payload: {json.dumps(data)}")
            return self.supabase.table('channels').insert(data).execute()
        except Exception as e:
            logger.error(f"Error adding channel {channel_id}: {e}")
            return None

db = Database()
