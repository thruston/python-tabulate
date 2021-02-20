import unittest
import doctest
import tabulate

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(tabulate))
    return tests

class TestTable(unittest.TestCase):

    def setUp(self):
        self.tab = tabulate.Table()

    def test_ab_ovo_creation(self):
        self.assertFalse(self.tab.data)
        self.assertTrue(self.tab.cols == 0)

    def test_append_lines(self):
        self.tab.append("First Second Third".split())
        self.tab.append("12 34 56".split())
        self.tab.append("78 90 120".split())

        self.assertTrue(self.tab.data)
        self.assertTrue(len(self.tab.data) == 3)
        self.assertTrue(self.tab.cols == 3)

    def test_tabulate(self):
        self.tab.append("First Second Third".split())
        self.tab.append("12 34 56".split())
        self.tab.append("78 90 120".split())
        self.assertEqual("\n" + str(self.tab),
'''
First  Second  Third
   12      34     56
   78      90    120''')

        self.tab.do("add")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
First  Second  Third
   12      34     56
   78      90    120
--------------------
   90     124    176
''')
        self.tab.do("xp add")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
First    12   78   90
Second   34   90  124
Third    56  120  176
---------------------
Total   102  288  390
''')
        self.tab.do("add mean")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
First    12   78   90
Second   34   90  124
Third    56  120  176
---------------------
Total   102  288  390
---------------------
Mean     51  144  195
''')

    def test_parselines(self):
        self.assertEqual(self.tab.indent, 0)
        self.tab.parse_lines('''
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
    2020-05-19  09:20:40  28.3  28.6  22.5  22.3  24.1  23.7  19.7  23.0  1428  50.5'''.splitlines())
        self.assertEqual(self.tab.cols, 12)
        self.assertEqual(len(self.tab.data), 17)
        self.assertEqual(self.tab.indent, 4)

    def test_arrange(self):
        self.tab.parse_lines('''
    2020-05-19  09:18:00  30.3  30.2  30.1  28.9  29.8  29.6  29.9  30.2   135   4.5
    2020-05-19  09:18:10  29.2  29.1  29.4  30.5  30.2  30.3  30.0  29.5   132   4.5
    2020-05-19  09:18:20  29.2  28.8  28.6  29.2  29.2  29.3  29.1  28.8   136   4.7
    2020-05-19  09:18:30  31.2  31.6  31.2  29.6  29.2  29.1  29.2  29.3   155   5.0
    2020-05-19  09:18:40  33.1  32.9  31.9  31.1  29.3  29.5  28.6  27.8   208   6.3
    2020-05-19  09:20:30  28.3  28.2  29.1  25.3  22.9  24.4  24.3  18.1  1375  48.6
    2020-05-19  09:20:40  28.3  28.6  22.5  22.3  24.1  23.7  19.7  23.0  1428  50.5'''.splitlines())

        self.tab.do("arr a:z")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.3  30.2  30.1  28.9  29.8  29.6  29.9  30.2   135   4.5
    2020-05-19  09:18:10  29.2  29.1  29.4  30.5  30.2  30.3  30.0  29.5   132   4.5
    2020-05-19  09:18:20  29.2  28.8  28.6  29.2  29.2  29.3  29.1  28.8   136   4.7
    2020-05-19  09:18:30  31.2  31.6  31.2  29.6  29.2  29.1  29.2  29.3   155   5.0
    2020-05-19  09:18:40  33.1  32.9  31.9  31.1  29.3  29.5  28.6  27.8   208   6.3
    2020-05-19  09:20:30  28.3  28.2  29.1  25.3  22.9  24.4  24.3  18.1  1375  48.6
    2020-05-19  09:20:40  28.3  28.6  22.5  22.3  24.1  23.7  19.7  23.0  1428  50.5
''')
        self.tab.do("arr xyz")
        self.assertEqual(str(self.tab) + "\n",
'''
    30.2   135   4.5
    29.5   132   4.5
    28.8   136   4.7
    29.3   155   5.0
    27.8   208   6.3
    18.1  1375  48.6
    23.0  1428  50.5
''')
        self.tab.do("arr ~(sqrt(b))") # sqrt should work with int
        self.assertEqual(str(self.tab) + "\n",
'''
    30.2   135   4.5  11.6189500386
    29.5   132   4.5  11.4891252931
    28.8   136   4.7  11.6619037897
    29.3   155   5.0  12.4498995980
    27.8   208   6.3  14.4222051019
    18.1  1375  48.6  37.0809924355
    23.0  1428  50.5  37.7888872554
''')

    def test_arrange_B(self):
        self.tab.parse_lines('''
    2020-05-19  09:18:00  30.3  30.2  30.1  28.9  29.8  29.6  29.9  30.2   135   4.5
    2020-05-19  09:18:10  29.2  29.1  29.4  30.5  30.2  30.3  30.0  29.5   132   4.5
    2020-05-19  09:18:20  29.2  28.8  28.6  29.2  29.2  29.3  29.1  28.8   136   4.7
    2020-05-19  09:18:30  31.2  31.6  31.2  29.6  29.2  29.1  29.2  29.3   155   5.0
    2020-05-19  09:18:40  33.1  32.9  31.9  31.1  29.3  29.5  28.6  27.8   208   6.3
    2020-05-19  09:20:30  28.3  28.2  29.1  25.3  22.9  24.4  24.3  18.1  1375  48.6
    2020-05-19  09:20:40  28.3  28.6  22.5  22.3  24.1  23.7  19.7  23.0  1428  50.5'''.splitlines())

        self.tab.do("arr -cd")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.1  28.9  29.8  29.6  29.9  30.2   135   4.5
    2020-05-19  09:18:10  29.4  30.5  30.2  30.3  30.0  29.5   132   4.5
    2020-05-19  09:18:20  28.6  29.2  29.2  29.3  29.1  28.8   136   4.7
    2020-05-19  09:18:30  31.2  29.6  29.2  29.1  29.2  29.3   155   5.0
    2020-05-19  09:18:40  31.9  31.1  29.3  29.5  28.6  27.8   208   6.3
    2020-05-19  09:20:30  29.1  25.3  22.9  24.4  24.3  18.1  1375  48.6
    2020-05-19  09:20:40  22.5  22.3  24.1  23.7  19.7  23.0  1428  50.5
