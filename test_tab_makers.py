#! /usr/bin/env python3

import unittest
import tabulate


class TestTableMakers(unittest.TestCase):

    def setUp(self):
        self.tab = tabulate.Table()
        self.rain = '''
Monday      Week  Mon  Tue  Wed  Thu  Fri  Sat   Sun  Total
-----------------------------------------------------------
2019-12-30     1  0.0  0.2  0.0  0.0  1.2  0.0   0.0    1.4

2020-01-06     2  0.5  0.0  0.0  6.4  0.0  0.1   1.7    8.7
2020-01-13     3  5.3  1.7  9.1  3.0  1.7  0.0   0.0   20.8
2020-01-20     4  0.0  0.0  0.0  0.0  0.0  0.1   2.3    2.4
2020-01-27     5  8.4  2.1  0.0  0.5  1.0  0.0   7.1   19.1

2020-02-03     6  0.1  0.0  0.0  0.0  0.0  1.5  10.6   12.2
2020-02-10     7  5.5  0.0  0.5  6.6  0.0  4.9  15.6   33.1
2020-02-17     8  0.2  3.3  1.0  3.8  0.0  0.5   1.0    9.8
2020-02-24     9  6.1  0.5  0.1  8.6  5.9  7.1   0.2   28.5
'''.strip()

        self.as_csv = '''
Monday,Week,Mon,Tue,Wed,Thu,Fri,Sat,Sun,Total
2019-12-30,1,0.0,0.2,0.0,0.0,1.2,0.0,0.0,1.4
2020-01-06,2,0.5,0.0,0.0,6.4,0.0,0.1,1.7,8.7
2020-01-13,3,5.3,1.7,9.1,3.0,1.7,0.0,0.0,20.8
2020-01-20,4,0.0,0.0,0.0,0.0,0.0,0.1,2.3,2.4
2020-01-27,5,8.4,2.1,0.0,0.5,1.0,0.0,7.1,19.1
2020-02-03,6,0.1,0.0,0.0,0.0,0.0,1.5,10.6,12.2
2020-02-10,7,5.5,0.0,0.5,6.6,0.0,4.9,15.6,33.1
2020-02-17,8,0.2,3.3,1.0,3.8,0.0,0.5,1.0,9.8
2020-02-24,9,6.1,0.5,0.1,8.6,5.9,7.1,0.2,28.5
'''.strip()

        self.as_markdown = '''
Monday     | Week | Mon | Tue | Wed | Thu | Fri | Sat |  Sun | Total
---------- | ---: | --: | --: | --: | --: | --: | --: | ---: | ----:
2019-12-30 |    1 | 0.0 | 0.2 | 0.0 | 0.0 | 1.2 | 0.0 |  0.0 |   1.4
2020-01-06 |    2 | 0.5 | 0.0 | 0.0 | 6.4 | 0.0 | 0.1 |  1.7 |   8.7
2020-01-13 |    3 | 5.3 | 1.7 | 9.1 | 3.0 | 1.7 | 0.0 |  0.0 |  20.8
2020-01-20 |    4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 |  2.3 |   2.4
2020-01-27 |    5 | 8.4 | 2.1 | 0.0 | 0.5 | 1.0 | 0.0 |  7.1 |  19.1
2020-02-03 |    6 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 1.5 | 10.6 |  12.2
2020-02-10 |    7 | 5.5 | 0.0 | 0.5 | 6.6 | 0.0 | 4.9 | 15.6 |  33.1
2020-02-17 |    8 | 0.2 | 3.3 | 1.0 | 3.8 | 0.0 | 0.5 |  1.0 |   9.8
2020-02-24 |    9 | 6.1 | 0.5 | 0.1 | 8.6 | 5.9 | 7.1 |  0.2 |  28.5
'''.strip()

        self.as_tex = r'''
Monday     & Week & Mon & Tue & Wed & Thu & Fri & Sat &  Sun & Total \cr
\noalign{\vskip2pt\hrule\vskip4pt}
2019-12-30 &    1 & 0.0 & 0.2 & 0.0 & 0.0 & 1.2 & 0.0 &  0.0 &   1.4 \cr
\noalign{\medskip}
2020-01-06 &    2 & 0.5 & 0.0 & 0.0 & 6.4 & 0.0 & 0.1 &  1.7 &   8.7 \cr
2020-01-13 &    3 & 5.3 & 1.7 & 9.1 & 3.0 & 1.7 & 0.0 &  0.0 &  20.8 \cr
2020-01-20 &    4 & 0.0 & 0.0 & 0.0 & 0.0 & 0.0 & 0.1 &  2.3 &   2.4 \cr
2020-01-27 &    5 & 8.4 & 2.1 & 0.0 & 0.5 & 1.0 & 0.0 &  7.1 &  19.1 \cr
\noalign{\medskip}
2020-02-03 &    6 & 0.1 & 0.0 & 0.0 & 0.0 & 0.0 & 1.5 & 10.6 &  12.2 \cr
2020-02-10 &    7 & 5.5 & 0.0 & 0.5 & 6.6 & 0.0 & 4.9 & 15.6 &  33.1 \cr
2020-02-17 &    8 & 0.2 & 3.3 & 1.0 & 3.8 & 0.0 & 0.5 &  1.0 &   9.8 \cr
2020-02-24 &    9 & 6.1 & 0.5 & 0.1 & 8.6 & 5.9 & 7.1 &  0.2 &  28.5 \cr
'''.strip()

        self.as_latex = r'''
Monday     & Week & Mon & Tue & Wed & Thu & Fri & Sat &  Sun & Total \\
\hline
2019-12-30 &    1 & 0.0 & 0.2 & 0.0 & 0.0 & 1.2 & 0.0 &  0.0 &   1.4 \\
\noalign{\medskip}
2020-01-06 &    2 & 0.5 & 0.0 & 0.0 & 6.4 & 0.0 & 0.1 &  1.7 &   8.7 \\
2020-01-13 &    3 & 5.3 & 1.7 & 9.1 & 3.0 & 1.7 & 0.0 &  0.0 &  20.8 \\
2020-01-20 &    4 & 0.0 & 0.0 & 0.0 & 0.0 & 0.0 & 0.1 &  2.3 &   2.4 \\
2020-01-27 &    5 & 8.4 & 2.1 & 0.0 & 0.5 & 1.0 & 0.0 &  7.1 &  19.1 \\
\noalign{\medskip}
2020-02-03 &    6 & 0.1 & 0.0 & 0.0 & 0.0 & 0.0 & 1.5 & 10.6 &  12.2 \\
2020-02-10 &    7 & 5.5 & 0.0 & 0.5 & 6.6 & 0.0 & 4.9 & 15.6 &  33.1 \\
2020-02-17 &    8 & 0.2 & 3.3 & 1.0 & 3.8 & 0.0 & 0.5 &  1.0 &   9.8 \\
2020-02-24 &    9 & 6.1 & 0.5 & 0.1 & 8.6 & 5.9 & 7.1 &  0.2 &  28.5 \\
'''.strip()

        self.as_tsv = '''
Monday    \tWeek\tMon\tTue\tWed\tThu\tFri\tSat\t Sun\tTotal
2019-12-30\t   1\t0.0\t0.2\t0.0\t0.0\t1.2\t0.0\t 0.0\t  1.4
2020-01-06\t   2\t0.5\t0.0\t0.0\t6.4\t0.0\t0.1\t 1.7\t  8.7
2020-01-13\t   3\t5.3\t1.7\t9.1\t3.0\t1.7\t0.0\t 0.0\t 20.8
2020-01-20\t   4\t0.0\t0.0\t0.0\t0.0\t0.0\t0.1\t 2.3\t  2.4
2020-01-27\t   5\t8.4\t2.1\t0.0\t0.5\t1.0\t0.0\t 7.1\t 19.1
2020-02-03\t   6\t0.1\t0.0\t0.0\t0.0\t0.0\t1.5\t10.6\t 12.2
2020-02-10\t   7\t5.5\t0.0\t0.5\t6.6\t0.0\t4.9\t15.6\t 33.1
2020-02-17\t   8\t0.2\t3.3\t1.0\t3.8\t0.0\t0.5\t 1.0\t  9.8
2020-02-24\t   9\t6.1\t0.5\t0.1\t8.6\t5.9\t7.1\t 0.2\t 28.5
'''.strip()

    def test_form(self):
        "try out some outputs"

        self.tab.parse_lines(self.rain.splitlines())
        self.assertEqual(str(self.tab), self.rain)

        self.tab.do("make csv")
        self.assertEqual(str(self.tab), self.as_csv)

        self.tab.do("make tsv")
        self.assertEqual(str(self.tab), self.as_tsv)

        self.tab.do("make tex")
        self.assertEqual(str(self.tab), self.as_tex)

        self.tab.do("make latex")
        self.assertEqual(str(self.tab), self.as_latex)

        self.tab.do("make pipe")
        self.assertEqual(str(self.tab), self.as_markdown)
