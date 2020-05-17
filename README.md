Tabulate
--------

Line up tabular material neatly.

An exportable module that will line up tabular material automatically 
saving you hours of time faffing about with format and alignment. 
As a script it provides a filter with a simple DSL that can be used to 
make and manipulate tables in editors that support external filters, as Vim does.

Toby Thurston -- 28 Apr 2020

Verbs in the DSL

    xp              transpose rows and cells
    sort [col]      sort by value of columns in the order given, use UPPERCASE to reverse
    add [function]  add sum, mean, var, sd etc to foot of column
    arr col-list    rearrange/insert/delete cols and/or do calculations on column values.
    dp dp-list      round numbers in each col to specified decimal places
    sf sf-list      round numbers in each col to specified significant figures
    make tex | latex | plain | csv | tsv | md   output in tex etc form
    wrap n          wrap columns in long table n times (default=2)
    unwrap n        unwrap cols in wide table (default=half number of cols)
    zip n           zip n rows together
    unzip n         unzip into n * the current number of rows & 1/n columns.

This filter is primarily intended to be used as an assitant for an editor that
allows you to filter a file, or a buffer, or a group of lines through an
external program.  Such as Vim.  The idea is that you create a Vim command that
calls this filter on a marked area in your file which is then replaced with the
(improved) output. It also works as a simple command line filter.  The details
of setting up Vim are explained below.  

This Python version can also be used as an external module so that you can line
up any table of text data.

## Motivation

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
R; you just want the simple totals.   That's what tabulate is for.  Calling ":Table add"
creates this:

   event  eruption  waiting
       1     3.600       79
       2     1.800       54
       3     3.333       74
       4     2.283       62
       5     4.533       85
   ------------------------
      15    15.549      354

OK, that's not perfect, but all you have to do now is change that 15 to "Total" (or just
undo the last change to get rid of the new line or whatever).

Tabulate also lets you transpose a table (to get this...)

    event         1      2      3      4      5
    eruption  3.600  1.800  3.333  2.283  4.533
    waiting      79     54     74     62     85

as well as, sort by any column in the table, rearrange the columns, delete columns,
or add new columns computed from the others.  It can't do everything you can do in a
spreadsheet but it can do most of the simple things, and you can use it right in the
middle of your favourite editor.

## Design

The overall flow is as follows

1. Deal with the command line in a nice flexible way.

2. Read <STDIN> and parse each line into a row of table cells.

3. Update the table according to the verbs given on the command line.

4. Work out the widths and alignments for each column in the finished table.

5. Print the table neatly to <STDOUT>

Note that you don't have to supply any verbs; so in this case step 3 takes no
time at all, and the default action is therefore just to line up your table
neatly.  Text columns are aligned left, numeric columns aligned right.

USAGE
-----

## Use from the command line

You are unlikely to want to do this much, but try something like this

   cat somefile.txt | python3 tabulate.py xp sort xp    # or whatever verbs you want

## Setting up a Table command in Vim

Add a line like the following to your ".vimrc" file.

    :command! -nargs=* -range=% Table <line1>,<line2>!python3 ~/python-tabulate/tabulate.py <q-args>

which you should adjust appropriately so your python can find where you put
tabulate.  You can of course use some word other than "Table" as the command
name. Perhaps "Tbl" ?  Take your pick, you can choose anything, except that Vim
insists on the name starting with an uppercase letter.

With this definition, when you type ":Table" in normal mode in Vim, it will call tabulate
on the current area and replace it with the output.  If you are in Visual Line mode then
the current area will just be the marked lines.  If you are in Normal mode then the current
area will be the whole file.

From now on, I'm assuming you are using a Vim :Table command to access tabulate

## Use from within Vim or GVim or MacVim, etc

    :Table [delimiter] [verb [option]]...

Use blank to separate the command line: the delimiter argument and any verbs or options must be
single blank-separated words.  Any word that looks like a verb will be treated as a verb, even
if you meant it to be an option.  See below for details.

The delimiter is used to split up each input line into cells.  It can be any string or regular
expression that's a valid argument to the perl `split` function.  Except one containing blanks
or a whole number between 0 and 9.  You can't use blanks (even inside quotes) because of the
simple way that I split up the command line, and so I use whole numbers to mean "split on at least
that many consecutive blanks" so if you use 1 as an argument the line will be split on every
blank space, and so on. The default argument is 2.  This means the line will be split at every occurrence
of two or more blanks.  This is generally what you want.  Consider this example.

    Item          Amount
    First label       23
    Second thing      45
    Third one         55
    Total            123

In most circumstances you can just leave the delimiter out and let it default to two or more spaces.
Incidentally, any tab characters in your input are silently converted to double spaces before parsing.

After the optional delimiter you should specify a sequence of verbs.  If the
verb needs an option then that goes right after the verb.  Verbs and options
are separated by blanks.  The parsing is very simple.  If it looks like a verb
it's treated as one.  If it doesn't, it's assumed to be an option.  Anything
coming after an option, but not recognized as a verb, causes an error.  A
message will be written back in the file.  You will probably want to use the
"undo" function after reading it.

