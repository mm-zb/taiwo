from urllib.request import urlopen, Request
import json

def lyric_to_url(lyric):
    url = 'https://genius.com/api/search/lyric?q='

    lyric = lyric.split()
    lyric = '%20'.join(lyric)

    url += lyric
    return url 



def get_songs(url):
    req = Request(
        url=url, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    #genius public api detects and blocks urllib, so need to pretend to come through Mozilla

    body = urlopen(req).read()

    response = json.loads(body)

    return response

def json_to_list(response):
    if not response['response']['sections'][0]['hits']:
        return []
    songs = list()
    for i in range(len(response['response']['sections'][0]['hits'])):
        snippet = response['response']['sections'][0]['hits'][i]['highlights'][0]['value']
        artist = response['response']['sections'][0]['hits'][i]['result']['primary_artist']['name']
        title = response['response']['sections'][0]['hits'][i]['result']['title']
        link = response['response']['sections'][0]['hits'][i]['result']['url']
        songs.append((snippet,artist,title,link))
    return songs
    


def main():
    url = lyric_to_url(input())
    response = get_songs(url)
    songs = json_to_list(response)
    if not songs:
        print('No results')
    else:
        for song in enumerate(songs):
            print((str(song[0]+1)+')  '+song[1][2]+' - '+song[1][1]+'\n'+song[1][3]+'\n'+song[1][0]+'\n'))