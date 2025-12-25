from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from config import SECRET_KEY, ADMIN_PASSWORD
from modules.database import db
import os
import logging

logger = logging.getLogger("Dashboard")

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)

class Admin(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return Admin(user_id) if user_id == 'admin' else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            login_user(Admin('admin'))
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    channels = db.get_monitored_channels()
    return render_template('dashboard.html', channels=channels)

@app.route('/api/channels', methods=['GET', 'POST'])
@login_required
def manage_channels():
    try:
        if request.method == 'POST':
            data = request.get_json()
            logger.info(f"Adding channel: {data}")
            db.supabase.table('channels').insert({
                'channel_id': str(data['channel_id']),
                'channel_link': data['channel_link'],
                'channel_name': data['channel_name'],
                'is_active': True
            }).execute()
            return jsonify({'status': 'success'})
        
        channels = db.get_monitored_channels()
        return jsonify(channels)
    except Exception as e:
        logger.error(f"API Error (channels): {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def manage_settings():
    try:
        if request.method == 'POST':
            data = request.get_json()
            logger.info(f"Updating settings: {data}")
            for key, value in data.items():
                db.update_setting(key, value)
            return jsonify({'status': 'success'})
        
        settings = {
            'welcome_message': db.get_setting('welcome_message'),
            'result_message_template': db.get_setting('result_message_template')
        }
        return jsonify(settings)
    except Exception as e:
        logger.error(f"API Error (settings): {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})
