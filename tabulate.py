#! /usr/bin/env python3
'''
Tabulate

A module to line up text tables
'''

# pylint: disable=C0103, C0301

import fileinput
import re
import string
import sys

import dateutil.parser as dup

def _check_type(cell):
    '''is this a number?
    '''
    try:
        float(cell)
        return 1
    except ValueError:
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


def transpose(data, _):
    '''Swap rows and columns
    '''
    transposed_data = []
    for i, row in enumerate(data):
        for j, cell in enumerate(row):
            if i == 0:
                transposed_data.append([])
            transposed_data[j].append(cell)
    return transposed_data[:]

def sort_rows_by_col(data, column):
    '''Sort the table
    '''
    if column is None:
        return sorted(data)

    def as_number(x):
        '''return something for sort to work with'''
        if x is None:
            return 1e12

        try:
            return float(x)
        except ValueError:
            pass

        try:
            dt = dup.parse(x)
            return int(dt.strftime("%s"))
        except ValueError:
            pass

        return -1e12

    def as_seminumeric_string(x):
        # treat null as blank
        if x is None:
            return ''

        # pad trailing numbers with zeros
        m = re.match(r'(.*\D)(\d+)\Z', x)
        if m is not None:
            return "{}{:012d}".format(m.group(1), int(m.group(2)))

        return x.upper()

    cols = len(data[0])
    reverse_sort = False
    if column in string.ascii_uppercase:
        reverse_sort = True
        column = column.lower()

    if column in string.ascii_lowercase:
        column = ord(column) - ord('a')

    try:
        c = int(column)
    except ValueError:
        return data

    if c >= cols:
        c = cols - 1
    mapped = list((as_number(r[c]), as_seminumeric_string(r[c]), r) for r in data)
    return list(row for _, _, row in sorted(mapped, reverse=reverse_sort))

    return data


def _normalize(data, na_string="-"):
    '''Fill in any blank cells at the end of each row
    '''
    cols = max(len(row) for row in data)
    normal_data = []
    for row in data:
        normal_data.append(row + [na_string] * (cols - len(row)))
    return normal_data[:]

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

    table = list()
    for line in fileinput.input([]):
        cells = re.split(in_sep, line.strip(), maxsplit=cell_limit)
        table.append(cells)

    table = _normalize(table)

    operations = {
        'xp': transpose,
        'sort': sort_rows_by_col,
    }

    while agenda:
        op = agenda.pop(0)
        if op not in operations:
            print(f'{op} ??')
            continue

        # get an argument if there is one
        argument = agenda.pop(0) if agenda else None
        # put it back if it is really the next op
        if argument in operations:
            agenda.insert(0, argument)
            argument = None

        table = operations[op](table, argument)

    print("\n".join(tabulate(table, cell_separator=out_sep, line_end=eol)))
