"""Plot arrays and DataFrames as histograms."""
from __future__ import division

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from plotting_utilities import (
    add_si_formatter,
    COLOURS as colours,
    default_figsize
)
import utilities


def normalisation_factor(hist, edges):
    """Return the normalisation factors for the histogram values.

    Returns an array of length len(hist), such that the integral of the
    histogram of hist*(1/factors) is 1.
    Keyword arguments:
    hist -- Array of histogram values (bin counts)
    edges -- Array of edge values, length of len(hist) + 1
    """
    count = hist.sum()
    width = np.diff(edges)
    return count*width


def freedman_diaconis_bin_width(xs):
    """Return optimal bin width for values according to Freedman-Diaconis."""
    q25, q75 = np.percentile(xs, [25, 75])
    iqr = q75 - q25
    # TODO: is this valid for weighted data? should we use weight.sum() for n?
    return 2*iqr*np.power(xs.size, -1/3)


def freedman_diaconis_nbins(xs, range):
    """Return optimal number of bins for xs plotted in the range (min, max)."""
    bin_width = freedman_diaconis_bin_width(xs)
    try:
        nbins = int(np.diff(range)[0]/bin_width)
    except OverflowError:
        nbins = 10
    return nbins


def binning(xs):
    """Return default ((min x, max x), bins) for values.

    The default range is the extent of the data, i.e. the minimum and maximum
    values. The default bin edges are defined by the Freedman-Diaconis rule,
    see the associated methods. If the FD rule fails for some reason, 20
    equal-width bins are chosen.
    """
    if len(xs) == 0:
        range = (0, 1)
        bins = 1
        return range, bins

    range = np.min(xs), np.max(xs)
    try:
        bins = freedman_diaconis_nbins(xs, range)
    except ValueError:
        # Probably too few entries, so just put something arbitrary in
        bins = 20

    return range, bins


def histogram_values(xs, range, bins, weights=None, density=False):
    # A non-integer number of bins will raise in future numpy versions
    try:
        bins[0]
    except TypeError:
        bins = np.int(bins)
    hist, edges = np.histogram(xs, range=range, bins=bins, weights=weights)

    if density:
        # hist may be a count of integers, needs to be floating point
        hist_prime = hist.astype(edges.dtype)
        norm_factor = normalisation_factor(hist_prime, edges)
    else:
        norm_factor = 1

    return hist, edges, norm_factor


def histogram(xs, range=None, bins=None, weights=None,
              density=False, filled=False, erf=np.sqrt,
              label=None, ax=None):
    """Plot the values as a histogram, show as points with errorbars.

    If multiple xs are given but range or bins are None, the default range
    and/or bins are defined bhy the `binning` method, computing using the first
    array in xs.

    Keyword arguments:
    xs -- Array, or list of arrays, of values
    range -- The range in x within which to plot the values
    bins -- The number of bins N, or an array of N + 1 bin edges, within which
      to partition and count the data
    density -- Normalise the histogram to have unit area if True
    filled -- Draw the histogram as a filled step function if True, else draw
      the bin values as points with errorbars in x as the bin width,
      and error bars in y as computed by the method passed to the `erf`
      kwarg.
    erf -- Method that accepts an array of values (`xs`) and returns an array
      of values that will be used as the y errorbar. The default, np.sqrt,
      assumes the count is Poisson-distributed
    label -- Label to add to the legend for the data. Should be a list of
      labels if xs is a list of values
    ax -- A matplotlib Axis object to draw the histogram on. A new axis will be
      created if None is provided

    Returns:
    (fig, ax) tuple -- Matplotlib Figure and Axis instance. fig is None if
      the ax argument is provided
    """
    # Create a figure and an axis if an axis hasn't been provided
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
    else:
        fig = None

    # Treat list of arrays an a single array consistently
    xs = utilities.as_list(xs)
    weights = utilities.as_list(weights, length=len(xs))
    label = utilities.as_list(label, length=len(xs))

    # Arbitrarily chose the first series to define the default binning
    default_range, default_binning = binning(xs[0])
    if range is None:
        range = default_range
    if bins is None:
        bins = default_binning

    # Keep track of the lowest count so that we can either set it to zero, or
    # to the lowest negative value
    hist_min = 0
    for x, w, l in zip(xs, weights, label):
        hist, edges, norm_factor = histogram_values(
            x, range, bins, weights=w, density=density
        )
        yerr = erf(hist)
        hist = hist/norm_factor
        yerr = yerr/norm_factor
        centres = (edges[:-1] + edges[1:])/2
        bin_widths = np.diff(edges)
        xerr = bin_widths/2.0

        if filled:
            # The prop_cycler is ignored for bar charts in MPL 1.5, see
            # matplotlib/matplotlib#5593 for the fix which will appear in v2.0+
            prop_cycler = ax._get_lines.prop_cycler
            color = next(prop_cycler)['color']
            # Do not draw the edge
            ax.bar(left=edges[:-1], height=hist, width=bin_widths,
                   linewidth=0, color=color, alpha=0.75, label=l)
        else:
            ax.errorbar(centres, hist, yerr, xerr,
                        label=l, fmt='.')

        if hist.min() < hist_min:
            hist_min = hist.min()

    if any(l is not None for l in label):
        ax.legend()

    # Display the number of entries per bin width, if the bin width is the same
    # for all bins
    ylabel = 'Entries'
    mean_width = bin_widths.mean()
    if np.all(np.isclose(bin_widths, mean_width)):
        ylabel += ' / {0}'.format(utilities.round_as_string(bin_widths[0]))
    else:
        ylabel += ' / bin'
    ax.set_ylabel(ylabel)

    # Force the x-axis to respect the binning range
    ax.set_xlim(*range)
    # Force the y-axis to go to zero or below, and add some headroom at the top
    ax_min, ax_max = ax.get_ylim()
    ax.set_ylim(0 if hist_min >= 0 else hist_min, 1.05*ax_max)

    return fig, ax


