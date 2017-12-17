import requests
import random
from bandsintown import Client
client = Client('technopark_ruliiiit')

URL = 'https://itunes.apple.com/search?'

def get_genre_by_artist_id(genre_id, **kwargs):
    default = {'term': 'artist',
               'genreId': genre_id,
               'limit': 200}

    for key in kwargs.keys():
        default[key] = kwargs[key]
    
    genres = requests.get(URL, params = default).json()['results']
    unique_artists = set(genre['artistName'] for genre in genres)
    valid_artists = []
    while len(valid_artists) < 5:
        get_random_artist = random.sample(unique_artists,1)[0]
        artist_request = client.get(get_random_artist)
        if 'errors' not in artist_request:
            valid_artists.append(get_random_artist)
        unique_artists.remove(get_random_artist)
    return valid_artists

print(get_genre_by_artist_id(20))



