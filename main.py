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


def main():
    col = MovieCollection('ratings.list')
    print col.get_size()

main()
