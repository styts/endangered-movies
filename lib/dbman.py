from imdb import parse_ratings, get_imdb_id
import sqlite3
import re
import unicodedata


class DBManager:
    def connect(self):
        self.conn = sqlite3.connect('sqlite.db')
        self.cursor = self.conn.cursor()

    def disconnect(self):
        self.cursor.close()
        self.conn.commit()

    def __init__(self):
        self.connect()

    def __del__(self):
        self.disconnect()

    def _clear_db(self):
        self.backup_imdbids()
        self.cursor.execute('DROP TABLE movies')
        self.cursor.execute('DROP TABLE torrents')
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE movies(title TEXT PRIMARY KEY,
                rating REAL, votes INTEGER, imdb_id TEXT)""")
        self.cursor.execute("""CREATE TABLE torrents(magnet TEXT PRIMARY KEY,
                title TEXT, seeds INTEGER)""")
        self.conn.commit()

    def restore_imdbs_backup(self):
        self.disconnect()
        import os
        os.system('sqlite3 sqlite.db < data/imdb_dump.sql')
        self.connect()
        print 'imdbids backup restored.'

    def backup_imdbids(self):
        import codecs
        fp = codecs.open('data/imdb_dump.sql', 'w', 'utf-8')
        self.cursor.execute(
                'SELECT title, imdb_id FROM movies WHERE imdb_id IS NOT NULL')
        rows = self.cursor.fetchall()
        for r in rows:
            t = r[0]
            i = r[1]
            t.encode('utf8')
            if i != 'UNKNOWN':
                s = """UPDATE movies SET imdb_id = "%s" WHERE
                title = "%s";\n""" % (i, t)
                fp.write(s)
        fp.close()
        print "imdb_ids backed up in data/imdb_dump.sql."

    def populate_imdb_ids(self):
        self.cursor.execute('SELECT title FROM movies WHERE imdb_id IS NULL')
        rows = self.cursor.fetchall()
        for r in rows:
            t = r[0]
            print t
            imdb_id = get_imdb_id(t)
            self.cursor.execute("""UPDATE movies SET imdb_id = ?
                    WHERE title = ?""",
                    (imdb_id, t))
            self.conn.commit()

    def populate_db(self, thresh_rat, thresh_votes):
        self._clear_db()

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
                self.cursor.execute('INSERT INTO movies VALUES(?, ?, ?, ?)',
                    (title.decode('utf-8'), r, v, None))

        # restore imdbids backup
        self.restore_imdbs_backup()
        # populate missing imdbs
        self.populate_imdb_ids()

        ### TORRENTS
        for l in open('data/b3_verified.txt', 'r'):
            s = l.split('|')
            mag = s[0]
            title = s[1]
            cat = s[2]
            if cat != 'Video Movies':  # others are not movies
                continue
            self.cursor.execute('INSERT INTO torrents VALUES(?, ?, 0)',
                    (mag, title.decode('utf-8')))

        self.conn.commit()

        ### TORRENTS SEEDS
        for l in open('data/b3_e003_torrents.txt', 'r'):
            s = l.split('|')
            mag = s[0]
            seeds = s[1]

            if seeds != '0':
                self.cursor.execute("""UPDATE torrents SET seeds = ?
                        WHERE magnet = ?""",
                        (seeds, mag))

            if seeds == '10':   # for better overview,
                                # just a few sporadic commits
                self.conn.commit()

        self.conn.commit()
        self.cursor.execute('DELETE FROM torrents WHERE seeds == 0')

        self.conn.commit()
        self.cursor.close()

    def do_match(self):
        def likify(t, y):
            t = re.sub('\(.*?\)$', '', t).strip()
            slug = unicodedata.normalize('NFKD', t)
            slug = slug.encode('ascii', 'ignore').lower()
            slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
            slug = re.sub(r'[-]+', '%', slug)
            m_like = '%%%s%%%s%%' % (slug, y)
            return m_like

        self.cursor.execute("""SELECT title, rating FROM movies
                ORDER BY rating DESC""")
        movies = self.cursor.fetchall()
        for m in movies:
            t = m[0]
            r = m[1]
            try:
                y = re.search('\((\d+).*?\)', t).groups(0)[0]
            except:
                y = ''
            likified = likify(t, y)
            #print likified
            self.cursor.execute("""SELECT seeds FROM torrents
            WHERE title LIKE "%s"
                    ORDER BY seeds DESC""" % likified)
            torrents = self.cursor.fetchall()
            try:
                s = int(torrents[0][0])
            except:
                s = 0
            if s == 0:
                print r, likified, t, torrents

    def print_stats(self):
        self.cursor.execute('SELECT count(*) FROM movies')
        n_movies = self.cursor.fetchone()[0]
        print 'Movies:', n_movies

        self.cursor.execute('SELECT count(*) FROM torrents')
        n_torrents = self.cursor.fetchone()[0]
        print 'Torrents:', n_torrents

    def print_list(self):
        self.cursor.execute("""SELECT title, rating, votes FROM movies
                ORDER BY rating DESC""")
        for m in self.cursor.fetchall():
            print m[1], m[2], m[0]

