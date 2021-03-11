#! /usr/bin/env python3
'''Tabulate

A module/script to line up text tables.
Toby Thurston -- 11 Mar 2021
'''

# pylint: disable=C0103, C0301

import argparse
import builtins
import collections
import csv
import decimal
import io
import itertools
import math
import os
import random
import re
import statistics
import string
import sys
import textwrap
import tokenize

import tab_fun_dates
import tab_fun_useful
import tab_fun_maths

# A great cat of functions for column maths, using the Decimal versions...
Panther = {
    'abs': builtins.abs,
    'bool': builtins.bool,
    'chr': builtins.chr,
    'divmod': builtins.divmod,
    'format': builtins.format,
    'int': builtins.int,
    'len': builtins.len,
    'ord': builtins.ord,
    'pow': builtins.pow,
    'round': builtins.round,
    'base': tab_fun_dates.base,
    'date': tab_fun_dates.date,
    'dow': tab_fun_dates.dow,
    'hms': tab_fun_dates.hms,
    'hr': tab_fun_dates.hr,
    'mins': tab_fun_dates.mins,
    'secs': tab_fun_dates.secs,
    'cos': tab_fun_maths.cos, 'cosd': tab_fun_maths.cosd,
    'sin': tab_fun_maths.sin, 'sind': tab_fun_maths.sind,
    'tan': tab_fun_maths.cos, 'tand': tab_fun_maths.tand,
    'hex': tab_fun_maths.decimal_to_hex,
    'oct': tab_fun_maths.decimal_to_oct,
    'pi': tab_fun_maths.PI,
    'tau': tab_fun_maths.TAU,
    'hypot': tab_fun_maths.pyth_add,
    'all': tab_fun_useful.t_all,
    'any': tab_fun_useful.t_any,
    'max': tab_fun_useful.t_max,
    'min': tab_fun_useful.t_min,
    'sorted': tab_fun_useful.t_sorted,
    'sum': tab_fun_useful.t_sum,
    'exp': lambda x: decimal.Decimal(x).exp(),
    'log': lambda x: decimal.Decimal(x).ln(),
    'log10': lambda x: decimal.Decimal(x).log10(),
    'sqrt': lambda x: decimal.Decimal(x).sqrt(),
    'reversed': lambda x: ''.join(reversed(x)),
    'Decimal': decimal.Decimal,
    '__builtins__': {},
}

# various number utils at this level

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
        return (int(tab_fun_dates.parse_date(x).strftime("%s")), x)
    except ValueError:
        pass

    # pad trailing numbers with zeros
    # Make A1, A2, A10 etc sortable...
    m = re.match(r'(.*\D)(\d+)\Z', x)
    if m is not None:
        return (alpha, m.group(1) + m.group(2).zfill(15))

    return (alpha, x)

def is_as_number(sss):
    '''Input (string) Output (boolean, any)
    if boolean is True, any is int or Decimal
    else any is string
    >>> is_as_number('')
    (False, '')
    >>> is_as_number("Label")
    (False, 'Label')
    >>> is_as_number("3.14")
    (True, Decimal('3.14'))
    >>> is_as_number('0')
    (True, Decimal('0'))
    >>> is_as_number('0x4F')
    (True, Decimal('79'))
    >>> is_as_number('0x40.0')
    (False, '0x40.0')
    >>> is_as_number('1,234,567')
    (True, Decimal('1234567'))
    >>> is_as_number('43%')
    (True, Decimal('0.43'))
    >>> is_as_number('-')
    (False, '-')
    >>> is_as_number('-902')
    (True, Decimal('-902'))
    >>> is_as_number('£34.00')
    (True, Decimal('34.00'))
    '''
    digits = '1234567890'
    ignore = '£$,_'
    signs = '+-'
    point = '.'
    alphabetics = 'xoabcdef'
    suffix = '%'

    if not all((c in digits + point + signs + ignore + alphabetics + suffix) for c in sss.lower()):
        return (False, sss)

    if not any((c in digits) for c in sss):
        return (False, sss)

    trial_number = ''.join(c for c in sss.lower() if c in digits + point + signs + alphabetics + suffix)

    try:
        return (True, decimal.Decimal(int(trial_number, 0)))
    except (ValueError, SyntaxError):
        pass

    try:
        if trial_number.endswith('%'):
            return (True, decimal.Decimal(trial_number[:-1])/100)
        return (True, decimal.Decimal(trial_number))
    except ArithmeticError:
        pass

    return (False, sss)

