#! /usr/bin/env python3

import unittest

import tabulate


class TestTableHelp(unittest.TestCase):

    def setUp(self):
        self.tab = tabulate.Table()
        self.help = '''
Try one of these: add arr ditto dp dup filter gen group help label
levels make noblanks nospace pivot pop push roll rule sf shuffle sort
tap uniq unwrap unzip wrap xp zip
        '''.strip()

        self.verbs = '''
Functions for arr: abs all angle any base bool caps chr cos cosd date
dir divmod dow epoch exp factors floor format hex hms hr hypot int len
log log10 lower max mexp min minp mins mlog oct ord pi pow randomd
reversed round secs sin sind sorted sqrt str sum tan tand tau time
upper
        '''.strip()

    def test_help(self):
        self.tab.do("help")
        self.assertEqual(str(self.tab), self.help)

        self.tab.do("help Arr")
        self.assertEqual(str(self.tab), self.verbs)
