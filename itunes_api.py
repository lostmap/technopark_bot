import requests
import random

URL = 'https://itunes.apple.com/search?'

def get_genre_by_artist_id(genre_id, **kwargs):
    default = { 'term' : 'music',
                'genreId' : genre_id,
                'limit' : 200,
                }
    for key in kwargs.keys():
        default[key] = kwargs[key]
    
    genres = requests.get(URL, params = default).json()['results']
    artists = set(genre['artistName'] for genre in genres)
    art = []
    for i in range(5):
        take = random.sample(artists,1)[0]
        art.append(take)
        artists.remove(take)
    return art

    



