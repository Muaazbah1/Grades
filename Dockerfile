FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and use virtual environment
RUN python -m venv /opt/venv

# Set working directory
WORKDIR /app

# Install dependencies into virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir telethon pyrogram pandas matplotlib seaborn supabase flask requests python-dotenv

# Copy project files
COPY . .

# Create data directories and set permissions
RUN mkdir -p data/downloads data/charts && \
    chmod -R 777 data

# Expose dashboard port
EXPOSE 5000

# Run the application using the virtual environment's python
CMD ["python", "main.py"]
