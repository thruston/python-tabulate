Tabulate
--------

Line up tabular material neatly.

An exportable module that will line up tabular material automatically, and so
save you hours of time faffing about with format and alignment.  As a script it
provides a filter with a simple DSL that can be used to make and manipulate
tables in editors that support external filters (such as Vim).

If your work involves editing lots of plain text you will get familiar with a
plain text editor such as Vim or Emacs or similar. You will get familiar with
the facilities for arranging code and paragraphs of plain text.  Eventually you
will need to create a table of data or other information, something like this

    event  eruption  waiting
        1     3.600       79
        2     1.800       54
        3     3.333       74
        4     2.283       62
        5     4.533       85

and you may find that your editor has some useful facilities for working in "block"
mode that help to manage the table.  But you might also find that the facilities are
just a little bit limited.   You want to know the totals of each column, but you
really didn't want to load the data into a spreadsheet or a statistics system like
R; you just want the simple totals.   That's what tabulate is for.  If you set it up
in Vim (see below) as a user command, then you can just say `:Table add` to get this:

    event  eruption  waiting
        1     3.600       79
        2     1.800       54
        3     3.333       74
        4     2.283       62
        5     4.533       85
    ------------------------
       15    15.549      354

OK, that's not perfect, but all you have to do now is change that 15 to `Total` (or just
undo the last change to get rid of the new lines or whatever).

Tabulate also lets you transpose a table (to get this...)

    event         1      2      3      4      5
    eruption  3.600  1.800  3.333  2.283  4.533
    waiting      79     54     74     62     85

as well as, sort by any column in the table, rearrange the columns, delete
columns, or add new columns computed from the others.  It can't do everything
you can do in a spreadsheet but it can do most of the simple things, and you
can use it right in the middle of your favourite editor.

Many of my Python scripts create tables of data that I need to share in plain
text (on Slack for example), and I often found myself loading the output into
Vim just so I could tidy it up with `tabulate`.  So I have re-written the original
Perl version of tabulate as a Python module that can be imported, and used to
tidy up a list of lists of data for printing directly as part of a script.

Toby Thurston -- 19 Feb 2021

## Usage and set up

You can use tabulate from the command line, from your editor, or as a Python module.
In each case, you use the same mini-language of verbs to act on your table.  These
are described in the next main section.

### Usage from the command line

You can run `tabulate.py` from the command line.  It will process lines from STDIN
or from an optional file path.

    usage: tabulate.py [-h] [--file FILE] [agenda [agenda ...]]

    positional arguments:
      agenda       [delimiter.maxsplit] [verb [option]]...

    optional arguments:
      -h, --help   show this help message and exit
      --file FILE  Source file name, defaults to STDIN

### Usage from within Vim

To use tabulate as a filter, you need first to add a line to your `.vimrc` file like this:

    :command! -nargs=* -range=% Table <line1>,<line2>!python3 ~/python-tabulate/tabulate.py <q-args>

which you should adjust appropriately so your python3 can find where you put
tabulate.  You can of course use some word other than `Table` as the command
name. Perhaps `Tbl` ?  Take your pick, you can choose anything, except that Vim
insists on the name starting with an uppercase letter.

With a definition like this, when you type `:Table` in normal mode in Vim, it
will call tabulate on the current area and replace it with the output.  If you
are in Visual Line mode then the current area will just be the marked lines.
If you are in Normal mode then the current area will be the whole file.

    :Table [delimiter.maxsplit] [verb [option]]...

### Writing the command line

Whether you are calling tabulate from Vim or the command line, the parsing of your
input is the same.

Use blanks to separate the arguments you type: the delimiter argument and any
verbs must be single blank-separated words.  Any word that looks like a verb
will be treated as a verb, even if you meant it to be an option.  See below for
details.  Options can in some cases contain blanks.

The delimiter is used to split up each input line into cells.  It can be any
single non-alphabetic character or a whole number between 0 and 9.  You can't use
blanks (even inside quotes) because of the simple way that I split up the
command line, and so I use whole numbers to mean `split on at least that many
consecutive blanks` so if you use 1 as an argument the line will be split on
every blank space, and so on. The default argument is 2.  This means the line
will be split at every occurrence of two or more blanks.  This is generally
what you want.  Consider this example.

    Item          Amount
    First label       23
    Second thing      45
    Third one         55
    Total            123

