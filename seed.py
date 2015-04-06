import json

import pandas as pd
import numpy as np

from requests import get
from pandas import Series, DataFrame

api_key = 'ed6cd1dd2b34712cbf3018387d28332b'

# endpoint
url = 'http://ws.audioscrobbler.com/2.0/'

# parameters needed to use the 'chart.getTopArtists' method
params = {'method': 'chart.getTopArtists', 'api_key': api_key, 'format': 'json', 'limit': 1000}

# IMPORTANT NOTE: in my personal testing, for a while the 'chart.getTopArtists' method failed
# to return information. this was most likely an issue on last.fm's side. if the issue persists,
# uncommenting the following line will allow you to test the code using 'chart.getHypedArtists'

# params['method'] = 'chart.getHypedArtists'

# a list of all necessary artist info
artists = get(url, params=params).json()['artists']['artist']
            
# will be used to construct a DataFrame the relates artists to tag counts                     
tag_series = []

# parameters needed to use the 'artist.getTopTags' method
params = {'method': 'artist.getTopTags', 'api_key': api_key, 'format':'json'}

for artist in artists:
    
    # we add the artist to the parameters
    params['artist'] = artist['name']
    
    tags = get(url, params=params).json()
    
    # the api tends to be error-prone, and will frequently not retrieve any tags for popular 
    # artists. in that case, we simply ignore the error and carry on after warning the user
    if 'toptags' in tags and 'tag' in tags['toptags']:
        tags = tags['toptags']['tag']
    else:
        print 'Warning: no tags found for artist: ' + artist['name']
        continue
        
    # if there is only one tag, 'tags' is a dict, instead of a list
    # we need to make sure 'tags' is always a list
    if isinstance(tags, dict):
        tags = [tags]
        
    # tag_info is used to build the Series that we in turn use to build the DataFrame
    tag_info = {}
    for tag in tags:
        # it is my understanding that when a tag has 'count' = 0, only one user submitted the
        # tag (otherwise, there simply wouldn't be a tag). therefore, 'count' = 0 really means a 
        # single tag. it follows that all counts should be incremented by 1, given that last.fm
        # apparently begins its count at 0. additionally, sometimes 'count' will be 0, in which
        # case I assume that 'count' is meant to be 0
        c = tag['count']
        if c == '':
            c = 0
        tag_info[tag['name']] = int(c) + 1
        
    
    # construct a series indexed on tag counts
    s = Series(tag_info, name=artist['name'])
    
    # add the series to our list
    tag_series.append(s)

# create the DataFrame. since 'count' = 0 really means 'count' = 1, missing info can therefore
# be filled as 0
tag_frame = DataFrame(tag_series).fillna(0)

def tag_association(t1, t2, df=tag_frame):
    v1, v2 = df[t1], df[t2]
    dot = np.dot(v1, v2)
    norm_prod = np.linalg.norm(v1) * np.linalg.norm(v2)
    cos_sim = dot / norm_prod
    return cos_sim
    
rh = tag_association('rap', 'hip hop')
rr = tag_association('rap', 'rock')
rc = tag_association('rap', 'country')

print 'Similarity between rap and hip-hop: ' + rh
print 'Similarity between rap and rock: ' + rr
print 'Similarity between rap and country: ' + rc

    