''')
        self.tab.do("arr abcz")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.1   4.5
    2020-05-19  09:18:10  29.4   4.5
    2020-05-19  09:18:20  28.6   4.7
    2020-05-19  09:18:30  31.2   5.0
    2020-05-19  09:18:40  31.9   6.3
    2020-05-19  09:20:30  29.1  48.6
    2020-05-19  09:20:40  22.5  50.5
''')

    def test_arrange_C(self):
        self.tab.parse_lines('''
    2020-05-19  09:18:00  30.3  30.2  30.1  28.9  29.8  29.6  29.9  30.2   135   4.5
    2020-05-19  09:18:10  29.2  29.1  29.4  30.5  30.2  30.3  30.0  29.5   132   4.5
    2020-05-19  09:18:20  29.2  28.8  28.6  29.2  29.2  29.3  29.1  28.8   136   4.7
    2020-05-19  09:18:30  31.2  31.6  31.2  29.6  29.2  29.1  29.2  29.3   155   5.0
    2020-05-19  09:18:40  33.1  32.9  31.9  31.1  29.3  29.5  28.6  27.8   208   6.3
    2020-05-19  09:20:30  28.3  28.2  29.1  25.3  22.9  24.4  24.3  18.1  1375  48.6
    2020-05-19  09:20:40  28.3  28.6  22.5  22.3  24.1  23.7  19.7  23.0  1428  50.5'''.splitlines())

        self.tab.do("arr abced")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.3  30.1  30.2
    2020-05-19  09:18:10  29.2  29.4  29.1
    2020-05-19  09:18:20  29.2  28.6  28.8
    2020-05-19  09:18:30  31.2  31.2  31.6
    2020-05-19  09:18:40  33.1  31.9  32.9
    2020-05-19  09:20:30  28.3  29.1  28.2
    2020-05-19  09:20:40  28.3  22.5  28.6
''')

        self.tab.do("arr abcdeE")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.3  30.1  30.2   30.2
    2020-05-19  09:18:10  29.2  29.4  29.1   59.3
    2020-05-19  09:18:20  29.2  28.6  28.8   88.1
    2020-05-19  09:18:30  31.2  31.2  31.6  119.7
    2020-05-19  09:18:40  33.1  31.9  32.9  152.6
    2020-05-19  09:20:30  28.3  29.1  28.2  180.8
    2020-05-19  09:20:40  28.3  22.5  28.6  209.4
''')

        self.tab.do("arr -z arr ~(y/z)")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.3  30.1  30.2  0.996688741722
    2020-05-19  09:18:10  29.2  29.4  29.1   1.01030927835
    2020-05-19  09:18:20  29.2  28.6  28.8  0.993055555556
    2020-05-19  09:18:30  31.2  31.2  31.6  0.987341772152
    2020-05-19  09:18:40  33.1  31.9  32.9  0.969604863222
    2020-05-19  09:20:30  28.3  29.1  28.2   1.03191489362
    2020-05-19  09:20:40  28.3  22.5  28.6  0.786713286713
