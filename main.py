#!env python
from imdb import parse_ratings
import sqlite3
#import os

thresh_rat = 3.0
thresh_votes = 10000


class Movie:
    title = ""
    rating = 0.0
    votes = 0

    def __init__(self, t, r, v):
        self.title = t
        self.rating = r
        self.votes = v


class MovieCollection:
    movies = []

    def __init__(self, fn, thresh_rat=3.0, thresh_votes=10000):
        rs = parse_ratings('ratings.list')

        for title in rs:
            s = rs[title]
            r = s[0]
            v = s[1]
            if r >= thresh_rat and v >= thresh_votes:
                self.movies.append(Movie(title, r, v))

    def get_size(self):
        return len(self.movies)


class Torrent:
    title = ""
    magnet = ""
    seeds = 0

    def __init__(self, t, m):
        self.title = t
        self.magnet = m

    def get_resolution():
        return "720p"


def populate_db():
    global thresh_rat, thresh_votes

    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()

    ### MOVIES
    rs = parse_ratings('data/ratings.list')

    for title in rs:
        s = rs[title]
        r = s[0]
        v = s[1]
        if r >= thresh_rat and v >= thresh_votes:
            cursor.execute('INSERT INTO movies VALUES(?, ?, ?)',
                (title.decode('utf-8'), r, v))

    ### TORRENTS
    for l in open('data/b3_verified.txt', 'r'):
        s = l.split('|')
        mag = s[0]
        title = s[1]
        cat = s[2]
        if cat != 'Video Movies':  # others are not movies
            continue
        cursor.execute('INSERT INTO torrents VALUES(?, ?, 0)', (mag, title.decode('utf-8')))

    conn.commit()

    ### TORRENTS SEEDS
    for l in open('data/b3_e003_torrents.txt', 'r'):
        s = l.split('|')
        mag = s[0]
        seeds = s[1]

        if seeds != '0':
            cursor.execute('UPDATE torrents SET seeds = ? WHERE magnet = ?', (seeds, mag))

        if seeds == '10':  # for better overview, just a few sporadic commits
            conn.commit()

    conn.commit()
    cursor.execute('DELETE FROM torrents WHERE seeds == 0')

    conn.commit()
    cursor.close()


def main():
    #col = MovieCollection('ratings.list')
    #print col.get_size()
    #m1 = col.movies[0]
    #print m1.title
    populate_db()

main()
