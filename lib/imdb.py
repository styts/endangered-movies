# -*- coding: utf-8 -*-

import re
import unicodedata
#============================== RATINGS ======================================#

# General rating format:
#'      2..222...2       5   5.2  "#1 College Sports Show, The" (2004)'

RATINGS_RE = r"""(?x)                          # turn on verbose mode
                 ^                             # grab from start
                 \s+                           #
                 (.*?) # distribution chars, 10 times
                 \s+                           #
                 (?P<votes>\d+)                # number of votes
                 \s+                           #
                 (?P<rating>\d+\.\d+)          # the rating 0-10.x
                 \s+                           #
                 (?P<title>.*)                 # the title
                 $                             # end of string
                 """

def parse_ratings(filename):
    """
    Parses ratings out of IMDB's ratings.list. Returns a map of IMDB
    titles to ratings.
    """
    matcher = re.compile(RATINGS_RE)
    #title_matcher = re.compile(TITLE_RE)
    ratings_index = {}

    with open(filename,"r") as f:
        for line in f:
            line = line.decode('latin1').encode('utf-8')
            match = matcher.match(line)
            if match:
                title = match.group('title')
                rating = match.group('rating')
                votes = match.group('votes')
                #if title[0] != '"': # is a movie
                ratings_index[title] = ( float(rating), int(votes) )

    return ratings_index


# TODO
def get_imdb_id(title):
    import json
    import urllib2, urllib
    url = 'http://www.imdbapi.com/?' + urllib.urlencode({'t': title.encode("utf-8")})
    print url
    f = urllib2.urlopen(url)
    response = f.read()
    j = json.loads(response)
    try:
        imdb = j['imdbID']
    except: # e.g. in 'A Man for All Seasons'
        imdb = 'UNKNOWN'

    print imdb
    #print j
    #print response
    #imdb = "a0205870"
    return imdb
