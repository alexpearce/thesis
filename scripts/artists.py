"""Plot data with our default styles."""
from plotting_utilities import COLOURS as colours


def curve(ax, x, y, **kwargs):
    """Plot curve of (x, y) points, passing kwargs to ax.errorbar."""
    fill = kwargs.pop('fill', False)
    if fill:
        opts = kwargs
    else:
        opts = dict(fmt='-', linestyle='-', linewidth=4, color=colours.blue)
        opts.update(kwargs)

    if fill:
        return ax.fill_between(x, 0, y, **opts)
    else:
        return ax.errorbar(x, y, **opts)


def points(ax, x, y, xerr, yerr, **kwargs):
    """Plot the (x, y) points with their (lo, hi) errors on the axis."""
    color = kwargs.get('color', colours.black)
    options = dict(
        fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2,
        color=color, markeredgecolor=color,
        # Assume that markers drawn with white should be hidden
        alpha=[1, 0][color == '#ffffff']
    )
    options.update(kwargs)

    return ax.errorbar(x, y, xerr=xerr, yerr=yerr, **options)


def bars(ax, left, value, width, **kwargs):
    """Plot the values as a bar chart on the axis."""
    opts = dict(color=colours.black, edgecolor=colours.black, linewidth=1)
    opts.update(kwargs)

    ax.bar(left, value, width=width, **opts)


def pulls(ax, left, pull, width, **kwargs):
    """Draw the data as a bar chart with +/- 2 sigma lines."""
    bars(ax, left, pull, width, **kwargs)

    # Plot +/- 2 sigma lines; 95% of the data should be within these lines
    ax.plot([left[0], left[-1] + width[-1]], [2, 2], color=colours.red)
    ax.plot([left[0], left[-1] + width[-1]], [-2, -2], color=colours.red)
    ax.set_ylim(-5, 5)
