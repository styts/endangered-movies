#!env python
from imdb import parse_ratings


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


class TorrentCollection:
    torrents = []
    titles = []  # used by fuzzywuzzy process

    def __init__(self):
        for l in open('b3_verified.txt', 'r'):
            s = l.split('|')
            mag = s[0]
            title = s[1]
            cat = s[2]
            if cat != 'Video Movies':  # others are not movies
                continue
            self.torrents.append(Torrent(title, mag))
            self.titles.append(title)

    def get_size(self):
        return len(self.torrents)

    def findMatchingTorrents(self, movie):
        from fuzzywuzzy import process
        print process.extract(movie.title, self.titles, limit=2)


def main():
    col = MovieCollection('ratings.list')
    print col.get_size()

    tc = TorrentCollection()
    print tc.get_size()

    m1 = MovieCollection.movies[0]  # random first movie
    tc.findMatchingTorrents(m1)


main()
