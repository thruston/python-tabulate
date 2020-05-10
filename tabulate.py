#! /usr/bin/env python3
'''
Tabulate

A module to line up text tables
'''

# pylint: disable=C0103, C0301

import decimal
import fileinput
import math
import random
import re
import statistics
import string
import sys

import dateutil.parser as dup

class Table:
    '''A class to hold a table -- and some functions thereon'''

    def __init__(self):
        " empty data and no rows or cols "
        self.data = []
        self.rows = 0
        self.cols = 0
        self.operations = {
            'add': self.append_reduction,
            'arr': self.arrange_columns,
            'ditto': self.copy_down,
            'dp': self.fix_decimal_places,
            'gen': self.generate_new_rows,
            'sf': self.fix_sigfigs,
            'shuffle': self.shuffle_rows,
            'sort': self.sort_rows_by_col,
            'unwrap': self.unrapper,
            'unzip': self.unzipper,
            'wrap': self.rapper,
            'xp': self.transpose,
            'zip': self.zipper,
        }

    def append(self, row, filler='-'):
        "add a row, maintaining rows and cols"
        n = len(row)
        if n < self.cols:
            row.extend([filler] * (self.cols - n))
        elif self.cols < n:
            for r in self.data:
                r.extend([filler] * (n - self.cols))
            self.cols = n

        self.data.append(row)
        self.rows += 1

    def transpose(self, _):
        '''Swap rows and columns
        '''
        self.data = list(map(list, zip(*self.data)))
        self.rows, self.cols = self.cols, self.rows

    def shuffle_rows(self, _):
        '''Re-arrange the rows at random'''
        random.shuffle(self.data)

    def fix_decimal_places(self, dp_string):
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
            except ValueError:
                return s

        self.data = list(list(_round(c, dp) for c, dp in zip(r, dp_values)) for r in self.data)


    def fix_sigfigs(self, sf_string):
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

    def generate_new_rows(self, count_or_range):
        "Add some more data on the bottom"
        alpha = 1
        try:
            omega = int(count_or_range)
        except ValueError:
            m = re.match(r'(-?\d+)\D(-?\d+)$', count_or_range)
            if m is None:
                omega = 10
            else:
                alpha, omega = (int(x) for x in m.groups())
        if alpha > omega:
            (alpha, omega) = (omega, alpha)

        for i in range(alpha, omega+1):
            self.append([i])

    def copy_down(self, _):
        '''Fix up ditto marks'''
        for r in range(1, self.rows):
            for c in range(self.cols):
                if self.data[r][c] == '"':
                    self.data[r][c] = self.data[r-1][c]

    def zipper(self, n):
        '''Put n rows side by side
        '''
        try:
            rows_to_zip = int(n)
        except TypeError:
            rows_to_zip = 2

        if rows_to_zip < 2:
            return

        new_data = []
        while self.data:
            new_row = []
            for _ in range(rows_to_zip):
                if self.data:
                    new_row.extend(self.data.pop(0))
            new_data.append(new_row)

        self.data = new_data[:]
        self.rows = len(self.data)
        self.cols = max(len(c) for c in self.data)

    def unzipper(self, n):
        '''The opposite of zip.  Split rows so that there are cols/n cols in each'''
        try:
            splits = int(n)
        except TypeError:
            splits = 2

        desired_cols = math.ceil(self.cols / splits)

        new_data = []
        for r in self.data:
            for i in range(splits):
                start = i * desired_cols
                stop = start + desired_cols
                new_data.append(r[start:stop])
        self.data = new_data[:]
        self.rows = len(self.data)
        self.cols = max(len(c) for c in self.data)

    def rapper(self, n):
        '''It's a wrap.'''
        try:
            groups = int(n)
        except TypeError:
            groups = 2

        rows_per_group = math.ceil(self.rows / groups)

        new_data = []
        for i in range(rows_per_group):
            new_row = []
            for j in range(groups):
                k = i + j * rows_per_group
                if k < self.rows:
                    new_row += self.data[k]
            new_data.append(new_row)

        self.data = new_data[:]
        self.rows = len(self.data)
        self.cols = max(len(c) for c in self.data)

    def _splitme(self, seq, parts):
        if parts > 0:
            size = math.ceil(len(seq) / parts)
            yield seq[:size]
            if parts > 1:
                yield from self._splitme(seq[size:], parts - 1)

    def unrapper(self, n):
        '''It's not a wrap'''
        try:
            groups = int(n)
        except TypeError:
            groups = 2

        new_data = []
        for col_list in self._splitme(range(self.cols), groups):
            for r in self.data:
                new_data.append(list(r[x] for x in col_list))

        self.data = new_data[:]
        self.rows = len(self.data)
        self.cols = max(len(c) for c in self.data)

    def append_reduction(self, fun):
        '''Reduce column and append result to foot of table
        '''
        if isinstance(fun, str) and hasattr(statistics, fun):
            fun = getattr(statistics, fun)
        elif callable(fun):
            pass
        else:
            fun = sum

        footer = []
        for c in range(self.cols):
            footer.append(fun(as_decimal(r[c]) for r in self.data))
        self.append(footer)

    def arrange_columns(self, perm):
        '''Arrange the columns of the table
        '''
        identity = string.ascii_lowercase[:self.cols]
        specials = '.?'
        # first expand any ~s
        perm = perm.replace("~", identity)

        # deal with deletions
        if perm == '-z': # special case
            perm = identity[:-1]
        elif perm.startswith('-'):
            perm = ''.join(sorted(set(identity) - set(perm)))
        else:
            perm = ''.join(x for x in perm if x in identity + specials)

        def _get_value(c, line_number, row):
            '''Find a suitable value given the perm character and a row of data
            '''
            if c == '.':
                return line_number

            if c == '?':
                return random.random()

            return row[ord(c) - ord('a')]

        self.data = list(list(_get_value(x, i + 1, r) for x in perm) for i, r in enumerate(self.data))

    def sort_rows_by_col(self, column):
        '''Sort the table
        '''
        if column is None:
            column = 'a'

        reverse_sort = False
        if column in string.ascii_uppercase:
            reverse_sort = True
            column = column.lower()

        if column in string.ascii_lowercase:
            column = ord(column) - ord('a')

        try:
            c = int(column)
        except ValueError:
            print('?! sort', column)
            return

        if c < 0:
            c += self.cols
        if c < 0:
            c = 0
        elif c >= self.cols:
            c = self.cols - 1
        assert 0 <= c < self.cols

        self.data = list(row for _, _, row in sorted(((as_number(r[c], reverse_sort),
                                                       as_seminumeric_string(r[c]), r)
                                                      for r in self.data), reverse=reverse_sort))


