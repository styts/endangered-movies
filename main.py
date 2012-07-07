#!env python
from imdb import parse_ratings, get_imdb_id
import sqlite3
import re
import unicodedata

thresh_rat = 3.0
thresh_votes = 5000


def _clear_db():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE movies')
    cursor.execute('DROP TABLE torrents')
    conn.commit()
    cursor.execute("""CREATE TABLE movies(title TEXT PRIMARY KEY,
            rating REAL, votes INTEGER, imdb_id TEXT)""")
    cursor.execute("""CREATE TABLE torrents(magnet TEXT PRIMARY KEY,
            title TEXT, seeds INTEGER)""")
    conn.commit()
    cursor.close()

def populate_imdb_ids():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title FROM movies WHERE imdb_id == ""')
    rows = cursor.fetchall()
    for r in rows:
        t = r[0]
        imdb_id = get_imdb_id(t)
        cursor.execute('UPDATE movies WHERE title == ? SET imdb_id = ?',
                t, imdb_id)
        conn.commit()


def populate_db():
    global thresh_rat, thresh_votes

    _clear_db()

    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()

    ### MOVIES
    rs = parse_ratings('data/ratings.list')

    for title in rs:
        s = rs[title]
        r = s[0]
        v = s[1]
        if title[0] == '"':  # it's a show
            continue
        if "(VG)" in title:  # it's a video game
            continue
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
        cursor.execute('INSERT INTO torrents VALUES(?, ?, 0)',
                (mag, title.decode('utf-8')))

    conn.commit()

    ### TORRENTS SEEDS
    for l in open('data/b3_e003_torrents.txt', 'r'):
        s = l.split('|')
        mag = s[0]
        seeds = s[1]

        if seeds != '0':
            cursor.execute('UPDATE torrents SET seeds = ? WHERE magnet = ?',
                    (seeds, mag))

        if seeds == '10':  # for better overview, just a few sporadic commits
            conn.commit()

    conn.commit()
    cursor.execute('DELETE FROM torrents WHERE seeds == 0')

    conn.commit()
    cursor.close()


def likify(t, y):
    t = re.sub('\(.*?\)$', '', t).strip()
    slug = unicodedata.normalize('NFKD', t)
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '%', slug)
    m_like = '%%%s%%%s%%' % (slug, y)
    return m_like


def do_match():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, rating FROM movies ORDER BY rating DESC')
    movies = cursor.fetchall()
    for m in movies:
        t = m[0]
        r = m[1]
        try:
            y = re.search('\((\d+).*?\)', t).groups(0)[0]
        except:
            y = ''
        likified = likify(t, y)
        #print likified
        cursor.execute("""SELECT seeds FROM torrents WHERE title LIKE "%s"
                ORDER BY seeds DESC""" % likified)
        torrents = cursor.fetchall()
        try:
            s = int(torrents[0][0])
        except:
            s = 0
        if s == 0:
            print r, likified, t, torrents


def print_stats():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()

    cursor.execute('SELECT count(*) FROM movies')
    n_movies = cursor.fetchone()[0]
    print 'Movies:', n_movies

    cursor.execute('SELECT count(*) FROM torrents')
    n_torrents = cursor.fetchone()[0]
    print 'Torrents:', n_torrents

    cursor.close()


def foo():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT title, rating, votes FROM movies
            ORDER BY rating DESC""")
    for m in cursor.fetchall():
        print m[1], m[2], m[0]


def main():
    #populate_db()
    #do_match()
    #foo()
    #print_stats()
    #populate_imdb_ids()
    t = 'Memento'
    imdb_id = get_imdb_id(t)
    print t, imdb_id
    pass

main()
