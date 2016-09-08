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


def highest_yield_bin(mode, species):
    """Return (pT, y) index of bin with highest (delta) mass yield."""
    if mode == DsToKKpi:
        mmode = 'DsTophipi'
    else:
        mmode = mode
    path = os.path.join(PREFIX.format(mmode), FNAME)
    f = ROOT.TFile(path)
    if mode == DstToD0pi:
        w = f.Get('workspace_{0}_delta_mass'.format(mmode))
    else:
        w = f.Get('workspace_{0}_mass'.format(mmode))

    parent = mode.split('To')[0]
    pT_idx = '{0}_PT_COM_pT_binning_bin'.format(parent) + '{0}'
    y_idx = '{0}_Y_COM_y_binning_bin'.format(parent) + '{1}'
    vname = 'yield_{0}'.format(species)
    vname += '_{{' + pT_idx + ';' + y_idx + '}}'
    max_val, max_pT, max_y = 0, -1, -1
    for y_bin in range(5):
        for pT_bin in range(15):
            v = w.var(vname.format(pT_bin, y_bin))
            if v.getVal() > max_val:
                max_val = v.getVal()
                max_pT = pT_bin
                max_y = y_bin

    print '{0} max {1} yield: {2:.0f}, bin ({3}, {4})'.format(
        mode, species, max_val, max_pT, max_y
    )
    return max_pT, max_y


def mass_fit(mode, bin=('integrated', 'integrated')):
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
    pT_bin, y_bin = bin
    c = f.Get('Mass/canvas_{0}_{1}_M_pT_bin_{2}_y_bin_{3}'.format(
        mmode, parent, pT_bin, y_bin
    ))
    c = c.GetListOfPrimitives().At(0)

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

    fig.savefig('output/{0}_mass_fit_pT_{1}_y_{2}.pdf'.format(
        mode, pT_bin, y_bin
    ))
    plt.close(fig)


def delta_mass_fit(mode, bin=('integrated', 'integrated')):
    assert(mode == DstToD0pi)
    path = os.path.join(PREFIX.format(mode), FNAME)
    f = ROOT.TFile(path)

    parent = mode.split('To')[0]
    pT_bin, y_bin = bin
    c = f.Get('Delta mass/canvas_{0}_{1}_delta_M_pT_bin_{2}_y_bin_{3}'.format(
        mode, parent, pT_bin, y_bin
    ))
    c = c.GetListOfPrimitives().At(0)

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

    fig.savefig('output/{0}_delta_mass_fit_pT_{1}_y_{2}.pdf'.format(
        mode, pT_bin, y_bin
    ))
    plt.close(fig)


def ipchisq_fit(mode, bin=('integrated', 'integrated')):
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
    pT_bin, y_bin = bin
    c = f.Get('IP chi^2/canvas_{0}_{1}_log_IPCHI2_OWNPV_pT_bin_{2}_y_bin_{3}'.format(  # noqa
        mmode, parent, pT_bin, y_bin
    ))
    c = c.GetListOfPrimitives().At(0)

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

    fig.savefig('output/{0}_ipchisq_fit_pT_{1}_y_{2}.pdf'.format(
        mode, pT_bin, y_bin
    ))
    plt.close(fig)


if __name__ == '__main__':
    for mode in MODES:
        pT_max_sig, y_max_sig = highest_yield_bin(mode, species='sig')
        pT_max_bkg, y_max_bkg = highest_yield_bin(mode, species='bkg')

        mass_fit(mode)
        mass_fit(mode, bin=(pT_max_sig, y_max_sig))
        mass_fit(mode, bin=(pT_max_bkg, y_max_bkg))

        if mode == DstToD0pi:
            delta_mass_fit(mode)
            delta_mass_fit(mode, bin=(pT_max_sig, y_max_sig))
            delta_mass_fit(mode, bin=(pT_max_bkg, y_max_bkg))

        ipchisq_fit(mode)
        ipchisq_fit(mode, bin=(pT_max_sig, y_max_sig))
        ipchisq_fit(mode, bin=(pT_max_bkg, y_max_bkg))
