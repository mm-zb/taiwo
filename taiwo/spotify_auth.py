import requests
from urllib.parse import urlencode
import base64
import webbrowser
import sqlite3

client_id = 'id'
client_secret = 'secret'

def get_code():
    auth_headers = {
        "client_id": 'id',
        "response_type": "code",
        "redirect_uri": "http://localhost:80/callback",
        "scope": "user-library-read user-top-read user-read-recently-played user-library-modify"
    }

    webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

def get_token(code):
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
    print(r)
    return [r.json()["access_token"],r.json()["refresh_token"]]

def refresh_access(user):
    conn = sqlite3.connect('logins.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username="'+str(user)+'"')
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
        "client_id": "id",
        "refresh_token": refresh_token,
        "redirect_uri": "http://localhost:80/callback"
    }
    #sets up headers and payload for JSON request to api for refreshing of token
    
    r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
    print(r)
    conn = sqlite3.connect('logins.db')
    c = conn.cursor()
    c.execute('UPDATE users SET access_token = "'+str(r)+'" WHERE username = "'+str(user)+'"')
    #executes SQL to add the updated token to database
    conn.close()
