import json
import translate
import config
from datetime import datetime
from telebot.types import InlineKeyboardButton
from telebot.types import InlineKeyboardMarkup
from telebot.types import ReplyKeyboardMarkup
from telebot.types import KeyboardButton
from telebot.types import Message
from common.database import DatabaseConnection
from common.bot import BotConnection
from helpers.users import UsersHelper
from abc import ABC, abstractmethod


class BaseController(ABC):
    def __init__(self):
        self.session = DatabaseConnection()
        self.bot = BotConnection()

    # Select
    @abstractmethod
    def select(self, message: Message, item_id: int) -> None:
        """Here is the logic of select item"""
        pass

    # View
    @abstractmethod
    def view(self, message: Message, item_id: int = None, page: int = 0) -> None:
        """Here is the logic of view items"""
        pass

    # Add
    def add(self, message: Message, item_id: int = None) -> None:
        """Ask for a name to be added"""
        if not UsersHelper.is_admin(message.chat.id):
            return

        self.bot.send_message(message.chat.id, translate.ENTER_NAME)
        self.bot.register_next_step_handler(message, self.add_callback, item_id)

    @abstractmethod
    def add_callback(self, message: Message, item_id: int):
        """Here is the logic of adding"""
        pass

    # Update
    def update(self, message: Message, update_id: int) -> None:
        """Ask for a name to be updated"""
        if not UsersHelper.is_admin(message.chat.id):
            return

        self.bot.send_message(message.chat.id, translate.ENTER_NEW_NAME)
        self.bot.register_next_step_handler(message, self.update_callback, update_id)

    @abstractmethod
    def update_callback(self, message: Message, update_id: int):
        """Here is the logic of updating"""
        pass

    # Delete
    @abstractmethod
    def delete(self, message: Message, delete_id: int):
        """Here is the logic of deleting"""
        pass

    # Change sort
    def change_sort(self, message: Message, item_id: int = None) -> None:
        if not UsersHelper.is_admin(message.chat.id):
            return

        self.bot.send_message(message.chat.id, translate.ENTER_SORT)
        self.bot.register_next_step_handler(message, self.change_sort_prepare, item_id)

    def change_sort_prepare(self, message: Message, update_id: int) -> None:
        try:
            sort = int(message.text)
            data = {"sort": sort, "updated": datetime.now()}
            self.change_sort_callback(message, data, update_id)
        except ValueError:
            self.bot.send_message(message.chat.id, translate.ENTER_NUMBER)

    @abstractmethod
    def change_sort_callback(self, message: Message, update_data: dict, update_id: int) -> None:
        pass

    # Keyboards
    def get_inline_keyboard(self, data, is_admin: bool) -> InlineKeyboardMarkup:
        """Getting inline keyboard by model data"""
        controller_name = self.__class__.__name__
        keyboard = InlineKeyboardMarkup()
        if not data:
            return keyboard

        for item in data:
            callback = {"action": controller_name + ".select", "params": item.id}
            button = InlineKeyboardButton(text=item.name, callback_data=json.dumps(callback))
            keyboard.add(button)

            if is_admin:
                callback = {"action": controller_name + ".update", "params": item.id}
                button1 = InlineKeyboardButton(text=translate.CHANGE, callback_data=json.dumps(callback))
                callback = {"action": controller_name + ".delete", "params": item.id}
                button2 = InlineKeyboardButton(text=translate.DELETE, callback_data=json.dumps(callback))
                keyboard.add(button1, button2)

                callback = {"action": controller_name + ".change_sort", "params": item.id}
                button = InlineKeyboardButton(text=translate.CHANGE_SORT, callback_data=json.dumps(callback))
                keyboard.add(button)

        return keyboard

    def get_keyboard(self) -> ReplyKeyboardMarkup:
        """Getting keyboard buttons"""
        keyboard = ReplyKeyboardMarkup()
        for row in config.BUTTONS:
            keyboard_buttons = []
            for item in row:
                keyboard_buttons.append(KeyboardButton(text=item))

            keyboard.add(*keyboard_buttons)

        return keyboard
