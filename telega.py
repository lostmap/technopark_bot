import telebot
from telebot import types

import musicgraph1 as mg

import bandsintown1 as bit

from bandsintown import Client
client = Client('technopark_ruliiiit')


token = '403882463:AAGFabioSaA1uY5Iku7v-lXVJegeIoP-J3E'
bot = telebot.TeleBot(token)


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


# чисто чтоб обновить список комманд или сообщения, крч нужная штука
@bot.message_handler(commands=['start'])
def event_search_by_genre(message):
    pass


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



# для ввода Артист, Город
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