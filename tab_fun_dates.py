#! /usr/bin/env python3
'''Date functions to use in tabulate `arr` expressions

Toby Thurston -- 10 Feb 2021

    "dow": tab_fun_dates.dow,
    "base": tab_fun_dates.base,
    "date": tab_fun_dates.date,
    "hms": tab_fun_dates.hms,
    "hr": tab_fun_dates.hr,
    "mins": tab_fun_dates.mins,
    "secs": tab_fun_dates.secs,

'''
import datetime

def parse_date(sss):
    '''Try to parse a date
    >>> parse_date("1 January 2001").isoformat()
    '2001-01-01'
    '''
    for fmt in ('%Y-%m-%d', '%Y%m%d', '%c', '%x', '%d %B %Y', '%d %b %Y', '%G-W%V-%u',
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

    You can actually use this to produce any strftime format...

    >>> dow("25 Dec 2001", "%c")
    'Tue Dec 25 00:00:00 2001'

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
    >>> base() - datetime.date.today().toordinal()
    0
    >>> datetime.date.today().toordinal() - base(-4) 
    4
    '''
    if sss is None:
        return datetime.date.today().toordinal()

    if isinstance(sss, int):
        return datetime.date.today().toordinal() + sss

    try:
        return parse_date(sss).toordinal()
    except (TypeError, ValueError):
        return f'base({sss})'

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
        return ordinal

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
