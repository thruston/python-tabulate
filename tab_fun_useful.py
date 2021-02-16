#! /usr/bin/env python3

def t_sorted(*args, reverse=False):
    '''sorted, allowing list of args or a single iterable
    and returning a tuple not a list

    >>> t_sorted((3,1,2))
    (1, 2, 3)

    >>> t_sorted(3,4,5,1,0)
    (0, 1, 3, 4, 5)

    >>> t_sorted(3,4,5,1,0, reverse=True)
    (5, 4, 3, 1, 0)

    '''
    try:
        it = iter(*args)
    except TypeError:
        return tuple(sorted(args, reverse=reverse))
    else:
        return tuple(sorted(it, reverse=reverse))