def _check_type(cell):
    '''is this a number? (or something similar)
    '''
    try:
        float(cell)
        return 1
    except ValueError:
        pass

    if cell == '-':
        return 1

    return 0

def tabulate(data, cell_separator='  ', line_end=''):
    '''Render the table neatly
    '''

    # first count the cols and measure them
    col_widths = []
    col_types = []
    cols = 0
    for row in data:
        for i, cell in enumerate(row):
            if i >= cols:
                cols += 1
                col_widths.append([])
                col_types.append([])

            col_widths[i].append(len(str(cell)))
            col_types[i].append(_check_type(cell))

    # decide how to align them
    for i in range(cols):
        col_widths[i] = max(col_widths[i])
        col_types[i] = '>' if sum(col_types[i])/len(col_types[i]) >= 0.8 else '<'

    # generate nicely lined up rows
    for row in data:
        out = []
        for i, cell in enumerate(row):
            out.append(f'{cell:{col_types[i]}{col_widths[i]}}')

        out.append(line_end)
        yield cell_separator.join(out).rstrip() # no trailing blanks

def as_number(x, backwards=False):
    '''return something for sort to work with'''
    alpha, omega = -1e12, 1e12
    if backwards:
        alpha, omega = omega, alpha

    if x is None:
        return omega # put it at the bottom

    try:
        return float(x)
    except ValueError:
        pass

    try:
        dt = dup.parse(x)
        return int(dt.strftime("%s"))
    except ValueError:
        pass

    return alpha # put strings at the top

def as_seminumeric_string(x):
    "Make A1, A2, A10 etc sortable..."
    # treat null as blank
    if x is None:
        return ''

    # pad trailing numbers with zeros
    m = re.match(r'(.*\D)(\d+)\Z', x)
    if m is not None:
        return "{}{:012d}".format(m.group(1), int(m.group(2)))

    return x.upper()

def as_decimal(n, na_value=decimal.Decimal('0')):
    "Make this a decimal"
    try:
        return decimal.Decimal(n)
    except decimal.InvalidOperation:
        return na_value


if __name__ == "__main__":

    agenda = (' '.join(sys.argv[1:])).split(None)

    try:
        delim = agenda.pop(0)
    except IndexError:
        delim = '2'

    if re.match(r'^[a-zA-Z]', delim):
        agenda.insert(0, delim)
        delim = '2'

    cell_limit = 0
    m = re.match(r'(\d*)\.(\d+)', delim)
    if m is not None:
        delim = m.group(1)
        if delim == '':
            delim = '2'
        cell_limit = int(m.group(2))

    if delim.isdigit():
        in_sep = re.compile(rf'\s{{{delim},}}')
        out_sep = ' ' * int(delim)
    else:
        in_sep = re.compile(re.escape(delim))
        out_sep = delim

    eol = ''

    table = Table()
    for line in fileinput.input([]):
        cells = re.split(in_sep, line.strip(), maxsplit=cell_limit)
        table.append(cells)

    while agenda:
        op = agenda.pop(0)
        if op not in table.operations:
            print(f'{op} ??')
            continue

        # get an argument if there is one
        argument = agenda.pop(0) if agenda else None
        # put it back if it is really the next op
        if argument in table.operations:
            agenda.insert(0, argument)
            argument = None

        table.operations[op](argument)

    print("\n".join(tabulate(table.data, cell_separator=out_sep, line_end=eol)))
