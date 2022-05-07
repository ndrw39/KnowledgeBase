import json
import controllers
import helpers
import models

from telebot import types
from datetime import datetime

BaseController = controllers.base.BaseController
SectionsController = controllers.sections.SectionsController
UsersHelper = helpers.users.UsersHelper
UsersModel = models.users.UsersModel
CentersModel = models.centers.CentersModel
SectionsModel = models.sections.SectionsModel


class CentersController(BaseController):
    def sendCenters(self, chat_id):
        controller_name = self.__class__.__name__
        is_admin = UsersHelper.is_admin(self.session, chat_id)
        centers = self.session.query(CentersModel).all()
        send_text = 'Пока нет ни одного центра'
        if centers:
            send_text = 'Выберите центр из списка:'

        keyboard = self.get_keyboard(centers, is_admin)

        if is_admin:
            callback = {"action": controller_name + ".add"}
            button = types.InlineKeyboardButton(text="Добавить", callback_data=json.dumps(callback))
            keyboard.add(button)

        self.bot.send_message(chat_id, send_text, reply_markup=keyboard)

    def add_callback(self, message, item_id):
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

    def update_callback(self, message, update_id):
        data = {"name": message.text, "updated": datetime.now()}
        self.session.query(CentersModel).filter_by(id=update_id).update(data)
        self.session.commit()
        self.sendCenters(message.chat.id)

    def check_relations(self, center_id):
        users = self.session.query(UsersModel).filter_by(center_id=center_id).first()
        centers = self.session.query(SectionsModel).filter_by(center_id=center_id).first()
        return not users and not centers

    def select(self, message, center_id):
        UsersHelper.update_center(self.session, message.chat.id, center_id)
        posts = SectionsController(self.session, self.bot)
        posts.select(message)
