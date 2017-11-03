import telebot
from telebot import types

import bandsintown1

from bandsintown import Client
client = Client('technopark_ruliiiit')


token = '403882463:AAGFabioSaA1uY5Iku7v-lXVJegeIoP-J3E'
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=["text"])
def handle_message(message):
    events = client.search(message.text, location='Moscow,Ru')
    mymessage = bandsintown1.create_message(events)
    print(mymessage)
    bot.send_message(message.chat.id, mymessage)











if __name__ == '__main__':

    bot.polling(none_stop=True)