def as_decimal(n, na_value=decimal.Decimal('0')):
    "Make this a decimal"
    try:
        return decimal.Decimal(n)
    except decimal.InvalidOperation:
        return na_value

def siggy(s, n):
    '''Reduce to n sig figs
    >>> siggy('1,234', 2)
    '1200'
    >>> siggy('Text', 1)
    'Text'
    >>> siggy('0', 10)
    '0'
    '''
    flag, number = is_as_number(s)
    if not flag:
        return s
    if number.is_zero():
        return '0'
    figs =  n - math.floor(abs(number).log10()) - 1
    return '{:f}'.format(round(number, figs))

def rounders(s, n):
    '''Round to n fixed places, if possible
    >>> rounders('4',0)
    '4'
    >>> rounders('Text', 1)
    'Text'
    >>> rounders('45%', 3)
    '0.450'
    >>> rounders('45%', 1)
    '0.4'
    '''
    flag, number = is_as_number(s)
    return f'{number:.{n}f}' if flag else s

def looks_like_formula(expression):
    '''Is this a formula?

    >>> looks_like_formula('Abc?')
    False
    >>> looks_like_formula('-1')
    False
    >>> looks_like_formula('a-1')
    True
    '''
    if all(x in string.ascii_letters + '?' for x in expression):
        return False
    try:
        int(expression)
    except (TypeError, ValueError):
        pass
    else:
        return False
    return True

def compile_as_decimal(expr):
    '''This function takes as expression give as an argument to
    one of the verbs like arr or filter or sort or tap, and compiles
    it so that we can execute it more efficiently.
    Two little bits of syntactic sugar are applied to the expression:
    First we make all tokens that look like floats (NUMBER and
    contains '.') into Decimals, so that we avoid the normal FP accuracy &
    rounding issues.  Second we translate '?' into a (decimal) random number.

    '''
    out = []
    try:
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
    except tokenize.TokenError:
        return (False, '?! tokens ' + expr)

    try:
        cc = compile(tokenize.untokenize(out), "<string>", 'eval')
    except (SyntaxError, ValueError):
        return (False, '?! syntax ' +  expr)
    else:
        return (True, cc)

def _replace_values(failed_expression, known_variables):
    '''replace the variables that we know about in the expression

    >>> _replace_values('sin(a)', {'a': 'angle'})
    'sin(angle)'
    >>> _replace_values("a/x", {'a': 'count', 'x': 'hide_this'})
    'count/hide_this'
    >>> _replace_values("a*3+0", {'a': 'count', 'x': 'hide_this'})
    'count*3'
    >>> _replace_values("(a/x)", {'a': 'count', 'x': 'hide_this'})
    'count/hide_this'
    >>> _replace_values("f'{a}'", {'a': 'count', 'x': 'hide_this', 'f': 'and this'})
    "f'{count}'"
    >>> _replace_values("f'{a:x}'", {'a': 'count', 'x': 'hide_this', 'f': 'and this'})
    "f'{count:x}'"
    >>> _replace_values("f'{a:#b}'", {'a': 'count', 'b': 'hide_this', 'f': 'and this'})
    "f'{count:#b}'"
    '''

    if failed_expression.startswith("f'") or failed_expression.startswith('f"') :
        prefix = 'f'
        failed_expression = failed_expression[1:]
    else:
        prefix = ''

    for k, v in known_variables.items():  # try not to sub format types
        failed_expression = re.sub(rf'(?<![:#^0-9_,]){k}\b', str(v), failed_expression)

    if failed_expression[0] == '(' and failed_expression[-1] == ')':
        failed_expression = failed_expression[1:-1]

    if failed_expression.endswith('+0'):
        failed_expression = failed_expression[:-2]

    return prefix + failed_expression


