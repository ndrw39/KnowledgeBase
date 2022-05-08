import json

from telebot.types import InlineKeyboardMarkup
from common.database import DatabaseConnection
from common.bot import BotConnection
from abc import ABC, abstractmethod
from telebot import types
from helpers.users import UsersHelper


class BaseController(ABC):
    def __init__(self):
        self.session = DatabaseConnection()
        self.bot = BotConnection()

    def get_keyboard(self, data, is_admin) -> InlineKeyboardMarkup:
        controller_name = self.__class__.__name__
        keyboard = types.InlineKeyboardMarkup()
        if data:
            for item in data:
                callback = {"action": controller_name + ".select", "params": item.id}
                item_name = item.name
                button = types.InlineKeyboardButton(text=item_name, callback_data=json.dumps(callback))
                keyboard.add(button)

                if is_admin:
                    callback = {"action": controller_name + ".update", "params": item.id}
                    button1 = types.InlineKeyboardButton(text='Изменить', callback_data=json.dumps(callback))
                    callback = {"action": controller_name + ".delete", "params": item.id}
                    button2 = types.InlineKeyboardButton(text='Удалить', callback_data=json.dumps(callback))
                    keyboard.add(button1, button2)

        return keyboard

    def add(self, message, item_id) -> None:
        if not UsersHelper.is_admin(message.chat.id):
            return

        self.bot.send_message(message.chat.id, "Выберите название:")
        self.bot.register_next_step_handler(message, self.add_callback, item_id)

    def update(self, message, update_id) -> None:
        if not UsersHelper.is_admin(message.chat.id):
            return

        self.bot.send_message(message.chat.id, "Выберите новое название:")
        self.bot.register_next_step_handler(message, self.update_callback, update_id)

    @abstractmethod
    def add_callback(self, message, item_id):
        pass

    @abstractmethod
    def update_callback(self, message, update_id):
        pass

    @abstractmethod
    def delete(self, message, delete_id):
        pass