''')
        self.tab.do("arr -z arr ~(sqrt(c)")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.3  30.1  30.2  5.50454357781
    2020-05-19  09:18:10  29.2  29.4  29.1  5.40370243444
    2020-05-19  09:18:20  29.2  28.6  28.8  5.40370243444
    2020-05-19  09:18:30  31.2  31.2  31.6  5.58569601751
    2020-05-19  09:18:40  33.1  31.9  32.9  5.75325994546
    2020-05-19  09:20:30  28.3  29.1  28.2  5.31977443131
    2020-05-19  09:20:40  28.3  22.5  28.6  5.31977443131
''')
        self.tab.do("arr -z arr ~(sqrt(c) dp 001144")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.3  30.1  30.2000  5.5045
    2020-05-19  09:18:10  29.2  29.4  29.1000  5.4037
    2020-05-19  09:18:20  29.2  28.6  28.8000  5.4037
    2020-05-19  09:18:30  31.2  31.2  31.6000  5.5857
    2020-05-19  09:18:40  33.1  31.9  32.9000  5.7533
    2020-05-19  09:20:30  28.3  29.1  28.2000  5.3198
    2020-05-19  09:20:40  28.3  22.5  28.6000  5.3198
''')
        self.tab.do("arr abccde roll d arr abc{c-d}ef")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.3   2.0  30.1  30.2000
    2020-05-19  09:18:10  29.2  -1.1  29.4  29.1000
    2020-05-19  09:18:20  29.2   0.0  28.6  28.8000
    2020-05-19  09:18:30  31.2   2.0  31.2  31.6000
    2020-05-19  09:18:40  33.1   1.9  31.9  32.9000
    2020-05-19  09:20:30  28.3  -4.8  29.1  28.2000
    2020-05-19  09:20:40  28.3   0.0  22.5  28.6000
''')
        self.tab.do("arr abc('Aok  {:.2f}'.format(f)")
        self.assertEqual(str(self.tab) + "\n",
'''
    2020-05-19  09:18:00  30.3  Aok 30.20
    2020-05-19  09:18:10  29.2  Aok 29.10
    2020-05-19  09:18:20  29.2  Aok 28.80
    2020-05-19  09:18:30  31.2  Aok 31.60
    2020-05-19  09:18:40  33.1  Aok 32.90
    2020-05-19  09:20:30  28.3  Aok 28.20
    2020-05-19  09:20:40  28.3  Aok 28.60
''')

    def test_gen_and_wrap_and_zip(self):
        self.tab.do("gen 16 wrap 4")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
1  5   9  13
2  6  10  14
3  7  11  15
4  8  12  16
''')
        self.tab.do("zip")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
1  5   9  13  2  6  10  14
3  7  11  15  4  8  12  16
''')
        self.tab.do("unwrap")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
1  5   9  13
3  7  11  15
2  6  10  14
4  8  12  16
''')
        self.tab.do("unzip")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
 1   5
 9  13
 3   7
11  15
 2   6
10  14
 4   8
12  16
''')
        self.tab.do("xp unzip arr acbd label")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
a  b   c   d
1  3   9  11
2  4  10  12
5  7  13  15
6  8  14  16
''')
        self.tab.do("shuffle sort B")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
a  b   c   d
6  8  14  16
5  7  13  15
2  4  10  12
1  3   9  11
''')
        self.tab.add_rule(-1)
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
a  b   c   d
6  8  14  16
5  7  13  15
2  4  10  12
------------
1  3   9  11
''')


    def test_ditto(self):
        self.tab.parse_lines('''
