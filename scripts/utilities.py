from __future__ import absolute_import, print_function
import math

import numpy as np

def round_to_significant(num, sig_figs):
    """Return (rounded_num, format_precision).

    rounded_num is num rounded to sig_figs significant figures.
    format_precision is the number of digits to format after the decimal.
    """
    sig_digit = int(math.floor(math.log10(abs(num))))
    sig_digit -= sig_figs - 1
    prec = -sig_digit if sig_digit < 0 else 0
    return round(num, -sig_digit), prec


def round_as_string(num, sig_figs=3, decimal_zeroes=False):
    """Return num as a string, rounded to sig_figs significant figures.

    If decimal zeros is False, trailing zeros after the decimal are removed.
    """
    rounded, fmtprecision = round_to_significant(num, sig_figs)
    s = '{{0:.{0}f}}'.format(fmtprecision).format(rounded)
    # Strip trailing zeros, and the decimal point if needed
    if not decimal_zeroes and '.' in s:
        while s[-1] == '0':
            s = s[:-1]
        if s[-1] == '.':
            s = s[:-1]
    return s


def double_buffer_to_list(buf, N):
    """Return a Python list from a C++ double array buffer of length N."""
    buf.SetSize(N)
    return np.array(buf, copy=True)


def as_list(x, length=1):
    """Return x if it is a list, else return x wrapped in a list."""
    if not isinstance(x, list):
        x = length*[x]
    return x
