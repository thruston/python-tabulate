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
        self.tab.parse_lol(self.rain)
        self.expected = '''
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

    def test_lol(self):
        "create table from lol"

        self.assertTrue(self.tab)
        self.assertEqual(len(self.tab), 9)
        self.assertEqual(self.tab.cols, 10)
        self.assertEqual(self.tab[-1], self.rain[-1])
        self.assertEqual(str(self.tab), self.expected)

    def test_copy_data(self):
        "copy and create new table"
        self.bat = tabulate.Table()
        self.bat.parse_lol(self.tab.copy())

        self.assertTrue(self.bat)
        self.assertEqual(len(self.bat), 9)
        self.assertEqual(self.bat.cols, 10)
        self.assertEqual(self.bat[-1], self.rain[-1])

        # extras are not copied...
        self.bat.add_rule(1)
        self.bat.add_blank(5)
        self.assertEqual(str(self.bat), self.expected)

    def test_parselines(self):
        "create table from lines"
        self.assertEqual(self.tab.indent, 0)
        self.tab.parse_lines('''# data has a long descriptive comment
    2020-05-19  09:18:00  30.3  30.2  30.1  28.9  29.8  29.6  29.9  30.2   135   4.5
    2020-05-19  09:18:10  29.2  29.1  29.4  30.5  30.2  30.3  30.0  29.5   132   4.5
    2020-05-19  09:18:20  29.2  28.8  28.6  29.2  29.2  29.3  29.1  28.8   136   4.7
    2020-05-19  09:18:30  31.2  31.6  31.2  29.6  29.2  29.1  29.2  29.3   155   5.0
    2020-05-19  09:18:40  33.1  32.9  31.9  31.1  29.3  29.5  28.6  27.8   208   6.3
    2020-05-19  09:18:50  29.1  29.2  30.2  31.0  31.8  31.2  31.9  30.2   197   6.8
    2020-05-19  09:19:00  32.3  30.7  26.8  23.8  25.2  24.6  21.3  19.4   326  10.1
    2020-05-19  09:19:10  31.4  33.1  26.2  20.2  14.5  15.6  12.9  14.6   494  15.7

    2020-05-19  09:19:20  32.9  33.1  31.5  27.4  32.8  32.8  26.5  15.2   671  20.4
    2020-05-19  09:19:30  30.9  30.9  26.3  25.0  24.8  24.9  23.9  25.1   729  23.6
    2020-05-19  09:19:40  34.3  34.0  29.5  23.8  24.0  24.1  22.6  20.3   869  25.3
    2020-05-19  09:19:50  31.0  30.9  28.2  26.6  26.0  25.8  19.4  19.9   980  31.6
    2020-05-19  09:20:00  29.8  29.7  28.6  25.5  25.2  25.3  23.9  17.2  1106  37.1
    2020-05-19  09:20:10  29.3  29.7  25.9  25.5  25.3  25.2  23.3  21.0  1189  40.6
    2020-05-19  09:20:20  30.1  29.8  27.1  25.0  25.3  24.1  22.7  21.7  1273  42.3
    2020-05-19  09:20:30  28.3  28.2  29.1  25.3  22.9  24.4  24.3  18.1  1375  48.6
    ----
    2020-05-19  09:20:40  28.3  28.6  22.5  22.3  24.1  23.7  19.7  23.0  1428  50.5'''.splitlines())
        self.assertEqual(self.tab.cols, 12)
        self.assertEqual(len(self.tab.data), 17)
        self.assertEqual(self.tab.indent, 4)

        self.assertEqual(str(self.tab), '''# data has a long descriptive comment
    2020-05-19  09:18:00  30.3  30.2  30.1  28.9  29.8  29.6  29.9  30.2   135   4.5
    2020-05-19  09:18:10  29.2  29.1  29.4  30.5  30.2  30.3  30.0  29.5   132   4.5
    2020-05-19  09:18:20  29.2  28.8  28.6  29.2  29.2  29.3  29.1  28.8   136   4.7
    2020-05-19  09:18:30  31.2  31.6  31.2  29.6  29.2  29.1  29.2  29.3   155   5.0
    2020-05-19  09:18:40  33.1  32.9  31.9  31.1  29.3  29.5  28.6  27.8   208   6.3
    2020-05-19  09:18:50  29.1  29.2  30.2  31.0  31.8  31.2  31.9  30.2   197   6.8
    2020-05-19  09:19:00  32.3  30.7  26.8  23.8  25.2  24.6  21.3  19.4   326  10.1
    2020-05-19  09:19:10  31.4  33.1  26.2  20.2  14.5  15.6  12.9  14.6   494  15.7

    2020-05-19  09:19:20  32.9  33.1  31.5  27.4  32.8  32.8  26.5  15.2   671  20.4
    2020-05-19  09:19:30  30.9  30.9  26.3  25.0  24.8  24.9  23.9  25.1   729  23.6
    2020-05-19  09:19:40  34.3  34.0  29.5  23.8  24.0  24.1  22.6  20.3   869  25.3
    2020-05-19  09:19:50  31.0  30.9  28.2  26.6  26.0  25.8  19.4  19.9   980  31.6
    2020-05-19  09:20:00  29.8  29.7  28.6  25.5  25.2  25.3  23.9  17.2  1106  37.1
    2020-05-19  09:20:10  29.3  29.7  25.9  25.5  25.3  25.2  23.3  21.0  1189  40.6
    2020-05-19  09:20:20  30.1  29.8  27.1  25.0  25.3  24.1  22.7  21.7  1273  42.3
    2020-05-19  09:20:30  28.3  28.2  29.1  25.3  22.9  24.4  24.3  18.1  1375  48.6
    --------------------------------------------------------------------------------
    2020-05-19  09:20:40  28.3  28.6  22.5  22.3  24.1  23.7  19.7  23.0  1428  50.5''')

    def test_tex(self):
        "parse TeX source"

        self.tab.parse_tex(r'''This&3&4\cr
% ignore this comment
The other & 34 & 91 \cr
\noalign{\medskip}
The other & 34 & 91 \cr
\noalign{\vskip2pt\hrule\vskip4pt}
Total & 71 & 186 \cr'''.splitlines())

        self.assertEqual(str(self.tab), '''
This        3    4
# ignore this comment
The other  34   91

The other  34   91
------------------
Total      71  186
'''.strip())

        self.tab.parse_tex(r'''This&3&4\\
The other & 34 & 91 \\
The other & 34 & 91 \\
\hline
Total & 71 & 186'''.splitlines())

        self.assertEqual(str(self.tab), '''
This        3    4
The other  34   91
The other  34   91
------------------
Total      71  186
'''.strip())

    def test_nothing(self):
        self.nulltab = tabulate.Table()
        self.nulltab.parse_lines("")
        self.assertEqual(str(self.nulltab), '')
