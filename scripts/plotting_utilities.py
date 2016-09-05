"""Utility classes and methods to help with matplotlib & pandas plotting."""
from collections import namedtuple
import math

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

Palette = namedtuple('Palette', ('black', 'red', 'blue', 'green'))
COLOURS = Palette('#333333', '#c64d50', '#4a71b2', '#52a966')


class SIOrderFormatter(matplotlib.ticker.ScalarFormatter):
    """If an exponent is shown, only show it in multiple-of-3 orders.

    If the normal ScalarFormatter would display 10^5, this shows 10^3.
    If normally 10^11, then use 10^9, etc.
    The reason for this is that multiple-of-3 orders are used for the SI
    prefixes, e.g. 50x10^3 MeV is more common, and more readable, than
    5x10^5 MeV.
    Inspired by https://stackoverflow.com/questions/3677368.
    """
    def _set_orderOfMagnitude(self, range):
        matplotlib.ticker.ScalarFormatter._set_orderOfMagnitude(self, range)
        self.orderOfMagnitude = 3*int(math.floor(self.orderOfMagnitude/3))


class Feature(object):
    """Container class for a feature (variable)."""
    def __init__(self, name, title, unit=None, transform=None):
        """Initialise a Feature object.

        Keyword arguments:
        name -- Name of the feature in a DataFrame
        title -- Display name
        unit -- Physical unit of the feature (default: None)
        transform -- Function to apply to feature when loading from DataFrame
        """
        self.name = name
        self.title = title
        self.unit = unit
        self.transform = transform

    def from_dataframe(self, df):
        if self.transform:
            return self.transform(df[self.name])
        else:
            return df[self.name]

def add_si_formatter(ax):
    fmt = SIOrderFormatter(useOffset=False)
    fmt.set_powerlimits((-3, 3))
    ax.get_xaxis().set_major_formatter(fmt)
    ax.get_yaxis().set_major_formatter(fmt)


def default_figsize():
    """Return the default figure size, as defined by MPL's rcParams"""
    return plt.rcParams['figure.figsize']


def pi_label(a=1, b=1):
    """Return a LaTeX label of a*pi/b."""
    if a == 0:
        return '0'

    sign = '-' if np.sign(a)*np.sign(b) == -1 else ''
    a = np.abs(a)
    b = np.abs(b)
    if a == 1 and b == 1:
        val = r'\pi'
    elif a == 1:
        val = r'\frac{{\pi}}{{{0}}}'.format(b)
    elif b == 1:
        val = r'{0}\pi'.format(a)
    else:
        val = r'\frac{{{0}\pi}}{{{1}}}'.format(a, b)
    return r'${0}{1}$'.format(sign, val)


def pi_axis(ax, fractions):
    """Label Axis with fractions of pi, defined by fraction 2-tuples."""
    values = [a*np.pi/b for a, b in fractions]
    labels = [pi_label(*fraction) for fraction in fractions]
    try:
        ax.set_ticks(values)
        ax.set_ticklabels(labels)
    except AttributeError:
        # AxesSubplot objects have different method names
        ax.set_xticks(values)
        ax.set_xticklabels(labels)
