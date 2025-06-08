import os
from os import getenv

API_ID = int(os.environ.get("API_ID", "26330942"))  # Replace "123456" with your actual api_id or use .env
API_HASH = os.environ.get("API_HASH", "5de9fd033aa828dfd3bf0c28adeee660")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7460074981:AAH3xfM8LwbSaxqh9HMW_1QKfYXSHKZBRU0")

OWNER_ID = int(os.environ.get("OWNER_ID", "6883471516"))  # Your Telegram user ID
SUDO_USERS = list(map(int, os.environ.get("SUDO_USERS", "6883471516").split()))  # Space-separated user IDs

MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://biklriplit:efaXfv2Ps9MRfner@cluster0.4hfu8zj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")##your mongo url eg: withmongodb+srv://xxxxxxx:xxxxxxx@clusterX.xxxx.mongodb.net/?retryWrites=true&w=majority
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002618428217"))  # Telegram channel ID (with -100 prefix)

PREMIUM_LOGS = os.environ.get("PREMIUM_LOGS", "")  # Optional here you'll get all logs
