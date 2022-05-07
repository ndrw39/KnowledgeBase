import json
import controllers
import helpers
import models

from telebot import types
from datetime import datetime

BaseController = controllers.base.BaseController
SectionsController = controllers.sections.SectionsController
UsersHelper = helpers.users.UsersHelper
PostsModel = models.posts.PostsModel


class PostsController(BaseController):
    per_page = 5

    def add_callback(self, message, section_id):
        if not UsersHelper.is_admin(self.session, message.chat.id):
            return

        name = message.text
        self.bot.send_message(message.chat.id, "Теперь отправьте содержание поста")
        self.bot.register_next_step_handler(message, self.add_callback_save, name, section_id)

    def add_callback_save(self, message, post_name, section_id):
        data = {
            "name": post_name,
            "section_id": section_id,
            "text":  message.text,
            "created": datetime.now(),
            "updated": datetime.now()
        }

        add = PostsModel(**data)
        self.session.add(add)
        self.session.commit()
        self.view_posts(message, section_id)

    def delete(self, message, delete_id):
        pass

    def update_callback(self, message, update_id):
        pass

    def view_posts(self, message, section_id=None, page=0):
        controller_name = self.__class__.__name__
        count = self.session.query(PostsModel) \
            .filter_by(section_id=section_id) \
            .count()

        posts = self.session.query(PostsModel). \
            filter_by(section_id=section_id)

        user_data = UsersHelper.getUser(self.session, message.chat.id)
        is_admin = user_data.type == "admin"
        if count > 0:
            posts.limit(self.per_page).offset(self.per_page * page)

        keyboard = self.get_keyboard(posts.all(), is_admin)

        if is_admin:
            callback = {"action": controller_name + ".question_add", "params": section_id}
            button = types.InlineKeyboardButton(text="Добавить", callback_data=json.dumps(callback))
            keyboard.add(button)

        sections = SectionsController(self.session, self.bot)

        if section_id:
            section = sections.get_parent(section_id)
            if section:
                callback = {"action": "SectionsController.select", "params": section.parent_id}
                button = types.InlineKeyboardButton(text='Назад', callback_data=json.dumps(callback))
                keyboard.add(button)

        self.bot.delete_message(message.chat.id, message.message_id)
        breadcrumbs = sections.get_breadcrumbs(user_data.center_id, section_id)
        self.bot.send_message(message.chat.id, breadcrumbs, reply_markup=keyboard)

    def select(self, message, post_id):
        posts = self.session.query(PostsModel). \
            filter_by(id=post_id).first()

        if not posts:
            return

        self.bot.send_message(message.chat.id, posts.text)
