import requests
import random

URL = 'http://api.musicgraph.com/api/v2/artist/search?'
API = 'a8a01a3244f9feb7c4e323b2015d4c5c'

#itunes:
#"https://itunes.apple.com/search?term=music&genreId"

def get_by_genre(genre):
    default = {
        'api_key': API,
        'genre': genre,
        'limit': 100
    }

    data = requests.get(URL, params=default).json()
    artists = data['data']
    artists_name = []
    for i in range(5):
        artists_name.append(random.choice(artists)['name'])
    return artists_name


def get_similar_artists(artist):    
    default = {
        'api_key': API,
        'similar_to': artist,
        'limit' : 5
     }

    data = requests.get(URL, params=default).json()
    artists = data['data']
    artists_name = []
    for artist in artists:
        artists_name.append(artist['name'])
    return artists_name












