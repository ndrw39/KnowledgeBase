import json
import math
import config
import translate
from telebot import types
from datetime import datetime
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
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
        if "media" not in json_prs or "entities" not in json_prs:
            if "text" not in json_prs:
                return

            text = json_prs["text"]
            json_prs = {
                "text": text,
                "entities": [],
                "media": []
            }

        if not json_prs["media"]:
            entities = []
            for entity in json_prs["entities"]:
                entities.append(types.MessageEntity.de_json(entity))

            self.bot.send_message(message.chat.id, json_prs["text"], entities=entities)
            return

        i = 0
        media_group = []
        for media in json_prs["media"]:
            if "type" not in media or "file_id" not in media:
                continue

            i += 1
            if i == 1:
                entities = []
                for entity in json_prs["entities"]:
                    entities.append(types.MessageEntity.de_json(entity))

                data = {
                    "type": media["type"],
                    "media": media["file_id"],
                    "caption": json_prs["text"],
                    "caption_entities": entities
                }
                media_group.append(types.InputMedia(**data))
                continue

            media_group.append(types.InputMedia(media["type"], media["file_id"]))
        try:
            self.bot.send_media_group(message.chat.id, media=media_group)
        except ApiTelegramException:
            self.bot.send_message(message.chat.id, translate.MEDIA_ERROR)

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
        if not message.text:
            self.bot.send_message(message.chat.id, translate.TEXT_ONLY)
            return

        self.bot.send_message(message.chat.id, translate.ENTER_POST_CONTENT)
        self.bot.register_next_step_handler(message, self.add_callback_save, message.text, section_id)

    def add_callback_save(self, message: Message, name: str, section_id: int) -> None:
        if not message.text:
            self.bot.send_message(message.chat.id, translate.TEXT_ONLY)
            return

        entities = []
        if "entities" in message.json:
            entities = message.json["entities"]

        json_data = {
            "text": message.text,
            "entities": entities,
            "media": []
        }

        data = {
            "name": name,
            "section_id": section_id,
            "json": json.dumps(json_data),
            "created": datetime.now(),
            "updated": datetime.now()
        }

        add = PostsModel(**data)
        self.session.add(add)
        self.session.commit()
        self.session.refresh(add)
        self.add_media(message, add.id)

    def add_media(self, message: Message, post_id: int):
        controller_name = self.__class__.__name__
        keyboard = types.InlineKeyboardMarkup()

        post = self.session.query(PostsModel).filter_by(id=post_id).first()

        callback = {"action": controller_name + ".view", "params": post.section_id}
        button1 = types.InlineKeyboardButton(text=translate.SAVE, callback_data=json.dumps(callback))

        callback = {"action": controller_name + ".add_media_callback", "params": post_id}
        button2 = types.InlineKeyboardButton(text=translate.ATTACH_MEDIA, callback_data=json.dumps(callback))
        keyboard.add(button1, button2)

        self.bot.send_message(message.chat.id, translate.SELECT_WHAT_NEXT, reply_markup=keyboard)

    def add_media_callback(self, message: Message, post_id: int):
        self.bot.send_message(message.chat.id, translate.ENTER_FILE)
        self.bot.register_next_step_handler(message, self.add_media_save, post_id)

    def add_media_save(self, message: Message, post_id: int):
        post = self.session.query(PostsModel).filter_by(id=post_id).first()
        if not post:
            return

        add_data = json.loads(post.json)
        json_data = message.json

        # Checking document (document can't be mixed with other media types)
        if add_data["media"]:
            for media in add_data["media"]:
                if ("document" in json_data and media["type"] != "document") \
                        or ("document" not in json_data and media["type"] == "document"):

                    self.bot.send_message(message.chat.id, translate.DOCUMENT_MIXED)
                    self.add_media(message, post_id)
                    return

                if ("voice" in json_data and media["type"] != "audio") \
                        or ("voice" not in json_data and media["type"] == "audio"):

                    self.bot.send_message(message.chat.id, translate.AUDIO_MIXED)
                    self.add_media(message, post_id)
                    return

                if ("audio" in json_data and media["type"] != "audio") \
                        or ("audio" not in json_data and media["type"] == "audio"):

                    self.bot.send_message(message.chat.id, translate.AUDIO_MIXED)
                    self.add_media(message, post_id)
                    return

        if "media" not in add_data:
            add_data["media"] = []

        if "entities" not in add_data:
            add_data["media"] = []

        if "photo" in json_data:
            add_data["media"].append({"type": "photo", "file_id": json_data["photo"][3]["file_id"]})
        elif "video" in json_data:
            add_data["media"].append({"type": "video", "file_id": json_data["video"]["file_id"]})
        elif "document" in json_data:
            add_data["media"].append({"type": "document", "file_id": json_data["document"]["file_id"]})
        elif "voice" in json_data:
            add_data["media"].append({"type": "audio", "file_id": json_data["voice"]["file_id"]})
        elif "audio" in json_data:
            add_data["media"].append({"type": "audio", "file_id": json_data["audio"]["file_id"]})
        else:
            self.bot.send_message(message.id, translate.UNDEFINED_TYPE)
            return

        data = {
            "json": json.dumps(add_data),
            "updated": datetime.now()
        }

        self.session.query(PostsModel).filter_by(id=post_id).update(data)
        self.session.commit()
        self.add_media(message, post_id)

    # Update
    def update_callback(self, message: Message, section_id: int) -> None:
        if not message.text:
            self.bot.send_message(message.chat.id, translate.TEXT_ONLY)
            return

        self.bot.send_message(message.chat.id, translate.ENTER_POST_CONTENT)
        self.bot.register_next_step_handler(message, self.update_callback_save, message.text, section_id)

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

    def get_inline_keyboard(self, data, is_admin: bool) -> types.InlineKeyboardMarkup:
        """Getting inline keyboard by model data"""
        controller_name = self.__class__.__name__
        keyboard = types.InlineKeyboardMarkup()
        if not data:
            return keyboard

        for item in data:
            callback = {"action": controller_name + ".select", "params": item.id}
            button = types.InlineKeyboardButton(text=item.name, callback_data=json.dumps(callback))
            keyboard.add(button)

            if is_admin:
                callback = {"action": controller_name + ".update", "params": item.id}
                button1 = types.InlineKeyboardButton(text=translate.CHANGE, callback_data=json.dumps(callback))
                callback = {"action": controller_name + ".add_media", "params": item.id}
                button2 = types.InlineKeyboardButton(text=translate.ATTACH_MEDIA, callback_data=json.dumps(callback))
                keyboard.add(button1, button2)

                callback = {"action": controller_name + ".change_sort", "params": item.id}
                button = types.InlineKeyboardButton(text=translate.CHANGE_SORT, callback_data=json.dumps(callback))
                keyboard.add(button)

        return keyboard
