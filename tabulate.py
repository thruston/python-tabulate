#! /usr/bin/env python3
'''
Tabulate

A module to line up text tables.
Toby Thurston -- Aug 2020

TODO:
    - Better support for TeX
    - Support units? MiB KiB etc like sort -h
    - Money cols (maybe)
    - Generic col type... 0 string 1 decimal 2 money 3 units ??

'''

# pylint: disable=C0103, C0301

import argparse
import collections
import csv
import datetime
import decimal
import itertools
import math
import os
import random
import re
import statistics
import string
import sys

decimal.getcontext().prec = 12

# Functions for column maths, using the Decimal versions, and
# also supporting ints...
def exp(d):
    '''exp for Decimals
    >>> exp(decimal.Decimal('0'))
    Decimal('1')
    >>> exp(decimal.Decimal('1'))
    Decimal('2.71828182846')
    >>> exp(2)
    Decimal('7.38905609893')
    '''
    return decimal.Decimal(d).exp()

def sqrt(d):
    '''sqrt for decimals
    >>> sqrt(decimal.Decimal('0'))
    Decimal('0')
    >>> sqrt(decimal.Decimal('1'))
    Decimal('1')
    >>> sqrt(decimal.Decimal('2'))
    Decimal('1.41421356237')
    >>> sqrt(121)
    Decimal('11')
    '''
    return decimal.Decimal(d).sqrt()

def log10(d):
    '''log base 10 for decimals
    >>> log10(decimal.Decimal('10'))
    Decimal('1')
    >>> log10(decimal.Decimal('100'))
    Decimal('2')
    >>> log10(1000)
    Decimal('3')
    '''
    return decimal.Decimal(d).log10()

def log(d):
    '''natural log for decimals (following math.log name...)
    >>> log(exp(decimal.Decimal('1')))
    Decimal('1.00000000000')
    >>> log(42)
    Decimal('3.73766961828')
    '''
    return decimal.Decimal(d).ln()

# Calendar functions for column arrangements
def parse_date(sss):
    '''Try to parse a date
    >>> parse_date("1 January 2001").isoformat()
    '2001-01-01'
    '''
    for fmt in ('%Y-%m-%d', '%Y%m%d', '%c', '%x', '%d %B %Y', '%d %b %Y',
                '%d %b %y', '%d %B %y', '%d/%m/%Y', '%d/%m/%y', '%a', '%A'):
        try:
            return datetime.datetime.strptime(sss, fmt).date()
        except ValueError:
            pass

    raise ValueError

def dow(sss, date_format="%a"):
    '''Is it Friday yet?
    >>> dow("1 January 2001")
    'Mon'
    >>> dow("1 January 2001", "%A")
    'Monday'
    '''
    try:
        return parse_date(sss).strftime(date_format)
    except (TypeError, ValueError):
        return "dow"

def base(sss=None):
    '''Get today's date as "base" number, or whatever date you give
    >>> base("1 January 2001")
    730486
    >>> base("1 January 1901")
    693961
    >>> base("01/01/01")
    730486
    >>> base("31 Dec 2000")-base("1 Jan 1901")
    36524
    '''
    try:
        return parse_date(sss).toordinal()
    except ValueError:
        return datetime.date.today().toordinal()

def date(ordinal=0):
    '''Turn a base number (or an epoch time or a millisecond epoch time) into a date
    >>> date(716257)
    '1962-01-17'
    >>> date(3652059)
    '9999-12-31'
    >>> date(3652060)
    '1970-02-12T06:27:40'
    >>> date(100000000000)
    '5138-11-16T09:46:40'
    >>> date(100000000001)
    '1973-03-03T09:46:40.001000'
    '''
    try:
        ordinal = int(ordinal)
    except (TypeError, ValueError):
        ordinal = 0

    if abs(ordinal) < 1000:
        dt = datetime.date.today() + datetime.timedelta(days=ordinal)
    elif ordinal > 100000000000: # about 5000 AD as an epoch
        dt = datetime.datetime.utcfromtimestamp(ordinal / 1000)
    elif ordinal > 3652059:  # max date
        dt = datetime.datetime.utcfromtimestamp(ordinal)
    else:
        try:
            dt = datetime.date.fromordinal(ordinal)
        except (TypeError, ValueError):
            dt = datetime.date.today()

    return dt.isoformat()

