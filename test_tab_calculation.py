#! /usr/bin/env python3

import unittest

import tabulate


class TestTableCalculation(unittest.TestCase):

    def setUp(self):
        self.tab = tabulate.Table()
        self.simple = '''
30.2   135   4.5
29.5   132   4.5
28.8   136   4.7
29.3   155   5.0
27.8   208   6.3
18.1  1375  48.6
23.0  1428  50.5
'''.strip()

    def test_functions(self):
        self.tab.parse_lines(self.simple.splitlines())
        self.tab.do("arr abc(sqrt(b))(sqrt(a))")
        self.assertEqual(str(self.tab), '''
30.2   135   4.5  11.6189500386  5.49545266561
29.5   132   4.5  11.4891252931  5.43139024560
28.8   136   4.7  11.6619037897  5.36656314600
29.3   155   5.0  12.4498995980  5.41294744109
27.8   208   6.3  14.4222051019  5.27257053059
18.1  1375  48.6  37.0809924355  4.25440947724
23.0  1428  50.5  37.7888872554  4.79583152331
'''.strip())
        self.tab.do("arr abc(log(b))(log(a))")
        self.assertEqual(str(self.tab), '''
30.2   135   4.5  4.90527477844  3.40784192438
29.5   132   4.5  4.88280192259  3.38439026335
28.8   136   4.7  4.91265488574  3.36037538714
29.3   155   5.0  5.04342511692  3.37758751602
27.8   208   6.3  5.33753807970  3.32503602070
18.1  1375  48.6  7.22620901010  2.89591193827
23.0  1428  50.5  7.26403014290  3.13549421593
'''.strip())
        self.tab.do("arr abc(log10(b))(log10(a))")
        self.assertEqual(str(self.tab), '''
30.2   135   4.5  2.13033376850  1.48000694296
29.5   132   4.5  2.12057393121  1.46982201598
28.8   136   4.7  2.13353890837  1.45939248776
29.3   155   5.0  2.19033169817  1.46686762035
27.8   208   6.3  2.31806333496  1.44404479592
18.1  1375  48.6  3.13830269817  1.25767857487
23.0  1428  50.5  3.15472820744  1.36172783602
'''.strip())
        self.tab.do("arr abc(divmod(b, 37))")
        self.assertEqual(str(self.tab), '''
30.2   135   4.5   3  24
29.5   132   4.5   3  21
28.8   136   4.7   3  25
29.3   155   5.0   4   7
27.8   208   6.3   5  23
18.1  1375  48.6  37   6
23.0  1428  50.5  38  22
'''.strip())
        self.tab.do("arr abc(sum(c,d,e))")
        self.assertEqual(str(self.tab), '''
30.2   135   4.5   31.5
29.5   132   4.5   28.5
28.8   136   4.7   32.7
29.3   155   5.0   16.0
27.8   208   6.3   34.3
18.1  1375  48.6   91.6
23.0  1428  50.5  110.5
'''.strip())

        self.tab.parse_lines('''
2020-05-19  09:18:00  30.3  30.1  30.2
2020-05-19  09:18:10  29.2  29.4  29.1
2020-05-19  09:18:20  29.2  28.6  28.8
2020-05-19  09:18:30  31.2  31.2  31.6
2020-05-19  09:18:40  33.1  31.9  32.9
2020-05-19  09:20:30  28.3  29.1  28.2
2020-05-19  09:20:40  28.3  22.5  28.6
'''.strip().splitlines())
        self.tab.do("arr ~(y/z)")
        self.assertEqual(str(self.tab), '''
2020-05-19  09:18:00  30.3  30.1  30.2  0.996688741722
2020-05-19  09:18:10  29.2  29.4  29.1   1.01030927835
2020-05-19  09:18:20  29.2  28.6  28.8  0.993055555556
2020-05-19  09:18:30  31.2  31.2  31.6  0.987341772152
2020-05-19  09:18:40  33.1  31.9  32.9  0.969604863222
2020-05-19  09:20:30  28.3  29.1  28.2   1.03191489362
2020-05-19  09:20:40  28.3  22.5  28.6  0.786713286713
'''.strip())
        self.tab.do("arr -z arr ~(sqrt(c) dp 001144")
        self.assertEqual(str(self.tab), '''
2020-05-19  09:18:00  30.3  30.1  30.2000  5.5045
2020-05-19  09:18:10  29.2  29.4  29.1000  5.4037
2020-05-19  09:18:20  29.2  28.6  28.8000  5.4037
2020-05-19  09:18:30  31.2  31.2  31.6000  5.5857
2020-05-19  09:18:40  33.1  31.9  32.9000  5.7533
2020-05-19  09:20:30  28.3  29.1  28.2000  5.3198
2020-05-19  09:20:40  28.3  22.5  28.6000  5.3198
'''.strip())
        self.tab.do("arr abccde roll d arr abc{c-d}ef")
        self.assertEqual(str(self.tab), '''
2020-05-19  09:18:00  30.3   2.0  30.1  30.2000
2020-05-19  09:18:10  29.2  -1.1  29.4  29.1000
2020-05-19  09:18:20  29.2   0.0  28.6  28.8000
2020-05-19  09:18:30  31.2   2.0  31.2  31.6000
2020-05-19  09:18:40  33.1   1.9  31.9  32.9000
2020-05-19  09:20:30  28.3  -4.8  29.1  28.2000
2020-05-19  09:20:40  28.3   0.0  22.5  28.6000
'''.strip())
        self.tab.do("arr abc('Aok  {:.2f}'.format(f)")
        self.assertEqual(str(self.tab), '''
2020-05-19  09:18:00  30.3  Aok 30.20
2020-05-19  09:18:10  29.2  Aok 29.10
2020-05-19  09:18:20  29.2  Aok 28.80
2020-05-19  09:18:30  31.2  Aok 31.60
2020-05-19  09:18:40  33.1  Aok 32.90
2020-05-19  09:20:30  28.3  Aok 28.20
2020-05-19  09:20:40  28.3  Aok 28.60
'''.strip())

        self.tab.do("arr abc?")
        self.assertTrue(all(0 <= x[1] < 1 for x in self.tab.column(3)))

        self.tab.do("arr abc(20*?+4)")
        self.assertTrue(all(4 <= x[1] < 24 for x in self.tab.column(3)))

    def test_normalize_and_tap(self):
        "Test table wide processing..."
        self.tab.parse_lines('''
Exposure category     Lung cancer  No lung cancer
-------------------------------------------------
Asbestos exposure               6              51
No asbestos exposure           52             941
'''.strip().splitlines())

        self.tab.do("tap /row_total dp 2")
        expected = '''
Exposure category     Lung cancer  No lung cancer
-------------------------------------------------
Asbestos exposure            0.11            0.89
No asbestos exposure         0.05            0.95
'''.strip()
        self.assertEqual(str(self.tab), expected)

        self.tab.do("tap *100 dp 0")
        expected = '''
Exposure category     Lung cancer  No lung cancer
-------------------------------------------------
Asbestos exposure              11              89
No asbestos exposure            5              95
'''.strip()
        self.assertEqual(str(self.tab), expected)

        self.tab.do("tap /total")
        expected = '''
Exposure category     Lung cancer  No lung cancer
-------------------------------------------------
Asbestos exposure           0.055           0.445
No asbestos exposure        0.025           0.475
'''.strip()
        self.assertEqual(str(self.tab), expected)

        self.tab.do("xp xp pop 0 tap divmod(x*1000, 37)")
        expected = '''
Asbestos exposure     1  18.000  12   1.000
No asbestos exposure  0  25.000  12  31.000
'''.strip()
        self.assertEqual(str(self.tab), expected)

    def test_mistakes(self):
        "Test capture of errors"
        sample = '''
a   1   2   3   4
b   5   6   7   8
c   9  10  11  12
d  13  14  15  16
'''.strip()
        self.tab.parse_lines(sample.splitlines())
        self.tab.do("tap")
        self.assertEqual(str(self.tab), sample)
        self.tab.do("arr")
        self.assertEqual(str(self.tab), sample)
        self.tab.do("filter")
        self.assertEqual(str(self.tab), sample)

        self.tab.do("arr ~(2..3)")
        self.assertEqual(str(self.tab), '?! syntax (2..3)\n' + sample)

        self.tab.do("tap x==4)")
        self.assertEqual(str(self.tab), '?! tokens x==4)\n' + sample)

        self.tab.do("tap x!4")
        self.assertEqual(str(self.tab), '?! syntax x!4\n' + sample)

        self.tab.do("tap x*undefined")  # undefined names are treated as strings
        self.assertEqual(str(self.tab), sample)

    def test_with_non_numbers(self):
        "Make sure subs work ok"
        data_with_header = '''
Name    Temp   Press     Vol
A     0.9757  0.8464  0.7741
B     0.0761  0.5375  0.7719
C     0.9557  0.3545  0.6033
D     0.7476  0.9234  0.8035
'''.strip()

        multiplied = '''
Name    Temp   Press     Vol   Press*Vol
A     0.9757  0.8464  0.7741  0.65519824
B     0.0761  0.5375  0.7719  0.41489625
C     0.9557  0.3545  0.6033  0.21386985
D     0.7476  0.9234  0.8035  0.74195190
'''.strip()
        z_err = '''
Name    Temp   Press     Vol       Vol/(1-2)
A     0.9757  0.8464  0.7741               -
B     0.0761  0.5375  0.7719          0.7719
C     0.9557  0.3545  0.6033         0.30165
D     0.7476  0.9234  0.8035  0.267833333333
'''.strip()

        self.tab.parse_lines(data_with_header.splitlines())
        self.assertEqual(str(self.tab), data_with_header)
        self.tab.do("arr abcd(c*d)")
        self.assertEqual(str(self.tab), multiplied)
        self.tab.do("arr abcd(d/(row_number-2))")
        self.assertEqual(str(self.tab), z_err)

    def test_with_string_manipulation(self):
        "Can we truncate things or join them?"
        input_list = '''
-rw-r--r--  1  toby  staff  961B  12 Mar 17:07  test_tab_command_line.py
-rw-r--r--  1  toby  staff  3.0K  14 May 17:35  test_tab_filter.py
-rw-r--r--  1  toby  staff  3.2K  12 Mar 17:07  test_tab_grouping.py
-rw-r--r--  1  toby  staff  811B  14 May 16:18  test_tab_help.py
-rw-r--r--  1  toby  staff  2.7K  23 Mar 11:27  test_tab_levels.py
-rw-r--r--  1  toby  staff  4.9K  12 Mar 17:07  test_tab_makers.py
-rw-r--r--  1  toby  staff  6.4K  12 Mar 17:07  test_tab_parsing.py
'''.strip()
        self.tab.parse_lines(input_list.splitlines())
        self.assertEqual(str(self.tab), input_list)

        self.tab.do("arr c(g[:4]) uniq")
        self.assertEqual(str(self.tab), "toby  test")
        print(self.tab)
