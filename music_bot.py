import telebot
from telebot import types

from geolocation.main import GoogleMaps
import requests

import os
import logging
from bandsintown import Client
from limiter import RateLimiter
from math import ceil
# импорт peewee для бд
import peeweedb as pw

import mymusicgraph as mg
import mybandsintown as bit

# concertMusicBot
#token = '419104336:AAEEFQD2ipnAv9B4ti-UZogq-9wGi9wYpfA'

# Черновичок
#token = '403882463:AAGFabioSaA1uY5Iku7v-lXVJegeIoP-J3E'

# lostMapMusicBot
token = '460978562:AAGf9KzIv2RQuBQ-nwDpWnm2D3BYy8IB5rw'

bot = telebot.TeleBot(token)
google_maps = GoogleMaps(api_key='AIzaSyCd9HpQnS40Bl2E1OxQBxJp8vmcP6PXpLo')
client = Client('technopark_ruliiiit')

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    filename="sample.log", level=logging.INFO)

limiter = RateLimiter()

# pushpin emoji
pushpin = u'\U0001F4CC'
# right emoji
left_arrow = u'\U00002B05'
# left emoji
right_arrow = u'\U000027A1'

@bot.message_handler(commands=['start'])
def starting(message):
    user_id = message.from_user.id
    if pw.is_exist(user_id):
        options_keyboard(message)
    else:
        msg = bot.send_message(message.chat.id, 'Hello, dear music fan! What city are you from?')
        bot.register_next_step_handler(msg, find_city)

def find_city(message):
    address = message.text
    try:
        location = google_maps.search(location=address)
    except:
        logging.error('City ', address, 'not found')
        msg = bot.send_message(message.chat.id, 'Try again')
        bot.register_next_step_handler(msg, find_city)
    else:
        if location.all():
            my_location = location.first()
            city = my_location.city
            city = city.decode('utf-8')

            if address != city:
                yes_or_no(message, city)
            else:
                user_id = message.from_user.id
                pw.add_user(user_id, city)
                options_keyboard(message)
        else:
            msg = bot.send_message(message.chat.id, 'Write city again, please!')
            bot.register_next_step_handler(msg, find_city)

def yes_or_no(message, city):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Yes', 'No']])
    msg = bot.send_message(message.chat.id, 'Did you mean ' + str(city) + '?', reply_markup=keyboard)
    user_id = message.from_user.id
    pw.add_user(user_id, city)
    bot.register_next_step_handler(msg, find_city_final)

def find_city_final(message):
    if message.text == 'Yes':
        options_keyboard(message)
    else:
        msg = bot.send_message(message.from_user.id, 'Write city again, please!')
        bot.register_next_step_handler(msg, find_city)
@bot.message_handler(regexp='<<Back')
def options_keyboard(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Search Artist', 'Search by genre',
                                                           'Search by similar', 'Preview', 'Bot menu']])
    #TODO лучше эту штуку сделать колбеком, чтобы не писалось каждый раз это тупое сообщение
    bot.send_message(message.chat.id, 'Welcome to the music world!', reply_markup=keyboard)


@bot.message_handler(regexp='Bot menu')
def bot_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['<<Back', 'Change city', 'Follow',
                                                           'Show favorites', 'Delete favorites']])
    #TODO лучше эту штуку сделать колбеком, чтобы не писалось каждый раз это тупое сообщение
    bot.send_message(message.chat.id, 'Here you can change your data', reply_markup=keyboard)

@bot.message_handler(regexp='Change city')
def change_city(message):
    msg = bot.send_message(message.chat.id, 'Write city, please!')
    bot.register_next_step_handler(msg, find_city)

@bot.message_handler(regexp='Search Artist')
def artist(message):
    msg = bot.send_message(message.chat.id, 'Write artist please')
    bot.register_next_step_handler(msg, search_by_artist)

def search_by_artist(message):
    artist = message.text
    artist_request = client.get(artist)
    if 'errors' not in artist_request:  #Идем дальше, если имя артиста корректно
        artist_id = artist_request['id']
        user_id = message.chat.id
        artist = artist_request['name']
        city = pw.get_city(user_id)
        if pw.is_artist_exist(artist_id): #Идем дальше, если артист есть в базе данных
            message_to_bandsintown(0, user_id, artist_id, city)
        else:                           #Если нет в базе, то проверяем наличие концертов
            events = client.events(artist)
            if events:                  #Если концерты есть, то добавляем артиста в базу
                pw.add_artist(artist_id, artist, events)
                message_to_bandsintown(0, user_id, artist_id, city)
            else:                       #В противном случае сообщаем об отсутствии ближайших концертов
                logging.error("Oooops. No " + " concert")
                bot.send_message(message.chat.id, 'У ' + artist + ' нет ближайших концертов')
    else:
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')
    options_keyboard(message)

