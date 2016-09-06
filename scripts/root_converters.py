"""Convert ROOT objects to numpy arrays, and plot them.

Methods ending in `_data` return numpy arrays, and those that don't end in
`_data` use those that do to draw ROOT objects directly on to matplotlib axes.
"""
import artists
import utilities

import numpy as np


def tgraphasymerrors_data(tgae):
    """Return x, y, xerr_lo, xerr_hi, yerr_lo, yerr_hi from the ROOT object."""
    N = tgae.GetN()
    x = utilities.double_buffer_to_list(tgae.GetX(), N)
    y = utilities.double_buffer_to_list(tgae.GetY(), N)
    xerr_lo = utilities.double_buffer_to_list(tgae.GetEXlow(), N)
    xerr_hi = utilities.double_buffer_to_list(tgae.GetEXhigh(), N)
    yerr_lo = utilities.double_buffer_to_list(tgae.GetEYlow(), N)
    yerr_hi = utilities.double_buffer_to_list(tgae.GetEYhigh(), N)

    return x, y, xerr_lo, xerr_hi, yerr_lo, yerr_hi


def roocurve_data(rc):
    """Return x, y from the ROOT object."""
    axis = rc.GetXaxis()
    xmin = axis.GetXmin()
    xmax = axis.GetXmax()
    # Walk along the curve in steps
    resolution = 1e-3
    step = (xmax - xmin)*resolution
    i = xmin
    x, y = [], []
    while i <= xmax:
        x.append(i)
        y.append(rc.interpolate(i))
        i += step

    return np.array(x), np.array(y)


def tgraphasymerrors(ax, tgae, **kwargs):
    """Plot the TGraphAsymErrors on the matplotlib axis."""
    x, y, xerr_lo, xerr_hi, yerr_lo, yerr_hi = tgraphasymerrors_data(tgae)

    return artists.points(
        ax, x, y, xerr=[xerr_lo, xerr_hi], yerr=[yerr_lo, yerr_hi],
        **kwargs
    )


def roocurve(ax, rc, **kwargs):
    """Plot the RooCurve on the matplotlib axis."""
    x, y = roocurve_data(rc)

    return artists.curve(ax, x, y, **kwargs)


def pull_plot(ax, pdf, data, **kwargs):
    """Plot the error-normalised PDF-data difference on the axis.

    Keyword arguments:
    ax -- matplotlib axis
    pdf -- RooCurve object
    data -- TGraphAsymErrors object
    """
    x, y, xerr_lo, xerr_hi, yerr_lo, yerr_hi = tgraphasymerrors_data(data)
    width = xerr_lo + xerr_hi
    left = x - xerr_lo
    # Be conservative and take the smallest error
    yerr = np.minimum(yerr_lo, yerr_hi)
    ypdf = np.array(map(pdf.interpolate, x))
    pull = (ypdf - y)/yerr

    artists.pulls(ax, left, pull, width, **kwargs)
