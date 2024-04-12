from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


API_TOKEN = "5783267477:AAGMGx6q2_s6-JPirrNYiYQ0UbA17l8dXXE"
# DB_NAME = os.path.join(BASE_DIR, 'bot_site', 'db.sqlite3')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
USER_ID = 2

RABBITMQ_LOGIN = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_QUEUE_NAME = f"newsletter_queue_{USER_ID}"
RABBITMQ_HOST_NAME = "rabbitmq"
RABBITMQ_CONNECT_RETRIES = 10
DELAY_BETWEEN_RETRIES = 5