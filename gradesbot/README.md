# Automated Telegram Grade System

A fully automated system that monitors Telegram channels for grade files, analyzes them, and notifies students of their results with performance charts.

## Features
- **Userbot Listener**: Monitors specified channels for PDF/XLSX/CSV files.
- **Data Engine**: Calculates Mean, SD, Median, Rank, and Percentile.
- **Visualization**: Generates Bell Curve charts for each student.
- **Notification Bot**: Sends private results to registered students.
- **Admin Dashboard**: Manage channels, settings, and view logs.

## Setup Instructions

### 1. Environment Variables
Create a `.env` file in the root directory:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_flask_secret_key
```

### 2. Database Setup
Run the provided `schema.sql` in your Supabase SQL Editor to create the necessary tables.

### 3. Installation
```bash
pip install -r requirements.txt
```

### 4. Running the System
```bash
python main.py
```

## Project Structure
- `main.py`: Main entry point.
- `modules/`: Core logic modules (listener, engine, notifier, database, dashboard).
- `templates/`: HTML templates for the admin dashboard.
- `data/`: Local storage for downloads and generated charts.
- `Dockerfile`: For containerized deployment.
