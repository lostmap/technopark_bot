import telebot
from telebot import types
import requests
import urllib

import bandsintown1 as bit

from bandsintown import Client
client = Client('technopark_ruliiiit')


token = '403882463:AAGFabioSaA1uY5Iku7v-lXVJegeIoP-J3E'
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=["text"])
def handle_message(message):
    events = client.events(message.text)
    my_message = bit.create_message(events)
    bot.send_message(message.chat.id, my_message)

    # send_photo(message)


#
# def send_photo(message):
#     bot.send_chat_action(message.chat.id, 'upload_photo')
#     bot.send_photo(message.chat.id, )













if __name__ == '__main__':

    bot.polling(none_stop=True)