def histogram_ratio(x1, x2, range=None, bins=None, weights=None,
                    erf=np.sqrt, ax=None):
    """Plot the ratio of the histograms of x1 and x2 arrays.

    Although `weights` can be a list of arrays, first for x1 and then for x2,
    unlike the `histogram` method the `range` and `bins` arguments cannot be
    different for x1 and x2.

    Keyword arguments:
    x1 -- Array of values used as the numerator in the ratio
    x2 -- Array of values used as the denominator in the ratio
    range -- The range in x within which to plot the values
    bins -- The number of bins N, or an array of N + 1 bin edges, within which
      to partition and count the data
    weights -- Number, or array of numbers, which with to weight the values
    erf -- Method that accepts an array of values (`x`) and returns an array
      of values that will be used as the y errorbar. The default, np.sqrt,
      assumes the count is Poisson-distributed
    ax -- A matplotlib Axis object to draw the histogram on. A new axis will be
      created if None is provided

    Returns:
    (fig, ax, chisq, ndof) tuple -- Matplotlib Figure and Axis instance,
      chi^2, and number of degrees of freedom. fig is None if the ax argument
      is provided. The statistics are computed after masking an NaN values from
      the ratio and uncertainties.
    """
    # Create a figure and an axis if an axis hasn't been provided
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
    else:
        fig = None

    weights = utilities.as_list(weights, length=2)

    # Arbitrarily chose the first series to define the default binning
    default_range, default_binning = binning(x1)
    if range is None:
        range = default_range
    if bins is None:
        bins = default_binning

    # weights = 1
    hist1, edges, norm_factor1 = histogram_values(
        x1, range, bins, weights=weights[0], density=True
    )
    hist2, _, norm_factor2 = histogram_values(
        x2, range, bins, weights=weights[1], density=True
    )
    yerr1 = erf(hist1)
    yerr2 = erf(hist2)

    # The edges for each histogram are the same, and this `edges` is the
    # variable defined in the previous loop
    xs = (edges[:-1] + edges[1:])/2
    xerr = (edges[1:] - edges[:-1])/2
    ratio = (hist1/hist2)*(norm_factor2/norm_factor1)
    # Assuming linear error propagation
    yerr = ratio*np.sqrt((yerr1/hist1)**2 + (yerr2/hist2)**2)
    ax.errorbar(xs, ratio, xerr=xerr, yerr=yerr, fmt='o')
    # Draw a red line at y = 1
    ax.plot([edges[0], edges[-1]], [1, 1], color=colours.red)
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylabel('Ratio')
    add_si_formatter(ax)

    mask = ~(np.isnan(ratio) | np.isnan(yerr))
    ratio = ratio[mask]
    yerr = yerr[mask]
    chisq = np.sum(((ratio - 1)/yerr)**2)
    ndof = ratio.size

    return fig, ax, chisq, ndof


