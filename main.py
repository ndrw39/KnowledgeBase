import telebot
import sys
sys.path.append('models')
from users import *
from telebot import types
from config import DATABASE_URL, API_TOKEN
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# create bd session
engine = create_engine(DATABASE_URL)
declarativeBase = declarative_base()
declarativeBase.metadata.create_all(engine)
session = sessionmaker(bind=engine)
bd = session()

# connect telegram
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def startCommand(message):
        userData = bd.query(Users).filter_by(chat_id=message.chat.id).one()
        # create new user
        if not userData:
            data = {
               "chat_id": message.chat.id,
               "firstname": message.chat.first_name,
               "lastname": message.chat.last_name,
               "type": "user",
               "state": "start",
               "created": datetime.now(),
               "updated": datetime.now()
            }
            add = Users(**data)
            bd.add(add)
            bd.commit()
            userData = bd.query(Users).filter_by(chat_id=message.chat.id).one()

        if not userData:
            bot.send_message(message.chat.id, 'Sorry, undefined error')
            return

        if userData.type == 'admin':
            bot.send_message(message.chat.id, 'admin')
        else:
            bot.send_message(message.chat.id, 'user')

bot.polling(none_stop=True, interval=0)