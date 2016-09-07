from __future__ import absolute_import, division, print_function
import os

import matplotlib.pyplot as plt
import ROOT
import root_pandas

from histograms import histogram
from root_converters import roocurve, tgraphasymerrors
from plotting_utilities import (
    COLOURS as colours,
    set_axis_labels
)

PREFIX = 'root://eoslhcb.cern.ch//eos/lhcb/user/a/apearce/CharmProduction/2015_MagDown_MC/{0}'  # noqa
FNAME = 'DVntuple.root'
DATA_PATHS = [
    os.path.join(PREFIX, str(idx), FNAME)
    for idx in range(1, 3)
]
EVT_TYPES = {
    'D0ToKpi': 27163003,
    'DpToKpipi': 21263010
}


def background_categories(mode):
    """Plot BKGCAT values."""
    tree = 'Tuple{0}/DecayTree'.format(mode)
    parent = mode.split('To')[0]
    columns = [
        '{0}_M'.format(parent),
        '{0}_BKGCAT'.format(parent)
    ]
    paths = [p.format(EVT_TYPES[mode]) for p in DATA_PATHS]
    df = root_pandas.read_root(paths, key=tree, columns=columns)
    df.columns = ['M', 'BKGCAT']

    if mode == 'D0ToKpi':
        mrange = (1800, 1930)
    elif mode == 'DpToKpipi':
        mrange = (1805, 1935)
    nbins = mrange[1] - mrange[0]

    signal = df.M[(df.BKGCAT == 0) | (df.BKGCAT == 10)]
    ghost = df.M[(df.BKGCAT == 60)]
    other = df.M[~((df.BKGCAT == 0) | (df.BKGCAT == 10) | (df.BKGCAT == 60))]
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    histogram([signal, ghost, other], range=mrange, bins=nbins,
              label=['Signal', 'Ghost background', 'Other background'], ax=ax)
    # Don't have the y-axis go to zero, and add some padding at the top
    ax.set_ylim(bottom=0.1, top=2*ax.get_ylim()[1])
    ax.set_yscale('log')
    set_axis_labels(ax, mode)
    ax.legend(loc='best')

    fig.savefig('output/{0}_BKGCAT.pdf'.format(mode))


def fits(mode):
    f = ROOT.TFile('~/Physics/CharmProduction/analysis/{0}_2015_MagDown_truth_matching_fit.root'.format(mode))  # noqa
    w = f.Get('workspace_{0}'.format(mode))

    parent = mode.split('To')[0]
    x = w.var('{0}_M'.format(parent))
    pdf_tot = w.pdf('pdf_m_tot')
    pdf_bkg = w.pdf('pdf_m_tot')
    data = w.data('data_binned')
    frame = x.frame()
    data.plotOn(frame)
    pdf_bkg.plotOn(frame)
    pdf_tot.plotOn(frame, ROOT.RooFit.Components('*bkg*'))

    plotobjs = [frame.getObject(i) for i in range(int(frame.numItems()))]
    tgraph, tcurve_tot, tcurve_bkg = plotobjs

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    roocurve(ax, tcurve_bkg, color=colours.red, linestyle=':',
             label='Background')
    roocurve(ax, tcurve_tot, color=colours.blue,
             label='Total fit')
    tgraphasymerrors(ax, tgraph, color=colours.black, label='MC data')

    ax.set_xlim((frame.GetXaxis().GetXmin(), frame.GetXaxis().GetXmax()))
    ax.set_ylim(top=1.2*ax.get_ylim()[1])

    # Swap the legend entry order so the data is first
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='best')

    set_axis_labels(ax, mode)

    fig.savefig('output/{0}_BKGCAT_fit.pdf'.format(mode))


if __name__ == '__main__':
    # background_categories('D0ToKpi')
    # background_categories('DpToKpipi')
    fits('D0ToKpi')
    fits('DpToKpipi')