def message_to_bandsintown(page, user_id, artist_id, city):
    bot.send_message(user_id, create_message_page(page, artist_id, city)['message'],
                     parse_mode='Markdown',
                     disable_web_page_preview=True,
                     reply_markup=pages_keyboard(0, artist_id, city))  # нулевая страница
    bot.send_message(user_id, create_photo(artist_id),
                     parse_mode='Markdown',
                     disable_notification=True)

def create_message_page(page, artist_id, city):
    events_old = eval(pw.get_event(artist_id))
    lines = 5
    answer = {}
    events = []

    for event_old in events_old:
        if event_old['venue']['city'] == city:
            events.append(event_old)

    if events:
        total_lines = len(events)
        message = "Artist: " + events[0]['artists'][0]['name'] + "\n\n"
        for event in range(0 + (lines * page), lines + (lines * page)):
            if event < total_lines:
                message += "*" + events[event]['title'] + "* \n"
                message += "Event date: " + events[event]['formatted_datetime'] + "\n"
         
                if events[event]['ticket_url']:
                    message += "[Buy tickets](" + events[event]['ticket_url'] + ")\n\n"
                else:
                    message += "[Buy tickets](" + events[event][0]['facebook_rsvp_url'] + ")\n\n"
        answer['message']   = message
        answer['page_max']  = ceil(total_lines / lines)
    else:
        message = 'У ' + events_old[0]['artists'][0]['name'] + ' нет ближайших концертов в ' + city
        answer['message']   = message
        answer['page_max']  = 1
    return answer

def create_photo(artist_id):
    events = eval(pw.get_event(artist_id))
    return "[" + pushpin + "](" + events[0]['artists'][0]['thumb_url'] + ")"

def pages_keyboard(page, artist_id, city): # создаем кнопки для листания блоков информации
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if page > 0: btns.append(types.InlineKeyboardButton(
        text=left_arrow,
        callback_data='{arrow}_{page}_{artist}_{city}'.format(arrow=left_arrow,
                                                       page=page - 1,
                                                       artist=artist_id,
                                                       city= city)))

    if page <  create_message_page(page, artist_id, city)['page_max'] - 1: btns.append(types.InlineKeyboardButton(
        text = right_arrow,
        callback_data = '{arrow}_{page}_{artist}_{city}'.format(arrow = right_arrow,
                                                         page = page + 1,
                                                         artist = artist_id,
                                                         city= city)))
    keyboard.add(*btns)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data)
def pages(call):
    # Обрабатываем нажатия кнопок
    arrow = call.data.split('_')[0]
    # Обработка стрелок
    if (arrow == left_arrow) or (arrow == right_arrow):
        page = call.data.split('_')[1]
        artist = call.data.split('_')[2]
        city = call.data.split('_')[3]
        if not limiter.can_send_to(call.message.chat.id):
            return
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=create_message_page(int(page), int(artist), city)['message'],
            parse_mode='Markdown',
            reply_markup=pages_keyboard(int(page), int(artist), city),
            disable_web_page_preview=True)

@bot.message_handler(regexp='Search by genre')
def genre(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*[types.KeyboardButton(genre) for genre in ['Rock', 'Electronic', 'Pop', 'Black',
                                                             'Rap/Hip Hop', 'Others']])
    bot.send_message(message.chat.id, "Chose style", reply_markup=keyboard)

@bot.message_handler(regexp='Rock')
def style(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*[types.KeyboardButton(genre) for genre in ['Rock', 'Metal', 'Alternative/Indie',
                                                             'Pop Rock', "90's Rock"]])
    msg = bot.send_message(message.chat.id, "Chose style", reply_markup=keyboard)
    bot.register_next_step_handler(msg, search_by_genre)

@bot.message_handler(regexp='Electronic')
def style(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*[types.KeyboardButton(genre) for genre in ['Electronica/Dance', 'Techno', "Drum n' Bass",
                                                             'Tropical']])
    msg = bot.send_message(message.chat.id, "Chose style", reply_markup=keyboard)
    bot.register_next_step_handler(msg, search_by_genre)

@bot.message_handler(regexp='Black')
def style(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*[types.KeyboardButton(genre) for genre in ['Soul/R&B', 'Jazz', 'Blues', 'Swing',
                                                             'New Age' ]])
    msg = bot.send_message(message.chat.id, "Chose style", reply_markup=keyboard)
    bot.register_next_step_handler(msg, search_by_genre)