In most circumstances you can just leave the delimiter out and let it default
to two or more spaces.  Incidentally, any tab characters in your input are
silently converted to double spaces before parsing.

You can also limit the number of cell splits done by adding a second number to
a numeric delimiter.  So "1.3" will use one or more spaces as the delimiter,
but will only make 4 columns. This is often handy when parsing log files etc.

After the optional delimiter you should specify a sequence of verbs.  If the
verb needs an option then that goes right after the verb.  Verbs and options
are separated by blanks.  The parsing is very simple.  If it looks like a verb
it's treated as one.  If it doesn't, it's assumed to be an option.  Anything
coming after an option, but not recognized as a verb, causes an error.  A
message will be written back in the file.  You will probably want to use the
`undo` function after reading it.

### Usage as a Python library

Tabulate can also be used from your own Python scripts.  If you have
data as a list of lists, or a  list of strings, then you can use `tabulate` to format
them neatly.  Something like this

```python
import tabulate
data = [('Item', 'Amount'), ('First label', 23), ('Second thing', 45), ('Third one', 55)]
tt = tabulate.Table()
tt.parse_lol(data)
tt.do("add")
print(tt)
```

which should produce

```
Item          Amount
First label       23
Second thing      45
Third one         55
--------------------
Total            123
```

`parse_lol` is expecting a list of lists (or list of iterables) as shown.  But
you can also use `tt.parse_lines(object_with_lines)` to read a file or a list of strings.

    tt.parse_lines(lines_thing, splitter=re.compile('\\s\\s+'), splits=0)

As shown, `parse_lines` takes two optional arguments:  a regex for splitting
and a maximum number of splits to make, where 0 means "as many as there are".

You could also add lines one at a time using the Table.append() method.  So the example
above could be done as
```python
data = [('Item', 'Amount'), ('First label', 23), ('Second thing', 45), ('Third one', 55)]
tt = tabulate.Table()
for row in data:
    tt.append(row)
tt.do("add")
print(tt)
```
The appended `row` is treated as an iterable. If you append a single string it will be
split up into letters following normal Python semantics.

The `do` method processes a list of verbs and options as described above.

The tabulate module overloads the `__str__` method, so that printing your Table object
will show it neatly tabulated.  If you want the individual lines, use the `tabulate()` method
to get a generator of neat lines.

See below for all the public methods provided by a `Table` object.

## Special rows

Any blank lines in your table are saved as special lines and reinserted at the
appropriate place on output. So if you have a long table you can use blanks to
separate blocks of data.  Similarly any lines consisting entirely of `-`
characters are treated as horizontal rules and reinserted (appropriately sized)
on output.  Any lines starting with `#` are treated as comment lines, and again
reinserted in the right places on output.

## Verbs in the DSL

If you do `help`, then tabulate will print "Try one of these:" followed by a list of 
all the defined verbs.  Like this:

    Try one of these: add arr cdiff ditto dp filter gen group help label make
    noblanks normalize nospace pivot pop roll rule sf shuffle sort tap uniq unwrap
    unzip wrap xp zip

The following thematic tables summarize the ones you are likely to use most.
Then they are all described in more detail below, in alphabetical order.

Rearrange the columns 

