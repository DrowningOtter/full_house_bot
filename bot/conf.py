from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# API_TOKEN = "6163460483:AAHV_XUd8eNW-Aw2DPNXuyZv55Ux3ydQHkE"
API_TOKEN = os.getenv("TGBOT_API_TOKEN")
if API_TOKEN == None:
    raise ValueError
# DB_NAME = os.path.join(BASE_DIR, 'bot_site', 'db.sqlite3')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# USER_ID = 2
USER_ID = os.getenv("USER_ID")
if USER_ID == None:
    raise ValueError

RABBITMQ_LOGIN = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_QUEUE_NAME = f"newsletter_queue_{USER_ID}"
RABBITMQ_HOST_NAME = "rabbitmq"
RABBITMQ_CONNECT_RETRIES = 10
DELAY_BETWEEN_RETRIES = 5