def hms(fractional_things):
    '''Turn decimal hours/degrees into h/d:mm:ss.fff

    >>> hms(57.2957795)
    '57:17:44.806'

    >>> hms(10801/3600)
    '3:00:01.000'
    '''
    hh, r = divmod(fractional_things, 1)
    mm, r = divmod(r * 60, 1)
    return "{}:{:02d}:{:06.3f}".format(int(hh), int(mm), r*60)

def hr(hms_word, s=0):
    '''Turn hh:mm:ss.sss into fractional hours

    >>> hr("12:34:56")
    12.582222222222223
    '''
    hours = 0
    for i, p in enumerate(hms_word.split(':')):
        hours += float(p) * 60 ** (s-i)
    return hours

def mins(hms_word):
    '''Turn hh:mm:ss.sss into fractional minutes
    >>> mins('1:23:45')
    83.75
    '''
    return hr(hms_word, 1)

def secs(hms_word):
    '''Turn hh:mm:ss.sss into fractional seconds
    >>> secs('1:23:45.67')
    5025.67
    '''
    return hr(hms_word, 2)

def si(amount):
    """If amount is a number, add largest possible SI suffix, 
    otherwise try to remove the suffix and return a value
    >>> si('10M')
    Decimal('10000000')
    >>> si(12315350)
    '12.31535 M'
    >>> si(10)
    '10'
    >>> si('.2 k')
    Decimal('200.0')

    """
    sips = ' kMGTPE'
    m = re.match(rf'([-+]?(?:\d+\.\d*|\.\d+|0|[1-9]\d*))\s*([{sips}])\Z', str(amount))
    if m is not None:
        return decimal.Decimal(m.group(1)) * 10 ** (3 * sips.index(m.group(2)))
    try:
        n = decimal.Decimal(amount)
    except decimal.InvalidOperation:
        return amount
    else:
        e = min(int(n.log10()/3), len(sips)-1)
        return '{:7.3f} {}'.format(n / (10 ** (3*e)), sips[e]).strip()


def is_as_decimal(sss):
    '''Is this a decimal, and if so what is the value?

    >>> is_as_decimal('')
    (False, '')
    >>> is_as_decimal("Label")
    (False, 'Label')
    >>> is_as_decimal("3.14")
    (True, Decimal('3.14'))
    >>> is_as_decimal('0')
    (True, Decimal('0'))
    '''
    try:
        return (True, decimal.Decimal(sss))
    except decimal.InvalidOperation:
        return (False, sss)

def as_decimal(n, na_value=decimal.Decimal('0')):
    "Make this a decimal"
    try:
        return decimal.Decimal(n)
    except decimal.InvalidOperation:
        return na_value


