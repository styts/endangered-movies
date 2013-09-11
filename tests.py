#!env python
import unittest
from lib.imdb import get_imdb_id


class Foo(unittest.TestCase):
    def test_imdb_id_Memento(self):
        """Tests that the IMDBAPI interface works"""
        self.assertEqual(get_imdb_id('Memento'), 'tt0209144')

if __name__ == '__main__':
    unittest.main()
