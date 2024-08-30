import requests
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import json

#testing spotify account details:
#robisi6374@rentaen.com
#abc12345678

code='AQCRLcUZdpzwfePVp1CheZcCIJ8OnC0y6B3g_xlZPRgkaCfLC_57-tByCrIC39o9oRdYBbC8_uxPyNX9KvsGCuQMNOzi4dxDCbxvfejwyL3vJtz-j7jHpYBxrS0EfOn6CDVGWL2NHzDezaZAdt5YnpFJyig3pzgJXJhFJBm1HBvHTczGxbSc6OMWQ3eJjeFSLNt1Esk'

client_id = 'd70f2af9728940bca6d4dced4ec393d8'
client_secret = '0f8fe05ce55349b687156b8ebcaa6840'

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