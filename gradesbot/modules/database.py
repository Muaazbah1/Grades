from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

class Database:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Warning: Supabase credentials not found in environment variables.")
            self.supabase = None
            return
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def get_user_by_student_id(self, student_id):
        if not self.supabase: return None
        response = self.supabase.table('users').select('*').eq('student_id', student_id).execute()
        return response.data[0] if response.data else None

    def get_all_users(self):
        if not self.supabase: return []
        response = self.supabase.table('users').select('*').execute()
        return response.data

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
        return self.supabase.table('grades').insert(data).execute()

    def get_monitored_channels(self):
        if not self.supabase: return []
        response = self.supabase.table('channels').select('*').eq('is_active', True).execute()
        return response.data

    def get_setting(self, key):
        if not self.supabase: return None
        response = self.supabase.table('settings').select('value').eq('key', key).execute()
        return response.data[0]['value'] if response.data else None

    def update_setting(self, key, value):
        if not self.supabase: return None
        return self.supabase.table('settings').update({'value': value}).eq('key', key).execute()

db = Database()
