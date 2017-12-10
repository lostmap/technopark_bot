import telebot
from telebot import types
from telebot.types import MessageEntity
from geolocation.main import GoogleMaps
import requests
import time
import logging
from bandsintown import Client
from limiter import RateLimiter

# импорт peewee для бд
import peeweedb as pw

import mymusicgraph as mg
import mybandsintown as bit

# token = '419104336:AAEEFQD2ipnAv9B4ti-UZogq-9wGi9wYpfA'
token = '403882463:AAGFabioSaA1uY5Iku7v-lXVJegeIoP-J3E'
bot = telebot.TeleBot(token)
google_maps = GoogleMaps(api_key='AIzaSyCd9HpQnS40Bl2E1OxQBxJp8vmcP6PXpLo')
client = Client('technopark_ruliiiit')

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    filename="sample.log", level=logging.INFO)

limiter = RateLimiter()


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
        user_id = message.from_user.id
        msg = bot.send_message(message.chat.id, 'Write city again, please!')
        bot.register_next_step_handler(msg, find_city)


def options_keyboard(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Change city', 'Search Artist', 'Search by genre',
                                                           'Search by similar']])
    #TODO лучше эту штуку сделать колбеком, чтобы не писалось каждый раз это тупое сообщение
    bot.send_message(message.chat.id, 'Ну хотя бы не крашнулся!', reply_markup=keyboard)


@bot.message_handler(regexp='Change city')
def change_city(message):
    pass
    # user_id = message.from_user.id
    # pw.add_user(user_id, city)


@bot.message_handler(regexp='Search Artist')
def artist(message):
    msg = bot.send_message(message.chat.id, 'Write artist please')
    bot.register_next_step_handler(msg, search_by_artist)


def search_by_artist(message):
    artist = message.text
    artist_request = client.get(artist)
    if 'errors' not in artist_request:
        artist_id = artist_request['id']
        user_id = message.chat.id
        artist = artist_request['name']
        city = pw.get_city(user_id)
        events = client.search(artist, location=city)

        if events:
            pw.add_artist(artist_id, artist, events)
            my_messages = bit.create_message(events)
            message_to_bandsintown(message, my_messages)
        else:
            city = pw.get_city(user_id)
            logging.error("Oooops. No " + artist + " concert")
            bot.send_message(message.chat.id, 'У ' + artist + ' нет ближайших концертов в ' + city)

        options_keyboard(message)

    else:
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')


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
            user_id = message.from_user.id
            city = pw.get_city(user_id)
            events = client.search(artist, location=city)
            if events:
                my_messages = bit.create_message(events)
                message_to_bandsintown(message, my_messages)
            else:
                logging.error("Oooops. No " + artist + " concert")
                bot.send_message(message.chat.id, 'У ' + artist + ' нет ближайших концертов')
        options_keyboard(message)


@bot.message_handler(regexp='Search by similar')
def similar(message):
    msg = bot.send_message(message.chat.id, 'Write artist, please')
    bot.register_next_step_handler(msg, search_by_similar)


def search_by_similar(message):
    pass  # TODO Опять работа с бд


# right emoji
left_arrow = u'\U00002B05'
# left emoji
right_arrow = u'\U000027A1'


def message_to_bandsintown(message, my_messages):
    bot.send_message(message.chat.id, my_messages[0]['text'],
                     parse_mode='Markdown',
                     disable_web_page_preview=True,
                     reply_markup=pages_keyboard(0, my_messages[0]['artist_id']))  # нулевая страница
    bot.send_message(message.chat.id, my_messages[0]['photo'],
                     parse_mode='Markdown',
                     disable_notification=True)


def pages_keyboard(page, artist_id):# создаем кнопки для листания блоков информации
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if page > 0: btns.append(types.InlineKeyboardButton(
        text=left_arrow, callback_data='{arrow}_{page}_{artist}'.format(arrow=left_arrow,
        page=page - 1, artist=artist_id)))
    # if page < len(artist_id_list[artist_id]) - 1: btns.append(types.InlineKeyboardButton(
    #     text = right_arrow, callback_data = '{arrow}_{page}_{artist}'.format(arrow = right_arrow,
    #         page = page + 1,
    #         artist = artist_id)))
    keyboard.add(*btns)
    return keyboard


@bot.message_handler(commands=['fan_of'])
def artist_search(message):
    artist_name = message.text[7:].strip()
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


# отправляет пользователю список избранных артистов
@bot.message_handler(commands=['favorites'])
def artist_search(message):
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


@bot.message_handler(commands=['del'])
def artist_search(message):
    artist_name = message.text[4:].strip()
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


@bot.message_handler(commands=['snip'])
def snippet_search(message):
    artist_name = message.text[5:].strip()
    datas = requests.get("https://itunes.apple.com/search?term="+ artist_name +"&entity=musicTrack&limit=3").json()['results']
    if datas:
        for data in datas:
            response = requests.get(data['previewUrl'])
            with open('out.m4a', 'wb') as f:
                f.write(response.content)
            music = open('out.m4a','rb')
            bot.send_audio(message.chat.id, music, performer=data['artistName'], title=data['trackName'])
    else:
        bot.send_message(message.chat.id, 'Имя исполнителя введено не верно')



if __name__ == '__main__':
    bot.polling(none_stop=True)