class Table:
    '''A class to hold a table -- and some functions thereon'''

    def __init__(self):
        " empty data and no rows or cols "
        self.data = []
        self.cols = 0
        self.indent = 0
        self.extras = collections.defaultdict(list)
        self.form = 'plain'
        self.operations = {
            'add': self._append_reduction,
            'arr': self._arrange_columns,
            'ditto': self._copy_down,
            'dp': self._fix_decimal_places,
            'gen': self._generate_new_rows,
            'group': self._add_grouping_blanks,
            'help': self._describe_operations,
            'make': self._set_output_form,
            'label': self._label_columns,
            'nospace': self._remove_spaces_from_values,
            'noblanks': self._remove_blank_extras,
            'pivot': self._wrangle,
            'pop': self.pop,
            'roll': self._roll_by_col,
            'sf': self._fix_sigfigs,
            'shuffle': self._shuffle_rows,
            'sort': self._sort_rows_by_col,
            'uniq': self._remove_duplicates_by_col,
            'unwrap': self._unrapper,
            'unzip': self._unzipper,
            'wrap': self._rapper,
            'xp': self._transpose,
            'zip': self._zipper,
        }

    def __str__(self):
        "Print neatly"
        return "\n".join(self.tabulate())

    def _describe_operations(self, _):
        '''What commands are defined?'''
        print('Try one of these: ' + ' '.join(sorted(self.operations)))

    def clear(self):
        "Clear data etc"
        self.data.clear()
        self.extras.clear()
        self.cols = 0
        self.indent = 0

    def parse_lines(self, lines_thing, splitter=re.compile(r'\s\s+'), splits=0, append=False):
        "Read lines from an iterable thing, and append to self"

        if not append:
            self.clear()
            self.indent = 99
        for raw_line in lines_thing:
            raw_line = raw_line.replace("\t", "    ")
            stripped_line = raw_line.strip()
            if not stripped_line:
                self.add_blank()
            elif set(stripped_line) == {'-'}:
                self.add_rule()
            elif stripped_line.startswith('#'):
                self.add_comment(stripped_line)
            else:
                self.append(splitter.split(stripped_line, maxsplit=splits))
                self.indent = min(self.indent, len(raw_line) - len(raw_line.lstrip()))
        # catch empty tables
        if not self.data:
            self.indent = 0

    def parse_lol(self, list_of_iterables, append=False):
        "pass lol into self.data"
        if not append:
            self.clear()
        for r in list_of_iterables:
            if not r:
                self.add_blank()
            elif set(''.join(str(x) for x in r)) == {'-'}:
                self.add_rule()
            else:
                self.append(r)

    def pop(self, n=None):
        "remove a row"

        if n is None:
            self.data.pop()
            return

        try:
            self.data.pop(int(n))
        except (IndexError, ValueError):
            return

    def append(self, row, filler=''):
        "add a row, maintaining cols"
        n = len(row)
        if n < self.cols:
            row.extend([filler] * (self.cols - n))
        elif self.cols < n:
            for r in self.data:
                r.extend([filler] * (n - self.cols))
            self.cols = n

        # they should all be strings, and normalize space in last column...
        self.data.append([str(x) for x in row[:-1]] + [' '.join(str(row[-1]).split())])

    def do(self, agenda):
        "Do what we've been asked..."
        if agenda and isinstance(agenda, str):
            agenda = agenda.split()
        while agenda:
            op = agenda.pop(0)
            if op not in self.operations:
                print(op, '??')
                continue

            # get any arguments
            argument = []
            while True:
                this = agenda.pop(0) if agenda else None
                # put it back if it is really the next op
                if this in self.operations:
                    agenda.insert(0, this)
                    this = None

                if this is None:
                    break

                argument.append(this)

            self.operations[op](' '.join(argument))

    def _label_columns(self, _):
        "add some labels in alphabetical order"
        self.data.insert(0, string.ascii_lowercase[:self.cols])

    def column(self, i):
        "get a column from the table - zero indexed"
        try:
            return [is_as_decimal(r[i]) for r in self.data]
        except IndexError:
            return []

    def add_blank(self, n=None):
        "flag a blank"
        if n is None:
            n = len(self.data)
        self.extras[n].append("blank")

    def add_rule(self, n=None):
        "mark a rule"
        if n is None:
            n = len(self.data)
        self.extras[n].append("rule")

    def add_comment(self, contents):
        "stash a comment line"
        self.extras[len(self.data)].append('#' + contents.lstrip('#'))

    def _set_output_form(self, form_name):
        "Set the form name, used in `tabulate`"
        self.form = form_name.lower()

    def _transpose(self, _):
        '''Swap rows and columns
        '''
        self.cols = len(self.data)
        self.data = list(list(r) for r in zip(*self.data))
        self.extras.clear()

    def _shuffle_rows(self, _):
        '''Re-arrange the data at random'''
        random.shuffle(self.data)
        self.extras.clear()

    def _remove_blank_extras(self, _):
        for i in range(len(self.data)):
            self.extras[i] = [x for x in self.extras[i] if x != "blank"]

    def _remove_spaces_from_values(self, joiner):
        '''Remove spaces from values -- this can make it easier to import into R'''
        if joiner is None:
            joiner = ''
        for i, row in enumerate(self.data):
            self.data[i] = [joiner.join(cell.split()) for cell in row]

    def _fix_decimal_places(self, dp_string):
        "Round all the numerical fields in each row"
        if dp_string is None:
            return

        if not dp_string.isdigit():
            return

        # extend as needed (you could use zip_longest, but this just as simple)
        dp_values = list(int(x) for x in dp_string) + [int(dp_string[-1])] * (self.cols - len(dp_string))

        def _round(s, n):
            try:
                return '{:.{n}f}'.format(decimal.Decimal(s), n=n)
            except decimal.InvalidOperation:
                return s

        self.data = list(list(_round(c, dp) for c, dp in zip(r, dp_values)) for r in self.data)

    def _fix_sigfigs(self, sf_string):
        "Round to n sig figs all the numeric fields in each row"
        if sf_string is None:
            return

        if not sf_string.isdigit():
            return

        # extend as needed (you could use zip_longest, but this just as simple)
        sf_values = list(int(x) for x in sf_string) + [int(sf_string[-1])] * (self.cols - len(sf_string))

        def _siggy(s, n):
            try:
                x = decimal.Decimal(s)
            except decimal.InvalidOperation:
                return s

            if x.is_zero():
                return 0

            return '{:f}'.format(round(x, n - int(math.floor(math.log10(abs(x)))) - 1))

        self.data = list(list(_siggy(c, sf) for c, sf in zip(r, sf_values)) for r in self.data)

    def _generate_new_rows(self, count_or_range):
        "Add some more data on the bottom"
        alpha = 1
        try:
            omega = int(count_or_range)
        except (TypeError, ValueError):
            m = re.match(r'(-?\d+)\D(-?\d+)$', count_or_range)
            if m is None:
                omega = 10
            else:
                alpha, omega = (int(x) for x in m.groups())
        if alpha > omega:
            (alpha, omega) = (omega, alpha)

        for i in range(alpha, omega+1):
            self.append([i])

    def _copy_down(self, _):
        '''Fix up ditto marks'''
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                if cell == '"' and i > 0:
                    self.data[i][j] = self.data[i-1][j]

    def _zipper(self, n):
        '''Put n rows side by side
        '''
        try:
            rows_to_zip = int(n)
        except (ValueError, TypeError):
            rows_to_zip = 2

        if rows_to_zip < 2:
            return

        old_data = self.data.copy()
        self.data.clear()
        self.cols = 0
        while old_data:
            new_row = []
            for _ in range(rows_to_zip):
                if old_data:
                    new_row.extend(old_data.pop(0))
            self.append(new_row)

        self.extras.clear()

    def _unzipper(self, n):
        '''The opposite of zip.  Split rows so that there are cols/n cols in each'''
        try:
            splits = int(n)
        except (ValueError, TypeError):
            splits = 2

        desired_cols = math.ceil(self.cols / splits)

        old_data = self.data.copy()
        self.data.clear()
        self.cols = 0
        for r in old_data:
            for i in range(splits):
                start = i * desired_cols
                stop = start + desired_cols
                self.append(r[start:stop])

        self.extras.clear()

    def _rapper(self, n):
        '''It's a wrap.'''
        try:
            groups = int(n)
        except (ValueError, TypeError):
            groups = 2

        rows_per_group = math.ceil(len(self.data) / groups)

        old_data = self.data.copy()
        self.data.clear()

        for i in range(rows_per_group):
            new_row = []
            for j in range(groups):
                k = i + j * rows_per_group
                try:
                    new_row += old_data[k]
                except IndexError:
                    pass
            self.append(new_row)

        self.extras.clear()

    def _splitme(self, seq, parts):
        if parts > 0:
            size = math.ceil(len(seq) / parts)
            yield seq[:size]
            if parts > 1:
                yield from self._splitme(seq[size:], parts - 1)

    def _unrapper(self, n):
        '''It's not a wrap'''
        try:
            groups = int(n)
        except (ValueError, TypeError):
            groups = 2

        old_data = self.data.copy()
        old_cols = self.cols
        groups = min(groups, old_cols) # no blanks on the end thank you

        self.data.clear()
        self.cols = 0
        self.extras.clear()

        for col_list in self._splitme(range(old_cols), groups):
            for r in old_data:
                self.append([r[x] for x in col_list])


    def _append_reduction(self, fun):
        '''Reduce column and append result to foot of table
        fun is the name, func is the callable.
        first see if this is the name of something in stats
        or something else callable, if none of those then use "sum"
        '''
        if isinstance(fun, str) and hasattr(statistics, fun):
            func = getattr(statistics, fun)
        elif callable(fun):
            func = fun
        else:
            func = sum
            fun = "Total"

        footer = []
        for c in range(self.cols):
            booleans, decimals = zip(*self.column(c))
            if not any(booleans):
                footer.append(fun)
            else:
                footer.append(func(itertools.compress(decimals, booleans)))

        self.add_rule()
        self.append(footer)

    def _wrangle(self, shape):
        '''Reflow / pivot / reshape from wide to long or long to wide

        pivot wide assumes that col -1 has values and -2 has col head values
        and everything else are keys. Does nothing if there are less than 3 cols.

        pivot long assumes only key is col A but you can add a letter or number
        to show where the keys stop -- so if the first three are keys then use "longc"
        or "long3" -- numbering from a=1

        '''
        if shape is None:
            return

        if self.cols < 3:
            return

        if "wide".startswith(shape.lower()):
            self._wrangle_wide()
            return

        if "count".startswith(shape.lower()):
            self._wrangle_wide(len)
            return

        if "any".startswith(shape.lower()):
            self._wrangle_wide(any)
            return

        m = re.match(r'long([1-9a-o])?', shape)
        if m is None:
            return

        if m.group(1) is None:
            last_key_col = 1
        else:
            try:
                last_key_col = int(m.group(1))
            except ValueError:
                last_key_col = ord(m.group(1)) - ord('a') + 1

        if self.cols - last_key_col > 1:
            self._wrangle_long(last_key_col)

    def _wrangle_wide(self, fun=sum):
        '''Reflow wide'''
        bags = collections.defaultdict(list)
        names_seen = dict()
        keys_seen = dict()
        header = self.data[0][:-2]
        for r in self.data[1:]:
            *key, name, value = r
            key = tuple(key)
            names_seen[name] = True
            keys_seen[key] = True
            bags[(key, name)].append(as_decimal(value))

        self.data = []
        self.cols = 0
        names = list(names_seen)
        self.append(header + names)
        for k in keys_seen:
            self.append(list(k) + [fun(bags[(k, n)]) for n in names])

    def _wrangle_long(self, keystop):
        '''Reflow long'''
        header = self.data[0][:keystop] + ['Name', 'Value']
        names = self.data[0][keystop:]
        wide_data = self.data[1:]
        self.data = []
        self.cols = 0

        self.append(header)
        for r in wide_data:
            for n, v in zip(names, r[keystop:]):
                self.append(r[:keystop] + [n, v])

    def _get_expr_list(self, given):
        '''Turn the user's argument into a tuple of expression strings

        >>> t = Table()
        >>> a = (1, 2, 3, 4, 5, 6, 7, 8)
        >>> t.parse_lol((a, a))
        >>> t._get_expr_list("abc")
        ['a', 'b', 'c']
        >>> t._get_expr_list("abcA")
        ['a', 'b', 'c', 'A']
        >>> t._get_expr_list("abc()e")
        ['a', 'b', 'c', 'e']
        >>> t._get_expr_list("abc(2+2)e")
        ['a', 'b', 'c', '(2+2)', 'e']
        >>> t._get_expr_list("abc(2+2**(4+5))e")
        ['a', 'b', 'c', '(2+2**(4+5))', 'e']
        >>> # allow missing trailing parens
        >>> t._get_expr_list("abc(2+2")
        ['a', 'b', 'c', '(2+2)']
        >>> t._get_expr_list("a-e")
        ['a', 'b', 'c', 'd', 'e']
        >>> t._get_expr_list("a-E")
        ['a', 'E']
        >>> t._get_expr_list("a-Z")
        ['a', 'H']
        >>> t._get_expr_list("e-a")
        ['e', 'd', 'c', 'b', 'a']
        >>> t._get_expr_list("a-z")
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        >>> t._get_expr_list("~z")
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'h']
        >>> t._get_expr_list("xyz")
        ['f', 'g', 'h']
        >>> t._get_expr_list("z")
        ['h']
        >>> t._get_expr_list("~(d/e)")
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', '(d/e)']


        '''
        identity = string.ascii_lowercase[:self.cols]
        in_parens = 0
        out = []
        expr = []
        last = ''

        # Allow counting from the right (but only xxyz)
        if '(' not in given and self.cols < 22:
            for a, b in zip("zyxw", reversed(identity)):
                given = given.replace(a, b)
                given = given.replace(a.upper(), b.upper())

        for c in given:
            if in_parens == 0:
                if c.lower() in identity + '?;.':
                    if last == '-' and out[-1] in identity and c in identity:
                        a = ord(out[-1])
                        b = ord(c)
                        if a < b:
                            out.extend([chr(x) for x in range(a+1, b)])
                        elif a > b:
                            out.extend([chr(x) for x in range(a-1, b, -1)])
                    out.append(c)
                elif c in '({':
                    in_parens = 1
                    expr = ['(']
                elif c == '~':
                    out.extend(x for x in identity)
                else:
                    pass # ignore anything else outside parens
                last = c
            else:
                if c == '}' and in_parens == 1: # allow } as ) at top level
                    c = ')'
                expr.append(c)
                if c in '({':
                    in_parens += 1
                elif c in ')}':
                    in_parens -= 1
                if in_parens == 0:
                    if len(expr) > 2: # ignore ()
                        out.append(''.join(expr))
        if in_parens > 0:
            out.append(''.join(expr) + ')' * in_parens)

        return out

    def _arrange_columns(self, perm):
        '''Arrange the columns of the table
        '''
        if perm is None:
            return

        # deletions...
        if perm[0] == '-':
            if '(' not in perm:
                delenda = list(ord(x) - ord('a') for x in self._get_expr_list(perm[1:]))
                self.data = list(list(x for i, x in enumerate(r) if i not in delenda) for r in self.data)
                self.cols = len(self.data[0])
            return

        identity = string.ascii_lowercase[:self.cols]
        specials = '.?;'

        perm = self._get_expr_list(perm)

        if all(x in identity + specials for x in perm):
            self._simple_rearrangement(perm)
        else:
            self._general_recalculation(perm)

    def _simple_rearrangement(self, perm):
        '''Just rearrange the columns... '''
        def _get_value(c, line_number, row):
            '''Find a suitable value given the perm character and a row of data
            '''
            if c == '.':
                return str(line_number)
            if c == '?':
                return str(random.random())
            if c == ';':
                return str(len(self.data))
            return row[ord(c) - ord('a')]

        self.data = list(list(_get_value(x, i + 1, r) for x in perm) for i, r in enumerate(self.data))
        self.cols = len(perm) # perm can delete and/or add columns

    def _general_recalculation(self, desiderata):
        '''Do some (decimal) arithmetic on each row...
        '''
        def _decimalize(expr):
            '''borrowed from the example decistmt
            '''
            import tokenize
            import io

            out = []
            for tn, tv, _, _, _ in tokenize.generate_tokens(io.StringIO(expr).readline):
                if tn == tokenize.NUMBER and '.' in tv:
                    out.append((tokenize.NAME, 'Decimal'))
                    out.append((tokenize.OP, '('))
                    out.append((tokenize.STRING, repr(tv)))
                    out.append((tokenize.OP, ')'))
                elif tv == '?':
                    out.append((tokenize.NAME, 'Decimal'))
                    out.append((tokenize.OP, '('))
                    out.append((tokenize.STRING, repr(random.random())))
                    out.append((tokenize.OP, ')'))
                else:
                    out.append((tn, tv))

            return tokenize.untokenize(out)

        identity = string.ascii_lowercase[:self.cols]

        old_data = self.data.copy()
        self.data.clear()
        self.cols = 0
        value_dict = {'Decimal': decimal.Decimal}
        for k in identity:
            value_dict[k.upper()] = 0 # accumulators
        for r in old_data:
            for k, v in zip(identity, r):
                try:
                    value_dict[k] = int(v) if v.isdigit() else decimal.Decimal(v)
                    value_dict[k.upper()] += value_dict[k]
                except decimal.InvalidOperation:
                    value_dict[k] = v

            # allow xyz to refer to cells counted from the end...
            for j, k in zip("zyxw", reversed(identity)):
                value_dict[j] = value_dict[k]
                value_dict[j.upper()] = value_dict[k.upper()]

            new_row = []
            for dd in desiderata:
                try:
                    new_row.append(eval(_decimalize(dd), globals(), value_dict))
                except (ValueError, TypeError, NameError, AttributeError):
                    new_row.append(dd)
            self.append(new_row)

    def _fancy_col_index(self, col_spec):
        '''Find me an index, returns index + T/F to say if letter was upper case
        '''

        if col_spec is None:
            col_spec = 'a'

        flag = False
        if col_spec in string.ascii_uppercase:
            flag = True
            col_spec = col_spec.lower()

        if col_spec in string.ascii_lowercase:
            col_spec = ord(col_spec) - ord('a')

        try:
            c = int(col_spec)
        except ValueError:
            print('?! colspec', col_spec)
            return (None, flag)

        if c < 0:
            c += self.cols
        if c < 0:
            c = 0
        elif c >= self.cols:
            c = self.cols - 1
        assert 0 <= c < self.cols
        return (c, flag)

    def _sort_rows_by_col(self, col_spec):
        '''Sort the table
        By default sort by all columns left to right.

        If the arg is a single number and abs(arg) < self.cols then sort on that column

        Otherwise sort in groups where the col spec indicates the groups of cols

        abc means use the concatenation of row[0] + row[1] + row[2]
        upper case groups mean reverse sort

        groups are done right to left...

        '''
        def _as_numeric_tuple(x, backwards=False):
            '''return something for sort to work with
            >>> _as_numeric_tuple("a")
            (-1000000000000.0, 'A')

            >>> _as_numeric_tuple("a", True)
            (1000000000000.0, 'A')

            >>> _as_numeric_tuple(None)
            (1000000000000.0, '')

            >>> _as_numeric_tuple("3.14")
            (3.14, '3.14')

            >>> _as_numeric_tuple("2020-05-01")
            (1588287600, '2020-05-01')

            >>> _as_numeric_tuple("2 May 2020")
            (1588374000, '2 MAY 2020')

            >>> _as_numeric_tuple("A19")
            (-1000000000000.0, 'A000000000000019')
            '''

            alpha, omega = -1e12, 1e12
            if backwards:
                alpha, omega = omega, alpha

            if x is None:
                return (omega, '') # put it at the bottom

            x = x.upper()

            try:
                return (float(x), x)
            except ValueError:
                pass

            try:
                return (int(parse_date(x).strftime("%s")), x)
            except ValueError:
                pass

            # pad trailing numbers with zeros
            # Make A1, A2, A10 etc sortable...
            m = re.match(r'(.*\D)(\d+)\Z', x)
            if m is not None:
                return (alpha, m.group(1) + m.group(2).zfill(15))

            return (alpha, x)

        identity = string.ascii_lowercase[:self.cols]
        if col_spec is None:
            col_spec = identity

        try:
            i = int(col_spec)
        except ValueError:
            i = None

        if i is not None:
            if -self.cols <= i < self.cols:
                self.data.sort(key=lambda row: _as_numeric_tuple(row[i], False))
            return

        for col in col_spec[::-1]:
            c, want_reverse = self._fancy_col_index(col)
            if c is None:
                continue
            self.data.sort(key=lambda row: _as_numeric_tuple(row[c], want_reverse), reverse=want_reverse)

    def _remove_duplicates_by_col(self, col_spec):
        '''like uniq, remove row if key cols match the row above
        '''
        cols_to_check = []
        for c in col_spec:
            i, _ = self._fancy_col_index(c)
            if i is None:
                continue
            cols_to_check.append(i)
        rows_to_delete = []
        previous_t = ''
        for i, row in enumerate(self.data):
            this_t = ' '.join(row[j] for j in cols_to_check)
            if previous_t == this_t:
                rows_to_delete.append(i)
            else:
                previous_t = this_t

        for i in reversed(rows_to_delete):
            del self.data[i]

    def _add_grouping_blanks(self, col_spec):
        '''Add blanks to show groups in given column
        '''
        if col_spec is None:
            col_spec = 'a'

        cols_to_check = []
        for c in col_spec:
            i, _ = self._fancy_col_index(c)
            if i is None:
                continue
            cols_to_check.append(i)
        last_tag = ''
        for i, row in enumerate(self.data):
            this_tag = ' '.join(row[j] for j in cols_to_check)
            if i > 0 and this_tag != last_tag and not self.extras[i]:
                self.extras[i].append("blank")
            last_tag = this_tag


    def _roll_by_col(self, col_spec):
        '''Roll columns, up, or down
        '''
        if col_spec is None:
            self.data.insert(0, self.data.pop())
        else:
            self.data = list(map(list, zip(*self.data)))
            for c in col_spec:
                i, up = self._fancy_col_index(c)
                if i is None:
                    continue
                if up:
                    self.data[i].append(self.data[i].pop(0))
                else:
                    self.data[i].insert(0, self.data[i].pop())
            self.data = list(map(list, zip(*self.data)))

    def tabulate(self):
        '''Generate nicely lined up rows
        '''
        if self.form == 'csv':
            w = csv.writer(sys.stdout, lineterminator=os.linesep)
            w.writerows(self.data)
            return

        eol_marker = ''
        separator = '  '
        blank_line = None
        comment_marker = None
        ruler = None
        if self.form == 'tex':
            separator = ' & '
            eol_marker = ' \\cr'
            comment_marker = '%'
            blank_line = "\\noalign{\\medskip}"
            ruler = "\\noalign{\\vskip2pt\\hrule\\vskip4pt}"
        elif self.form == 'latex':
            separator = ' & '
            eol_marker = ' \\\\'
            comment_marker = '%'
            blank_line = "\\noalign{\\medskip}"
            ruler = "\\hline"
        elif self.form == 'tsv':
            separator = '\t'
        elif self.form == 'pipe':
            separator = ' | '
            ruler = 'piped'
        else:
            blank_line = ''
            comment_marker = '#'
            ruler = 'plain'

        widths = [max(len(row[i]) for row in self.data) for i in range(self.cols)]
        aligns = []
        for i in range(self.cols):
            booleans, _ = zip(*self.column(i))
            aligns.append('>' if sum(booleans)/len(booleans) > 1/2 else '<')

        def _pipe_rule(w, a):
            '''A rule for piped format, given width and alignment
            '''
            return '-' * (w-1) + (':' if a == '>' else '-')

        # generate nicely lined up rows
        for i, row in enumerate(self.data):
            for ex in self.extras[i]:
                if ex == 'rule' and ruler is not None:
                    if ruler == "plain":
                        yield ' ' * self.indent + '-' * (sum(widths) + self.cols * len(separator) - len(separator) + len(eol_marker))
                    elif ruler == "piped":
                        yield ' ' * self.indent + separator.join(_pipe_rule(w, a) for w, a in zip(widths, aligns))
                    else:
                        yield ruler

                elif ex == 'blank' and blank_line is not None:
                    yield blank_line

                elif ex.startswith('#') and comment_marker is not None:
                    yield comment_marker + ex[1:]

            out = []
            for j, cell in enumerate(row):
                out.append(f'{cell:{aligns[j]}{widths[j]}}')

            yield ' ' * self.indent + separator.join(out).rstrip() + eol_marker # no trailing blanks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("agenda", nargs='*', help="[delimiter.maxsplit] [verb [option]]...")
    parser.add_argument("--file", help="Source file name, defaults to STDIN")
    args = parser.parse_args()

    agenda = ' '.join(args.agenda).replace('\\', '').split(None)

    try:
        delim = agenda.pop(0)
    except IndexError:
        delim = '2'

    if re.match(r'^[a-zA-Z]', delim):
        agenda.insert(0, delim)
        delim = '2'

    cell_limit = 0
    mm = re.match(r'(\d*)\.(\d+)', delim)
    if mm is not None:
        delim = mm.group(1)
        if delim == '':
            delim = '2'
        cell_limit = int(mm.group(2))

    if delim.isdigit():
        in_sep = re.compile(rf'\s{{{delim},}}')
    else:
        in_sep = re.compile(re.escape(delim))

    fh = sys.stdin if args.file is None else open(args.file)

    table = Table()
    if delim == ',':
        table.parse_lol(csv.reader(fh))
    else:
        table.parse_lines(fh, splitter=in_sep, splits=cell_limit)
    table.do(agenda)
    print(table)

    if args.file is not None:
        fh.close()