def histogram_data(feature, data, label=None, ratio=False, **kwargs):
    """Plot feature from the data.

    Supports at most one of the feature and data arguments being lists, but not
    both simultaneously. If multiple features are defined, the same dataset is
    used to get the values. If multiple datasets are defined, the same feature
    is plotted from each dataset.

    If ratio is true, the ratio axis is returned as well.

    Keyword arguments:
    feature -- Feature object, or list of such objects
    data -- LcTopXX object containing the data, or a list of such objects
    ratio -- Show a ratio between two arrays of values. A ValueError is raised
      if there are more than two arrays of values to be plotted
    kwargs -- Passed to the `histogram` method

    Returns:
    If `ratio` is False:
      (fig, ax_hist) -- Figure, Axis for histogram
    If `ratio` is True:
      (fig, ax_hist, ax_ratio, chisq, ndof) -- Figure, Axis for histogram,
        Axis for ratio, and chi^2 and N_DoF as computed by `histogram_ratio`
    """
    weights = kwargs.pop('weights', None)
    density = kwargs.get('density', False)

    data = utilities.as_list(data)
    feature = utilities.as_list(feature)
    single_data = len(data) == 1
    single_feature = len(feature) == 1
    if not single_data and not single_feature:
        raise ValueError('Cannot have multiple datasets and features')
    if single_data:
        series = [f.from_dataframe(data[0].df) for f in feature]
        # If there's only a single dataset and a single feature, the label of
        # the data should be that of the dataset, as the feature label will be
        # used as the x-axis label
        if label is None and not single_feature:
            label = [f.title for f in feature]
    if single_feature:
        feature = feature[0]
        series = [feature.from_dataframe(d.df) for d in data]
        if label is None:
            label = [r'${0}$'.format(d.mode_latex) for d in data]
    weights = utilities.as_list(weights, length=len(series))

    # We can't compute a meaning x-axis label if there are multiple features
    if single_feature:
        xlabel = feature.title
        if feature.unit is not None:
            xlabel += ' [{0}]'.format(feature.unit)
    else:
        xlabel = ''

    # Taller figure to accomodate the ratio plot
    if ratio and len(series) != 2:
        raise ValueError('Cannot draw a ratio without exactly 2 series')
    if ratio:
        figsize = plt.rcParams['figure.figsize']
        fig = plt.figure(figsize=(figsize[0], 1.25*figsize[1]))
        gs = plt.GridSpec(2, 1, height_ratios=[4, 1])
        ax_ratio = fig.add_subplot(gs[1])
        ax_hist = fig.add_subplot(gs[0], sharex=ax_ratio)

        # Don't show the x-axis labels or exponents
        [xtl.set_visible(False) for xtl in ax_hist.get_xticklabels()]
        ax_hist.get_xaxis().get_offset_text().set_visible(False)
    else:
        fig = plt.figure()
        ax_hist = fig.add_subplot(1, 1, 1)
        ax_hist.set_xlabel(xlabel)

    ax_hist.minorticks_on()
    add_si_formatter(ax_hist)

    histogram(series, weights=weights, ax=ax_hist, label=label, **kwargs)
    ax_hist.legend(loc='best')

    # We're plotting data here, actual particle candidates, so say so in the
    # y-axis label. Say 'arbitrary' for a normalised histogram as the scale
    # doesn't correspond to a count
    count = 'Arbitrary units' if density else 'Candidates'
    ylabel = ax_hist.get_ylabel().replace('Entries', count)
    # Different features may have different units (weird to plot them together
    # in that case, but OK, it can happen)
    if single_feature and feature.unit is not None:
        ylabel += '$\,${0}'.format(feature.unit)
    ax_hist.set_ylabel(ylabel)

    if ratio:
        range = kwargs.get('range', None)
        bins = kwargs.get('bins', None)
        erf = kwargs.get('erf', np.sqrt)
        _, _, chisq, ndof = histogram_ratio(
            *series, range=range, bins=bins, weights=weights, erf=erf,
            ax=ax_ratio
        )
        # Reduce padding between axes
        gs.tight_layout(fig, pad=0.1)
        ax_ratio.set_xlabel(xlabel)
        ax_ratio.set_ylim(0.5, 1.5)

    if ratio:
        return fig, ax_hist, ax_ratio, chisq, ndof
    else:
        return fig, ax_hist


def histogram2d_features(features, data, range=(None, None), bins=(100, 100),
                         weights=None, logz=False):
    assert(len(features) == 2)
    featx, featy = features
    seriesx = featx.from_dataframe(data.df)
    seriesy = featy.from_dataframe(data.df)
    rangex, rangey = range

    # Use the extent of the data if no range is specified
    if rangex is None:
        rangex = (np.min(seriesx), np.max(seriesx))
        padding = 0.05*(rangex[1] - rangex[0])
        rangex = (rangex[0] - padding, rangex[1] + padding)
    if rangey is None:
        rangey = (np.min(seriesy), np.max(seriesy))
        padding = 0.05*(rangey[1] - rangey[0])
        rangey = (rangey[0] - padding, rangey[1] + padding)
    range = (rangex, rangey)

    hist, xedges, yedges = np.histogram2d(seriesx, seriesy,
                                          range=range, bins=bins,
                                          weights=weights)

    xlabel = featx.title
    ylabel = featy.title
    if featx.unit is not None:
        xlabel += ' [{0}]'.format(featx.unit)
    if featy.unit is not None:
        ylabel += ' [{0}]'.format(featy.unit)

    # Widen the default figure size along x to compensate for the colour bar
    figsize = default_figsize()
    fig = plt.figure(figsize=(1.25*figsize[0], figsize[1]))
    ax = fig.add_subplot(1, 1, 1)
    ax.minorticks_on()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    norm = matplotlib.colors.LogNorm() if logz else None
    # The cmin parameter value will mean bin values below 0 won't be coloured
    counts, xedges, yedges, image = ax.hist2d(
        seriesx, seriesy, range=range, bins=bins, weights=weights,
        cmin=1e-7, cmap='viridis', norm=norm
    )
    fig.colorbar(image, ax=ax)
    add_si_formatter(ax)

    return fig, ax
