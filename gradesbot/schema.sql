-- SQL Schema for Telegram Grade System

-- Users table to store student information and their Telegram IDs
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    tg_id BIGINT UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grades table to store processed grade records
CREATE TABLE IF NOT EXISTS grades (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    subject_name VARCHAR(255) NOT NULL,
    grade FLOAT NOT NULL,
    rank INT,
    percentile FLOAT,
    file_source VARCHAR(255),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(student_id) ON DELETE CASCADE
);

-- Monitored channels table
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT UNIQUE NOT NULL,
    channel_link VARCHAR(255),
    channel_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System settings table
CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Initial settings
INSERT INTO settings (key, value) VALUES 
('welcome_message', 'Welcome to the Grade Notification Bot! Please register your Student ID.'),
('result_message_template', 'Subject: {subject}\nGrade: {grade}\nRank: {rank}\nPercentile: {percentile}%'),
('admin_password_hash', 'pbkdf2:sha256:260000$default_hash') -- Default password should be changed
ON CONFLICT (key) DO NOTHING;
