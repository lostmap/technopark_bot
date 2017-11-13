import telebot
from telebot import types
import sqlite3

import musicgraph1 as mg

import bandsintown1 as bit

from bandsintown import Client
client = Client('technopark_ruliiiit')


token = '403882463:AAGFabioSaA1uY5Iku7v-lXVJegeIoP-J3E'
bot = telebot.TeleBot(token)

import logging

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    filename="sample.log", level=logging.INFO)


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


#кнопка для жанров
def genre_buttons(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=genre, callback_data=genre) for genre in ['Rock', 'Alternative/Indie', 'Pop',
                                                                                               'Jazz', 'Soul/R&B', 'Blues',
                                                                                              'Rap/Hip Hop', 'Folk']])
    bot.send_message(message.chat.id, "Какой жанр выберешь?", reply_markup=keyboard)

#для того же
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    call.message.text = '/genre ' + call.data
    event_search_by_genre(call.message)



# #для /genre жанр
# @bot.message_handler(commands=['genre'])
# def event_search_by_genre(message):
#     my_artists = mg.get_by_genre(message.text[7:])
#     bot.send_message(message.chat.id, "\n".join(my_artists))
#     for artist in my_artists:
#         events = client.events(artist)
#         if events:
#             my_messages = bit.create_message(events)
#             for my_message in my_messages:
#                 bot.send_message(message.chat.id, my_message, parse_mode='HTML')

# для /genre жанр, город
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
                if events:
                    my_messages = bit.create_message(events)
                    for my_message in my_messages:
                        bot.send_message(message.chat.id, my_message, parse_mode='HTML')
        else:
            my_artists = mg.get_by_genre(params[0])
            bot.send_message(message.chat.id, "\n".join(my_artists))
            for artist in my_artists:
                events = client.events(artist)
                if events:
                    my_messages = bit.create_message(events)
                    for my_message in my_messages:
                        bot.send_message(message.chat.id, my_message, parse_mode='HTML')



# поиск по датам в дипозоне))
# @bot.message_handler(commands=['date'])
# def date_search(message):
#     params = message.text[6:]
#     events = client.search(params,  location='Moscow,Ru', date='2017-12-30,2018-03-25')
#     print(events)
    # if events:
    #     my_messages = bit.create_message(events)
    #     for my_message in my_messages:
    #         bot.send_message(message.chat.id, my_message, parse_mode='HTML')


# для /similar артист
@bot.message_handler(commands=['similar'])
def event_search_by_similar(message):
    my_artists = mg.get_similar_artists(message.text[9:])
    print(message.text[9:])
    # if 'errors' not in my_artists:
    bot.send_message(message.chat.id, "\n".join(my_artists))
    for artist in my_artists:
        events = client.events(artist)
        if events:
            my_messages = bit.create_message(events)
            for my_message in my_messages:
                bot.send_message(message.chat.id, my_message, parse_mode='HTML')


# для ввода Артист, Город
@bot.message_handler(content_types=["text"])
def artist_search(message):

    params = message.text.split(",")
    if len(params) == 2:
        events = client.search(params[0].strip(), location=params[1].strip())
    else:
        events = client.events(params[0])

    try:
        my_messages = bit.create_message(events)
    except:
        logging.error("Ooops")
        bot.send_message(message.chat.id, 'try again')
        return
    else:
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