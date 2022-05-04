import telebot
import sys
import json
sys.path.append('models')
from usersModel import *
from centersModel import *
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
        userData = usersModel.getOrCreateByTg(bd, message)
        if not userData:
            bot.send_message(message.chat.id, 'Sorry, undefined error')
            return

        centers = centersModel.getAll(bd)
        keyboard = types.InlineKeyboardMarkup()
        if centers:
            text = 'Выберите центр из списка:'
            i = 0
            for center in centers:
                i += 1
                callback = '{"action" : "getCenter", "id" : ' + str(center.id) + '}'
                button = types.InlineKeyboardButton(text=str(i) + ") " + center.name, callback_data=callback)
                keyboard.add(button)

                if userData.type == 'admin':
                    callback = '{"action" : "updateCenter", "id" : ' + str(center.id) + '}'
                    button1 = types.InlineKeyboardButton(text='🖋 Изменить', callback_data=callback)
                    callback = '{"action" : "deleteCenter", "id" : ' + str(center.id) + '}'
                    button2 = types.InlineKeyboardButton(text='❌ Удалить', callback_data=callback)
                    keyboard.add(button1, button2)
        else:
            text = '😐 Пока нет ни одного центра'

        if userData.type == 'admin':
            callback = '{"action" : "addCenter"}'
            button = types.InlineKeyboardButton(text="✅ Добавить центр", callback_data=callback)
            keyboard.add(button)

        bot.send_message(message.chat.id, text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: True)
def allCallbacks(callback):
    callbackData = json.loads(callback.data)
    if not 'action' in callbackData:
        bot.send_message(message.chat.id, 'Sorry, undefined error')
        return

    if callbackData['action'] == 'addCenter':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Введите название центра:')
        bot.register_next_step_handler(callback.message,addCenterCallback)
        return

    if callbackData['action'] == 'updateCenter':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Введите название центра:')
        bot.register_next_step_handler(callback.message,updateCenterCallback, callbackData['id'])
        return

    if callbackData['action'] == 'deleteCenter':
        centersModel.delete(bd, callbackData['id'])
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        startCommand(callback.message)
        return

def addCenterCallback(message):
    centersModel.add(bd, message.text)
    startCommand(message)

def updateCenterCallback(message, updateID):
    centersModel.update(bd, updateID, message.text)
    startCommand(message)

bot.polling(none_stop=True, interval=0)