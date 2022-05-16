import json
import math

import config
import translate
from telebot import types
from datetime import datetime
from telebot.types import Message
from controllers.base import BaseController
from helpers.users import UsersHelper
from helpers.sections import SectionsHelper
from models.posts import PostsModel
from helpers.router import Router


class PostsController(BaseController):
    # Select
    def select(self, message: Message, post_id: int = None) -> None:
        post = self.session.query(PostsModel).filter_by(id=post_id).first()
        if not post:
            return

        json_prs = json.loads(post.json)

        if "text" in json_prs:
            entities = None
            if "entities" in json_prs:
                entities = []
                for entity in json_prs["entities"]:
                    entities.append(types.MessageEntity.de_json(entity))

            self.bot.send_message(message.chat.id, json_prs["text"], entities=entities)
        else:
            media_group = []
            if "photo" in json_prs:
                photo = json_prs["photo"]
                caption = None
                if "caption" in json_prs:
                    caption = json_prs["caption"]
                media_group.append(types.InputMediaPhoto(photo[3]["file_id"], caption=caption))
                self.bot.send_media_group(message.chat.id, media=media_group)

    # View
    def view(self, message: Message, section_id: int = None, page: int = 0) -> None:
        controller_name = self.__class__.__name__
        per_page = config.PER_PAGE

        count = self.session.query(PostsModel) \
            .filter_by(section_id=section_id) \
            .count()

        posts = self.session.query(PostsModel). \
            filter_by(section_id=section_id). \
            order_by(PostsModel.sort.asc()). \
            limit(per_page).offset(per_page * int(page))

        user_data = UsersHelper.getUser(message.chat.id)
        is_admin = user_data.type == "admin"

        # Keyboard
        keyboard = self.get_inline_keyboard(posts.all(), is_admin)

        # Pagination
        max_pages = math.ceil(count / per_page) - 1
        paginator_buttons = []
        if int(page) > 0:
            return_page = str(int(page) - 1)
            callback = {"action": controller_name + ".view", "params": str(section_id) + "|" + return_page}
            button = types.InlineKeyboardButton(text=translate.RETURN, callback_data=json.dumps(callback))
            paginator_buttons.append(button)

        if count > per_page and not (max_pages == int(page)):
            return_page = str(int(page) + 1)
            callback = {"action": controller_name + ".view", "params": str(section_id) + "|" + return_page}
            button = types.InlineKeyboardButton(text=translate.NEXT, callback_data=json.dumps(callback))
            paginator_buttons.append(button)

        if len(paginator_buttons) > 0:
            keyboard.add(*paginator_buttons)

        if is_admin:
            callback = {"action": controller_name + ".add", "params": section_id}
            button = types.InlineKeyboardButton(text=translate.ADD, callback_data=json.dumps(callback))
            keyboard.add(button)

        if section_id:
            section = SectionsHelper.get_parent(section_id)
            if section:
                callback = {"action": "SectionsController.select", "params": section.parent_id}
                button = types.InlineKeyboardButton(text=translate.RETURN, callback_data=json.dumps(callback))
                keyboard.add(button)

        self.bot.delete_message(message.chat.id, message.message_id)
        breadcrumbs = SectionsHelper.get_breadcrumbs(user_data.center_id, section_id)
        self.bot.send_message(message.chat.id, breadcrumbs, reply_markup=keyboard)

    # Add
    def add_callback(self, message: Message, section_id: int) -> None:
        name = message.text
        if not name:
            self.bot.send_message(message.chat.id, translate.TEXT_ONLY)
            return

        self.bot.send_message(message.chat.id, translate.ENTER_POST_CONTENT)
        self.bot.register_next_step_handler(message, self.add_callback_save, name, section_id)

    def add_callback_save(self, message: Message, name: str, section_id: int) -> None:
        data = {
            "name": name,
            "section_id": section_id,
            "json": json.dumps(message.json),
            "created": datetime.now(),
            "updated": datetime.now()
        }

        add = PostsModel(**data)
        self.session.add(add)
        self.session.commit()
        self.view(message, section_id)

    # Update
    def update_callback(self, message: Message, section_id: int) -> None:
        name = message.text
        if not name:
            self.bot.send_message(message.chat.id, translate.TEXT_ONLY)
            return

        self.bot.send_message(message.chat.id, translate.ENTER_POST_CONTENT)
        self.bot.register_next_step_handler(message, self.update_callback_save, name, section_id)

    def update_callback_save(self, message: Message, name: str, update_id: int) -> None:
        data = {
            "name": name,
            "json": json.dumps(message.json),
            "updated": datetime.now()
        }

        self.session.query(PostsModel).filter_by(id=update_id).update(data)
        self.session.commit()
        post = self.session.query(PostsModel).filter_by(id=update_id).first()
        if not post:
            return

        self.view(message, post.section_id)

    # Delete
    def delete(self, message: Message, delete_id: int) -> None:
        if not UsersHelper.is_admin(message.chat.id):
            return

        post = self.session.query(PostsModel).filter_by(id=delete_id).first()
        if not post:
            return

        section_id = post.section_id
        self.session.query(PostsModel).filter_by(id=delete_id).delete()
        self.session.commit()

        Router("SectionsController", "select", [message, section_id])

    # Sort
    def change_sort_callback(self, message: Message, update_data: dict, update_id: int) -> None:
        self.session.query(PostsModel).filter_by(id=update_id).update(update_data)
        self.session.commit()
        post = self.session.query(PostsModel).filter_by(id=update_id).first()
        if not post:
            return

        self.view(message, post.section_id)
