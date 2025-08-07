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
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
                # in case of genius changing permissions again:
                # navigate to 'https://genius.com/api/search/lyric?q=whos%20calling' in browser
                # inspect element, go to network, rerequest
                # copy user-agent into this header
                }
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
    
