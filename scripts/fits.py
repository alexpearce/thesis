import os

import matplotlib.pyplot as plt
import ROOT

import artists
from plotting_utilities import (
    add_si_formatter,
    COLOURS as colours,
    set_axis_labels
)
from root_converters import roocurve, roocurve_data, tgraphasymerrors

PREFIX = '~/Physics/CharmProduction/output/{0}/2015/MagDown/fitting'
FNAME = 'fits_two_Step.root'
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
PARENT = {
    D0ToKpi: 'D^{0}',
    DpToKpipi: 'D^{+}',
    DsToKKpi: 'D_{s}^{+}',
    DstToD0pi: 'D^{*+}'
}
CHILDREN = {
    D0ToKpi: 'K^{-}\pi^{+}',
    DpToKpipi: 'K^{-}\pi^{+}\pi^{+}',
    DsToKKpi: 'K^{-}K^{+}\pi^{+}',
    DstToD0pi: 'K^{-}\pi^{+}\pi^{+}_{\mathrm{Soft}}'
}


def mass_fit(mode):
    if mode == DsToKKpi:
        mmode = 'DsTophipi'
    else:
        mmode = mode
    path = os.path.join(PREFIX.format(mmode), FNAME)
    f = ROOT.TFile(path)

    if mode != DstToD0pi:
        parent = mode.split('To')[0]
    else:
        parent = 'D0'
    c = f.Get('Mass/canvas_{0}_{1}_M_pT_bin_integrated_y_bin_integrated_no_pulls'.format(mmode, parent))  # noqa

    it = c.GetListOfPrimitives().MakeIterator()
    primitive = it.Next()
    frame = None
    tgraph = None
    while primitive:
        name = primitive.GetName()
        if 'frame_' in name:
            frame = primitive
        if '#text{data}' in name:
            tgraph = primitive
        primitive = it.Next()

    tcurve_tot = c.GetPrimitive('Fit')
    tcurve_sig = c.GetPrimitive('Sig. + Sec.')
    tcurve_bkg = c.GetPrimitive('Comb. bkg.')

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(1, 1, 1)
    roocurve(ax, tcurve_bkg, color='#6d91cd', linestyle='-', fill=True,
             label='Comb. bkg.')
    roocurve(ax, tcurve_tot, color=colours.blue,
             label='Fit')
    tgraphasymerrors(ax, tgraph, color=colours.black,
                     label=r'${0}$ data'.format(PARENT[mode]))

    ax.set_xlim((frame.GetXaxis().GetXmin(), frame.GetXaxis().GetXmax()))
    # ax.set_ylim(top=1.2*ax.get_ylim()[1])

    # Swap the legend entry order so the data is first
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper left')

    add_si_formatter(ax, xaxis=False)
    if mode == DstToD0pi:
        set_axis_labels(ax, D0ToKpi)
    else:
        set_axis_labels(ax, mode)

    # # 20 MeV below the upper x limit
    # x = ax.get_xlim()[1] - 20
    # # 5% below the upper y limit
    # y = ax.get_ylim()[1]*0.9
    # ax.text(x, y,
    #         'LHCb\n' + r'$\sqrt{s} = 13\,$TeV',
    #         fontsize='24',
    #         horizontalalignment='center',
    #         verticalalignment='center')

    fig.savefig('output/{0}_mass_fit.pdf'.format(mode))


