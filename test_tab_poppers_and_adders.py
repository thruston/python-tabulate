#! /usr/bin/env python3
"Tests for tabulate"

import unittest
import tabulate


class TestTablePoppersAdders(unittest.TestCase):
    '''Test add pop and push
    '''

    def setUp(self):
        self.tab = tabulate.Table()
        self.rain = '''
Monday      Week  Mon  Tue  Wed  Thu  Fri   Sat   Sun  Total
------------------------------------------------------------
2019-12-30     1  0.0  0.2  0.0  0.0  1.2   0.0   0.0    1.4
2020-01-06     2  0.5  0.0  0.0  6.4  0.0   0.1   1.7    8.7
2020-01-13     3  5.3  1.7  9.1  3.0  1.7   0.0   0.0   20.8
2020-01-20     4  0.0  0.0  0.0  0.0  0.0   0.1   2.3    2.4
2020-01-27     5  8.4  2.1  0.0  0.5  1.0   0.0   7.1   19.1
2020-02-03     6  0.1  0.0  0.0  0.0  0.0   1.5  10.6   12.2
2020-02-10     7  5.5  0.0  0.5  6.6  0.0   4.9  15.6   33.1
2020-02-17     8  0.2  3.3  1.0  3.8  0.0   0.5   1.0    9.8
2020-02-24     9  6.1  0.5  0.1  8.6  5.9   7.1   0.2   28.5
2020-03-02    10  0.0  0.0  4.3  0.0  3.0  12.4   0.0   19.7
'''.strip()
        self.rain_summary = '''
Monday      Week  Mon  Tue  Wed  Thu  Fri   Sat   Sun  Total
------------------------------------------------------------
2019-12-30     1  0.0  0.2  0.0  0.0  1.2   0.0   0.0    1.4
2020-01-06     2  0.5  0.0  0.0  6.4  0.0   0.1   1.7    8.7
2020-01-13     3  5.3  1.7  9.1  3.0  1.7   0.0   0.0   20.8
2020-01-20     4  0.0  0.0  0.0  0.0  0.0   0.1   2.3    2.4
2020-01-27     5  8.4  2.1  0.0  0.5  1.0   0.0   7.1   19.1
2020-02-03     6  0.1  0.0  0.0  0.0  0.0   1.5  10.6   12.2
2020-02-10     7  5.5  0.0  0.5  6.6  0.0   4.9  15.6   33.1
2020-02-17     8  0.2  3.3  1.0  3.8  0.0   0.5   1.0    9.8
2020-02-24     9  6.1  0.5  0.1  8.6  5.9   7.1   0.2   28.5
2020-03-02    10  0.0  0.0  4.3  0.0  3.0  12.4   0.0   19.7
------------------------------------------------------------
Min            1  0.0  0.0  0.0  0.0  0.0   0.0   0.0    1.4
Median         5  0.2  0.0  0.0  0.5  0.0   0.1   1.0   12.2
Mean           5  2.2  0.6  1.2  2.4  1.1   2.2   3.3   14.1
Max           10  8.4  3.3  9.1  8.6  5.9  12.4  15.6   33.1
'''.strip()
        self.total_rain = '''
Monday      Week   Mon  Tue   Wed   Thu   Fri   Sat   Sun  Total
----------------------------------------------------------------
2019-12-30     1   0.0  0.2   0.0   0.0   1.2   0.0   0.0    1.4
2020-01-06     2   0.5  0.0   0.0   6.4   0.0   0.1   1.7    8.7
2020-01-13     3   5.3  1.7   9.1   3.0   1.7   0.0   0.0   20.8
2020-01-20     4   0.0  0.0   0.0   0.0   0.0   0.1   2.3    2.4
2020-01-27     5   8.4  2.1   0.0   0.5   1.0   0.0   7.1   19.1
2020-02-03     6   0.1  0.0   0.0   0.0   0.0   1.5  10.6   12.2
2020-02-10     7   5.5  0.0   0.5   6.6   0.0   4.9  15.6   33.1
2020-02-17     8   0.2  3.3   1.0   3.8   0.0   0.5   1.0    9.8
2020-02-24     9   6.1  0.5   0.1   8.6   5.9   7.1   0.2   28.5
2020-03-02    10   0.0  0.0   4.3   0.0   3.0  12.4   0.0   19.7
----------------------------------------------------------------
Total         55  26.1  7.8  15.0  28.9  12.8  26.6  38.5  155.7
'''.strip()
        self.mean_rain = '''
Monday      Week   Mon   Tue  Wed   Thu   Fri   Sat   Sun  Total
----------------------------------------------------------------
2019-12-30     1   0.0   0.2  0.0   0.0   1.2   0.0   0.0    1.4
2020-01-06     2   0.5   0.0  0.0   6.4   0.0   0.1   1.7    8.7
2020-01-13     3   5.3   1.7  9.1   3.0   1.7   0.0   0.0   20.8
2020-01-20     4   0.0   0.0  0.0   0.0   0.0   0.1   2.3    2.4
2020-01-27     5   8.4   2.1  0.0   0.5   1.0   0.0   7.1   19.1
2020-02-03     6   0.1   0.0  0.0   0.0   0.0   1.5  10.6   12.2
2020-02-10     7   5.5   0.0  0.5   6.6   0.0   4.9  15.6   33.1
2020-02-17     8   0.2   3.3  1.0   3.8   0.0   0.5   1.0    9.8
2020-02-24     9   6.1   0.5  0.1   8.6   5.9   7.1   0.2   28.5
2020-03-02    10   0.0   0.0  4.3   0.0   3.0  12.4   0.0   19.7
----------------------------------------------------------------
Mean         5.5  2.61  0.78  1.5  2.89  1.28  2.66  3.85  15.57
'''.strip()
        self.max_rain = '''
Monday      Week  Mon  Tue  Wed  Thu  Fri   Sat   Sun  Total
------------------------------------------------------------
2019-12-30     1  0.0  0.2  0.0  0.0  1.2   0.0   0.0    1.4
2020-01-06     2  0.5  0.0  0.0  6.4  0.0   0.1   1.7    8.7
2020-01-13     3  5.3  1.7  9.1  3.0  1.7   0.0   0.0   20.8
2020-01-20     4  0.0  0.0  0.0  0.0  0.0   0.1   2.3    2.4
2020-01-27     5  8.4  2.1  0.0  0.5  1.0   0.0   7.1   19.1
2020-02-03     6  0.1  0.0  0.0  0.0  0.0   1.5  10.6   12.2
2020-02-10     7  5.5  0.0  0.5  6.6  0.0   4.9  15.6   33.1
2020-02-17     8  0.2  3.3  1.0  3.8  0.0   0.5   1.0    9.8
2020-02-24     9  6.1  0.5  0.1  8.6  5.9   7.1   0.2   28.5
2020-03-02    10  0.0  0.0  4.3  0.0  3.0  12.4   0.0   19.7
------------------------------------------------------------
Max           10  8.4  3.3  9.1  8.6  5.9  12.4  15.6   33.1
'''.strip()
        self.median_rain = '''
Monday      Week   Mon  Tue   Wed   Thu  Fri   Sat   Sun  Total
---------------------------------------------------------------
2019-12-30     1   0.0  0.2   0.0   0.0  1.2   0.0   0.0    1.4
2020-01-06     2   0.5  0.0   0.0   6.4  0.0   0.1   1.7    8.7
2020-01-13     3   5.3  1.7   9.1   3.0  1.7   0.0   0.0   20.8
2020-01-20     4   0.0  0.0   0.0   0.0  0.0   0.1   2.3    2.4
2020-01-27     5   8.4  2.1   0.0   0.5  1.0   0.0   7.1   19.1
2020-02-03     6   0.1  0.0   0.0   0.0  0.0   1.5  10.6   12.2
2020-02-10     7   5.5  0.0   0.5   6.6  0.0   4.9  15.6   33.1
2020-02-17     8   0.2  3.3   1.0   3.8  0.0   0.5   1.0    9.8
2020-02-24     9   6.1  0.5   0.1   8.6  5.9   7.1   0.2   28.5
2020-03-02    10   0.0  0.0   4.3   0.0  3.0  12.4   0.0   19.7
---------------------------------------------------------------
Median       5.5  0.35  0.1  0.05  1.75  0.5   0.3  1.35  15.65
'''.strip()
        self.sorted_by_total = '''
Monday      Week   Mon   Tue  Wed   Thu   Fri   Sat   Sun  Total
----------------------------------------------------------------
2019-12-30     1   0.0   0.2  0.0   0.0   1.2   0.0   0.0    1.4
2020-01-20     4   0.0   0.0  0.0   0.0   0.0   0.1   2.3    2.4
2020-01-06     2   0.5   0.0  0.0   6.4   0.0   0.1   1.7    8.7
2020-02-17     8   0.2   3.3  1.0   3.8   0.0   0.5   1.0    9.8
2020-02-03     6   0.1   0.0  0.0   0.0   0.0   1.5  10.6   12.2
2020-01-27     5   8.4   2.1  0.0   0.5   1.0   0.0   7.1   19.1
2020-03-02    10   0.0   0.0  4.3   0.0   3.0  12.4   0.0   19.7
2020-01-13     3   5.3   1.7  9.1   3.0   1.7   0.0   0.0   20.8
2020-02-24     9   6.1   0.5  0.1   8.6   5.9   7.1   0.2   28.5
2020-02-10     7   5.5   0.0  0.5   6.6   0.0   4.9  15.6   33.1
----------------------------------------------------------------
Mean         5.5  2.61  0.78  1.5  2.89  1.28  2.66  3.85  15.57
'''.strip()

    def test_adders(self):
        "It's the adding up..."
        self.tab.parse_lines(self.rain.splitlines())
        self.assertEqual(str(self.tab), self.rain)

        self.tab.do("rule add")
        self.assertEqual(str(self.tab), self.total_rain)

        self.tab.do("pop add mean")
        self.assertEqual(str(self.tab), self.mean_rain)

        self.tab.do("pop add median")
        self.assertEqual(str(self.tab), self.median_rain)

        self.tab.do("pop add max")
        self.assertEqual(str(self.tab), self.max_rain)

        self.tab.do("pop add summary dp 001")
        self.assertEqual(str(self.tab), self.rain_summary)

    def test_special_adding(self):
        "And the taking away..."
        self.tab.clear()
        self.tab.parse_lines('''
Year              Class A              Class B
2001   0.9955302869874892  0.32216042430627556
2003   0.5050938597046872  0.20169540227995664
2005  0.47432722599413435   0.4916281875757852
2007   0.8846767634771708   0.6758599498240474
2009   0.7307419168402146  0.20096087617739122
'''.strip().splitlines())

        self.tab.do("rule add mean")
        self.assertEqual(str(self.tab), '''
Year              Class A              Class B
2001   0.9955302869874892  0.32216042430627556
2003   0.5050938597046872  0.20169540227995664
2005  0.47432722599413435   0.4916281875757852
2007   0.8846767634771708   0.6758599498240474
2009   0.7307419168402146  0.20096087617739122
----------------------------------------------
Mean       0.718074010601       0.378460968033
'''.strip())

    def test_unknown_function(self):
        self.tab.parse_lines(self.rain.splitlines())
        self.assertEqual(str(self.tab), self.rain)

        self.tab.do("rule add gmean")
        self.assertEqual(str(self.tab), '? gmean\n' + self.rain)

    def test_poppers(self):
        "Various pop push manoeuvers..."
        self.tab.parse_lines(self.rain.splitlines())
        self.assertEqual(str(self.tab), self.rain)

        self.tab.do("pop push")
        self.assertEqual(str(self.tab), self.rain)

        self.tab.do("pop 0 push 0")
        self.assertEqual(str(self.tab), self.rain)

        self.tab.do("rule add mean")
        self.assertEqual(str(self.tab), self.mean_rain)

        self.tab.do("pop sort z push")
        self.assertEqual(str(self.tab), self.sorted_by_total)

        self.tab.do("roll pop 0 push")
        self.assertEqual(str(self.tab), self.sorted_by_total)

        self.tab.do("pop 94")  # index out of bounds == nop
        self.assertEqual(str(self.tab), self.sorted_by_total)

        self.tab.do("push")  # push with no preceding pop == nop
        self.assertEqual(str(self.tab), self.sorted_by_total)

        self.tab.do("pop push 94")  # index out of bounds ok on insert
        self.assertEqual(str(self.tab), self.sorted_by_total)
