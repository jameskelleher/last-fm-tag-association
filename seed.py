# Goal: Construct a data set that relates Last.fm tags to each other, revealing 
# which genres (and other tags) are most associated.

# Details: Using the Last.fm API, collect the top tags among a large set of popular
# artists (1000 or more). This data should be structured and stored in whatever
# format you deem most efficient. From this raw data, create a metric that
# compares how strongly associated the tags are to each other. Feel free to
# include any weighting or balancing in your metric, as long as you can explain it.

# Methods: we can get a value of association between two tags using the method of cosine similarity.
# First, we assemble the information into a DataFrame of tag counts per artist. This DataFrame is
# indexed by artist, with each tag appearing as a column head. As all columns from the DataFrame are
# indexed identically, we can treat two columns as two vectors in the same vector space and simply
# find the cosine of the angle between them to get a value of association. For two vectors of
# postive values, the outcome will be in [0, 1]: 0 for no association, and 1 for perfect association.
# Note we are not concerned with the magnitude of either vector, but rather with their orientation.
# In other terms, we are attempting to identify how highly correlated they are.

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

# we can use the following function to generate cosine similarities for two tag strings. the
# default DataFrame is the tag_frame generated above, though the user can specify another one.
# additinoally, i've incldued a 'binary mode' that maps each element of the vectors to a 1 or
# a 0. this can be used if the user is interested in analyzing completely unweighted
# associations between two tags. given the number of 'junk tags' with low tag count, i've also
# included an option for a user to set a threshold for how many counts a tag needs to have
# before it can be included in the binary option. the verbose mode is used to print the
# results to the console.
def tag_association(t1, t2, binary=False, bin_thresh=1, df=tag_frame, verbose=False):
    v1, v2 = df[t1], df[t2]
    if binary:
        v1 = v1.apply(lambda x: 1 if x >= bin_thresh else 0)
        v2 = v2.apply(lambda x: 1 if x >= bin_thresh else 0)
    dot = np.dot(v1, v2)
    norm_prod = np.linalg.norm(v1) * np.linalg.norm(v2)
    cos_sim = dot / norm_prod
    if verbose:
        if binary:
            bm = ' in binary mode'
        else:
            bm = ''
        print 'Similarity between '+t1+' and '+t2+bm+': '+str(cos_sim)
    return cos_sim
    
# some test runs of the tag_association function
tag_association('rap', 'hip hop', verbose=True)
tag_association('rap', 'rock', verbose=True)
tag_association('rap', 'rock', binary=True, verbose=True)
tag_association('rap', 'country', verbose=True)

    