@bot.message_handler(regexp='Others')
def style(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*[types.KeyboardButton(genre) for genre in ['Country',  'Folk', 'Instrumental',
                                                             'Latin', 'Reggae/Ska']])
    msg = bot.send_message(message.chat.id, "Chose style", reply_markup=keyboard)
    bot.register_next_step_handler(msg, search_by_genre)

def search_by_genre(message):

    genre = message.text
    try:
        my_artists = mg.get_by_genre(genre)
    except:
        logging.error("Oooops. " + genre + " is invalid genre")
        bot.send_message(message.chat.id, 'Такого жанра нет')
    else:
        bot.send_message(message.chat.id, "\n".join(my_artists))
        for artist in my_artists:
            artist_request = client.get(artist)
            if 'errors' not in artist_request:  #Идем дальше, если имя артиста корректно
                artist_id = artist_request['id']
                user_id = message.chat.id
                artist = artist_request['name']
                city = pw.get_city(user_id)
                if pw.is_artist_exist(artist_id): #Идем дальше, если артист есть в базе данных
                    message_to_bandsintown(0, user_id, artist_id, city)
                else:                           #Если нет в базе, то проверяем наличие концертов
                    events = client.events(artist)
                    if events:                  #Если концерты есть, то добавляем артиста в базу
                        pw.add_artist(artist_id, artist, events)
                        message_to_bandsintown(0, user_id, artist_id, city)
                    else:                       #В противном случае сообщаем об отсутствии ближайших концертов
                        logging.error("Oooops. No " + " concert")
                        bot.send_message(message.chat.id, 'У ' + artist + ' нет ближайших концертов')
            else:
                bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')
        options_keyboard(message)

@bot.message_handler(regexp='Search by similar')
def similar(message):
    msg = bot.send_message(message.chat.id, 'Write artist, please')
    bot.register_next_step_handler(msg, search_by_similar)

def search_by_similar(message):

    mg.get_similar_artists(message)


@bot.message_handler(regexp='Follow')
def fan_of_handler(message):
    msg = bot.send_message(message.chat.id, 'Write artist, please')
    bot.register_next_step_handler(msg, fan_of)


def fan_of(message):
    artist_name = message.text
    artist_request = client.get(artist_name)
    if 'errors' not in artist_request:
        artist_id = artist_request['id']
        user_id = message.from_user.id
        artist_name = artist_request['name']
        events = client.events(artist_name)
        pw.add_relation(user_id, artist_id, artist_name, events)
        bot.send_message(message.chat.id, artist_name + ' добавлен в список избранных')
    else:
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')



@bot.message_handler(regexp='Show favorites')
def favorites(message):
    artists = pw.get_relations(message.chat.id)
    artist_message = ""

    if artists:
        i = 1
        for artist in artists:
            artist_message += str(i) + ") " + artist + "\n"
            i += 1
    else:
        artist_message = 'Список избранных исполнителей пуст'

    bot.send_message(message.chat.id, artist_message, parse_mode='Markdown')


@bot.message_handler(regexp='Delete favorites')
def delete_handler(message):
    msg = bot.send_message(message.chat.id, 'Write artist, please')
    bot.register_next_step_handler(msg, delete)


def delete(message):
    artist_name = message.text
    artist_request = client.get(artist_name)
    if 'errors' not in artist_request:
        artist_id = artist_request['id']
        user_id = message.from_user.id
        artist_name = artist_request['name']
        result = pw.del_relation(user_id, artist_id)
        if result:
            bot.send_message(message.chat.id, artist_name + ' удален из списка избранных')
        else:
            bot.send_message(message.chat.id, artist_name + ' отсутсвует в списке избранных')
    else:
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')

@bot.message_handler(regexp='Preview')
def preview(message):
    msg = bot.send_message(message.chat.id, 'Write artist, please')
    bot.register_next_step_handler(msg, snippet_search)

def snippet_search(message):
    artist_name = message.text
    datas = requests.get("https://itunes.apple.com/search?term="+ artist_name +"&entity=musicTrack&limit=3").json()['results']
    if datas:
        for data in datas:
            response = requests.get(data['previewUrl'])
            with open('out.m4a', 'a+b') as music:
                music.write(response.content)
                music.seek(0)
                bot.send_audio(message.chat.id, music, performer=data['artistName'], duration=data["trackTimeMillis"] / 1000,
                           title=data['trackName'])
            os.remove('out.m4a')
    else:
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')

if __name__ == '__main__':
    bot.polling(none_stop=True)