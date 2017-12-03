import telebot
from telebot import types
from telebot.types import MessageEntity

token = '460978562:AAGf9KzIv2RQuBQ-nwDpWnm2D3BYy8IB5rw'
bot = telebot.TeleBot(token)

import mymusicgraph as mg
import mybandsintown as bit
from bandsintown import Client

client = Client('technopark_ruliiiit')

import requests
import time
import sqlite3
import logging

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    filename="sample.log", level=logging.INFO)

left_arrow  = u'\U00002B05' #right emoji
right_arrow = u'\U000027A1' #left emoji

from limiter import RateLimiter

limiter = RateLimiter()

artist_id_list = {}

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

"""
@bot.message_handler(commands=['genre'])
def event_search_by_genre(message):
    my_artists = mg.get_by_genre(message.text[7:])
    bot.send_message(message.chat.id, "\n".join(my_artists))
    for artist in my_artists:
        events = client.events(artist)
        if events:
            my_messages = bit.create_message(events)
            artist_id_list[my_messages[0]['artist_id']] = my_messages # TODO создай класс
            bot.send_message(message.chat.id, my_messages[0]['text'], parse_mode='Markdown',
                disable_web_page_preview = True,
                reply_markup = pages_keyboard(0, my_messages[0]['artist_id'])) #нулевая страница
            bot.send_message(message.chat.id, my_messages[0]['photo'], parse_mode='Markdown',
                disable_notification = True)
"""
"""
@bot.message_handler(commands=['genre'])
def event_search_by_genre(message):
    if len(message.text) == 6:
        genre_buttons(message)
    else:
        params = message.text.split(",")
        params[0] = params[0][7:].strip()

        if len(params) == 2:
            my_artists = mg.get_by_genre(params[0])
            bot.send_message(message.chat.id, "\n".join(my_artists))
            for artist in my_artists:
                events = client.search(artist, location=params[1].strip())
                try:
                    my_messages = bit.create_message(events)
                    artist_id_list[my_messages[0]['artist_id']] = my_messages
                except:
                    logging.error("Ooops")
                    bot.send_message(message.chat.id, 'try again')
                    return
                else:
                    message_to_bandsintown(message, my_messages)
        else:
            my_artists = mg.get_by_genre(params[0])
            bot.send_message(message.chat.id, "\n".join(my_artists))
            for artist in my_artists:
                events = client.events(artist)
                try:
                    my_messages = bit.create_message(events)
                    artist_id_list[my_messages[0]['artist_id']] = my_messages
                except:
                    logging.error("Ooops")
                    bot.send_message(message.chat.id, 'try again')
                    return
                else:
                    message_to_bandsintown(message, my_messages)
"""
def message_to_bandsintown(message, my_messages):
    bot.send_message(message.chat.id, my_messages[0]['text'],
                        parse_mode='Markdown',
                        disable_web_page_preview = True,
                        reply_markup = pages_keyboard(0, my_messages[0]['artist_id'])) #нулевая страница
    bot.send_message(message.chat.id, my_messages[0]['photo'],
                        parse_mode='Markdown',
                        disable_notification = True)

@bot.message_handler(commands=['genre'])
def event_search_by_genre(message):
    if len(message.text) == 6:
        genre_buttons(message)
    else:
        genre = message.text[7:]
        try:
            my_artists = mg.get_by_genre(genre)
        except:
            logging.error("Oooops. " + genre + " is invalid genre")
            bot.send_message(message.chat.id, 'Такого жанра нет')
        else:
            bot.send_message(message.chat.id, "\n".join(my_artists))
            for artist in my_artists:
                events = client.events(artist)
                try:
                    my_messages = bit.create_message(events)
                    artist_id_list[my_messages[0]['artist_id']] = my_messages
                except:
                    logging.error("Oooops. No " + artist + " concert")
                    bot.send_message(message.chat.id, 'У ' + artist + ' нет ближайших концертов')
                else:
                    message_to_bandsintown(message, my_messages)

def genre_buttons(message): #кнопка для жанров
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=genre[5:], callback_data=genre) for genre in ['genreRock', 'genreAlternative/Indie', 'genrePop',
                                                                                               'genreJazz', 'genreSoul/R&B', 'genreBlues',
                                                                                              'genreRap/Hip Hop', 'genreFolk']])
    bot.send_message(message.chat.id, "Какой жанр выберешь?", reply_markup=keyboard)

# @bot.message_handler(commands=['date'])
# def date_search(message):
#     params = message.text[6:]
#     events = client.search(params,  location='Moscow,Ru', date='2017-12-30,2018-03-25')
#     print(events)
    # if events:
    #     my_messages = bit.create_message(events)
    #     for my_message in my_messages:
    #         bot.send_message(message.chat.id, my_message, parse_mode='HTML')
 #содержит результаты поиска по каждому артисту

@bot.message_handler(content_types=["text"])
def artist_search(message):
    params = message.text.split(",")
    if len(params) == 2:
        events = client.search(params[0].strip(), location=params[1].strip())
    else:
        events = client.events(params[0])
    try:
        my_messages = bit.create_message(events)
        artist_id_list[my_messages[0]['artist_id']] = my_messages
    except:
        logging.error("Ooops. No " + message.text + " artist")
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')
    else:
        message_to_bandsintown(message, my_messages)


def pages_keyboard(page, artist_id): #создаем кнопки для листания блоков информации
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if page > 0: btns.append(types.InlineKeyboardButton(
        text = left_arrow, callback_data = '{arrow}_{page}_{artist}'.format(arrow = left_arrow,
            page = page - 1,
            artist = artist_id)))
    if page < len(artist_id_list[artist_id]) - 1: btns.append(types.InlineKeyboardButton(
        text = right_arrow, callback_data = '{arrow}_{page}_{artist}'.format(arrow = right_arrow,
            page = page + 1,
            artist = artist_id)))
    keyboard.add(*btns)
    return keyboard # возвращаем объект клавиатуры

#@bot.callback_query_handler(func=lambda call: True)
##def callback_inline(call):
  #  call.message.text = '/genre ' + call.data
   # event_search_by_genre(call.message)

@bot.callback_query_handler(func = lambda call: call.data)  
def pages(call): #Обрабатываем нажатия кнопок
    arrow = call.data.split('_')[0]
    if call.data[:5] == 'genre': #Обработка жанров
        call.message.text = '/genre ' + call.data[5:]
        event_search_by_genre(call.message)
    if (arrow == left_arrow) or (arrow == right_arrow): #Обработка стрелок
        page    = call.data.split('_')[1]
        artist  = call.data.split('_')[2]
        bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = artist_id_list[int(artist)][int(page)]['text'],
            parse_mode = 'Markdown', 
            reply_markup = pages_keyboard(int(page),int(artist)),
            disable_web_page_preview = True)

#my_messages = bit.create_message(events)
#for my_message in my_messages:
#     bot.send_message(message.chat.id, my_message['text'], parse_mode='Markdown', disable_web_page_preview = True)
#bot.send_message(message.chat.id, my_messages[0]['photo'], parse_mode='Markdown', disable_notification = True)

# @bot.message_handler(content_types=["text"])
# def recommendations(message):
#     events = client.recommended(message.text, location='Moscow,Ru', only_recs=True)
#     my_messages = bit.create_message(events)
#     for my_message in my_messages:
#         bot.send_message(message.chat.id, my_message)

if __name__ == '__main__':

    bot.polling(none_stop=True)
