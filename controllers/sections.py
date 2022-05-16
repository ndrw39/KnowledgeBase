import json
import math
import config
import translate
from telebot import types
from datetime import datetime
from telebot.types import Message
from controllers.base import BaseController
from helpers.users import UsersHelper
from models.posts import PostsModel
from models.sections import SectionsModel
from helpers.sections import SectionsHelper
from helpers.router import Router


class SectionsController(BaseController):
    # Select
    def select(self, message: Message, section_id: int = None) -> None:
        allow_post = self.session.query(PostsModel).filter_by(section_id=section_id).first()
        if allow_post:
            Router("PostsController", "view", [message, section_id])
            return

        self.view(message, section_id)

    # View
    def view(self, message: Message, section_id: int = None, page: int = 0) -> None:
        controller_name = self.__class__.__name__
        per_page = config.PER_PAGE
        user_data = UsersHelper.getUser(message.chat.id)
        if not user_data:
            return

        center_id = user_data.center_id
        count = self.session.query(SectionsModel) \
            .filter_by(parent_id=section_id, center_id=center_id) \
            .count()

        sections = self.session.query(SectionsModel). \
            filter_by(parent_id=section_id, center_id=center_id). \
            order_by(SectionsModel.sort.asc()). \
            limit(per_page).offset(per_page * int(page))

        is_admin = UsersHelper.is_admin(message.chat.id)

        # Keyboard
        keyboard = self.get_inline_keyboard(sections.all(), is_admin)

        # Pagination
        max_pages = math.ceil(count / per_page) - 1
        paginator_buttons = []
        if int(page) > 0:
            return_page = str(int(page) - 1)
            callback = {"action": controller_name + ".select", "params": str(section_id) + "|" + return_page}
            button = types.InlineKeyboardButton(text=translate.RETURN, callback_data=json.dumps(callback))
            paginator_buttons.append(button)

        if count > per_page and not (max_pages == int(page)):
            return_page = str(int(page) + 1)
            callback = {"action": controller_name + ".select", "params": str(section_id) + "|" + return_page}
            button = types.InlineKeyboardButton(text=translate.NEXT, callback_data=json.dumps(callback))
            paginator_buttons.append(button)

        if len(paginator_buttons) > 0:
            keyboard.add(*paginator_buttons)

        # Add button and sort
        if is_admin:
            callback = {"action": controller_name + ".add", "params": section_id}
            button = types.InlineKeyboardButton(text=translate.ADD, callback_data=json.dumps(callback))
            keyboard.add(button)

        # Return button
        if section_id:
            section = SectionsHelper.get_parent(section_id)
            if section:
                callback = {"action": controller_name + ".select", "params": section.parent_id}
                button = types.InlineKeyboardButton(text=translate.RETURN, callback_data=json.dumps(callback))
                keyboard.add(button)

        self.bot.delete_message(message.chat.id, message.message_id)
        breadcrumbs = SectionsHelper.get_breadcrumbs(center_id, section_id)
        self.bot.send_message(message.chat.id, breadcrumbs, reply_markup=keyboard)

        if count == 0 and not section_id:
            self.bot.send_message(message.chat.id, translate.EMPTY, reply_markup=self.get_keyboard())

    # Add
    def add(self, message: Message, parent_id: int = None) -> None:
        controller_name = self.__class__.__name__
        keyboard = types.InlineKeyboardMarkup()

        post = self.session.query(SectionsModel).filter_by(parent_id=parent_id).first()
        if post:
            self.add_callback(message, parent_id)
            return

        callback = {"action": controller_name + ".add_callback", "params": parent_id}
        button1 = types.InlineKeyboardButton(text=translate.SECTION, callback_data=json.dumps(callback))
        callback = {"action": "PostsController.add", "params": parent_id}
        button2 = types.InlineKeyboardButton(text=translate.POST, callback_data=json.dumps(callback))
        keyboard.add(button1, button2)

        self.bot.delete_message(message.chat.id, message.message_id)
        self.bot.send_message(message.chat.id, translate.SELECT_ADD_TYPE, reply_markup=keyboard)

    def add_callback(self, message: Message, parent_id: int = None) -> None:
        user = UsersHelper.getUser(message.chat.id)
        if not user.type == "admin" or not user.center_id:
            return

        data = {
            "name": message.text,
            "parent_id": parent_id,
            "created": datetime.now(),
            "updated": datetime.now(),
            "center_id": user.center_id
        }

        add = SectionsModel(**data)
        self.session.add(add)
        self.session.commit()
        self.view(message, parent_id)

    # Update
    def update_callback(self, message: Message, update_id: int) -> None:
        data = {"name": message.text, "updated": datetime.now()}
        self.session.query(SectionsModel).filter_by(id=update_id).update(data)
        self.session.commit()
        section = SectionsHelper.get_parent(update_id)
        if section:
            self.select(message, section.parent_id)

    # Delete
    def delete(self, message: Message, delete_id: int) -> None:
        if not UsersHelper.is_admin(message.chat.id):
            return

        posts = self.session.query(PostsModel).filter_by(section_id=delete_id).first()
        section = self.session.query(SectionsModel).filter_by(parent_id=delete_id).first()

        if posts or section:
            text = translate.RELATIONS_ERROR
            self.bot.send_message(message.chat.id, text)
            return

        self.session.query(SectionsModel).filter_by(id=delete_id).delete()
        self.session.commit()
        section = SectionsHelper.get_parent(delete_id)

        if section:
            self.select(message, section.parent_id)

        self.select(message)

    # Sort
    def change_sort_callback(self, message: Message, update_data: dict, update_id: int) -> None:
        self.session.query(SectionsModel).filter_by(id=update_id).update(update_data)
        self.session.commit()

        section = SectionsHelper.get_parent(update_id)
        if section:
            self.view(message, section.parent_id)
