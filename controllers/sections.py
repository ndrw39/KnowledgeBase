import json
from telebot import types
from datetime import datetime
from controllers.base import BaseController
from helpers.users import UsersHelper
from models.posts import PostsModel
from models.sections import SectionsModel
from helpers.sections import SectionsHelper
from helpers.router import Router


class SectionsController(BaseController):
    per_page = 5

    def question_add(self, message, parent_id) -> None:
        controller_name = self.__class__.__name__
        keyboard = types.InlineKeyboardMarkup()

        post = self.session.query(SectionsModel).filter_by(parent_id=parent_id).first()
        if post:
            self.add(message, parent_id)
            return

        callback = {"action": controller_name + ".add", "params": parent_id}
        button1 = types.InlineKeyboardButton(text='Раздел', callback_data=json.dumps(callback))
        callback = {"action": "PostsController.add", "params": parent_id}
        button2 = types.InlineKeyboardButton(text='Пост', callback_data=json.dumps(callback))
        keyboard.add(button1, button2)

        self.bot.delete_message(message.chat.id, message.message_id)
        self.bot.send_message(message.chat.id, "Выберите что добавить:", reply_markup=keyboard)

    def add_callback(self, message, parent_id) -> None:
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
        self.select(message, parent_id)

    def select(self, message, parent_id=None, page=0) -> None:
        allow_post = self.session.query(PostsModel).filter_by(section_id=parent_id).first()
        if allow_post:
            Router("PostsController", "view_posts", [message, parent_id])
            return

        controller_name = self.__class__.__name__
        user_data = UsersHelper.getUser(message.chat.id)
        if not user_data:
            return

        center_id = user_data.center_id
        count = self.session.query(SectionsModel) \
            .filter_by(parent_id=parent_id, center_id=center_id) \
            .count()

        sections = self.session.query(SectionsModel). \
            filter_by(parent_id=parent_id, center_id=center_id)

        is_admin = UsersHelper.is_admin(message.chat.id)
        if count > 0:
            sections.limit(self.per_page).offset(self.per_page * page)

        keyboard = self.get_keyboard(sections.all(), is_admin)

        if is_admin:
            callback = {"action": controller_name + ".question_add", "params": parent_id}
            button = types.InlineKeyboardButton(text="Добавить", callback_data=json.dumps(callback))
            keyboard.add(button)

        if parent_id:
            section = SectionsHelper.get_parent(parent_id)
            if section:
                callback = {"action": controller_name + ".select", "params": section.parent_id}
                button = types.InlineKeyboardButton(text='Назад', callback_data=json.dumps(callback))
                keyboard.add(button)

        self.bot.delete_message(message.chat.id, message.message_id)
        breadcrumbs = SectionsHelper.get_breadcrumbs(center_id, parent_id)
        self.bot.send_message(message.chat.id, breadcrumbs, reply_markup=keyboard)

    def update_callback(self, message, update_id) -> None:
        data = {"name": message.text, "updated": datetime.now()}
        self.session.query(SectionsModel).filter_by(id=update_id).update(data)
        self.session.commit()
        section = SectionsHelper.get_parent(update_id)
        if section:
            self.select(message, section.parent_id)

    def delete(self, message, delete_id) -> None:
        posts = self.session.query(PostsModel).filter_by(section_id=delete_id).first()
        section = self.session.query(SectionsModel).filter_by(parent_id=delete_id).first()

        if posts or section:
            text = "Нельзя удалить раздел, сначала удалите посты или разделы внутри"
            self.bot.send_message(message.chat.id, text)
            return

        self.session.query(SectionsModel).filter_by(id=delete_id).delete()
        section = SectionsHelper.get_parent(delete_id)

        if section:
            self.select(message, section.parent_id)

        self.select(message)

    def check_relations(self, section_id) -> bool:
        section = self.session.query(PostsModel).filter_by(section_id=section_id).first()
        return not section
