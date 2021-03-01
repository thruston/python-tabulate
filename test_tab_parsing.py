#! /usr/bin/env python3

import unittest
import tabulate

class TestTableParsing(unittest.TestCase):

    def setUp(self):
        self.tab = tabulate.Table()
        self.rain = [
            "Monday Week Mon Tue Wed Thu Fri Sat Sun Total".split(),
            ['--'],
            "2020-01-13 3 5.3 1.7 9.1 3.0 1.7 0.0 0.0 20.8".split(),
            "2020-01-27 5 8.4 2.1 0.0 0.5 1.0 0.0 7.1 19.1".split(),
            "2020-02-03 6 0.1 0.0 0.0 0.0 0.0 1.5 10.6 12.2".split(),
            "2020-02-10 7 5.5 0.0 0.5 6.6 0.0 4.9 15.6 33.1".split(),
            [],
            "2020-02-24 9 6.1 0.5 0.1 8.6 5.9 7.1 0.2 28.5".split(),
            "2020-03-02 10 0.0 0.0 4.3 0.0 3.0 12.4 0.0 19.7".split(),
            "2020-03-09 11 0.0 4.3 6.3 1.3 1.0 1.0 0.0 13.9".split(),
            "2020-03-30 14 0.1 0.1 10.9 0.0 0.0 0.0 0.0 11.1".split()
        ]

    def test_lol(self):
        "create table from lol"
        self.tab.parse_lol(self.rain)
        
        self.assertTrue(self.tab)
        self.assertEqual(len(self.tab), 9)
        self.assertEqual(self.tab.cols, 10)
        self.assertEqual(self.tab[-1], self.rain[-1])

        expected = '''
Monday      Week  Mon  Tue   Wed  Thu  Fri   Sat   Sun  Total
-------------------------------------------------------------
2020-01-13     3  5.3  1.7   9.1  3.0  1.7   0.0   0.0   20.8
2020-01-27     5  8.4  2.1   0.0  0.5  1.0   0.0   7.1   19.1
2020-02-03     6  0.1  0.0   0.0  0.0  0.0   1.5  10.6   12.2
2020-02-10     7  5.5  0.0   0.5  6.6  0.0   4.9  15.6   33.1

2020-02-24     9  6.1  0.5   0.1  8.6  5.9   7.1   0.2   28.5
2020-03-02    10  0.0  0.0   4.3  0.0  3.0  12.4   0.0   19.7
2020-03-09    11  0.0  4.3   6.3  1.3  1.0   1.0   0.0   13.9
2020-03-30    14  0.1  0.1  10.9  0.0  0.0   0.0   0.0   11.1
'''.strip()
        self.assertEqual(str(self.tab), expected)
