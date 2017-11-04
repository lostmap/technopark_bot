import requests

URL = 'http://api.musicgraph.com/api/v2/artist/search?'
API = 'a8a01a3244f9feb7c4e323b2015d4c5c'

def get_by_genre(genre, **kwargs):
    default = {
    'api_key' : API,
    'genre' : genre,
    'limit' : 10,
 }
    for key in kwargs.keys():
        default[key] = kwargs[key]
    data = requests.get(URL,params = default).json()
    artists = data['data']
    artists_name = []
    for artist in artists:
        artists_name.append(artist['name'])
    return artists_name

# get_by_genre('Rock')