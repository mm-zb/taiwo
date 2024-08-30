import requests
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import json


client_id = 'id'
client_secret = 'secret'

def request_top_songs(token):
    print(token)
    req = Request(
        url="https://api.spotify.com/v1/me/top/tracks?limit=30", 
        headers={"Authorization":'Bearer '+str(token)}
    )

    body = urlopen(req).read()
    response = json.loads(body)
    return response

def request_top_artists(token):
    req = Request(
        url="https://api.spotify.com/v1/me/top/artists?limit=5", 
        headers={"Authorization":'Bearer '+str(token)}
    )
    
    body = urlopen(req).read()
    response = json.loads(body)
    return response

def clean_top_songs(data):
    songs = list()
    for i in range(30):
        id = data['items'][i]['id']
        artist = data['items'][i]['artists'][0]['name']
        name = data['items'][i]['name']
        popularity = data['items'][i]['popularity']
        songs.append((id,name,artist,popularity))
    return songs
