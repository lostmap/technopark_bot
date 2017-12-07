import telebot
from telebot import types
from telebot.types import MessageEntity
from geolocation.main import GoogleMaps
import requests
import time
import logging
from bandsintown import Client
from limiter import RateLimiter


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
    msg = bot.send_message(message.chat.id, 'Hello, dear music fan! What city are you from?')
    bot.register_next_step_handler(msg, find_city)


def find_city(message):
    address = message.text
    try:
        location = google_maps.search(location=address)
    except:
        logging.error('City ', address, 'not found')
        bot.send_message(message.chat.id, 'Try again')
    else:
        if location.all():
            my_location = location.first()
            city = my_location.city
            city = city.decode('utf-8')

            if address != city:
                yes_or_no(message, city)
            else:
                pass  # TODO Липко добавляет город в бд
                options_keyboard(message)
        else:
            msg = bot.send_message(message.chat.id, 'Write city again, please!')
            bot.register_next_step_handler(msg, find_city)


def yes_or_no(message, city):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Yes', 'No']])
    msg = bot.send_message(message.chat.id, 'Did you mean ' + str(city) + '?', reply_markup=keyboard)
    bot.register_next_step_handler(msg, find_city_final)


def find_city_final(message):
    if message.text == 'Yes':
        pass #TODO Липко добавляет город в бд
        options_keyboard(message)
    else:
        msg = bot.send_message(message.chat.id, 'Write city again, please!')
        bot.register_next_step_handler(msg, find_city)


def options_keyboard(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Change city', 'Search Artist', 'Search by genre',
                                                           'Search by similar']])
    #TODO лучше эту штуку сделать колбеком, чтобы не писалось каждый раз это тупое сообщение
    bot.send_message(message.chat.id, 'Welcome to the music world!', reply_markup=keyboard)


@bot.message_handler(regexp='Change city')
def change_city(message):
    pass # TODO



@bot.message_handler(regexp='Search Artist')
def artist(message):
    msg = bot.send_message(message.chat.id, 'Write artist please')
    bot.register_next_step_handler(msg, search_by_artist)


def search_by_artist(message):
    artist = message.text
    events = client.search(artist, location='Moscow, Ru')  # TODO тут надо вставить город из бд
    print(events)
    try:
        my_messages = bit.create_message(events)
    except:
        logging.error("Oooops. No " + artist + " concert")
        bot.send_message(message.chat.id, 'У ' + artist + ' нет ближайших концертов')
    else:
        message_to_bandsintown(message, my_messages)
        options_keyboard(message)


@bot.message_handler(regexp='Search by genre')
def genre(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*[types.KeyboardButton(genre) for genre in ['Rock', 'Alternative/Indie', 'Pop', 'Jazz', 'Soul/R&B',
                                                             'Blues', 'Rap/Hip Hop', 'Folk']])
    msg = bot.send_message(message.chat.id, "Chose genre", reply_markup=keyboard)
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
            events = client.search(artist, location='Moscow, Ru') # TODO тут надо вставить город из бд
            try:
                my_messages = bit.create_message(events)
            except:
                logging.error("Oooops. No " + artist + " concert")
                bot.send_message(message.chat.id, 'У ' + artist + ' нет ближайших концертов')
            else:
                message_to_bandsintown(message, my_messages)
                options_keyboard(message)




@bot.message_handler(regexp='Search by similar')
def similar(message):
    msg = bot.send_message(message.chat.id, 'Write artist, please')
    bot.register_next_step_handler(msg, search_by_similar)


def search_by_similar(message):
    pass  # TODO Опять работа с бд



left_arrow  = u'\U00002B05' #right emoji
right_arrow = u'\U000027A1' #left emoji


def message_to_bandsintown(message, my_messages):
    bot.send_message(message.chat.id, my_messages[0]['text'],
                     parse_mode='Markdown',
                     disable_web_page_preview=True,
                     reply_markup=pages_keyboard(0, my_messages[0]['artist_id']))  # нулевая страница
    bot.send_message(message.chat.id, my_messages[0]['photo'],
                     parse_mode='Markdown',
                     disable_notification=True)


def pages_keyboard(page, artist_id): #создаем кнопки для листания блоков информации
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






if __name__ == '__main__':
    bot.polling(none_stop=True)