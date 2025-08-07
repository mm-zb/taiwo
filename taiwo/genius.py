from urllib.request import urlopen, Request
from urllib.parse import quote
import json
def search_lyrics(lyrics: str) -> list:
    # lyrics: a sentence
    # return: list of 4-tuples of strings

    def find_url(lyrics: str) -> str:
        # lyrics: a sentence
        # return: a url 
        url = 'https://genius.com/api/search/lyric?q='
        return url + quote(lyrics)

    def request(url: str) -> dict:
        # url: a url
        # return: complex json dictionary

        req = Request(
            url=url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        body = urlopen(req).read()
        response = json.loads(body)
        return response

    def parse_response(response: dict) -> list:
        # response: complex json dictionary
        # return: list of 4-tuples of strings

        hits = response['response']['sections'][0]['hits']
        if not hits:
            return []
        
        songs = [(
                    hit['highlights'][0]['value'],              #snippet
                    hit['result']['primary_artist']['name'],    #artist
                    hit['result']['title'],                     #title
                    hit['result']['url']                        #link
                ) for hit in hits]
        return songs
    
    url = find_url(lyrics)
    response = request(url)
    songs = parse_response(response)
    return songs
    
