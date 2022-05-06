import json

from models.centers import CentersModel
from datetime import datetime
from helpers.users import UsersHelper
from models.users import UsersModel
from models.sections import SectionsModel
from telebot import types


class CentersController:
    def __init__(self, session, bot):
        self.session = session
        self.bot = bot

    def sendCenters(self, chat_id):
        controller_name = self.__class__.__name__
        is_admin = UsersHelper.is_admin(self.session, chat_id)
        centers = self.session.query(CentersModel).all()
        keyboard = types.InlineKeyboardMarkup()
        send_text = 'Пока нет ни одного центра'

        if centers:
            send_text = 'Выберите центр из списка:'

            for center in centers:
                callback = {"action": "PostController.select", "item_id": center.id}
                center_name = center.name
                button = types.InlineKeyboardButton(text=center_name, callback_data=json.dumps(callback))
                keyboard.add(button)

                if is_admin:
                    callback = {"action": controller_name + ".update", "item_id": center.id}
                    button1 = types.InlineKeyboardButton(text='🖋 Изменить центр', callback_data=json.dumps(callback))
                    callback = {"action": controller_name + ".delete", "item_id": center.id}
                    button2 = types.InlineKeyboardButton(text='❌ Удалить центр', callback_data=json.dumps(callback))
                    keyboard.add(button1, button2)

        if is_admin:
            callback = {"action": controller_name + ".add"}
            button = types.InlineKeyboardButton(text="✅ Добавить центр", callback_data=json.dumps(callback))
            keyboard.add(button)

        self.bot.send_message(chat_id, send_text, reply_markup=keyboard)

    def add(self, message):
        self.bot.send_message(message.chat.id, "Выберите название центра:")
        self.bot.register_next_step_handler(message, self.add_callback)

    def add_callback(self, message):
        data = {
            "name": message.text,
            "created": datetime.now(),
            "updated": datetime.now(),
        }

        add = CentersModel(**data)
        self.session.add(add)
        self.session.commit()
        self.sendCenters(message.chat.id)

    def delete(self, message, delete_id):
        if not self.check_relations(delete_id):
            message = "Этот центр связан с юзерами и постами. Его можно только изменить"
            self.bot.send_message(message.chat.id, message)
            return

        self.bot.delete_message(message.chat.id, message.message_id)
        self.session.query(CentersModel).filter_by(id=delete_id).delete()
        self.sendCenters(message.chat.id)

    def update(self, message, update_id):
        self.bot.send_message(message.chat.id, "Выберите новое название центра:")
        self.bot.register_next_step_handler(message, self.update_callback, update_id)

    def update_callback(self, message, update_id):
        data = {"name": message.text, "updated": datetime.now()}
        self.session.query(CentersModel).filter_by(id=update_id).update(data)
        self.session.commit()
        self.sendCenters(message.chat.id)

    def check_relations(self, center_id):
        users = self.session.query(UsersModel).filter_by(center_id=center_id).first()
        centers = self.session.query(SectionsModel).filter_by(center_id=center_id).first()
        return not users and not centers
