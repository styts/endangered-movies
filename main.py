#!env python
"""Endangered Movies

Usage: main.py [options]

Options:
    -l, --list      List Movies
    -s, --stats     Display # of Movies and Torrents
    -v, --version   Show version.
    -h, --help      Disply this message
    --imdbs         Populate imdb_ids from imdbAPI.com
    --match         Match movies to their torrents
    --populate      Populate DB from imdb files (HANDLE WITH CARE)
    --backup        Backup imdbs
    --restore       Restore imdbs
"""
import docopt
from lib.dbman import DBManager

thresh_rat = 3.0
thresh_votes = 5000


def main():
    global thresh_rat, thresh_votes
    dbm = DBManager()

    args = docopt.docopt(__doc__, version='0.1.1rc')
    if args['--list']:
        dbm.print_list()
    if args['--stats']:
        dbm.print_stats()
    if args['--imdbs']:
        dbm.populate_imdb_ids()
    if args['--match']:
        dbm.do_match()
    if args['--populate']:
        dbm.populate_db(thresh_rat, thresh_votes)
    if args['--backup']:
        dbm.backup_imdbids()
    if args['--restore']:
        dbm.restore_imdbs_backup()

if __name__ == '__main__':
    main()
