import requests
from urllib.parse import urlencode
import base64
import webbrowser
import sqlite3

#on zayanbaig spotify account
#the one i use to listen to songs

code='AQCRLcUZdpzwfePVp1CheZcCIJ8OnC0y6B3g_xlZPRgkaCfLC_57-tByCrIC39o9oRdYBbC8_uxPyNX9KvsGCuQMNOzi4dxDCbxvfejwyL3vJtz-j7jHpYBxrS0EfOn6CDVGWL2NHzDezaZAdt5YnpFJyig3pzgJXJhFJBm1HBvHTczGxbSc6OMWQ3eJjeFSLNt1Esk'

client_id = 'd70f2af9728940bca6d4dced4ec393d8'
client_secret = '0f8fe05ce55349b687156b8ebcaa6840'

def get_code():
    auth_headers = {
        "client_id": 'd70f2af9728940bca6d4dced4ec393d8',
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
        "client_id": "d70f2af9728940bca6d4dced4ec393d8",
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



if False:

    code = get_code()

    r =get_token(code)
    json = r.json()
    print(r)
    print('/n/n/n/n/n/n/n/n/n/n')
    print(json)