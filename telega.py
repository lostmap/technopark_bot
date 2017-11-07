import telebot
from telebot import types
import requests
import urllib
from telebot.types import MessageEntity

import musicgraph1 as mg

import bandsintown1 as bit

import sqlite3

from bandsintown import Client
client = Client('technopark_ruliiiit')


token = '403882463:AAGFabioSaA1uY5Iku7v-lXVJegeIoP-J3E'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def artist_search(message):
    conn = sqlite3.connect('music_bot.sqlite')
    c = conn.cursor()
    user_id = message.from_user.id
    c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    if row is None:
        c.execute("insert into users values (?, ?) ", (user_id, user_id))
        conn.commit()
    c.close()
    conn.close()


@bot.message_handler(commands=['fan_of'])
def artist_search(message):
    artist_name = message.text[7:].strip()
    artist_request = client.get(artist_name)
    if 'errors' not in artist_request:
        artist_id = artist_request['id']
        user_id = message.from_user.id
        conn = sqlite3.connect('music_bot.sqlite')
        c = conn.cursor()
        c.execute('SELECT user_id, artist_id FROM favorites WHERE user_id = ? AND artist_id = ?', (user_id, artist_id))
        row = c.fetchone()
        if row is None:
            c.execute("insert into favorites values (?, ?) ", (user_id, artist_id))
            conn.commit()

        c.execute('SELECT artist_id FROM artists WHERE artist_id = ?', (artist_id,))
        row = c.fetchone()
        if row is None:
            events = client.events(artist_name)
            last_concert_date = events[len(events)-1]['datetime']
            c.execute("insert into artists values (?, ?) ", (artist_id, last_concert_date))
            conn.commit()
        c.close()
        conn.close()
    else:
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')


@bot.message_handler(commands=['genre'])
def event_search_by_genre(message):
    my_artists = mg.get_by_genre(message.text[7:])
    bot.send_message(message.chat.id, "\n".join(my_artists))
    for artist in my_artists:
        events = client.events(artist)
        if events:
            my_messages = bit.create_message(events)
            for my_message in my_messages:
                bot.send_message(message.chat.id, my_message, parse_mode='HTML')





# @bot.message_handler(commands=['date'])
# def date_search(message):
#     params = message.text[6:]
#     events = client.search(params,  location='Moscow,Ru', date='2017-12-30,2018-03-25')
#     print(events)
    # if events:
    #     my_messages = bit.create_message(events)
    #     for my_message in my_messages:
    #         bot.send_message(message.chat.id, my_message, parse_mode='HTML')


@bot.message_handler(content_types=["text"])
def artist_search(message):
    params = message.text.split(",")
    if len(params) == 2:
        events = client.search(params[0].strip(), location=params[1].strip())
    else:
        events = client.events(params[0])
    print(events)
    my_messages = bit.create_message(events)
    for my_message in my_messages:
        bot.send_message(message.chat.id, my_message, parse_mode='HTML')






# @bot.message_handler(content_types=["text"])
# def recommendations(message):
#     events = client.recommended(message.text, location='Moscow,Ru', only_recs=True)
#     my_messages = bit.create_message(events)
#     for my_message in my_messages:
#         bot.send_message(message.chat.id, my_message)




if __name__ == '__main__':

    bot.polling(none_stop=True)
