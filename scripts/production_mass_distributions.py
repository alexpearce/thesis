from __future__ import absolute_import, division, print_function
import math
import os

import matplotlib.pyplot as plt
import root_pandas
from uncertainties import ufloat

from histograms import histogram

PREFIX = 'root://eoslhcb.cern.ch//eos/lhcb/user/a/apearce/CharmProduction/2015_MagDown'  # noqa
FNAME = 'DVntuple.root'
DATA_PATHS = [
    os.path.join(PREFIX, str(idx), FNAME)
    for idx in range(0, 93)
    # File 79 only has a DsTopipipi tree
    if idx != 79
]
D0ToKpi = 'D0ToKpi'
DpToKpipi = 'DpToKpipi'
DsToKKpi = 'DsToKKpi'
DstToD0pi = 'DstToD0pi_D0ToKpi'
MODES = [
    D0ToKpi,
    DpToKpipi,
    DsToKKpi,
    DstToD0pi
]
CHILDREN = {
    D0ToKpi: 'K^{-}\pi^{+}',
    DpToKpipi: 'K^{-}\pi^{+}\pi^{+}',
    DsToKKpi: 'K^{-}K^{+}\pi^{+}',
    DstToD0pi: 'K^{-}\pi^{+}\pi^{+}_{\mathrm{Soft}}'
}
MASS_RANGES = {
    D0ToKpi: (1800, 1930),
    DpToKpipi: (1805, 1935),
    DsToKKpi: (1900, 2040),
    DstToD0pi: (1950, 2080)
}


def mass_distributions(mode, offline_selection):
    if mode == 'DsToKKpi':
        mmode = 'DsTophipi'
    else:
        mmode = mode
    if offline_selection:
        paths = ['~/Physics/CharmProduction/output/{0}/2015/MagDown/DVntuple_Real.root'.format(mmode)]  # noqa
        tree = 'Tuple{0}/DecayTree'.format(mmode)
    else:
        paths = DATA_PATHS
        tree = 'Tuple{0}/DecayTree'.format(mode)
        if mode == DstToD0pi:
            paths = [p for p in paths if '67' not in p]
    mass_name = mode.split('To')[0] + '_M'
    df = root_pandas.read_root(paths, key=tree, columns=[mass_name])
    # Each mode ntuple has a different name for the parent mass, so normalise
    df.columns = ['M']

    m_min, m_max = MASS_RANGES[mode]
    # 1 bin per MeV
    nbins = int(m_max - m_min)

    fig, ax = histogram(df.M, range=(m_min, m_max), bins=nbins)
    ax.set_ylabel(r'Candidates / ($1\,\mathrm{MeV}/c^{2}$)')
    ax.set_xlabel(r'$m(' + CHILDREN[mode] + ')$ [$\mathrm{MeV}/c^{2}$]')

    figname = '{0}_mass'.format(mode)
    if offline_selection:
        figname += '_offline_selection'
    fig.savefig('output/{0}.pdf'.format(figname))

    return df.index.size


for mode in MODES:
    nonline = mass_distributions(mode, offline_selection=False)
    noffline = mass_distributions(mode, offline_selection=True)
    nonline = ufloat(nonline, math.sqrt(nonline))
    noffline = ufloat(noffline, math.sqrt(noffline))
    eff = 100*noffline/nonline
    print(r'\{0} & {1:.0f} \pm {2:.0f} & {3:.0f} \pm {4:.0f} & {5:.3f} \pm {6:.3f} \\'.format(  # noqa
        mode,
        nonline.nominal_value, nonline.std_dev,
        noffline.nominal_value, noffline.std_dev,
        eff.nominal_value, eff.std_dev
    ))