DESCRIPTION
-----------

## Verbs

In all the examples below you need to prefix the command with ":Table".  You can string
together as many verbs (plus optional arguments) as you like.

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

### add [sum|mean|median|stdev|variance|...] - insert the sum|mean|etc at the bottom of a column

`add` adds the total to the foot of a column.  The default option is `sum`, but
it can be any method from the Python3 `statistics` library: `mean`, `median`,
`mode`, `stdev`, `variance`, and so on.  Non-numerical entries in a column count 
as zeros.  A rule is added before the total row.  Given the simple table above `add` produces:

    First   100
    Second  200
    Third   300
    -----------
    0       600


### sort [a|b|c|...] - sort on column a|b|etc

`sort` sorts the table on the given column.  "a" is the first, "b" the second, etc.
If you use upper case letters, "A", "B", etc the sort direction is reversed.
An index beyond the last column is automatically adjusted so "sort z" sorts on the last column
assuming you have fewer than 26 columns).

You can only sort on one column at a time, but if you want to sort on column b
then column a, you can do "sort a sort b" to get the desired effect.

### uniq [a|b|c|...] - filter out duplicated rows

`uniq` removes duplicate rows from the table.  With no argument the whole
row is used as the key.  But if you provide a list of columns the key will
consist of the values in those columns.  So "uniq a" will remove all rows with
duplicate values in column "a" and so on...

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
you might find it easier to transpose the table first with "xp" and then use
the regular line editing facilities in Vim to rearrange the rows, before
transposing them back to columns.   You might also use the `label` verb to add
alphabetic labels to the bottom of all the columns before you start.

Note: Astute readers may spot a problem here.  The sequence "arr add" meaning
"delete cols b and c and duplicate col d" won't work because "add" is a
valid verb.  In this case (as similar ones) just put a pair of empty braces
on the end, like so "arr add{}".

Besides letters to identify column values you can use "?" to insert a random number,
and "." to insert the current row number and ";" to insert the total number of rows.

You can also insert arbitrary calculated columns by putting an expression in curly braces or parentheses

- `arr ab(a+b)` adds a new column that contains the sum of the values in the first two

- `arr a(a**2)(sqrt(a))` adds two new cols with square and square root of the value in col 1.

- `arr ~{sqrt(a)}` keeps all existing cols and adds a new col with the square root of the value in col 1.

and so on.  Each single letter "a", "b", etc is changed into the corresponding
cell value and then the resulting expression is evaluated. You can use most
normal built-in or `math` function: sin, cos, atan2, sqrt, log, exp, int, abs, and so on.

You can use operators like "." to concatenate values, but you can't include a
space in your formula because this confuses the command line processing
earlier.  So an extra operator is included: the operator "_" will concatenate
with a space.  Any sequence of more than one letter (like "bad") or any letter
that does not refer to a letter in your table (possibly like "z") will be
treated as a plain string.

Note that you should use lower case letters only to refer to each column value.
If you use an upper case letter, "A", "B", etc, it will be replaced by the
cumulative sum of the corresponding column, in other words the sum of the
values in the column from the top of the table to the current row. So given

    First   1
    Second  2
    Third   3

`arr abB` gives you,

    First   1  1
    Second  2  3
    Third   3  6

You can also refer to the "previous" value of a column, so if you prefix a column
letter with ^ it will pick up the value for that column in the row above.  So `arr ab{^b}`
with the table above gives you

    First   1  1
    Second  2  1
    Third   3  2

Note that the upper case letters also work inside a {curly brace} expression, so you can include them
and the ^-prefix in normal expressions.

There are also some very simple date routines included.  `base` returns the number of days
since 1 Jan in the year 1 (assuming the Gregorian calendar extended backwards).  The argument
should be blank for today, or in the form "yyyy-mm-dd".  `date` does the opposite: given
a number that represents the number of days since the year dot, it returns the date in "yyyy-mm-dd" form.
There's also `dow` which takes a date and returns the day of the week, as a three letter string.

So given a table with a column of dates, like this

    2011-01-17
    2011-02-23
    2011-03-19
    2011-07-05

the command "arr a{dow(a)}" creates this

    2011-01-17  Mon
    2011-02-23  Wed
    2011-03-19  Sat
    2011-07-05  Tue

alternatively "arr a{base()-base(a)}" will produce the days from each date to today.

    2011-01-17  1681
    2011-02-23  1644
    2011-03-19  1620
    2011-07-05  1512

and "arr a{date(base(a)+140)}" will add 20 weeks to each date

    2011-01-17  2011-06-06
    2011-02-23  2011-07-13
    2011-03-19  2011-08-06
    2011-07-05  2011-11-22

As a convenience is the number given to "date()" is less than 1000, then it's assumed that you mean
a delta on today rather than a day in the pre-Christian era.  So "date(70)" will produce the date in 10 weeks time,
and "date(-91)" will give you the date three months ago, and so on.  "date()" produces today's date.

Note: dates will also be recognized in the form yyyymmdd or yyyy/mm/dd, etc.  The exact matching expression is

    \A([12]\d\d\d)\D?([01]\d)\D?([0123]\d)\Z

