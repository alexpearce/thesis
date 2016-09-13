import os

import matplotlib.pyplot as plt
import root_pandas

from histograms import histogram
from plotting_utilities import add_si_formatter

PATH = '~/Physics/CharmProduction/output/{0}/2015/MagDown/'
FNAME = 'DVntuple_MC.root'


def com_boost(mode):
    """Plots comparing distributions before and after the CoM boost."""
    tree = 'Tuple{0}/DecayTree'.format(mode)
    parent = mode.split('To')[0]
    columns = [
        '{0}_M'.format(parent),
        # '{0}_MC_ISPROMPT'.format(parent),
        # '{0}_BKGCAT'.format(parent),
        '{0}_PT{{,_COM}}'.format(parent),
        '{0}_Y{{,_COM}}'.format(parent)
    ]
    selection = '&&'.join([
        '{0}_MC_ISPROMPT == 1'.format(parent),
        '{0}_BKGCAT < 20'.format(parent)
    ])
    path = os.path.join(PATH.format(mode), FNAME)
    df = root_pandas.read_root(path, key=tree, columns=columns,
                               where=selection)
    df.columns = ['M', 'PT', 'PT_COM', 'Y', 'Y_COM']

    pt = df.PT/1e3
    pt_com = df.PT_COM/1e3
    pt_range = (0, 15)
    pt_nbins = 60

    y = df.Y
    y_com = df.Y_COM
    y_range = (1.5, 5.5)
    y_nbins = 40

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    histogram([pt, pt_com], range=pt_range, bins=pt_nbins,
              label=[r'Lab.\ frame', '$pp$ CoM frame'], ax=ax)
    add_si_formatter(ax, xaxis=False)
    ax.set_xlabel(r'$D^{0}$ $p_{\mathrm{T}}$ [$\mathrm{GeV}/c^{2}$]')
    ax.set_ylabel(r'Candidates / (0.25 $\mathrm{GeV}/c^{2}$)')
    ax.legend(loc='best')
    fig.savefig('output/{0}_MC_PT.pdf'.format(mode))

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    histogram([y, y_com], range=y_range, bins=y_nbins,
              label=[r'Lab.\ frame', '$pp$ CoM frame'], ax=ax)
    add_si_formatter(ax, xaxis=False)
    ax.set_xlabel(r'$D^{0}$ rapidity')
    ax.set_ylabel(r'Candidates / 0.1')
    ax.legend(loc='best')
    fig.savefig('output/{0}_MC_Y.pdf'.format(mode))


if __name__ == "__main__":
    com_boost('D0ToKpi')
