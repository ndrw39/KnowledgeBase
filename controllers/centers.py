import json
import translate
from datetime import datetime
from telebot.types import Message
from telebot.types import InlineKeyboardButton
from controllers.base import BaseController
from helpers.users import UsersHelper
from helpers.router import Router
from models.users import UsersModel
from models.centers import CentersModel
from models.sections import SectionsModel


class CentersController(BaseController):
    # Select
    def select(self, message: Message, center_id: int) -> None:
        UsersHelper.update_center(message.chat.id, center_id)
        self.bot.send_message(message.chat.id, translate.REMEMBER, reply_markup=self.get_keyboard())
        Router("SectionsController", "select", [message])

    # View
    def view(self, message: Message, center_id: int = None, page: int = 0) -> None:
        controller_name = self.__class__.__name__
        is_admin = UsersHelper.is_admin(message.chat.id)
        centers = self.session.query(CentersModel)\
            .order_by(CentersModel.sort.asc())\
            .all()

        send_text = translate.EMPTY_CENTERS
        if centers:
            send_text = translate.SELECT_CENTERS

        keyboard = self.get_inline_keyboard(centers, is_admin)
        if is_admin:
            callback = {"action": controller_name + ".add"}
            button = InlineKeyboardButton(text=translate.ADD, callback_data=json.dumps(callback))
            keyboard.add(button)

        self.bot.send_message(message.chat.id, send_text, reply_markup=keyboard)

    # Add
    def add_callback(self, message: Message, center_id: int) -> None:
        data = {"name": message.text, "created": datetime.now(), "updated": datetime.now()}
        add = CentersModel(**data)

        self.session.add(add)
        self.session.commit()
        self.view(message)

    # Update
    def update_callback(self, message: Message, update_id: int) -> None:
        data = {"name": message.text, "updated": datetime.now()}
        self.session.query(CentersModel).filter_by(id=update_id).update(data)
        self.session.commit()
        self.view(message)

    # Delete
    def delete(self, message: Message, delete_id: int) -> None:
        if not UsersHelper.is_admin(message.chat.id):
            return

        users = self.session.query(UsersModel).filter_by(center_id=delete_id).first()
        section = self.session.query(SectionsModel).filter_by(center_id=delete_id).first()
        if not users and not section:
            return

        self.bot.delete_message(message.chat.id, message.message_id)
        self.session.query(CentersModel).filter_by(id=delete_id).delete()
        self.session.commit()
        self.view(message)

    # Sort
    def change_sort_callback(self, message: Message, update_data: dict, update_id: int) -> None:
        self.session.query(CentersModel).filter_by(id=update_id).update(update_data)
        self.session.commit()
        self.view(message)


