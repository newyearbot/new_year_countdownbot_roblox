import requests
import datetime
import time
import os
import logging
from flask import Flask
import threading

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# --- Flask server for uptime pings ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run).start()

# --- Roblox bot setup ---
COOKIE = os.getenv("ROBLOSECURITY")
URL = "https://users.roblox.com/v1/description"

session = requests.Session()
session.cookies[".ROBLOSECURITY"] = COOKIE
session.headers.update({
    "Content-Type": "application/json",
    "User-Agent": "RobloxBot/1.0"
})

# Function to fetch and set X-CSRF token
def refresh_csrf():
    r = session.post(URL, json={})
    if "x-csrf-token" in r.headers:
        token = r.headers["x-csrf-token"]
        session.headers["X-CSRF-TOKEN"] = token
        logging.info("🔑 Refreshed CSRF token")
    else:
        logging.error("❌ Could not get CSRF token")

def get_countdown():
    now = datetime.datetime.utcnow()
    new_year = datetime.datetime(now.year + 1, 1, 1, 0, 0, 0)
    delta = new_year - now
    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"Countdown to New Year: {days}d {hours}h {minutes}m {secs}s"

# --- Main loop ---
refresh_csrf()  # get token before first update

while True:
    bio_text = get_countdown()
    response = session.post(URL, json={"description": bio_text})
    if response.status_code == 200:
        logging.info(f"✅ Updated bio: {bio_text}")
    elif response.status_code == 403:
        logging.warning("⚠️ CSRF token expired, refreshing...")
        refresh_csrf()
    else:
        logging.error(f"❌ Error: {response.text}")
    time.sleep(60)
