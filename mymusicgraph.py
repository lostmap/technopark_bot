import requests
import random
from bandsintown import Client
import logging

client = Client('technopark_ruliiiit')

URL = 'http://api.musicgraph.com/api/v2/artist/search?'

API = 'a64bda6196fb21ac8bfdca756803a746'

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
        'name': artist,
        'limit': 1
     }
    try:
        data = requests.get(URL, params=default).json()
    except:
        return 'errors'
    else:
        if data['data']:
            search = data['data'][0]['id']
        else:
            return 'errors'
        URL2 = "http://api.musicgraph.com/api/v2/artist/" + search + "/similar?api_key=" +  API + "&limit=100"
        try:
            artists_info = requests.get(URL2).json()['data']
        except:
            return 'errors'
        else:
            unique_artists = set(artist['name'] for artist in artists_info)
            valid_artists = []
            while len(valid_artists) < 5:
                get_random_artist = random.sample(unique_artists,1)[0]
                try:
                    artist_request = client.get(get_random_artist)
                except:
                    unique_artists.remove(get_random_artist)
                else:
                    if 'errors' not in artist_request:
                        valid_artists.append(get_random_artist)
                    unique_artists.remove(get_random_artist)
            return valid_artists








