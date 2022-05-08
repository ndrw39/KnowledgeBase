import json
from common.bot import BotConnection
from helpers.users import UsersHelper
from helpers.router import Router


@BotConnection().message_handler(commands=['start'])
def start_command(message):
    user_data = UsersHelper.getUser(message.chat.id)
    if not user_data:
        user_data = UsersHelper.createUser(message.chat.id, message.chat.first_name, message.chat.last_name)

    if not user_data.center_id:
        Router("CentersController", "send_centers", [message.chat.id])
        return

    Router("SectionsController", "select", [message])


@BotConnection().callback_query_handler(func=lambda callback: True)
def all_callbacks(callback):
    callback_data = json.loads(callback.data)
    if "action" not in callback_data:
        return

    parts = callback_data["action"].split(".")
    controller = parts[0]
    method = parts[1]
    arguments = [callback.message]

    if "params" in callback_data:
        arguments.append(callback_data["params"])

    Router(controller, method, arguments)


@BotConnection().message_handler(commands=['change_type'])
def change_type(message):
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


BotConnection().polling(none_stop=True, interval=0)