-  Act 3  -  -  Enzo Florimo, Hakan Hagegard, Arleen Auger, Barbara Bonney, The Drottningholm Court Theatre Orchestra, Arnold Oestman
1.  "  "Io vi dico, signor"  [1:10]  "
2.  "  Sull'aria...Cosa mi narri!...Che soave zefiretto...  [2:42]  "
3.  "  "Ricevete, o padroncina" - "Queste sono, Madama"  [3:58]   "
4.  "  Ecco la marcia...Eh, gia, solita usanza  [5:58]   "'''.splitlines())
        self.tab.do("ditto pop 0")
        self.assertEqual(str(self.tab) + "\n",
'''
1.  Act 3  "Io vi dico, signor"                                 [1:10]  Enzo Florimo, Hakan Hagegard, Arleen Auger, Barbara Bonney, The Drottningholm Court Theatre Orchestra, Arnold Oestman
2.  Act 3  Sull'aria...Cosa mi narri!...Che soave zefiretto...  [2:42]  Enzo Florimo, Hakan Hagegard, Arleen Auger, Barbara Bonney, The Drottningholm Court Theatre Orchestra, Arnold Oestman
3.  Act 3  "Ricevete, o padroncina" - "Queste sono, Madama"     [3:58]  Enzo Florimo, Hakan Hagegard, Arleen Auger, Barbara Bonney, The Drottningholm Court Theatre Orchestra, Arnold Oestman
4.  Act 3  Ecco la marcia...Eh, gia, solita usanza              [5:58]  Enzo Florimo, Hakan Hagegard, Arleen Auger, Barbara Bonney, The Drottningholm Court Theatre Orchestra, Arnold Oestman
''')


    def test_dates(self):
        self.tab.append(['Date'])
        self.tab.append(['2011-01-17'])
        self.tab.append(['2011-02-23'])
        self.tab.append(['2011-03-19'])
        self.tab.append(['2011-07-05'])

        self.tab.do("arr a{dow(a)}")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
Date        dow
2011-01-17  Mon
2011-02-23  Wed
2011-03-19  Sat
2011-07-05  Tue
''')

        self.tab.do("pop 0 arr a{base('2020-05-22')-base(a)}")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
2011-01-17  3413
2011-02-23  3376
2011-03-19  3352
2011-07-05  3244
''')

        self.tab.do("arr a{date(base(a)+140)}")
        self.assertEqual("\n" + str(self.tab) + "\n",
'''
2011-01-17  2011-06-06
2011-02-23  2011-07-13
2011-03-19  2011-08-06
2011-07-05  2011-11-22
''')

    def test_pivot(self):
        self.tab.parse_lines('''
    Exposure category     Lung cancer  No lung cancer
    -------------------------------------------------
    Asbestos exposure               6              51
    No asbestos exposure           52             941'''.splitlines())

        self.tab.do("pivot long")
        self.assertEqual(str(self.tab), '''
    Exposure category     Name            Value
    -------------------------------------------
    Asbestos exposure     Lung cancer         6
    Asbestos exposure     No lung cancer     51
    No asbestos exposure  Lung cancer        52
    No asbestos exposure  No lung cancer    941''')


    def test_pivot_wide(self):
        self.tab.parse_lines('''
    Region  Quarter  Sales
    ----------------------
    East    Q1        1200
    East    Q2        1100
    East    Q3        1500
    East    Q4        2200
    West    Q1        2200
    West    Q2        2500
    West    Q3        1990
    West    Q4        2600'''.splitlines())

        self.tab.do("pivot wide")
        self.assertEqual(str(self.tab), '''
    Region    Q1    Q2    Q3    Q4
    ------------------------------
    East    1200  1100  1500  2200
    West    2200  2500  1990  2600''')


    def test_sigs(self):
        self.tab.parse_lines('''
542.749399417  -15.5717609184  627.192940841   631.280992769
-97.3064669801   661.178535659  2.92479400244  -196.030889264
2.79458901524   2.25469838398  1.35272022538  -167.473042336
3.61204687909   3.01674488783  8.67507861887   2.11712190196'''.splitlines())

        self.tab.do("sf 4")
        self.assertEqual(str(self.tab), '''
 542.7  -15.57  627.2   631.3
-97.31   661.2  2.925  -196.0
 2.795   2.255  1.353  -167.5
 3.612   3.017  8.675   2.117''')

    def test_complex_gen(self):
        '''Test out gen with ABCn argument and some of the 
        smarter bits of pivot'''
        self.tab.do("gen PQ4")
        expected = '''
P  P  P  P
P  P  P  Q
P  P  Q  P
P  P  Q  Q
P  Q  P  P
P  Q  P  Q
P  Q  Q  P
P  Q  Q  Q
Q  P  P  P
Q  P  P  Q
Q  P  Q  P
Q  P  Q  Q
Q  Q  P  P
Q  Q  P  Q
Q  Q  Q  P
Q  Q  Q  Q
'''.strip()
        self.assertEqual(str(self.tab), expected)

        self.tab.do("label pivot count add")
        expected = '''
