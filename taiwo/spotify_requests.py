from urllib.parse import urlencode
from urllib.request import urlopen, Request
import json

import config

client_id = config.SPOTIFY_ID
client_secret = config.SPOTIFY_SECRET

def request(url, token):
    req = Request(
        url=url, 
        headers={"Authorization":f"Bearer {str(token)}"}
    )

    body = urlopen(req).read()
    response = json.loads(body)
    return response

def request_top_songs(token, limit=30):
    return request(f"https://api.spotify.com/v1/me/top/tracks?limit={limit}", token)

def request_top_artists(token, limit=5):
    return request(f"https://api.spotify.com/v1/me/top/artists?limit={limit}", token)

def clean_top_songs(songs, limit=30):

    top_songs = [(
        song['id'],                 #song_id
        song['name'],               #name
        song['artists'][0]['name'], #artist
        song['popularity']          #popularity
    ) for song in songs['items']]
    return top_songs
