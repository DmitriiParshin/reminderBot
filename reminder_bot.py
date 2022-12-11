from datetime import datetime, date
from logging import getLogger, StreamHandler

from envparse import Env

import telebot
from telebot.types import Message

from create_db import SQLiteClient
from manager import UserManager
from telegram_client import TelegramClient


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")

env = Env()
CHAT_ID = env.int("CHAT_ID")
TOKEN = env.str("TOKEN")


class LoggerBot(telebot.TeleBot):
    def __init__(
            self,
            telegram_client: TelegramClient,
            user_manager: UserManager,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.telegram_client = telegram_client
        self.user_manager = user_manager

    def setup_resources(self):
        self.user_manager.setup()

    def shutdown_resources(self):
        self.user_manager.shutdown()

    def shutdown(self):
        self.shutdown_resources()


telegram_client = TelegramClient(
    token=TOKEN,
    base_url="https://api.telegram.org/"
)
user_manager = UserManager(SQLiteClient("users.db"))
bot = LoggerBot(
    token=TOKEN,
    telegram_client=telegram_client,
    user_manager=user_manager
)


@bot.message_handler(commands=["start"])
def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    create_new_user = False

    user = bot.user_manager.get_user(user_id=str(user_id))
    if not user:
        bot.user_manager.create_user(
            user_id=str(user_id),
            username=username,
            chat_id=chat_id
        )
        create_new_user = True
    bot.reply_to(
        message=message,
        text=str(f"Вы {'уже' if not create_new_user else ''} "
                 f"зарегистрированы: {username}. Ваш user_id: {user_id}")
    )


def handle_standup_speech(message: Message):
    bot.user_manager.update_date(
        user_id=str(message.from_user.id),
        updated_date=date.today()
    )
    bot.send_message(
        chat_id=CHAT_ID,
        text=f"Пользователь {message.from_user.username} "
             f"говорит {message.text}"
    )
    bot.reply_to(message, text="Спасибо большое! Желаю успехов "
                               "и хорошего дня!")


@bot.message_handler(commands=["say_standup_speech"])
def say_standup_speech(message: Message):
    bot.reply_to(message, text="Привет! Чем ты занимался вчера? "
                               "Что будешь делать сегодня? "
                               "Какие есть трудности?")
    bot.register_next_step_handler(message, handle_standup_speech)


def create_error_message(error: Exception) -> str:
    return f"{datetime.now()} <> {error.__class__} <> {error}"


while True:
    try:
        bot.setup_resources()
        bot.polling()
    except Exception as error:
        error_message = create_error_message(error)
        bot.telegram_client.post(
            method="sendMessage",
            params={"text": error_message, "chat_id": CHAT_ID}
        )
        logger.error(error_message)
        bot.shutdown()
