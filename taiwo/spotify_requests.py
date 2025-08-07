from urllib.request import urlopen, Request
import json

def _request(url: str, token: str) -> dict:
    # url: url
    # token: hash-like token
    # return: json 
    req = Request(
        url=url, 
        headers={"Authorization":f"Bearer {token}"}
    )

    body = urlopen(req).read()
    response = json.loads(body)
    return response

def request_top_songs(token: str, limit=30) -> dict:
    return _request(f"https://api.spotify.com/v1/me/top/tracks?limit={limit}", token)

def request_top_artists(token: str, limit=5) -> dict:
    return _request(f"https://api.spotify.com/v1/me/top/artists?limit={limit}", token)

def clean_top_songs(json_data: dict, limit=30) -> list:
    # json_data: json dict
    # return: list of 4-tuple containing song information 
    top_songs = [(
        song['id'],                 #song_id
        song['name'],               #name
        song['artists'][0]['name'], #artist
        song['popularity']          #popularity
    ) for song in json_data['items'][:limit]]
    return top_songs
