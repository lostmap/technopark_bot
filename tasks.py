import datetime
from music_bot import message_to_bandsintown
from celery import Celery
import peeweedb as pw
app = Celery('tasks', broker='amqp://guest@localhost//', backend='amqp')


from bandsintown import Client
client = Client('technopark_ruliiiit')


@app.task
def send_update_message(artist_id, new_events):
    users_dict = pw.get_users_dict(artist_id)
    to_bnt = pw.get_b_t_n(artist_id)
    for user_chat_id in users_dict.keys():
        message_to_bandsintown(0, user_chat_id, to_bnt, users_dict[user_chat_id], new_events)
        #print(0, user_chat_id, to_bnt, users_dict[user_chat_id])
        #print("\n\n\n\n")
        return user_chat_id, users_dict[user_chat_id]


@app.task
def add_days(days):

    for artist_id, artist_name, artist_information in pw.get_artist_generator():
        update_events = client.events(artist_name)
        old_events = eval(artist_information)
        new_events = []
        if update_events != old_events:
            pw.set_new_information(artist_id, update_events)
            for event in update_events:
                if event not in old_events:
                    new_events.append(event)
            send_update_message(artist_id, new_events)


app.conf.update(
    CELERYBEAT_SCHEDULE={
        'multiply-each-10-seconds': {
            'task': 'tasks.add_days',
            'schedule': datetime.timedelta(minutes=3),
            'args': (2, )
        },
    },
)
