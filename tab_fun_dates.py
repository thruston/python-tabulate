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
    >>> parse_date(730486).isoformat()
    '2001-01-01'
    >>> parse_date("1 January 2001").isoformat()
    '2001-01-01'
    >>> parse_date(base("1 January 2001")).isoformat()
    '2001-01-01'
    >>> parse_date("6/7/95").isoformat()
    '1995-07-06'
    >>> parse_date("2022-W47-2").isoformat()
    '2022-11-22'
    >>> parse_date("Fri 1st Apr 2022").isoformat()
    '2022-04-01'
    >>> parse_date("Sat 29th July 2023").isoformat()
    '2023-07-29'
    >>> parse_date("Fri 29th Sept 2023").isoformat()
    '2023-09-29'
    >>> parse_date("Sat 19th Mar 2022").isoformat()
    '2022-03-19'
    '''
    try:
        if 0 < int(sss) < 900000:
            return datetime.date.fromordinal(sss)
    except (TypeError, ValueError) as e:
        pass

    days = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()
    try:
        iso_dow = 1 + days.index(str(sss).capitalize())
    except ValueError:
        pass
    else:
        if 1 <= iso_dow <= 7:
            year, week = datetime.datetime.today().strftime("%G-%V").split("-")
            return datetime.datetime.strptime(f'{year}-W{week}-{iso_dow}', "%G-W%V-%u").date()

    sss = str(sss).replace('Sept ', 'Sep ')

    for fmt in ('%Y-%m-%d', '%Y%m%d', '%d %B %Y', '%d %b %Y', '%G-W%V-%u', '%d-%b-%Y',
                '%d %b %y', '%d %B %y', '%d/%m/%Y', '%d/%m/%y', '%B %d, %Y',
                '%A %d %B %Y',
                '%a %dth %b %Y', '%a %dst %b %Y', '%a %dnd %b %Y', '%a %drd %b %Y',
                '%a %dth %B %Y', '%a %dst %B %Y', '%a %dnd %B %Y', '%a %drd %B %Y',
                '%m/%d/%Y',
                '%c', '%x'):
        try:
            return datetime.datetime.strptime(str(sss), fmt).date()
        except ValueError:
            pass

    raise ValueError


def dow(sss, date_format="%a"):
    '''Is it Friday yet?
    >>> dow("1 January 2001")
    'Mon'
    >>> dow(base("1 January 2001"))
    'Mon'
    >>> dow("31/12/2021")
    'Fri'
    >>> dow("1 January 2001", "%A")
    'Monday'
    >>> dow("date")
    '%a'

    You can actually use this to produce any strftime format...

    >>> dow("25 Dec 2001", "%c")
    'Tue Dec 25 00:00:00 2001'

    '''
    try:
        return parse_date(sss).strftime(date_format)
    except (TypeError, ValueError):
        return date_format


def base(sss=None):
    '''Get today's date as "base" number, or whatever date you give
    >>> base("1 January 2001")
    730486
    >>> base("1 January 1901")
    693961
    >>> base("01/01/01")
    730486
    >>> base("20010102")
    730487
    >>> base(20010102)
    730487
    >>> base("2001-01-03")
    730488
    >>> base("03-jan-2001")
    730488
    >>> base("31 Dec 2000")-base("1 Jan 1901")
    36524
    >>> base() - datetime.date.today().toordinal()
    0
    >>> datetime.date.today().toordinal() - base(-4)
    4
    >>> base('Date')
    'base(Date)'
    '''
    if sss is None:
        return datetime.date.today().toordinal()

    if isinstance(sss, int) and abs(sss) < 1000:
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
    '1970-02-12T07:27:40'
    >>> date(100000000000)
    '5138-11-16T09:46:40'
    >>> date(100000000001)
    '1973-03-03T09:46:40.001000'
    >>> date(10) == (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
    True
    >>> date('ts')
    'date(ts)'
    >>> date(-10000000000000000000000000) == date(0)
    True
    >>> date(-2000) == date(0)
    True
    '''
    try:
        ordinal = int(ordinal)
    except (TypeError, ValueError):
        ordinal = base(ordinal)
        if ordinal.startswith('base'):
            return ordinal.replace('base', 'date')

    if abs(ordinal) < 1000:
        dt = datetime.date.today() + datetime.timedelta(days=ordinal)
    elif ordinal > 100000000000:  # about 5000 AD as an epoch, so assume epoch ms
        dt = datetime.datetime.fromtimestamp(ordinal / 1000)
    elif ordinal > datetime.date.max.toordinal():  # > max date, so assume epoch seconds
        dt = datetime.datetime.fromtimestamp(ordinal)
    else:
        try:
            dt = datetime.date.fromordinal(ordinal)
        except (TypeError, ValueError, OverflowError):
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
    return "{}:{:02d}:{:06.3f}".format(int(hh), int(mm), r * 60)


def hr(hms_word, s=0):
    '''Turn hh:mm:ss.sss into fractional hours

    >>> hr("12:34:56")
    12.582222222222223
    '''
    hours = 0
    for i, p in enumerate(hms_word.split(':')):
        hours += float(p) * 60 ** (s - i)
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


def as_time(time_string):
    '''Turn a possible time into hh:mm

    >>> a = ['12 midnight', '12.00 a.m.', '12:01 am', '1:00a.m.', '9am', '11.00am', '11:59 a.m.']
    >>> a += ['Noon', '12 noon', '12:00 pm', '12:01 p.m.', '1:00pm', '4 p.m.', '11:00p.m.', '11:59 pm', '12:00']
    >>> ' '.join(as_time(x) for x in a)
    '00:00 00:00 00:01 01:00 09:00 11:00 11:59 12:00 12:00 12:00 12:01 13:00 16:00 23:00 23:59 12:00'
    '''
    ts = ''.join(time_string.lower().split()).replace('.', '').replace(':', '')
    if ts in ('noon', '12noon', '12pm', '1200pm'):
        return '12:00'
    if ts in ('midnight', '12midnight', '12am', '1200am'):
        return '00:00'
    if ts.endswith('am'):
        if len(ts) <= 4:
            hh = int(ts[:-2]) % 12
            mm = 0
        else:
            hh = int(ts[:-4]) % 12
            mm = int(ts[-4:-2])
        return f'{hh:02d}:{mm:02d}'
    if ts.endswith('pm'):
        if len(ts) <= 4:
            hh = int(ts[:-2]) % 12 + 12
            mm = 0
        else:
            hh = int(ts[:-4]) % 12 + 12
            mm = int(ts[-4:-2])
        return f'{hh:02d}:{mm:02d}'

    return time_string


def epoch(date_time_string):
    '''Turn date time into epoch secs

    >>> epoch("01/01/1970 00:00")
    '0'
    >>> epoch("2000-12-31 23:59:59")
    '978307199'
    >>> epoch("Thursday")
    'Thursday'
    '''
    for fd in ('%Y-%m-%d', '%d/%m/%Y', '%d-%b-%Y', '%Y%m%d'):
        for ft in ('%H:%M:%S', '%H:%M', '%H%M%S'):
            try:
                dt = datetime.datetime.strptime(date_time_string, f'{fd} {ft}').replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                pass
            else:
                return f'{dt.timestamp():.0f}'
    return date_time_string
