from __future__ import absolute_import, division, print_function
import math
import os

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import root_pandas
from uncertainties import ufloat

from histograms import histogram
from plotting_utilities import (
    add_si_formatter,
    COLOURS as colours
)

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
PDG_MASS = {
    D0ToKpi: 1864.84,
    DstToD0pi: 2010.26,
    DpToKpipi: 1869.61,
    DsToKKpi: 1968.30
}


def mass_distributions(mode, offline_selection, regions=False):
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
    columns = [mass_name]
    if mode == DstToD0pi:
        columns += ['D0_M', 'Dst_delta_M']
    df = root_pandas.read_root(paths, key=tree, columns=columns)
    # Each mode ntuple has a different name for the parent mass, so normalise
    if mode == DstToD0pi:
        df.columns = ['M', 'DzM', 'DM']
    else:
        df.columns = ['M']

    m_min, m_max = MASS_RANGES[mode]
    # 1 bin per MeV
    nbins = int(m_max - m_min)

    fig, ax = histogram(df.M, range=(m_min, m_max), bins=nbins)

    if regions and mode != DstToD0pi:
        nominal_m = PDG_MASS[mode]
        signal_window = patches.Rectangle(
            (nominal_m - 20, 0), 40, ax.get_ylim()[1],
            facecolor=colours.blue, edgecolor='none', alpha=0.25
        )
        sideband_lo = patches.Rectangle(
            (nominal_m - 60, 0), 20, ax.get_ylim()[1],
            facecolor=colours.red, edgecolor='none', alpha=0.25
        )
        sideband_hi = patches.Rectangle(
            (nominal_m + 40, 0), 20, ax.get_ylim()[1],
            facecolor=colours.red, edgecolor='none', alpha=0.25
        )
        ax.add_patch(signal_window)
        ax.add_patch(sideband_lo)
        ax.add_patch(sideband_hi)

    ax.set_ylabel(r'Candidates / ($1\,\mathrm{MeV}/c^{2}$)')
    ax.set_xlabel(r'$m(' + CHILDREN[mode] + ')$ [$\mathrm{MeV}/c^{2}$]')
    add_si_formatter(ax, xaxis=False)

    figname = '{0}_mass'.format(mode)
    if offline_selection:
        figname += '_offline_selection'
    if regions:
        figname += '_regions'
    fig.savefig('output/{0}.pdf'.format(figname))

    if mode == DstToD0pi:
        nominal_dz = PDG_MASS[D0ToKpi]
        dz_window = ((nominal_dz - 20) < df.DzM) & (df.DzM < (nominal_dz + 20))
        fig, ax = histogram(df.DM[dz_window], range=(139, 155), bins=320)
        ax.set_ylabel(r'Candidates / ($0.05\,\mathrm{MeV}/c^{2}$)')
        ax.set_xlabel((
            r'$m(' + CHILDREN[mode] + r') - m(' + CHILDREN[D0ToKpi] + r')$ '
            r'[$\mathrm{MeV}/c^{2}$]'
        ))
        add_si_formatter(ax, xaxis=False)

        if regions:
            nominal_dm = PDG_MASS[DstToD0pi] - nominal_dz
            signal_window = patches.Rectangle(
                (nominal_dm - 3, 0), 6, ax.get_ylim()[1],
                facecolor=colours.blue, edgecolor='none', alpha=0.25
            )
            sideband_hi = patches.Rectangle(
                (nominal_dm + 4.5, 0), 4.5, ax.get_ylim()[1],
                facecolor=colours.red, edgecolor='none', alpha=0.25
            )
            ax.add_patch(signal_window)
            ax.add_patch(sideband_hi)

        figname = '{0}_delta_mass'.format(mode)
        if offline_selection:
            figname += '_offline_selection'
        if regions:
            figname += '_regions'
        fig.savefig('output/{0}.pdf'.format(figname))

    return df.index.size


MODES = [DstToD0pi]
for mode in MODES:
    nonline = mass_distributions(mode, offline_selection=False)
    noffline = mass_distributions(mode, offline_selection=True)
    mass_distributions(mode, offline_selection=True, regions=True)
    nonline = ufloat(nonline, math.sqrt(nonline))
    noffline = ufloat(noffline, math.sqrt(noffline))
    eff = 100*noffline/nonline
    print(r'\{0} & {1:.0f} \pm {2:.0f} & {3:.0f} \pm {4:.0f} & {5:.3f} \pm {6:.3f} \\'.format(  # noqa
        mode,
        nonline.nominal_value, nonline.std_dev,
        noffline.nominal_value, noffline.std_dev,
        eff.nominal_value, eff.std_dev
    ))
