import telebot
from telebot import types
import requests
import urllib

from telebot.types import MessageEntity

import musicgraph1 as mg

import bandsintown1 as bit

from bandsintown import Client
client = Client('technopark_ruliiiit')


token = '403882463:AAGFabioSaA1uY5Iku7v-lXVJegeIoP-J3E'
bot = telebot.TeleBot(token)




# @bot.message_handler(content_types=["text"])
# def artist_search(message):
#     events = client.events(message.text)
#     try:
#         my_messages = bit.create_message(events)
#         for my_message in my_messages:
#             bot.send_message(message.chat.id, my_message)
#     except Exception:
#         bot.send_message(message.chat.id, "Концерты " + message.text + " не найдены" )


@bot.message_handler(content_types=["text"])
def artist_search(message):
    # events = client.events(message.text)
    # my_messages = bit.create_message(events)
    # for my_message in my_messages:
    #     bot.send_message(message.chat.id, my_message)

    bot.sendPhoto(message.chat.id, )


# @bot.message_handler(content_types=["text"])
# def event_search_by_genre(message):
#     my_artists = mg.get_by_genre(message.text)
#     bot.send_message(message.chat.id, "\n".join(my_artists))
#     for artist in my_artists:
#         try:
#             events = client.events(artist)
#             my_messages = bit.create_message(events)
#             bot.send_message(message.chat.id, "\n".join(my_messages))
#         except Exception:
#             print ("Mist")



# @bot.message_handler(content_types=["text"])
# def date_search(message):
#     events = client.search(message.text,  location='Moscow,Ru', date='2017-12-30,2018-03-25')
#     my_messages = bit.create_message(events)
#     for my_message in my_messages:
#         bot.send_message(message.chat.id, my_message)


# @bot.message_handler(content_types=["text"])
# def recommendations(message):
#     events = client.recommended(message.text, location='Moscow,Ru', only_recs=True)
#     my_messages = bit.create_message(events)
#     for my_message in my_messages:
#         bot.send_message(message.chat.id, my_message)




if __name__ == '__main__':

    bot.polling(none_stop=True)
