#! /usr/bin/env python3
'''
Tabulate

A module to line up text tables
'''

# pylint: disable=C0103, C0301

import collections
import datetime
import decimal
import fileinput
import math
import random
import re
import statistics
import string
import sys

import dateutil.parser as dup

decimal.getcontext().prec = 12

# Functions for column maths
def exp(d):
    return d.exp()
def sqrt(d):
    return d.sqrt()
def log(d):
    return d.log10()
def ln(d):
    return d.ln()

def dow(sss):
    try:
        return dup.parse(sss).strftime("%a")
    except (TypeError, ValueError):
        return sss

def base(sss=None):
    try:
        dt = dup.parse(sss)
    except (TypeError, ValueError):
        dt = datetime.date.today()
    return dt.toordinal()

def date(ordinal=0):
    try:
        ordinal = int(ordinal)
    except (TypeError, ValueError):
        ordinal = 0

    if abs(ordinal) < 1000:
        dt = datetime.date.today() + datetime.timedelta(days=ordinal)
    elif ordinal > 1000000000000:
        dt = datetime.datetime.utcfromtimestamp(ordinal / 1000)
    elif ordinal > 1000000000:
        dt = datetime.datetime.utcfromtimestamp(ordinal)
    else:
        try:
            dt = datetime.date.fromordinal(ordinal)
        except (TypeError, ValueError):
            dt = datetime.date.today()

    return dt.isoformat()