so you must use 4 digit years, but you can use any non-digit as a separator.  It also means
that you can use dates like 2011-12-32.  You'll find that date(base('2011-12-32')) returns '2012-01-01'.

To get dates in this sorted format (which is the ISO standard by the way), you can use `etos` and `utos`.
`etos` takes European dates in the form dd/mm/yyyy and returns yyyy-mm-dd; `utos` takes US dates in the form mm/dd/yyyy.
Note that they still both expect full year numbers.  There's only so much automation that's worth while.

There's also a `month_number` function that takes a string that looks like a month and returns an appropriate number.


### dp [nnnnn...] - round numbers to n decimal places

As delivered tabulate calculates with 12 decimal places, so you might need to round your answers a bit.
This is what `dp` does.  The required argument is a string of digits indicating how many decimal places
between 0 and 9 you want for each column.  There's no default, it just does nothing with no argument, but
if your string is too short the last digit is repeated as necessary.  So to round everything to a whole number
do "dp 0".  To round the first col to 0, the second to 3 and the rest to 4 do "dp 034", and so on.

### make [plain|tex|latex|csv|tsv] - set the output format

`make` sets the output format.   Normally this happens automagically, but if, for example, you want to separate
your input data by single spaces, you might find it helpful to do ":Table 1 make plain" to line everything up
with the default two spaces.   Or you might want explicitly to make a plain table into TeX format.

Note that this only affects the rows, it won't magically generate the TeX or LaTeX table preamble.

The CSV option should produce something that you can easily import into Excel
or similar spreadsheets.  However beware that it's not very clever: fields with
commas in will be enclosed with "double quotes", but my routines are designed
to be simple rather than fool proof.  To get back from CSV form to plain form
do `Table , make plain`, (or just the undo command in Vi).

The TSV option can be used when you want to import into Word -- you can use Table.. Convert Text to Table...
using tabs as the column separator

### reshape [long|wide] - expand or condense data tables for R

This is used to take a square table and make it a long one.  It's best explained with an example.

Consider the following table.

    Exposure category     Lung cancer  No lung cancer
    Asbestos exposure               6              51
    No asbestos exposure           52             941

Nice and compact, but the values are in a 2x2 matrix rather than a useful column.  Sometimes you want
them to look like this.

    Exposure category     Key             Value
    Asbestos exposure     Lung cancer         6
    Asbestos exposure     No lung cancer     51
    No asbestos exposure  Lung cancer        52
    No asbestos exposure  No lung cancer    941

And that's what "reshape long" does.  Here's another example.

    Region      Quarter     Sales
    East        Q1          1200
    East        Q2          1100
    East        Q3          1500
    East        Q4          2200
    West        Q1          2200
    West        Q2          2500
    West        Q3          1990
    West        Q4          2600

With this input, "reshape wide" gives you this

    Region    Q1    Q2    Q3    Q4
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

as input, "wrap" gives you

    East  Q1  1200  West  Q1  2200
    East  Q2  1100  West  Q2  2500
    East  Q3  1500  West  Q3  1990
    East  Q4  2200  West  Q4  2600

while "wrap 3" gives

    East  Q1  1200  East  Q4  2200  West  Q3  1990
    East  Q2  1100  West  Q1  2200  West  Q4  2600
    East  Q3  1500  West  Q2  2500

"unwrap" does the opposite - the option is the number of columns you want in the new output, and defaults
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

as input, "zip" gives you

    Q1  East  1200  Q1  West  2200
    Q2  East  1100  Q2  West  2500
    Q3  East  1500  Q3  West  1990
    Q4  East  2200  Q4  West  2600

"unzip" does the opposite.  The option is the number of rows to combine.  The default is 2, so that
you zip every other row, and unzip the table in half (as it were).

### label - add alphabetic labels to all the columns

`label` simply adds an alphabetic label at the top of the
columns to help you work out which is which when rearranging.

### gen - generate rows

`gen a..b` where `a` and `b` are integers, and `..` is any non-numeric character sequence,
will generate a table with a single column of integers running from `a` to `b`.  `gen 10` is
interpreted as `gen 1..10`.

If the table already has some data, then the single column will be appended as new rows at the bottom
of the existing column "a".

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

=back

## Special rows

Any blank lines in your table are saved as special lines and reinserted at the
appropriate place on output. So if you have a long table you can use blanks
to separate blocks of data.  Similarly any lines consisting entirely of "-" characters
are treated as horizontal rules and reinserted (appropriately sized) on output.
Any lines starting with "#" are treated as comment lines, and again reinserted in the
right places on output.

## Support for TeX and LaTeX

`tabulate` also supports tables neatly in TeX and LaTeX documents.  To convert
a plain table to TeX format use "make tex".  If you already have a TeX table
then `tabulate` automatically spots the TeX delimiters "&" and "\cr", and puts
them back in when it formats the output. Everything else works as described
above.  If you convert from plain to TeX format, then any horizontal rules will
be converted to the appropriate bit of TeX input to get a neat output rule.
No attempt is made to create a preamble for you.

