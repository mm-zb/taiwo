import requests
from urllib.parse import urlencode
import base64
import webbrowser
import sqlite3

import config

client_id = config.SPOTIFY_ID
client_secret = config.SPOTIFY_SECRET

def get_code() -> None:
    auth_headers = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "http://localhost:80/callback",
        "scope": "user-library-read user-top-read user-read-recently-played user-library-modify"
    }

    webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

def get_token(code: str) -> tuple[str, str]:
    # code: client auth code for spotify account
    # return: tuple of the access and refresh token

    encoded_credentials = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")

    token_headers = {
        "Authorization": "Basic " + encoded_credentials,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:80/callback"
    }
    r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
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
    
    conn.close()

    refresh_token = data[4]
    encoded_credentials = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")
    token_headers = {
        "Authorization": "Basic " + encoded_credentials,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh_token,
        "redirect_uri": "http://localhost:80/callback"
    }
    #sets up headers and payload for JSON request to api for refreshing of token
    
    r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
    conn = sqlite3.connect('logins.db')
    c = conn.cursor()
    c.execute('UPDATE users SET access_token = "'+str(r)+'" WHERE username = "'+str(user)+'"')
    #executes SQL to add the updated token to database
    conn.close()
