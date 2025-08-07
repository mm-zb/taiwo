import requests
from urllib.parse import urlencode
import base64
import webbrowser
import sqlite3

import config

CLIENT_ID = config.SPOTIFY_ID
CLIENT_SECRET = config.SPOTIFY_SECRET
ENCODED_CREDENTIALS = base64.b64encode(CLIENT_ID.encode() + b':' + CLIENT_SECRET.encode()).decode("utf-8")
TOKEN_HEADERS = {
        "Authorization": "Basic " + ENCODED_CREDENTIALS,
        "Content-Type": "application/x-www-form-urlencoded"
    }

def get_code() -> None:
    auth_headers = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://localhost:80/callback",
        "scope": "user-library-read user-top-read user-read-recently-played user-library-modify"
    }

    webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

def get_token(code: str) -> tuple[str, str]:
    # code: client auth code for spotify account
    # return: tuple of the access and refresh token

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:80/callback"
    }
    r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=TOKEN_HEADERS)
    parsed = r.json()
    return (parsed["access_token"], parsed["refresh_token"])

def refresh_access(user: str) -> None:
    # user: username in a string
    # return: None
    
    conn = sqlite3.connect('logins.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username="'+user+'"')
    data = c.fetchall()[0]
    #executes SQL to get user's data
    

    refresh_token = data[4]
    token_data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "refresh_token": refresh_token,
    }
    #sets up headers and payload for JSON request to api for refreshing of token
    
    r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=TOKEN_HEADERS)
    c.execute('UPDATE users SET access_token = "'+str(r)+'" WHERE username = "'+str(user)+'"')
    #executes SQL to add the updated token to database
    conn.close()