- arr col-list     rearrange/insert/delete cols and/or do calculations on column values.
- wrap n           wrap columns in long table n times (default=2)
- unwrap n         unwrap cols in wide table (default=half number of cols)
- zip n            zip n rows together into a single row with n * more columns
- unzip n          unzip into n * the current number of rows & 1/n columns
- pivot wide|long  reshape, tidyr, melt/cast, simple tables
- [xp](#xp---transpose-the-table)        transpose rows and cells

Rearrange or filter the rows

    sort [col]       sort by value of columns in the order given, use UPPERCASE to reverse
    uniq [col]       remove rows where the value of col is the same as the row above
    group [col]      insert special blank rows between different values in given col
    filter expr      select rows where "expr" evaluates to True
    pop [n]          remove row n, where n is 0-indexed and defaults to -1 

Decorate / adjust the whole table

    label            add alphabetic labels at the top
    add [function]   add sum, mean, var, sd etc to foot of each column
    normalize        normalize the numeric values so that they add to 1
    tap x-expr       adjust the numeric values with the given expression
    dp dp-list       round numbers in each col to specified decimal places
    sf sf-list       round numbers in each col to specified significant figures
    make tex | latex | plain | csv | tsv | md   output in tex etc form

You can string together as many verbs (plus optional arguments) as you like.


*TODO* -- put this in order....

### xp - transpose the table

`xp` just transposes the entire table. It takes no options.

    First   100
    Second  200
    Third   300

becomes

    First  Second  Third
    100    200     300

It's often useful in combination with verbs that operate on columns like `sort` or `add`.
So the sequence `xp add xp` will give you row totals, for example.

### add - insert the sum|mean|etc at the bottom of a column

    add [sum|mean|median|q95|...] 

`add` adds the total to the foot of a column.  The default option is `sum`, but
it can be any method from the Python3 `statistics` library: `mean`, `median`,
`mode`, `stdev`, `variance`, and so on, plus `q95` for the 95%-ile.
Non-numerical entries in a column are ignored.  A rule is added before the
total row.  Given this:

    First   100
    Second  200
    Third   300

then `add` produces:

    First   100
    Second  200
    Third   300
    -----------
    Total   600

If you want to change the function, or if you have changed a value and you want to update
the total, then you need to get rid of the total line first.  There is a slick way to do this.
Given a table like the one immediately above with a total row, try `pop add mean`:

    First   100
    Second  200
    Third   300
    -----------
    Mean    200

The `pop` removes the last row before adding the new function.  You can use the same trick
if you change one or more of the values and want to update the total.

### sort - sort on column

    sort [a|b|c|...] 

`sort` sorts the table on the given column.  `a` is the first, `b` the second, etc.
If you use upper case letters, `A`, `B`, etc the sort direction is reversed.
An index beyond the last column is automatically adjusted so `sort z` sorts on the last column
assuming you have fewer than 26 columns).

You can sort on a sequence of columns by just giving a longer string.
So `sort abc` is the same as `sort c sort b sort a` (but slightly quicker).

The default is to sort by all columns from right to left.

### uniq - filter out duplicated rows

    uniq [a|b|c|...]

`uniq` removes duplicate rows from the table.  With no argument the first
column is used as the key.  But if you provide a list of columns the key will
consist of the values in those columns.  So `uniq af` will remove all rows with
duplicate values in column `a` and `f`, so that you are left with just the rows
where the values in these columns are distinct.

### filter - select rows where "expression" is True

    filter [expression]

In long tables it is sometimes useful to pick out only some of the rows.  You can do this 
with `filter`.   Say you have a table of rainfall data like this:

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

and you want only to keep the rows where the Total value is greater than 10, then you
can try `filter j>10` to get

    Monday      Week  Mon  Tue   Wed  Thu  Fri   Sat   Sun  Total
    2020-01-13     3  5.3  1.7   9.1  3.0  1.7   0.0   0.0   20.8
    2020-01-27     5  8.4  2.1   0.0  0.5  1.0   0.0   7.1   19.1
    2020-02-03     6  0.1  0.0   0.0  0.0  0.0   1.5  10.6   12.2
    2020-02-10     7  5.5  0.0   0.5  6.6  0.0   4.9  15.6   33.1
    2020-02-24     9  6.1  0.5   0.1  8.6  5.9   7.1   0.2   28.5
    2020-03-02    10  0.0  0.0   4.3  0.0  3.0  12.4   0.0   19.7
    2020-03-09    11  0.0  4.3   6.3  1.3  1.0   1.0   0.0   13.9
    2020-03-30    14  0.1  0.1  10.9  0.0  0.0   0.0   0.0   11.1

