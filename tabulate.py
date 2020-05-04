#! /usr/bin/env python3
'''
Tabulate

A module to line up text tables
'''

# pylint: disable=C0103, C0301

import decimal
import fileinput
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
            'xp': self.transpose,
            'sort': self.sort_rows_by_col,
            'add': self.append_reduction,
            'arr': self.arrange_columns,
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
        # first expand any ~s
        perm = perm.replace("~", identity)

        # deal with deletions
        if perm == '-z': # special case
            perm = identity[:-1]
        elif perm.startswith('-'):
            perm = ''.join(sorted(set(identity) - set(perm)))

        perm = list(ord(x) - ord('a') for x in perm)

        for i, row in enumerate(self.data):
            self.data[i] = list(row[j] for j in perm)

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
