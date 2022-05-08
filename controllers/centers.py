import json
from telebot import types
from datetime import datetime
from controllers.base import BaseController
from helpers.users import UsersHelper
from helpers.router import Router
from models.users import UsersModel
from models.centers import CentersModel
from models.sections import SectionsModel


class CentersController(BaseController):

    def send_centers(self, chat_id) -> None:
        controller_name = self.__class__.__name__
        is_admin = UsersHelper.is_admin(chat_id)
        centers = self.session.query(CentersModel)\
            .order_by(CentersModel.sort.asc())\
            .all()

        send_text = 'Пока нет ни одного центра'
        if centers:
            send_text = 'Выберите центр из списка:'

        keyboard = self.get_inline_keyboard(centers, is_admin)
        if is_admin:
            callback = {"action": controller_name + ".add"}
            button = types.InlineKeyboardButton(text="Добавить", callback_data=json.dumps(callback))
            keyboard.add(button)

        self.bot.send_message(chat_id, send_text, reply_markup=keyboard)

    def add_callback(self, message, item_id) -> None:
        data = {"name": message.text, "created": datetime.now(), "updated": datetime.now()}
        add = CentersModel(**data)

        self.session.add(add)
        self.session.commit()

        user = UsersHelper.getUser(message.chat.id)
        if user and user.center_id:
            Router("SectionsController", "select", [message])
            return

        Router("CentersController", "send_centers", [message.chat.id])

    def delete(self, message, delete_id) -> None:
        if not UsersHelper.is_admin(message.chat.id):
            return

        if not self.check_relations(delete_id):
            message = "Этот центр связан с юзерами и постами. Его можно только изменить"
            self.bot.send_message(message.chat.id, message)
            return

        self.bot.delete_message(message.chat.id, message.message_id)
        self.session.query(CentersModel).filter_by(id=delete_id).delete()
        self.session.commit()
        self.send_centers(message.chat.id)

    def update_callback(self, message, update_id) -> None:
        data = {"name": message.text, "updated": datetime.now()}
        self.session.query(CentersModel).filter_by(id=update_id).update(data)
        self.session.commit()
        self.send_centers(message.chat.id)

    def change_sort_callback(self, message, update_id) -> None:
        try:
            sort = int(message.text)
            data = {"sort": sort, "updated": datetime.now()}
            self.session.query(CentersModel).filter_by(id=update_id).update(data)
            self.session.commit()
            self.send_centers(message.chat.id)
        except ValueError:
            self.bot.send_message(message.chat.id, "Введите цифру")

    def check_relations(self, center_id) -> bool:
        users = self.session.query(UsersModel).filter_by(center_id=center_id).first()
        centers = self.session.query(SectionsModel).filter_by(center_id=center_id).first()
        return not users and not centers

    def select(self, message, center_id) -> None:
        UsersHelper.update_center(message.chat.id, center_id)
        self.bot.send_message(message.chat.id, "Запомнили ваш выбор", reply_markup=self.get_keyboard())
        Router("SectionsController", "select", [message])