class Table:
    '''A class to hold a table -- and some functions thereon'''

    def __init__(self):
        " empty data and no rows or cols "
        decimal.getcontext().prec = 12
        self.data = []
        self.cols = 0
        self.indent = 0
        self.extras = collections.defaultdict(set)
        self.form = 'plain'
        self.messages = []
        self.stack = [] # used to cache popped items
        self.operations = {
            'add': self._append_reduction,
            'arr': self._arrange_columns,
            'ditto': self._copy_down,
            'dp': self._fix_decimal_places,
            'dup': self._duplicate_item,
            'filter': self._select_matching_rows,
            'gen': self._generate_new_rows,
            'group': self._add_grouping_blanks,
            'help': self._describe_operations,
            'make': self._set_output_form,
            'label': self._label_columns,
            'nospace': self._remove_spaces_from_values,
            'noblanks': self._remove_blank_extras,
            'pivot': self._wrangle,
            'pop': self.pop,
            'push': self.push,
            'roll': self._roll_by_col,
            'rule': self.add_rule,
            'tap': self._apply_function_to_numeric_values,
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

        out = self.messages + list(self.tabulate())
        self.messages.clear()
        return "\n".join(out)

    def __getitem__(self, i):
        "Like a list..."
        return self.data[i]

    def __len__(self):
        "Also like a list..."
        return len(self.data)

    def _describe_operations(self, dsl_verb=''):
        '''What commands are defined?'''
        if dsl_verb.lower() == 'arr':
            verbs = sorted(x for x in Panther if x[0] in string.ascii_lowercase)
            msg = f'Functions for arr: {" ".join(verbs)}'
        else:
            msg = f'Try one of these: {" ".join(sorted(self.operations))}'
        self.messages.extend(textwrap.wrap(msg))

    def clear(self):
        "Clear data etc"
        self.data.clear()
        self.extras.clear()
        self.cols = 0
        self.indent = 0

    def _duplicate_item(self, n):
        "Duplicate an item"
        self.stack.append(self.pop(n)) # pop puts it on the stack first, so this does it twice
        self.push(n)
        self.push(n)

    def parse_tex(self, lines_thing, append=False):
        "Read lines from an iterable thing of TeX source, and append to self"

        if not append:
            self.clear()
        self.indent = 0
        eol_pattern = re.compile(r'\s*\\(cr|\\)\Z')
        amp_pattern = re.compile(r'\s*&\s*')
        for line in lines_thing:
            line = eol_pattern.sub('', line.strip())
            if line == "\\noalign{\\medskip}":
                self.add_blank()
            elif line == "\\hline":
                self.add_rule()
            elif line == "\\noalign{\\vskip2pt\\hrule\\vskip4pt}":
                self.add_rule()
            elif line.startswith('%'):
                self.add_comment(line[1:].rstrip())
            else:
                self.append(amp_pattern.split(line))

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

    def parse_lol(self, list_of_iterables, append=False, filler=''):
        "pass lol into self.data"
        if not append:
            self.clear()
        for r in list_of_iterables:
            if not r:
                self.add_blank()
            elif set(''.join(str(x) for x in r)) == {'-'}:
                self.add_rule()
            else:
                self.append(r, filler)

    def pop(self, n=None):
        '''Remove an entire row, saving it in case we want it later
        and allow them to be pushed back'''

        if n is None or n == '':
            r = self.data.pop()
        else:
            try:
                r = self.data.pop(int(n))
            except (IndexError, ValueError):
                r = None

        if r is not None:
            self.stack.append(r)

        return r

    def push(self, n=None):
        '''Put back a popped row, if possible'''
        try:
            r = self.stack.pop()
        except IndexError:
            return  # do nothing if stack is empty

        try:
            n = int(n)
        except (ValueError, TypeError):
            n = len(self.data)
        self.insert(n, r) # the semantics of insert take care of indexes out of bounds

    def append(self, iterable, filler=''):
        "insert at the end"
        self.insert(len(self.data), iterable, filler)

    def insert(self, i, iterable, filler=''):
        "add a row, maintaining cols"
        row = list(iterable)
        n = len(row)
        if n < self.cols:
            row.extend([filler] * (self.cols - n))
        elif self.cols < n:
            for r in self.data:
                r.extend([filler] * (n - self.cols))
            self.cols = n

        # they should all be strings, and normalize space in last column...
        self.data.insert(i, [str(x) for x in row[:-1]] + [' '.join(str(row[-1]).split())])

    def copy(self):
        "Implement the standard copy method"
        return self.data[:]

    def do(self, agenda=None):
        "Do what we've been asked..."
        if agenda is None:
            return
        if not isinstance(agenda, list):
            agenda = str(agenda).split()
        while agenda:
            op = agenda.pop(0)
            if op not in self.operations:
                self.messages.append(f'?? {op}')
                continue

            # get any arguments
            argument = []
            while agenda and agenda[0] not in self.operations:
                argument.append(agenda.pop(0))

            self.operations[op](' '.join(argument))

    def _label_columns(self, names=''):
        "add some labels"
        # make list of pairs like so (word from names or None, letter)
        # we can then "overlay" the names using the a or b construction
        # below.  The point of doing this is to make sure that if the
        # user only gives two names, the 3rd, 4th etc cols will still
        # be labelled c, d, etc.  If you have more than 26 cols
        # cols 27+ will get fillers instead of labels
        pairs = itertools.zip_longest(names.split(), string.ascii_lowercase)
        self.insert(0, list(a or b for a, b in pairs)[:self.cols])

    def column(self, i):
        "get a column from the table - zero indexed"
        try:
            return [is_as_number(r[i]) for r in self.data]
        except IndexError:
            return []

    def _valid_data_index(self, s):
        '''turn s into an index for self.data
        default to len(self.data)
        '''
        n = len(self.data)
        try:
            i = int(s)
        except (TypeError, ValueError):
            return n
        if i + n < 0:
            return 0
        if i < 0:
            return i + n
        if i > n:
            return n
        return i

    def add_blank(self, n=None):
        "flag a blank"
        self.extras[self._valid_data_index(n)].add("blank")

    def add_rule(self, n=None):
        "mark a rule"
        self.extras[self._valid_data_index(n)].add("rule")

    def add_comment(self, contents, n=None):
        "stash a comment line"
        self.extras[self._valid_data_index(n)].add('#' + contents.lstrip('#'))

    def _set_output_form(self, form_name):
        "Set the form name, used in `tabulate`"
        self.form = form_name.lower()

    def _transpose(self, _):
        '''Swap rows and columns
        '''
        self.cols = len(self.data)
        self.data = list(list(r) for r in zip(*self.data))
        self.extras.clear()

    def _select_matching_rows(self, expression):
        '''Filter the table to rows where expression is true
        '''
        if not expression:
            return

        ok, cc = compile_as_decimal(expression)
        if not ok:
            self.messages.append(cc)
            return

        old_data = self.data[:]
        self.data.clear()
        identity = string.ascii_lowercase[:self.cols]
        value_dict = {}
        value_dict['rows'] = len(old_data)
        for k in identity:
            value_dict[k.upper()] = 0 # accumulators

        for i, r in enumerate(old_data):
            value_dict['row_number'] = i + 1
            for k, v in zip(identity, r):
                flag, value_dict[k] = is_as_number(v)
                if flag:
                    value_dict[k.upper()] += value_dict[k]

            try:
                wanted = eval(cc, Panther, value_dict)
            except (TypeError, NameError):
                wanted = True  # default to keeping the row
            if wanted:
                self.append(r)
            elif i > 1 and i in self.extras:
                self.extras.pop(i) # remove extras if line not wanted (unless we are at the top)

        if not self.data:
            self.cols = 0

    def _shuffle_rows(self, _):
        '''Re-arrange the data at random'''
        random.shuffle(self.data)
        self.extras.clear()

    def _remove_blank_extras(self, _):
        for i in range(len(self.data)):
            self.extras[i].discard('blank')

    def _remove_spaces_from_values(self, joiner):
        '''Remove spaces from values -- this can make it easier to import into R'''
        if joiner:
            self.data = [[joiner.join(cell.split()) for cell in row] for row in self.data]
        else:
            self.data = [[''.join(cell.title().split()) for cell in row] for row in self.data]

    def _apply_function_to_numeric_values(self, fstring):
        '''fstring should be a maths expression with an x, as x+1 or 2**x etc
        which is to be applied to each numeric value in the table. If there is
        no x in the expression, we add one to the front, so you can write things
        like "+1" or "/4" as fstrings....
        '''
        if not fstring:
            return

        if "x" not in fstring and fstring[0] in ('*', '/', '+', '-', '<', '>', '='):
            fstring = "x" + fstring

        ok, cc = compile_as_decimal(fstring)
        if not ok:
            self.messages.append(cc)
            return

        values = {
            "x": 0,
            "rows": len(self.data),
            "cols": self.cols,
            "total":  sum(as_decimal(x) for row in self.data for x in row),
            "row_number": 0,
            "col_number": 0,
            "row_total": 0,
            "col_total": 0,
        }
        col_totals = [sum(x[1] for x in self.column(i) if x[0]) for i in range(self.cols)]

        old_rows = self.data[:]
        self.data.clear()
        errors = set()
        for row in old_rows:
            new_row = []
            values['row_number'] += 1
            values['row_total'] = sum(as_decimal(x) for x in row)
            for i, cell in enumerate(row):
                values['col_number'] = i + 1
                values['col_total'] = col_totals[i]
                ok, values['x'] = is_as_number(cell)
                if not ok:
                    new_row.append(cell)
                    continue
                try:
                    new_value = eval(cc, Panther, values)
                except (NameError, ValueError) as e:
                    errors.add(f'?! {fstring} <- {e!r}')
                    new_row.append(cell)
                else:
                    if isinstance(new_value, tuple):
                        new_row.extend(new_value)
                    else:
                        new_row.append(new_value)

            self.append(new_row)

        # if errors is null this does nothing...
        self.messages.extend(sorted(errors))

    def _apply_formats(self, f_string, f_function):
        "Used for DP and SF"
        if f_string is None or not f_string.isdigit():
            return
        # extend as needed (you could use zip_longest, but this just as simple)
        f_values = list(int(x) for x in f_string) + [int(f_string[-1])] * (self.cols - len(f_string))
        self.data = list(list(f_function(c, v) for c, v in zip(r, f_values)) for r in self.data)

    def _fix_decimal_places(self, dp_string):
        "Round all the numerical fields in each row"
        self._apply_formats(dp_string, rounders)

    def _fix_sigfigs(self, sf_string):
        "Round to n sig figs all the numeric fields in each row"
        self._apply_formats(sf_string, siggy)

    def _generate_new_rows(self, count_or_range):
        "Add some more data on the bottom"

        # simple integer
        if count_or_range.isdigit():
            self.parse_lol(list([x+1] for x in range(int(count_or_range))), append=True)
            return

        # integer range -4:99 etc...
        m = re.match(r'([-+]?\d+)(?:\.\.|:|::|--)([-+]?\d+)$', count_or_range)
        if m is not None:
            alpha, omega = (int(x) for x in m.groups())
            if alpha > omega:
                (alpha, omega) = (omega, alpha)
            self.parse_lol(list([x] for x in range(alpha, omega+1)), append=True)
            return

        # Labels * Cols...
        m = re.match(r'([A-Za-z]+)(\d)$', count_or_range)
        if m is not None:
            labels = m.group(1)
            columns = int(m.group(2))
            self.parse_lol(list([*x] for x in itertools.product(labels, repeat=columns)), append=True)
            return

    def _copy_down(self, marker):
        '''Fix up ditto marks'''
        if marker.strip() == "":
            marker = '"'
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                if cell == marker and i > 0:
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
        or something else built in that we like, if none of those then use "sum"
        '''

        if hasattr(statistics, fun):
            func = getattr(statistics, fun)
        elif fun == "q75" and hasattr(statistics, "quantiles"):
            func = lambda data: statistics.quantiles(data, n=4)[-1]
        elif fun == "q95" and hasattr(statistics, "quantiles"):
            func = lambda data: statistics.quantiles(data, n=20)[-1]
        elif fun in "min max all any sum".split():
            func = getattr(builtins, fun)
        elif fun == "prod":
            func = math.prod
        else:
            func = sum
            fun = 'total'

        footer = []
        for c in range(self.cols):
            booleans, decimals = zip(*self.column(c))
            if not any(booleans):
                footer.append(fun.title())
            else:
                footer.append(func(itertools.compress(decimals, booleans)))

        self.append(footer)

    def _wrangle(self, shape):
        '''Reflow / pivot / reshape from wide to long or long to wide

        pivot wide assumes that col -1 has values and -2 has col head values
        and everything else are keys. Does nothing if there are less than 3 cols.

        pivot long assumes only key is col A but you can add a letter or number
        to show where the keys stop -- so if the first three are keys then use "longc"
        or "long3" -- numbering from a=1

        '''
        if not shape or self.cols < 3:
            return

        pivot_function_for = {
            'wide': builtins.sum,
            'sum': builtins.sum,
            'count': builtins.len,
            'mean':  lambda a: statistics.mean(a) if a else 'NA',
            'any': builtins.any,
        }

        for k in pivot_function_for:
            if k.startswith(shape.lower()):
                self._wrangle_wide(pivot_function_for[k])
                return

        m = re.match(r'long([1-9a-o])?$', shape)
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
        >>> t._get_expr_list("abc(2+2**(4+3.5))e")
        ['a', 'b', 'c', '(2+2**(4+3.5))', 'e']
        >>> # allow missing trailing parens
        >>> t._get_expr_list("abc(2+2")
        ['a', 'b', 'c', '(2+2)']
        >>> t._get_expr_list("a..e")
        ['a', 'b', 'c', 'd', 'e']
        >>> t._get_expr_list("a..E")
        ['a', 'E']
        >>> t._get_expr_list("a..Z")
        ['a', 'H']
        >>> t._get_expr_list("e..a")
        ['e', 'd', 'c', 'b', 'a']
        >>> t._get_expr_list("a..z")
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        >>> t._get_expr_list("~z")
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'h']
        >>> t._get_expr_list("xyz")
        ['f', 'g', 'h']
        >>> t._get_expr_list("z")
        ['h']
        >>> t._get_expr_list("~(d/e)")
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', '(d/e)']
        >>> t._get_expr_list("(a..c/2)")
        ['(a/2)', '(b/2)', '(c/2)']
        '''
        identity = string.ascii_lowercase[:self.cols]
        in_parens = 0
        out = []
        expr = []

        # Allow counting from the right (but only xxyz)
        # only for simple_rearrangement here -- this shold probably refactor to there...
        if '(' not in given and self.cols < 22:
            for a, b in zip("zyxw", reversed(identity)):
                given = given.replace(a, b)
                given = given.replace(a.upper(), b.upper())

        # this is a kuldge to attempt to support ranges in calcs...
        def _replicate(mob):
            '''replicate the string from the mob'''
            prefix, a, b, suffix = mob.groups()
            if prefix is None:
                prefix = ''
            if suffix is None:
                suffix = ''
            a = min(ord(a), ord(identity[-1]))
            b = min(ord(b), ord(identity[-1]))
            if a > b:
                r = range(a, b-1, -1)
            else:
                r = range(a, b+1)

            return ''.join([prefix + chr(x) + suffix for x in r])

        given = re.sub(r'(.*?[^a-z])?([a-z])\.\.([a-z])([^a-z].*)?', _replicate, given)

        for c in given:
            if in_parens == 0:
                if c.lower() in identity + '?':
                    out.append(c)
                elif c in '({':
                    in_parens = 1
                    expr = ['(']
                elif c == '~':
                    out.extend(x for x in identity)
                else:
                    pass # ignore anything else outside parens
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
        if not perm:
            return

        # deletions...
        if perm[0] == '-':
            if '(' not in perm:
                delenda = list(ord(x) - ord('a') for x in self._get_expr_list(perm[1:]))
                self.data = list(list(x for i, x in enumerate(r) if i not in delenda) for r in self.data)
                self.cols = len(self.data[0])
            return

        perm = self._get_expr_list(perm)
        identity = string.ascii_lowercase[:self.cols]

        def _get_value(row, c):
            '''Find a suitable value given the perm character and a row of data
            '''
            return str(random.random()) if c == '?' else row[ord(c) - ord('a')]

        if all(x in identity + '?' for x in perm):
            self.data = list(list(_get_value(r, x) for x in perm) for r in self.data)
            self.cols = len(perm) # perm can delete and/or add columns
            return

        # make it into a list tuples
        desiderata = []
        for x in perm:
            ok, cc = compile_as_decimal(x)
            if not ok:
                self.messages.append(cc)
                return
            desiderata.append((cc, x))

        old_data = self.data.copy()
        self.data.clear()
        self.cols = 0
        value_dict = {}
        value_dict['rows'] = len(old_data)
        for k in identity:
            value_dict[k.upper()] = 0 # accumulators

        for row_number, r in enumerate(old_data):
            for k, v in zip(identity, r):
                flag, value_dict[k] = is_as_number(v)
                if flag:
                    value_dict[k.upper()] += value_dict[k]

            # allow xyz to refer to cells counted from the end...
            for j, k in zip("zyxw", reversed(identity)):
                value_dict[j] = value_dict[k]
                value_dict[j.upper()] = value_dict[k.upper()]

            # and note the line number
            value_dict['row_number'] = row_number + 1

            new_row = []
            for compiled_code, literal_code in desiderata:
                try:
                    new_value = eval(compiled_code, Panther, value_dict)
                    if isinstance(new_value, tuple):
                        new_row.extend(new_value)
                    else:
                        new_row.append(new_value)
                except (ValueError, TypeError, NameError, AttributeError, decimal.InvalidOperation):
                    new_row.append(_replace_values(literal_code, value_dict))
                except ZeroDivisionError:
                    new_row.append("-")
            self.append(new_row)

    def _fancy_col_index(self, col_spec):
        '''Find me an index, returns index + T/F to say if letter was upper case
        '''
        assert col_spec

        flag = False
        if col_spec in string.ascii_uppercase:
            flag = True
            col_spec = col_spec.lower()

        if col_spec in string.ascii_lowercase:
            col_spec = ord(col_spec) - ord('a')

        try:
            c = int(col_spec)
        except ValueError:
            self.messages.append('?! colspec ' + col_spec)
            return (None, flag)

        if c >= self.cols:
            c = self.cols - 1
        assert 0 <= c < self.cols
        return (c, flag)

    def _sort_rows_by_col(self, col_spec=None):
        '''Sort the table
        By default sort by all columns left to right.

        If the arg is a single number and abs(arg) < self.cols then sort on that column

        Otherwise sort in groups where the col spec indicates the groups of cols

        abc means use the concatenation of row[0] + row[1] + row[2]
        upper case groups mean reverse sort

        groups are done right to left...

        '''
        if looks_like_formula(col_spec):
            self.do(f"arr ({col_spec})~ sort a arr -a")
            return

        identity = string.ascii_lowercase[:self.cols]
        if col_spec is None or col_spec == '':
            col_spec = identity

        try:
            i = int(col_spec)
        except ValueError:
            for col in col_spec[::-1]:
                c, want_reverse = self._fancy_col_index(col)
                if c is None:
                    continue
                self.data.sort(key=lambda row: as_numeric_tuple(row[c], want_reverse), reverse=want_reverse)
        else:
            if -self.cols <= i < self.cols:
                self.data.sort(key=lambda row: as_numeric_tuple(row[i], False))

    def _remove_duplicates_by_col(self, col_spec):
        '''like uniq, remove row if key cols match the row above
        '''
        if col_spec is None or col_spec == '':
            cols_to_check = list(range(self.cols))
        else:
            cols_to_check = []
            for c in col_spec:
                i, _ = self._fancy_col_index(c)
                if i is None:
                    continue
                cols_to_check.append(i)

        if not cols_to_check:
            return

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
        if not col_spec:
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
                self.extras[i].add("blank")
            last_tag = this_tag

    def _roll_by_col(self, col_spec):
        '''Roll columns, up, or down
        '''
        if not col_spec:
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
        # this roundabout approach makes tabulate more consistent
        # for speed you could make csv write directly to sys.stdout
        if self.form == 'csv':
            out = io.StringIO()
            w = csv.writer(out, lineterminator=os.linesep)
            w.writerows(self.data)
            for line in out.getvalue().splitlines():
                yield line
            out.close()
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("agenda", nargs='*', help="[delimiter.maxsplit] [verb [option]]...")
    parser.add_argument("--file", help="Source file name, defaults to STDIN")
    args = parser.parse_args()

    # Join the agenda args into one string, remove any backslash (for Vim), and split into a list
    agenda = ' '.join(args.agenda).replace('\\', '').split(None)

    # Get the delimiter from the agenda if possible
    try:
        delim = agenda.pop(0)
    except IndexError:
        delim = None
    else:
        # If the removed delim is starts with alphabetic, put it back and reset delim to None
        if re.match(r'^[a-zA-Z]', delim):
            agenda.insert(0, delim)
            delim = None

    table = Table()
    fh = io.StringIO(sys.stdin.read()) if args.file is None else open(args.file)
    if delim is None:
        first_line = fh.readline().strip()
        fh.seek(0)
        # guess delim from content: csv , tex & latex & pipe |
        if (first_line.count(' ') == 0 and first_line.count(',') > 2) or ('","' in first_line):
            table.parse_lol(csv.reader(fh))

        elif first_line.count('&') > 0 and first_line.endswith("\\cr"):
            table.parse_tex(fh)
            table.do('make tex')

        elif first_line.count('&') > 0 and first_line.endswith("\\\\"):
            table.parse_tex(fh)
            table.do('make latex')

        elif first_line.count('|') > 2:
            table.parse_lines(fh, splitter=re.compile(r'\s*\|\s*'))

        else:
            table.parse_lines(fh, splitter=re.compile(r'\s{2,}'))

    elif delim == ',':
        table.parse_lol(csv.reader(fh))

    else:
        # check for a maxsplit spec ".3", "2.4" etc
        mm = re.match(r'(\d*)\.(\d+)', delim)
        if mm is not None:
            delim = mm.group(1)
            if delim == '':
                delim = '2'
            cell_limit = int(mm.group(2))
        else:
            cell_limit = 0
        if delim.isdigit():
            in_sep = re.compile(rf'\s{{{delim},}}')
        else:
            in_sep = re.compile(re.escape(delim))
        table.parse_lines(fh, splitter=in_sep, splits=cell_limit)
    table.do(agenda)
    print(table)

    if args.file is not None:
        fh.close()