a      b      P  Q
P      P      2  2
P      Q      2  2
Q      P      2  2
Q      Q      2  2
------------------
Total  Total  8  8
'''.strip()
        self.assertEqual(str(self.tab), expected)

        self.tab.do("pop add mean")
        expected = '''
a     b     P  Q
P     P     2  2
P     Q     2  2
Q     P     2  2
Q     Q     2  2
----------------
Mean  Mean  2  2
'''.strip()
        self.assertEqual(str(self.tab), expected)

        self.tab.do("rule 1")
        expected = '''
a     b     P  Q
----------------
P     P     2  2
P     Q     2  2
Q     P     2  2
Q     Q     2  2
----------------
Mean  Mean  2  2
'''.strip()
        self.assertEqual(str(self.tab), expected)

    def test_normalize_and_tap(self):
        "Test table wide processing..."
        self.tab.parse_lines('''
Exposure category     Lung cancer  No lung cancer
-------------------------------------------------
Asbestos exposure               6              51
No asbestos exposure           52             941
'''.strip().splitlines())

        self.tab.do("normalize dp 2")
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

    def test_filter(self):
        "Select matching rows"
        self.tab.parse_lines('''
Monday      Week  Mon  Tue   Wed  Thu  Fri   Sat   Sun  Total
2019-12-30     1  0.0  0.2   0.0  0.0  1.2   0.0   0.0    1.4
2020-01-06     2  0.5  0.0   0.0  6.4  0.0   0.1   1.7    8.7
2020-01-13     3  5.3  1.7   9.1  3.0  1.7   0.0   0.0   20.8
2020-01-20     4  0.0  0.0   0.0  0.0  0.0   0.1   2.3    2.4
2020-01-27     5  8.4  2.1   0.0  0.5  1.0   0.0   7.1   19.1
2020-02-03     6  0.1  0.0   0.0  0.0  0.0   1.5  10.6   12.2
2020-02-10     7  5.5  0.0   0.5  6.6  0.0   4.9  15.6   33.1
2020-02-17     8  0.2  3.3   1.0  3.8  0.0   0.5   1.0    9.8
2020-02-24     9  6.1  0.5   0.1  8.6  5.9   7.1   0.2   28.5
2020-03-02    10  0.0  0.0   4.3  0.0  3.0  12.4   0.0   19.7
2020-03-09    11  0.0  4.3   6.3  1.3  1.0   1.0   0.0   13.9
2020-03-16    12  3.6  1.3   0.0  0.0  0.0   0.5   0.0    5.4
2020-03-23    13  0.0  0.0   0.0  0.0  0.0   0.0   0.0    0.0
2020-03-30    14  0.1  0.1  10.9  0.0  0.0   0.0   0.0   11.1
'''.strip().splitlines())
        self.tab.do('filter j>10')
        expected = '''
Monday      Week  Mon  Tue   Wed  Thu  Fri   Sat   Sun  Total
2020-01-13     3  5.3  1.7   9.1  3.0  1.7   0.0   0.0   20.8
2020-01-27     5  8.4  2.1   0.0  0.5  1.0   0.0   7.1   19.1
2020-02-03     6  0.1  0.0   0.0  0.0  0.0   1.5  10.6   12.2
2020-02-10     7  5.5  0.0   0.5  6.6  0.0   4.9  15.6   33.1
2020-02-24     9  6.1  0.5   0.1  8.6  5.9   7.1   0.2   28.5
2020-03-02    10  0.0  0.0   4.3  0.0  3.0  12.4   0.0   19.7
2020-03-09    11  0.0  4.3   6.3  1.3  1.0   1.0   0.0   13.9
2020-03-30    14  0.1  0.1  10.9  0.0  0.0   0.0   0.0   11.1
'''.strip()
        self.maxDiff = None
        self.assertEqual(str(self.tab), expected)


    def test_nothing(self):
        some_lines = '''
Monday      Week  Mon  Tue  Wed  Thu  Fri  Sat  Sun  Total
2020-01-13     3  5.3  1.7  9.1  3.0  1.7  0.0  0.0   20.8
2020-01-27     5  8.4  2.1  0.0  0.5  1.0  0.0  7.1   19.1
'''.strip()
        self.tab.parse_lines(some_lines.splitlines())
        self.assertEqual(str(self.tab), some_lines)
        self.tab.do()
        self.assertEqual(str(self.tab), some_lines)


if __name__ == "__main__":
    unittest.main()
