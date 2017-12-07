import telebot
from telebot import types
from telebot.types import MessageEntity

token = '419104336:AAEEFQD2ipnAv9B4ti-UZogq-9wGi9wYpfA'
bot = telebot.TeleBot(token)

#   from geolocation.main import GoogleMaps

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

import urllib
from limiter import RateLimiter
from urllib.request import Request

limiter = RateLimiter()

artist_id_list = {}

"""
url= Request('https://audio-ssl.itunes.apple.com/apple-assets-us-std-000001/AudioPreview128/v4/86/57/db/8657db48-d13f-12a8-5e97-a85d643bbb09/mzaf_1991099723058618655.plus.aac.p.m4a', headers={'User-Agent': 'Mozilla/5.0'})
with open('out.m4a','wb') as f:
    f.write(urllib.request.urlopen(url).read())
"""
"""
@bot.message_handler(content_types=["text"])
def test(message):
    address = message.text
    google_maps = GoogleMaps(api_key='AIzaSyCd9HpQnS40Bl2E1OxQBxJp8vmcP6PXpLo')
    location = google_maps.search(location=address)
    my_location = location.first()
    print(my_location)
"""
def message_to_bandsintown(message, my_messages):
    if not limiter.can_send_to(message.chat.id):
        time.sleep(1)
    bot.send_message(message.chat.id, my_messages[0]['text'],
                        parse_mode='Markdown',
                        disable_web_page_preview = True,
                        reply_markup = pages_keyboard(0, my_messages[0]['artist_id'])) #нулевая страница
    if not limiter.can_send_to(message.chat.id):
        time.sleep(1)
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
            if not limiter.can_send_to(message.chat.id):
                time.sleep(1)
            bot.send_message(message.chat.id, 'Такого жанра нет')
        else:
            if not limiter.can_send_to(message.chat.id):
                time.sleep(1)
            bot.send_message(message.chat.id, "\n".join(my_artists))
            for artist in my_artists:
                events = client.events(artist)
                try:
                    my_messages = bit.create_message(events)
                    artist_id_list[my_messages[0]['artist_id']] = my_messages
                except:
                    logging.error("Oooops. No " + artist + " concert")
                    if not limiter.can_send_to(message.chat.id):
                        time.sleep(1)
                    bot.send_message(message.chat.id, 'У ' + artist + ' нет ближайших концертов')
                else:
                    message_to_bandsintown(message, my_messages)

def genre_buttons(message): #кнопка для жанров
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=genre[5:], callback_data=genre) for genre in ['genreRock', 'genreAlternative/Indie', 'genrePop',
                                                                                               'genreJazz', 'genreSoul/R&B', 'genreBlues',
                                                                                              'genreRap/Hip Hop', 'genreFolk']])
    if not limiter.can_send_to(message.chat.id):
        time.sleep(1)
    bot.send_message(message.chat.id, "Какой жанр выберешь?", reply_markup=keyboard)


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
        if not limiter.can_send_to(message.chat.id):
            time.sleep(1)
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')
    else:
        message_to_bandsintown(message, my_messages)
        #music = open('out.m4a','rb')
        #bot.send_audio(message.chat.id, music, performer='Deuce', title='How I Cum')



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
        if not limiter.can_send_to(call.message.chat.id):
            return
        bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = artist_id_list[int(artist)][int(page)]['text'],
            parse_mode = 'Markdown', 
            reply_markup = pages_keyboard(int(page),int(artist)),
            disable_web_page_preview = True)

if __name__ == '__main__':

    bot.polling(none_stop=True)
