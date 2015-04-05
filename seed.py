import requests
import json

api_key = 'ed6cd1dd2b34712cbf3018387d28332b'
# api_secret = 'c24df07c9de358b09d0991fd623df366'

url = 'http://ws.audioscrobbler.com/2.0/'

resp = requests.get(url, params={'method': 'chart.getTopArtists',
                                 'api_key': api_key,
                                 'format': 'json',
                                 'limit': 1000})
                                 
artists = json.loads(resp.text)['artists']['artist']

params = {'method': }
for artist in artists:
    artist_tags = requests.get(url, params=)