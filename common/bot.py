import telebot
import config as config


class BotConnection:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = telebot.TeleBot(config.API_TOKEN)

        return cls.instance
