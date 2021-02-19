import decimal

decimal.DefaultContext.prec = 12

PIC = ''.join('3.1415926535 8979323846 2643383279 5028841971 6939937510 5820974944 5923078164 0628620899 8628034825 3421170679'.split())
PI = 0+decimal.Decimal(PIC)
TAU = PI + PI
ONE = decimal.Decimal('1')
ZERO = decimal.Decimal('0')

def adjust(x):
    ''' Reduce x to the range -pi to pi
    
    >>> adjust(7)
    Decimal('0.71681469282')
    >>> adjust(PI)
    Decimal('3.14159265359')
    >>> adjust(-PI)
    Decimal('3.14159265359')

    '''
    x = x % TAU
    if not -PI < x <= PI:
        x -= TAU.copy_sign(x)
    assert -PI < x <= PI
    return x 

def degrees(x):
    '''return radians -> degrees
    >>> degrees(1)
    Decimal('57.2957795131')
    >>> degrees(TAU)
    Decimal('360')
    >>> degrees(0)
    Decimal('0')
    '''
    if not x:
        return ZERO
    return x / PI * 180

def radians(x):
    ''' return degrees -> radians
    >>> radians(90)
    Decimal('1.57079632679')
    >>> radians(0)
    Decimal('0')
    '''
    if not x:
        return decimal.Decimal('0')
    return x * PI / 180

def expand_series(x, s, t):
    '''Used for sin and cos
    '''
    decimal.getcontext().prec += 2
    f = y = s
    x = x*x
    old = y
    n = 0
    while True:
        n += 2
        f = -f * x / (n * (n + t))
        y = y + f
        if y==old:
            break
        old = y
    decimal.getcontext().prec -= 2
    return +y

def sin(x):
    x = adjust(x)
    return expand_series(x, x, 1)

def cos(x):
    x = adjust(x)
    return expand_series(x, 1, -1)

def tan(x):
    x = adjust(x)
    return expand_series(x, x, 1) / expand_series(x, 1, -1)

def sind(x):
    "sin in degrees"
    return sin(x * PI / 180)

def cosd(x):
    "cos in degrees"
    return cos(x * PI / 180)

def tand(x):
    "tan in degrees"
    return tan(x * PI / 180)
    
def pyth_add(a, b):
    "Pythagorean addition"
    return (ONE * a * a + b * b).sqrt()

def si(amount):
    """If amount is a number, add largest possible SI suffix,
    otherwise try to remove the suffix and return a value
    >>> si('10M')
    Decimal('10000000')
    >>> si(12315350)
    '12.315 M'
    >>> si(10)
    '10.000'
    >>> si('.2 k')
    Decimal('200.0')

    """
    sips = ' kMGTPE'
    m = re.match(rf'([-+]?(?:\d+\.\d*|\.\d+|0|[1-9]\d*))\s*([{sips}])\Z', str(amount))
    if m is not None:
        return decimal.Decimal(m.group(1)) * 10 ** (3 * sips.index(m.group(2)))
    try:
        n = decimal.Decimal(amount)
    except decimal.InvalidOperation:
        return amount
    else:
        e = min(int(n.log10()/3), len(sips)-1)
        return '{:7.3f} {}'.format(n / (10 ** (3*e)), sips[e]).strip()
