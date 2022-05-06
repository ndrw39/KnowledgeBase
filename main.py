import telebot
import json
import config
from helpers.users import UsersHelper
from controllers.centers import CentersController
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# create bd session
engine = create_engine(config.DATABASE_URL)
declarative_base = declarative_base()
declarative_base.metadata.create_all(engine)
session = sessionmaker(bind=engine)
session = session()

# connect telegram
bot = telebot.TeleBot(config.API_TOKEN)

# instance
center_controller = CentersController(session, bot)

assoc_controllers = {
    "CentersController": center_controller,
}


@bot.message_handler(commands=['start'])
def start_command(message):
    user_data = UsersHelper.getUser(session, message.chat.id)
    if not user_data:
        data = [
            session,
            message.chat.id,
            message.chat.firstname,
            message.chat.lastname
        ]
        user_data = UsersHelper.createUser(*data)

    is_admin = user_data.type == "admin"

    if not user_data.center_id or is_admin:
        center_controller.sendCenters(message.chat.id)
        return


@bot.callback_query_handler(func=lambda callback: True)
def all_callbacks(callback):
    callback_data = json.loads(callback.data)
    if "action" not in callback_data:
        return

    parts = callback_data["action"].split(".")
    controller = parts[0]
    method = parts[1]
    arguments = [callback.message]

    if controller not in assoc_controllers:
        return

    if "item_id" in callback_data:
        arguments.append(callback_data["item_id"])

    call_method = getattr(assoc_controllers[controller], method)
    call_method(*arguments)


bot.polling(none_stop=True, interval=0)