Notice that the header row was included.  If the expression causes an error (in
this case because you can't compare a string to a number) then the row will
always be included.  The expressions should be valid bits of Python and can use
the same subset of built-in and maths functions as the normal row arrangements
with `arr`, and single letters refer to the value of the cells in the way
described for `arr` above.  Again like `arr` you can use the variables `rows`
and `row_number` in the expression: `rows` is the count of rows in your table, and 
`row_number` starts at 1 and is incremented by 1 on successive rows.
You could use this to pick out every other row: `filter row_number % 2`. 
(If you are calling tabulate from the Vim command line, use `row_number \% 2`.)

The default is to do nothing.  


### arr - rearrange the columns

    arr [arrange-expression] 

At it simplest `arr` lets you rearrange, duplicate, or delete columns.  So if you have a
four column table then:

- `arr dabc` puts the fourth column first
- `arr aabcd` duplicates the first column
- `arr cd` deletes the first two columns
- `arr abc` keeps only the first three columns

and so on.  If you want to keep everything and simply add an extra column at
the end, there's a shortcut to save you typing lots of column letters: `arr
~a` will keep *all* the columns and then add a copy of the first one
on the end.  If you want to do more complicated things with lots of columns,
you might find it easier to transpose the table first with `xp` and then use
the regular line editing facilities in Vim to rearrange the rows, before
transposing them back to columns.   You might also use the `label` verb to add
alphabetic labels to the bottom of all the columns before you start.

Note: Astute readers may spot a problem here.  The sequence `arr add` meaning
`delete cols b and c and duplicate col d` won't work because `add` is a
valid verb.  In this case (as similar ones) just put a pair of empty braces
on the end, like so `arr add{}`.

Besides letters to identify column values you can use `?` to insert a random number,
and `.` to insert the current row number and `;` to insert the total number of rows.

Note that you should use lower case letters only to refer to each column value.
If you use an upper case letter, `A`, `B`, etc, it will be replaced by the
cumulative sum of the corresponding column, in other words the sum of the
values in the column from the top of the table to the current row. So given

    First   1
    Second  2
    Third   3

`arr abB` gives you,

    First   1  1
    Second  2  3
    Third   3  6

You can also insert arbitrary calculated columns by putting an expression in curly braces or parentheses

- `arr ab(a+b)` adds a new column that contains the sum of the values in the first two

- `arr a(a**2)(sqrt(a))` adds two new cols with square and square root of the value in col 1.

- `arr ~{sqrt(a)}` keeps all existing cols and adds a new col with the square root of the value in col 1.

and so on.  Each single letter `a`, `b`, etc is changed into the corresponding
cell value and then the resulting expression is evaluated. You can use a subset of the
normal built-in or `math` functions; besides all the BIFs you get `log`, `log10`, `exp`
and `sqrt`, as shown above.

Curly braces are only treated as parentheses at the top level (and this only for compatibility
with the old Perl version of tabulate), so you can put them in normal Python expressions like

    arr ab('{} {}'.format(c, d))

which (incidentally) shows one way to concatenate two columns into one.  You can include
spaces in your formula;  The argument to `arr` ends at the next operation or the end
of the command line.  The access to Python in (more or less) entirely general, but is
only really intended for simple manipulation of a few values, so don't expect too much.
But (assuming you are using Python 3.6 or better by now) you could also write the above
example as

    arr ab(f"{c} {d}")

which you might find more convenient.

You can also use "?" in a formula to get a random number, but you can't use "."
or ";" because it makes a mess of the parsing.  If you want the current row
number or the total number of rows use the pre-defined variables `row_number`
and `rows` in your formula. So with the simple table from above, 
`arr ~(f'{row_number}/{rows}')` should produce this:

    First   1  1  1/3
    Second  2  3  2/3
    Third   3  6  3/3

There are also some simple date routines included.  `base` returns the number
of days since 1 Jan in the year 1 (assuming the Gregorian calendar extended
backwards).  The argument should be blank for today, or some recognisable form
of a date.  `date` does the opposite: given a number that represents the number
of days since the year dot, it returns the date in `yyyy-mm-dd` form.  There's
also `dow` which takes a date and returns the day of the week, as a three
letter string.

So given a table with a column of dates, like this

    2011-01-17
    2011-02-23
    2011-03-19
    2011-07-05

The command `arr a{dow(a)}` creates this

    2011-01-17  Mon
    2011-02-23  Wed
    2011-03-19  Sat
    2011-07-05  Tue

Alternatively `arr a{base()-base(a)}` will produce the days from each date to today.

    2011-01-17  3413
    2011-02-23  3376
    2011-03-19  3352
    2011-07-05  3244

And `arr a{date(base(a)+140)}` will add 20 weeks to each date

    2011-01-17  2011-06-06
    2011-02-23  2011-07-13
    2011-03-19  2011-08-06

As a convenience, if the number given to `date()` is less than 1000, then it's
assumed that you mean a delta on today rather than a day in the pre-Christian
era.  So `date(70)` will produce the date in 10 weeks time, and `date(-91)`
will give you the date three months ago, and so on.  `date()` produces today's
date.  If the number you give date is large, it will be interpreted as epoch
seconds, and if it is very large, epoch milliseconds.

Note: `base()` will actually recognize dates in several different (mainly ISO or British) forms
as well as `yyyy-mm-dd`, as follows:

    Example                   strftime format used
    ----------------------------------------------
    2020-12-25                %Y-%m-%d
    20201225                  %Y%m%d
    2020-W52-5                %G-W%V-%u
    Fri Dec 25 12:34:56 2020  %c
    12/25/20                  %x
    25 December 2020          %d %B %Y
    25 Dec 2020               %d %b %Y
    25 Dec 20                 %d %b %y
    25 December 20            %d %B %y
    25/12/2020                %d/%m/%Y
    25/12/20                  %d/%m/%y
    Fri                       %a
    Friday                    %A

This table shows the strftime formats used.  This is not as clever as using
`dateutil.parser` but it does mean that tabulate only uses the standard Python3
libraries.

There are also useful functions to convert HH:MM:SS to fractional hours, minutes or seconds.
`hms()` takes fractional hours and produces `hh:mm:ss`, while `hr`, `mins`, and `secs` go the other way.

### tap - apply a function to each numerical value

    tap [x-expression]

This is useful for adjusting all the numeric values in your table at once,
perhaps for making byte values into megabytes etc.  Given values with headings like this

    Category  Type A  Type B
    ------------------------
    First         34      21
    Second        58      72

`tap +1000` will produce

    Category  Type A  Type B
    ------------------------
    First       1034    1021
    Second      1058    1072

and then `tap log(x)` produces

    Category         Type A         Type B
    --------------------------------------
    First     6.94119005507  6.92853781816
    Second    6.96413561242  6.97728134163

if you omit `x` from your "x-expression", it will be added to the front, this means the default is to
replace each cell by itself.  If your expression is not valid Python or includes undefined names, the cells 
will be unchanged.

### dp - round numbers to n decimal places

    dp [nnnnn...]

As delivered, tabulate calculates with 12 decimal places, so you might need to round your answers a bit.
This is what `dp` does.  The required argument is a string of digits indicating how many decimal places
between 0 and 9 you want for each column.  There's no default, it just does nothing with no argument, but
if your string is too short the last digit is repeated as necessary.  So to round everything to a whole number
do `dp 0`.  To round the first col to 0, the second to 3 and the rest to 4 do `dp 034`, and so on.
Cells that contain values that are not numbers are not changed, so applying `dp 4` to a table like this:

    Category         Type A         Type B
    --------------------------------------
    First     6.94119005507  6.92853781816
    Second    6.96413561242  6.97728134163

should produce

    Category  Type A  Type B
    ------------------------
    First     6.9412  6.9285
    Second    6.9641  6.9773


### make - set the output format

    make [plain|pipe|tex|latex|csv|tsv]

`make` sets the output format. 

- `plain` is the default, where each cell is separate by two or more spaces, and there is no EOL mark
- `pipe` will attempt to make a markdown table
- `tex` will use `&` to separate the cells and put `\cr` at the end
- `latex` is the same except the EOL is `\\`

Note that these last two only affect the rows, tabulate won't magically generate the TeX or LaTeX table preamble.

The `make csv` option should produce something that you can easily import into Excel
or similar spreadsheets.  The output is produced with the standard Python CSV writer,
so double quotes will be added around cell values where needed.  

The `make tsv` option can be used when you want to import into Word -- you can
use Table... Convert Text to Table...  using tabs as the column separator.

### pivot - expand or condense data tables for R

    pivot [long|wide]

This is used to take a square table and make it a long one.  It's best explained with an example.

Consider the following table.

    Exposure category     Lung cancer  No lung cancer
    -------------------------------------------------
    Asbestos exposure               6              51
    No asbestos exposure           52             941

Nice and compact, but the values are in a 2x2 matrix rather than a useful column.  Sometimes you want
them to look like this, where each column is a variable and each row is an observation.

    Exposure category     Name            Value
    -------------------------------------------
    Asbestos exposure     Lung cancer         6
    Asbestos exposure     No lung cancer     51
    No asbestos exposure  Lung cancer        52
    No asbestos exposure  No lung cancer    941

And that's what `pivot long` does.  Here's another example.

    Region  Quarter  Sales
    ----------------------
    East    Q1        1200
    East    Q2        1100
    East    Q3        1500
    East    Q4        2200
    West    Q1        2200
    West    Q2        2500
    West    Q3        1990
    West    Q4        2600

With this input, `pivot wide` gives you this

    Region    Q1    Q2    Q3    Q4
    ------------------------------
    East    1200  1100  1500  2200
    West    2200  2500  1990  2600

Notice that parts of the headings may get lost in transposition.
Notice also that you *need* a heading so some sort, otherwise `pivot wide` will
mangle the first row of your data.  So you might like to use `label` before `pivot`.

The `pivot wide` function assumes that the right hand column contains numeric values 
and the second-from-the-right column contains the names you want as new column headings.
Any non-numeric value in the values column is treated as 0.  If you have duplicate names
in the names column then the corresponding values will be added together.

### wrap and unwrap - reshape table in blocks

    wrap [n] 
    unwrap [n]

Here is another way to reshape a table.  Given

    East  Q1  1200
    East  Q2  1100
    East  Q3  1500
    East  Q4  2200
    West  Q1  2200
    West  Q2  2500
    West  Q3  1990
    West  Q4  2600

as input, `wrap` gives you

    East  Q1  1200  West  Q1  2200
    East  Q2  1100  West  Q2  2500
    East  Q3  1500  West  Q3  1990
    East  Q4  2200  West  Q4  2600

while `wrap 3` gives

    East  Q1  1200  East  Q4  2200  West  Q3  1990
    East  Q2  1100  West  Q1  2200  West  Q4  2600
    East  Q3  1500  West  Q2  2500

`unwrap` does the opposite - the option is the number of columns you want in the new output, and defaults
to half the number of columns in the input.

### zip and unzip - reshape a table by rows
    
    zip [n] 
    unzip [n]

Re-shape a table row by row.  Given

    Q1  East  1200
    Q1  West  2200
    Q2  East  1100
    Q2  West  2500
    Q3  East  1500
    Q3  West  1990
    Q4  East  2200
    Q4  West  2600

as input, `zip` gives you

    Q1  East  1200  Q1  West  2200
    Q2  East  1100  Q2  West  2500
    Q3  East  1500  Q3  West  1990
    Q4  East  2200  Q4  West  2600

`unzip` does the opposite.  The option is the number of rows to combine.  The default is 2, so that
you zip every other row, and unzip the table in half (as it were).

### normalize - adjust values so that they sum to one

    normalize [table] 

Given this table

    Exposure category     Lung cancer  No lung cancer
    -------------------------------------------------
    Asbestos exposure               6              51
    No asbestos exposure           52             941

`normalize` produces this

    Exposure category         Lung cancer  No lung cancer
    -----------------------------------------------------
    Asbestos exposure      0.105263157895  0.894736842105
    No asbestos exposure  0.0523665659617  0.947633434038

Each value has been divided by the row total so that each row now adds to 1.
You can combine this with other functions to get percentages or neater values.
For example, with the original table you could do `normalize tap *100 dp 1` to get   

    Exposure category     Lung cancer  No lung cancer
    -------------------------------------------------
    Asbestos exposure            10.5            89.5
    No asbestos exposure          5.2            94.8

If you want the whole table to add to 1 then do `normalize table`:

    Exposure category          Lung cancer   No lung cancer
    -------------------------------------------------------
    Asbestos exposure     0.00571428571429  0.0485714285714
    No asbestos exposure   0.0495238095238   0.896190476190

If you want the columns to add to 1 then use `xp normalize xp`:

    Exposure category        Lung cancer   No lung cancer
    -----------------------------------------------------
    Asbestos exposure     0.103448275862  0.0514112903226
    No asbestos exposure  0.896551724138   0.948588709677

(But note that `xp` gets rid of your rules, so I actually did that with
`xp normalize xp rule 1`)

### rule - add a rule

    rule [n]

Adds a rule after line `n` where the top line is line 1.  If `n` is larger than
the number of rows in the table, the rule will be added after the last line, however it will not get 
shown when the table is tabulated unless you have added more data by then.
To add a line just before the last line (to show a total or a footer) use `rule -1`

### label - add alphabetic labels to all the columns

    label [name name ...]

`label` adds labels at the top of each column.  You can supply zero or more
names that you would like to use as single words separated by blanks.  The only
restriction is that you can't use any of the DSL verbs.  If you supply too many
the excess are just ignored, if you don't supply enough, then the labels
default to single letters of the alphabet.  This means that if you don't supply
any names, the columns will be labeled `a`, `b`, `c`, etc which might help you
work out which is which when rearranging.

### gen - generate new rows

`gen a..b` where `a` and `b` are integers, and `..` is any non-numeric character sequence,
will generate a table with a single column of integers running from `a` to `b`.  `gen 10` is
interpreted as `gen 1..10`.

If the table already has some data, then the single column will be appended as new rows at the bottom
of the existing column `a`.

To get more general new rows try `gen` with a pattern like `AB2`, which will produce:

    A  A
    A  B
    B  A
    B  B

or `gen PQR2`

    P  P
    P  Q
    P  R
    Q  P
    Q  Q
    Q  R
    R  P
    R  Q
    R  R

The argument should be a string of letters followed by a single digit.  The
digit controls the number of columns created, and all the required combinations
of letters in the string will be used to generate rows.

### shuffle - rearrange the rows with a Fisher-Yates shuffle.

This is implemented using `random.shuffle`

Here's a one liner to generate a random 4x4 arrangement of the numbers 1 to 16:
(start with a blank file)

    :Table gen 16 shuffle wrap 4

produces (for example):

     5   7   4   9
    13   2   3   8
    15   1   6  16
    12  11  10  14


### roll [col-list] - roll the values in one or more colum

Roll like the stack on an HP RPN calculator.  So with the shuffled table above, `roll b`
would produce this:

     5  11   4   9
    13   7   3   8
    15   2   6  16
    12   1  10  14

Upper case letters roll up, so `roll B` would have produced

     5   2   4   9
    13   1   3   8
    15  11   6  16
    12   7  10  14

As with `sort` you can string column letters together.

One use of this is to calculate the differences between a series of timestamps,
so for example with a list of epoch milliseconds like this, how long was the
gap between each one?

    10099  1534951868290
    10070  1534951868808
    10091  1534951869177
    10085  1534951870335
    10085  1534951873005

You can find that with `arr abb roll c arr ab(b-c)` to get:

    10099  1534951868290  -4715
    10070  1534951868808    518
    10091  1534951869177    369
    10085  1534951870335   1158
    10085  1534951873005   2670

The negative number at the top shows you the difference between
the last and the first. (And hence the new column sums to zero).

### nospace [filler] - remove spaces from cell values

This is useful for the `read.table` function in R, that by default treats all blanks including
single ones as delimiters.  Given this table

    Exposure category     Name            Value
    -------------------------------------------
    Asbestos exposure     Lung cancer         6
    Asbestos exposure     No lung cancer     51
    No asbestos exposure  Lung cancer        52
    No asbestos exposure  No lung cancer    941

`:Table nospace` will produce:

    Exposurecategory    Name          Value
    ---------------------------------------
    Asbestosexposure    Lungcancer        6
    Asbestosexposure    Nolungcancer     51
    Noasbestosexposure  Lungcancer       52
    Noasbestosexposure  Nolungcancer    941

since that's a litte hard to read you can also specify an optional filler character.  `:Table nospace .` would have
produced this:

    Exposure.category     Name            Value
    -------------------------------------------
    Asbestos.exposure     Lung.cancer         6
    Asbestos.exposure     No.lung.cancer     51
    No.asbestos.exposure  Lung.cancer        52
    No.asbestos.exposure  No.lung.cancer    941

so that all spaces are replaced by periods.  Now you can read that into R
without an error.

## Methods available for a Table object

The `Table` class defined by `tabulate` provides the following instance methods.
To use them you need to instantiate a table, then call the methods on that
instance.

    t = tabulate.Table()
    t.parse_lol(data_rows)
    t.do("add")
    print(t)

An instance of a `Table` is essentially an augmented list of lists, so
it implements most of the normal Python list interface, except that you
can't assign to it directly.  Instead you should use one of the two
data parsing methods to insert data.

### `parse_lol(list_of_iterables, append=False, filler='')`

Parse a list of iterables into your table instance.  By default this will
replace any existing values in the instance but if you add `append=True` the
new values will be appended (or rather the old values will not be cleared first).

Note that you can use lists or tuples or strings as the "rows" in the list of iterables.
The "rows" can vary in length, and short ones will be expanded using the optional
filler string, so that they are all the same length. The default filler is an empty string
so quite often you will not notice this expansion.

After this expansion each row in the list of iterables is passed to the `append` method.

### `parse_lines(lines_thing, splitter=re.compile(r'\s\s+'), splits=0, append=False)`

Parse a list of plain text lines into your table instance.  Each line will be split up
using the compiled regular expression passed as the `splitter` argument.  The default pattern is
two or more blanks.  The `splits` argument controls how many splits you want.  The append
argument behaves the same as for `parse_lol`.  If it is false (default) then any data
in the table instance will be cleared first.

This method will recognise rules (any line consisting of only "---" chars), blanks,
and comments (lines with leading '#').

### List like methods

You can use some of the regular list syntax with a Table instance.  So after

    t = tabulate.Table()
    t.parse_lol(list_of_iterables)

you can get the number of rows with `len(t)`, and you can get the first row with `t[0]`
and the last with `t[-1]`, and so on.  A non-integer index, or an index that is too big
will raise the normal list exceptions.  A row will be returned as a list of strings.
(Even the strings that look like numbers will be returned as strings).  You can also
return slices, so `t[::2]` gives you every other row, while `t[:]` gives you a raw copy
of all the data.

#### `append(row, filler='')`

Add a new row to the bottom of the table.  The row should be an iterable as above.

#### `insert(i, row, filler='')`

Insert a new row after line `i`.   Note that both `append` and `insert` maintain
the other properties of the table instance.

#### `pop(n=None)`

Remove row `n` (or the last one if `n` is `None`).  The row will be returned as a
list of strings.

#### `clear()`

Remove all the rows of data from your table instance.

### `column(i)`

Get a column from the table.  The data is returned as a list of 2-tuples.
Each tuple is either:

- True, followed by a numeric value as a Decimal object
- False, followed by a string that does not look like a number

So (for example) you could get the total of the numbers in column 2 of your
table like this

    sum(x[1] for x in t.column(2) if x[0])

### `do(agenda)`

Apply a sequence of DSL verbs and options to the contents of the table.
The verbs are described above.  Separate each verb and option by one or more blanks.

### `add_blank(n=None)`

Add a special blank line after row `n`, or at the end if `n` is None

### `add_rule(n=None)`

Add a special rule line after row `n` or at the end if `n` is None

### `add_comment(contents)`

Add a special comment line after row `n` or at the end if `n` is None

### `tabulate()`

Return a generator object, that will yield a tabulated string for each row in the table.
You can print your table neatly like this:

    for r in t.tabulate():
        print(r)

or perhaps

    print("\n".join(t.tabulate()))

except that you don't need to do that because the Table objects implement the magic printing
interface, so that all you have to do is

    print(t)

and `t.tabulate()` will be called automatically.  The `tabulate` method will use the current settings
for separators, so if you have done `t.do('make csv')` you will get lines of values with commas.
