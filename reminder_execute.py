import datetime
import time
from logging import getLogger, StreamHandler

from envparse import Env

from create_db import SQLiteClient
from telegram_client import TelegramClient
from reminder import Reminder

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")

env = Env()

TOKEN = env.str("TOKEN")
FROM_TIME = env.str("FROM_TIME", default="18:00")
TO_TIME = env.str("TO_TIME", default="22:00")
REMINDER_PERIOD = env.int("REMINDER_PERIOD", default=900)
SLEEP_CHECK_PERIOD = env.int("SLEEP_CHECK_PERIOD", default=3600)

database_client = SQLiteClient("/home/dimaska/Dev/reminderBot/users.db")
telegram_client = TelegramClient(
    token=TOKEN,
    base_url="https://api.telegram.org"
)
reminder = Reminder(
    database_client=database_client,
    telegram_client=telegram_client
)
reminder.setup()

start_time = datetime.datetime.strptime(FROM_TIME, '%H:%M').time()
end_time = datetime.datetime.strptime(TO_TIME, '%H:%M').time()

while True:
    now_time = datetime.datetime.now().time()
    if start_time <= now_time <= end_time:
        reminder()
        time.sleep(REMINDER_PERIOD)
    else:
        time.sleep(SLEEP_CHECK_PERIOD)
