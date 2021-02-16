import decimal

decimal.DefaultContext.prec = 12

PIC = ''.join('3.1415926535 8979323846 2643383279 5028841971 6939937510 5820974944 5923078164 0628620899 8628034825 3421170679'.split())
PI = 0+decimal.Decimal(PIC)
TAU = PI + PI

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
        return decimal.Decimal('0')
    return x / pi() * 180

def radians(x):
    ''' return degrees -> radians
    >>> radians(90)
    Decimal('1.57079632679')
    >>> radians(0)
    Decimal('0')
    '''
    if not x:
        return decimal.Decimal('0')
    return x * pi() / 180

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
    '''sin in degrees
    >>> sind(30)
    Decimal('0.500000000000')
    '''
    return sin(radians(x))

def cosd(x):
    '''Cos in degrees

    >>> round(cosd(45)**2, 11)
    Decimal('0.50000000000')
    '''
    return cos(radians(x))
    