class Table:
    '''A class to hold a table -- and some functions thereon'''

    def __init__(self):
        " empty data and no rows or cols "
        self.data = []
        self.rows = 0
        self.cols = 0
        self.indent = 999
        self.extras = collections.defaultdict(str)
        self.separator = '  ' # two spaces
        self.eol_marker = ''
        self.operations = {
            'add': self.append_reduction,
            'arr': self.arrange_columns,
            'ditto': self.copy_down,
            'dp': self.fix_decimal_places,
            'gen': self.generate_new_rows,
            'make': self.set_output_form,
            'label': self.label_columns,
            'pivot': self.wrangle,
            'roll': self.roll_by_col,
            'sf': self.fix_sigfigs,
            'shuffle': self.shuffle_rows,
            'sort': self.sort_rows_by_col,
            'uniq': self.remove_duplicates_by_col,
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

    def label_columns(self, _):
        "add some labels in alphabetical order"
        self.data.insert(0, string.ascii_lowercase[:self.cols])
        self.rows += 1

    def column(self, i):
        "get a column from the table - zero indexed"
        try:
            return [(is_decimal(r[i]), as_decimal(r[i])) for r in self.data]
        except IndexError:
            return []

    def row(self, i):
        "get a row - zero indexed"
        try:
            return [(is_decimal(c), as_decimal(c)) for c in self.data[i]]
        except IndexError:
            return []

    def add_blank(self):
        "flag a blank"
        self.extras[self.rows] = "blank"

    def add_rule(self):
        "mark a rule"
        self.extras[self.rows] = "rule"

    def add_comment(self, contents):
        "stash a comment line"
        self.extras[self.rows] = '#' + contents.lstrip('#')

    def set_output_form(self, form_name):
        "Set the seps"
        form = form_name.lower()
        if form == 'plain':
            self.separator = '  '
        elif form == 'tex':
            self.separator = ' & '
            self.eol_marker = ' \\cr'
        elif form == 'latex':
            self.separator = ' & '
            self.eol_marker = ' \\\\'
        elif form == 'tsv':
            self.separator = '\t'
        elif form == 'single':
            self.separator = ' '
        else:
            pass

    def transpose(self, _):
        '''Swap rows and columns
        '''
        self.data = list(map(list, zip(*self.data)))
        self.rows, self.cols = self.cols, self.rows
        self.extras.clear()

    def shuffle_rows(self, _):
        '''Re-arrange the rows at random'''
        random.shuffle(self.data)
        self.extras.clear()

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
        self.extras.clear()

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
        self.extras.clear()

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
        self.extras.clear()

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
        self.extras.clear()

    def append_reduction(self, fun):
        '''Reduce column and append result to foot of table
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
                footer.append(func(decimals))

        self.add_rule()
        self.append(footer)

    def wrangle(self, shape):
        '''Reflow / pivot / reshape from wide to long or long to wide

        pivot wide assumes that col -1 has values and -2 has col head values
        and everything else are key. Does nothing if there are less than 3 cols.

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
        self.rows = self.cols = 0
        names = sorted(names_seen)
        self.append(header + names)
        for k in keys_seen:
            self.append(list(k) + [fun(bags[(k, n)]) for n in names])

    def _wrangle_long(self, keystop):
        '''Reflow long'''
        header = self.data[0][:keystop] + ['Name', 'Value']
        names = self.data[0][keystop:]
        wide_data = self.data[1:]
        self.data = []
        self.rows = self.cols = 0

        self.append(header)
        for r in wide_data:
            for n, v in zip(names, r[keystop:]):
                self.append(r[:keystop] + [n, v])

    def arrange_columns(self, perm):
        '''Arrange the columns of the table
        '''
        identity = string.ascii_lowercase[:self.cols]
        specials = '.?;'
        # first expand any ~s
        perm = perm.replace("~", identity)

        # deal with deletions
        if perm == '-z' and self.cols < 26: # special case
            perm = identity[:-1]
        elif perm.startswith('-'):
            perm = ''.join(sorted(set(identity) - set(perm)))

        def _get_value(c, line_number, row):
            '''Find a suitable value given the perm character and a row of data
            '''
            if c == '.':
                return line_number
            if c == '?':
                return random.random()
            if c == ';':
                return self.rows
            return row[ord(c) - ord('a')]

        if all(x in identity + specials for x in perm):
            self.data = list(list(_get_value(x, i + 1, r) for x in perm) for i, r in enumerate(self.data))
            self.cols = len(perm) # perm can delete and/or add columns
            return

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

        def _get_expressions(perm):
            in_parens = 0
            token = ''
            for c in perm:
                if c.lower() not in identity + specials + '(){}' and in_parens == 0:
                    continue

                if c == '{':
                    c = '('
                elif c == '}':
                    c = ')'

                token += c

                if c == '(':
                    in_parens += 1
                    continue

                if c == ')':
                    in_parens -= 1

                if in_parens == 0:
                    yield token
                    token = ''

            if token:
                yield token + ')' * in_parens

        desiderata = list(_get_expressions(perm))
        old_data = self.data[:]
        self.data = []
        self.rows = self.cols = 0
        value_dict = {'Decimal': decimal.Decimal}
        for k in identity:
            value_dict[k.upper()] = 0 # accumulators
        for r in old_data:
            for k, v in zip(identity, r):
                try:
                    value_dict[k] = decimal.Decimal(v)
                    value_dict[k.upper()] += value_dict[k]
                except decimal.InvalidOperation:
                    value_dict[k] = v

            new_row = []
            for dd in desiderata:
                try:
                    new_row.append(str(eval(_decimalize(dd), globals(), value_dict)))
                except (TypeError, NameError, AttributeError):
                    new_row.append(dd)
            self.append(new_row)

    def fancy_col_index(self, col_spec):
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

    def sort_rows_by_col(self, col_spec):
        '''Sort the table
        '''
        if col_spec is None:
            self.data.sort(key=lambda row: as_numeric_tuple(row[0], False))
        else:
            for col in col_spec:
                c, want_reverse = self.fancy_col_index(col)
                if c is None:
                    continue
                self.data.sort(key=lambda row: as_numeric_tuple(row[c], want_reverse), reverse=want_reverse)

    def remove_duplicates_by_col(self, col_spec):
        '''like uniq, remove row if key cols match the row above
        '''
        cols_to_check = []
        for c in col_spec:
            i, _ = self.fancy_col_index(c)
            if i is None:
                continue
            cols_to_check.append(i)
        rows_to_delete = []
        previous_t = ''.join(self.data[0][j] for j in cols_to_check)
        for i in range(1, self.rows):
            this_t = ' '.join(self.data[i][j] for j in cols_to_check)
            if previous_t == this_t:
                rows_to_delete.append(i)
            else:
                previous_t = this_t

        for i in reversed(rows_to_delete):
            del self.data[i]
            self.rows -= 1

    def roll_by_col(self, col_spec):
        '''Roll columns, up, or down
        '''
        self.data = list(map(list, zip(*self.data)))
        for c in col_spec:
            i, up = self.fancy_col_index(c)
            if i is None:
                continue
            if up:
                self.data[i].append(self.data[i].pop(0))
            else:
                self.data[i].insert(0, self.data[i].pop())
        self.data = list(map(list, zip(*self.data)))

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

def tabulate(data, indent=0, cell_separator='  ', line_end='', special_dict=collections.defaultdict(str)):
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
        col_types[i] = '>' if sum(col_types[i])/len(col_types[i]) >= 1/2 else '<'

    # generate nicely lined up rows
    for r, row in enumerate(data):
        if special_dict[r] == 'rule':
            yield ' ' * indent + '-' * len(out)
        elif special_dict[r] == 'blank':
            yield ' ' * (indent + len(out))
        elif special_dict[r].startswith('#'):
            yield special_dict[r]

        out = []
        for c, cell in enumerate(row):
            out.append(f'{cell:{col_types[c]}{col_widths[c]}}')

        out = cell_separator.join(out).rstrip() + line_end # no trailing blanks
        yield ' ' * indent + out

def as_numeric_tuple(x, backwards=False):
    '''return something for sort to work with
    >>> as_numeric_tuple("a")
    (-1000000000000.0, 'A')

    >>> as_numeric_tuple("a", True)
    (1000000000000.0, 'A')

    >>> as_numeric_tuple(None)
    (1000000000000.0, '')

    >>> as_numeric_tuple("3.14")
    (3.14, '3.14')

    >>> as_numeric_tuple("2020-05-01")
    (1588287600, '2020-05-01')

    >>> as_numeric_tuple("2 May 2020")
    (1588374000, '2 MAY 2020')

    >>> as_numeric_tuple("A19")
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
        return (int(dup.parse(x).strftime("%s")), x)
    except ValueError:
        pass

    # pad trailing numbers with zeros
    # Make A1, A2, A10 etc sortable...
    m = re.match(r'(.*\D)(\d+)\Z', x)
    if m is not None:
        return (alpha, m.group(1) + m.group(2).zfill(15))

    return (alpha, x)

def as_decimal(n, na_value=decimal.Decimal('0')):
    "Make this a decimal"
    try:
        return decimal.Decimal(n)
    except decimal.InvalidOperation:
        return na_value

def is_decimal(n):
    "Is this a decimal"
    try:
        _ = decimal.Decimal(n)
        return True
    except decimal.InvalidOperation:
        return False

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
    else:
        in_sep = re.compile(re.escape(delim))

    table = Table()

    for raw_line in fileinput.input([]):
        raw_line = raw_line.replace("\t", "    ")
        stripped_line = raw_line.strip()
        if not stripped_line:
            table.add_blank()
        elif set(stripped_line) == {'-'}:
            table.add_rule()
        elif stripped_line.startswith('#'):
            table.add_comment(stripped_line)
        else:
            table.append(re.split(in_sep, stripped_line, maxsplit=cell_limit))
            table.indent = min(table.indent, len(raw_line) - len(raw_line.lstrip()))
    if table.rows == 0:
        table.indent = 0

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

    print("\n".join(tabulate(table.data, indent=table.indent,
                             special_dict=table.extras,
                             cell_separator=table.separator,
                             line_end=table.eol_marker)))
