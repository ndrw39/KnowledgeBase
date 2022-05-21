import json
from common.bot import BotConnection as bot
from helpers.users import UsersHelper
from helpers.router import Router

admins = UsersHelper.get_admins()
for admin in admins:
    bot().send_message(admin.chat_id, "Bot was started")


@bot().message_handler(commands=['start'])
def start_command(message):
    bot().clear_step_handler_by_chat_id(chat_id=message.chat.id)
    user_data = UsersHelper.getUser(message.chat.id)
    if not user_data:
        user_data = UsersHelper.createUser(message.chat.id, message.chat.first_name, message.chat.last_name)

    if not user_data.center_id:
        Router("CentersController", "view", [message])
        return

    Router("SectionsController", "select", [message])


@bot().message_handler(commands=['change'])
def change_type(message):
    bot().clear_step_handler_by_chat_id(chat_id=message.chat.id)

    user_data = UsersHelper.getUser(message.chat.id)
    if not user_data:
        return

    is_admin = user_data.type == "admin"
    if not user_data.change_type == 1:
        return

    if is_admin:
        UsersHelper.change_type(message.chat.id, "user")
    else:
        UsersHelper.change_type(message.chat.id, "admin")

    start_command(message)


@bot().message_handler(content_types=['text'])
def change_center(message):
    bot().clear_step_handler_by_chat_id(chat_id=message.chat.id)

    if message.text == "Сменить центр":
        Router("CentersController", "view", [message])
    elif message.text == "Новости":
        bot().send_message(message.chat.id, "Скоро будет")
    elif message.text == "На главную":
        start_command(message)


@bot().callback_query_handler(func=lambda callback: True)
def all_callbacks(callback):
    bot().clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)

    callback_data = json.loads(callback.data)
    if "action" not in callback_data:
        return

    parts = callback_data["action"].split(".")
    controller = parts[0]
    method = parts[1]
    arguments = [callback.message]

    types = {
        "None": None,
        "False": False,
        "True": True
    }

    if "params" in callback_data:
        params = str(callback_data["params"])
        parts = params.split("|")
        for part in parts:
            if part in types:
                part = types[part]

            arguments.append(part)

    Router(controller, method, arguments)


bot().polling(none_stop=True, interval=0)
