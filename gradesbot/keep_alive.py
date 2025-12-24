import time
import requests
import os

# This script can be run as a sidecar to ping the health endpoint
# to prevent services like Render or Heroku from sleeping.

URL = os.getenv('HEALTH_CHECK_URL', 'http://localhost:5000/health')
INTERVAL = int(os.getenv('PING_INTERVAL', '300')) # 5 minutes

def ping():
    while True:
        try:
            response = requests.get(URL)
            print(f"Pinged {URL}, status: {response.status_code}")
        except Exception as e:
            print(f"Ping failed: {e}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    ping()
