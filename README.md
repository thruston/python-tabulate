Tabulate
--------

Line up tabular material neatly.

An exportable module that will line up tabular material automatically saving
you hours of time faffing about with format and alignment.  As a script it
provides a filter with a simple DSL that can be used to make and manipulate
tables in editors that support external filters, as Vim does.

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
text (on Slack for example), and I often find myself loading the output into
Vim just so I can tidy it up with tabulate.  So I have re-written the original
Perl version of tabulate as a Python module that can be imported, and used to
tidy up a list of lists of data for printing.

Toby Thurston -- 4 Jun 2020

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

## Verbs in the DSL

    xp               transpose rows and cells
    sort [col]       sort by value of columns in the order given, use UPPERCASE to reverse
    uniq [col]
    add [function]   add sum, mean, var, sd etc to foot of column
    arr col-list     rearrange/insert/delete cols and/or do calculations on column values.
    dp dp-list       round numbers in each col to specified decimal places
    sf sf-list       round numbers in each col to specified significant figures
    make tex | latex | plain | csv | tsv | md   output in tex etc form
    wrap n           wrap columns in long table n times (default=2)
    unwrap n         unwrap cols in wide table (default=half number of cols)
    zip n            zip n rows together
    unzip n          unzip into n * the current number of rows & 1/n columns.
    pivot wide|long  reshape, tidyr, melt/cast, simple tables
    roll [col]

You can string together as many verbs (plus optional arguments) as you like.

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

### add [sum|mean|...] - insert the sum|mean|etc at the bottom of a column

`add` adds the total to the foot of a column.  The default option is `sum`, but
it can be any method from the Python3 `statistics` library: `mean`, `median`,
`mode`, `stdev`, `variance`, and so on.  Non-numerical entries in a column are ignored.
A rule is added before the total row.  Given the simple table above `add` produces:

    First   100
    Second  200
    Third   300
    -----------
    Total   600


### sort [a|b|c|...] - sort on column a|b|etc

`sort` sorts the table on the given column.  `a` is the first, `b` the second, etc.
If you use upper case letters, `A`, `B`, etc the sort direction is reversed.
An index beyond the last column is automatically adjusted so `sort z` sorts on the last column
assuming you have fewer than 26 columns).

You can sort on a sequence of columns by just giving a longer string.
So `sort abc` is the same as `sort a sort b sort c` (but slightly quicker).

### uniq [a|b|c|...] - filter out duplicated rows

`uniq` removes duplicate rows from the table.  With no argument the first
column is used as the key.  But if you provide a list of columns the key will
consist of the values in those columns.  So `uniq af` will remove all rows with
duplicate values in column `a` and `f`, so that you are left with just the rows
where the values in these columns are distinct.

### arr [arrange-expression] - rearrange the columns

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

You can also insert arbitrary calculated columns by putting an expression in curly braces or parentheses

- `arr ab(a+b)` adds a new column that contains the sum of the values in the first two

- `arr a(a**2)(sqrt(a))` adds two new cols with square and square root of the value in col 1.

- `arr ~{sqrt(a)}` keeps all existing cols and adds a new col with the square root of the value in col 1.

and so on.  Each single letter `a`, `b`, etc is changed into the corresponding
cell value and then the resulting expression is evaluated. You can use most
normal built-in or `math` functions; besides all the BIFs you get `log`, `log10`, `exp`
and `sqrt`, as shown above. If you want any others from `math`, you need to prefix them
with `math`, so use `math.sin`, `math.cos`, etc...

Curly braces are only treated as parens at the top level (and this only for compatibility
with the old Perl version of tabulate), so you can put them in normal Python expressions like

    arr ab('{} {}'.format(c, d))

which (incidentally) shows you how to concatenate two columns into one.  You can include
spaces in your formula.  The argument to `arr` ends at the next operation or the end
of the command line.

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

There are also some very simple date routines included.  `base` returns the number of days
since 1 Jan in the year 1 (assuming the Gregorian calendar extended backwards).  The argument
should be blank for today, or in the form `yyyy-mm-dd`.  `date` does the opposite: given
a number that represents the number of days since the year dot, it returns the date in `yyyy-mm-dd` form.
There's also `dow` which takes a date and returns the day of the week, as a three letter string.

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

As a convenience is the number given to `date()` is less than 1000, then it's
assumed that you mean a delta on today rather than a day in the pre-Christian
era.  So `date(70)` will produce the date in 10 weeks time, and `date(-91)`
will give you the date three months ago, and so on.  `date()` produces today's
date.  If the number you give date is large, it will be interpreted as epoch
seconds, and if it is very large, epoch milliseconds.

Note: `base()` will recognize dates in the form yyyymmdd or yyyy/mm/dd,
etc, or anything that dateutil.parser can read.

### dp [nnnnn...] - round numbers to n decimal places

As delivered tabulate calculates with 12 decimal places, so you might need to round your answers a bit.
This is what `dp` does.  The required argument is a string of digits indicating how many decimal places
between 0 and 9 you want for each column.  There's no default, it just does nothing with no argument, but
if your string is too short the last digit is repeated as necessary.  So to round everything to a whole number
do `dp 0`.  To round the first col to 0, the second to 3 and the rest to 4 do `dp 034`, and so on.

### make [plain|tex|latex|csv|tsv] - set the output format

`make` sets the output format.   Normally this happens automagically, but if, for example, you want to separate
your input data by single spaces, you might find it helpful to do `:Table 1 make plain` to line everything up
with the default two spaces.   Or you might want explicitly to make a plain table into TeX format.

Note that this only affects the rows, it won't magically generate the TeX or LaTeX table preamble.

The CSV option should produce something that you can easily import into Excel
or similar spreadsheets.  However beware that it's not very clever: fields with
commas in will be enclosed with `double quotes`, but my routines are designed
to be simple rather than fool proof.  To get back from CSV form to plain form
do `Table , make plain`, (or just the undo command in Vi).

The TSV option can be used when you want to import into Word -- you can use Table.. Convert Text to Table...
using tabs as the column separator

### pivot [long|wide] - expand or condense data tables for R

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

### wrap [n] | unwrap [n]

Another way to reshape a table.  Given

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

### zip [n] | unzip [n]

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

### label - add alphabetic labels to all the columns

`label` simply adds an alphabetic label at the top of the
columns to help you work out which is which when rearranging.

### gen - generate rows

`gen a..b` where `a` and `b` are integers, and `..` is any non-numeric character sequence,
will generate a table with a single column of integers running from `a` to `b`.  `gen 10` is
interpreted as `gen 1..10`.

If the table already has some data, then the single column will be appended as new rows at the bottom
of the existing column `a`.

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


## Special rows

Any blank lines in your table are saved as special lines and reinserted at the
appropriate place on output. So if you have a long table you can use blanks
to separate blocks of data.  Similarly any lines consisting entirely of `-` characters
are treated as horizontal rules and reinserted (appropriately sized) on output.
Any lines starting with `#` are treated as comment lines, and again reinserted in the
right places on output.