def delta_mass_fit(mode):
    assert(mode == DstToD0pi)
    path = os.path.join(PREFIX.format(mode), FNAME)
    f = ROOT.TFile(path)

    parent = mode.split('To')[0]
    c = f.Get('Delta mass/canvas_{0}_{1}_delta_M_pT_bin_integrated_y_bin_integrated_no_pulls'.format(mode, parent))  # noqa

    it = c.GetListOfPrimitives().MakeIterator()
    primitive = it.Next()
    frame = None
    tgraph = None
    while primitive:
        name = primitive.GetName()
        if 'frame_' in name:
            frame = primitive
        if '#text{data}' in name:
            tgraph = primitive
        primitive = it.Next()

    tcurve_tot = c.GetPrimitive('Fit')
    tcurve_sig = c.GetPrimitive('Sig. + Sec.')
    tcurve_bkg = c.GetPrimitive('Comb. bkg.')

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(1, 1, 1)
    roocurve(ax, tcurve_bkg, color='#6d91cd', linestyle='-', fill=True,
             label='Comb. bkg.')
    roocurve(ax, tcurve_tot, color=colours.blue,
             label='Fit')
    tgraphasymerrors(ax, tgraph, color=colours.black,
                     label=r'${0}$ data'.format(PARENT[mode]))

    ax.set_xlim((frame.GetXaxis().GetXmin(), frame.GetXaxis().GetXmax()))
    # ax.set_ylim(top=1.2*ax.get_ylim()[1])

    # Swap the legend entry order so the data is first
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper right')

    add_si_formatter(ax, xaxis=False)
    ax.set_xlabel((
        r'$m(K^{-}\pi^{+}\pi^{+}_{\mathrm{Soft}}) - '
        r'm(K^{-}\pi^{+})$ [MeV/$c^{2}$]'
    ))
    ax.set_ylabel('Candidates / (0.05 MeV/$c^{2}$)')

    # 2.5 MeV above the lower x limit
    x = ax.get_xlim()[0] + 2.5
    # 5% below the upper y limit
    y = ax.get_ylim()[1]*0.9
    ax.text(x, y,
            'LHCb\n' + r'$\sqrt{s} = 13\,$TeV',
            fontsize='24',
            horizontalalignment='center',
            verticalalignment='center')

    fig.savefig('output/{0}_delta_mass_fit.pdf'.format(mode))


def ipchisq_fit(mode):
    if mode == DsToKKpi:
        mmode = 'DsTophipi'
    else:
        mmode = mode
    path = os.path.join(PREFIX.format(mmode), FNAME)
    f = ROOT.TFile(path)

    if mode != DstToD0pi:
        parent = mode.split('To')[0]
    else:
        parent = 'D0'
    c = f.Get('IP chi^2/canvas_{0}_{1}_log_IPCHI2_OWNPV_pT_bin_integrated_y_bin_integrated_no_pulls'.format(mmode, parent))  # noqa

    it = c.GetListOfPrimitives().MakeIterator()
    primitive = it.Next()
    frame = None
    tgraph = None
    while primitive:
        name = primitive.GetName()
        if 'frame_' in name:
            frame = primitive
        if '#text{data}' in name:
            tgraph = primitive
        primitive = it.Next()

    tcurve_tot = c.GetPrimitive('Fit')
    tcurve_sig = c.GetPrimitive('Signal')
    tcurve_sec = c.GetPrimitive('Secondary')
    tcurve_bkg = c.GetPrimitive('Comb. bkg.')

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(1, 1, 1)
    bkgx, bkgy = roocurve_data(tcurve_bkg)
    secx, secy = roocurve_data(tcurve_sec)
    assert (bkgx == secx).all()
    artists.curve(ax, bkgx, bkgy + secy, color='#9fb9e5', linestyle='-',
                  fill=True, label='Secondary')
    roocurve(ax, tcurve_tot, color=colours.blue,
             label='Fit')
    roocurve(ax, tcurve_bkg, color='#6d91cd', linestyle='-', fill=True,
             label='Comb. bkg.')
    tgraphasymerrors(ax, tgraph, color=colours.black,
                     label=r'${0}$ data'.format(PARENT[mode]))

    ax.set_xlim((frame.GetXaxis().GetXmin(), frame.GetXaxis().GetXmax()))
    # ax.set_ylim(top=1.2*ax.get_ylim()[1])

    # Swap the legend entry order so the data is first
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper right')

    add_si_formatter(ax, xaxis=False)
    ax.set_xlabel(r'$\ln{\chi^{2}_{\mathrm{IP}}}$')
    ax.set_ylabel('Candidates / 0.2')

    # # 3 units above the lower x limit
    # x = ax.get_xlim()[0] + 3
    # # 10% below the upper y limit
    # y = ax.get_ylim()[1]*0.9
    # ax.text(x, y,
    #         'LHCb\n' + r'$\sqrt{s} = 13\,$TeV',
    #         fontsize='24',
    #         horizontalalignment='center',
    #         verticalalignment='center')

    fig.savefig('output/{0}_ipchisq_fit.pdf'.format(mode))


if __name__ == '__main__':
    mass_fit(D0ToKpi)
    mass_fit(DpToKpipi)
    mass_fit(DsToKKpi)
    mass_fit(DstToD0pi)

    delta_mass_fit(DstToD0pi)

    ipchisq_fit(D0ToKpi)
    ipchisq_fit(DpToKpipi)
    ipchisq_fit(DsToKKpi)
    ipchisq_fit(DstToD0pi)
