from __future__ import division
import itertools
import os

import matplotlib.pyplot as plt
import numpy as np
import ROOT

import utilities

PREFIX = 'root://eoslhcb.cern.ch//eos/lhcb/user/a/apearce/CharmProduction/CalibrationFiles/tracking'  # noqa
FNAME = 'Ratio_EM15_GP03.root'


def tracking_table():
    f = ROOT.TFile.Open(os.path.join(PREFIX, FNAME))
    h = f.Get('Ratio')

    xax = h.GetXaxis()
    yax = h.GetYaxis()
    # Convert momentum from GeV to MeV
    xedges = utilities.double_buffer_to_list(xax.GetXbins().GetArray(),
                                             xax.GetNbins() + 1)*1e3
    yedges = utilities.double_buffer_to_list(yax.GetXbins().GetArray(),
                                             yax.GetNbins() + 1)
    nbinsx = xedges.size - 1
    nbinsy = yedges.size - 1
    contents = []
    errors = []
    for y in range(1, 1 + nbinsy):
        row = []
        rowerr = []
        for x in range(1, 1 + nbinsx):
            v = h.GetBinContent(x, y)
            # if v == 0:
            #     row.append(np.nan)
            #     rowerr.append(np.nan)
            # else:
            row.append(h.GetBinContent(x, y))
            rowerr.append(h.GetBinError(x, y))
        contents.append(row)
        errors.append(rowerr)

    contents = np.array(contents)
    errors = np.array(errors)
    # Mask zero factors
    contents = np.ma.masked_where(contents == 0, contents)

    X, Y = np.meshgrid(xedges, yedges)
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(1, 1 ,1)

    image = ax.pcolormesh(X, Y, contents,
                          cmap='YlOrRd', edgecolors='None')

    # Plot correlation value within each cell
    centrex = (xedges[:-1] + xedges[1:])/2
    centrey = (yedges[:-1] + yedges[1:])/2
    for i, j in itertools.product(range(nbinsx), range(nbinsy)):
        x = centrex[i]
        y = centrey[j]
        val = contents[j][i]
        err = errors[j][i]
        if val is np.ma.masked:
            continue

        # Find which of white and black would give the best contrast
        # against the colour of this cell
        # http://stackoverflow.com/a/3943023/596068
        r, g, b, _ = image.to_rgba(val)
        if (r*0.299 + g*0.587 + b*0.114) > 0.729:
            color = '#000000'
        else:
            color = '#ffffff'

        ax.text(x, y,
                r'${0:.2f} \pm {1:.2f}$'.format(float(val), float(err)),
                color=color,
                horizontalalignment='center',
                verticalalignment='center')

    ax.set_xscale('log')
    ax.set_xlabel(r'$p$ [MeV/$c$]')
    ax.set_ylabel(r'$\eta$')
    ax.set_xlim(left=xedges[0], right=xedges[-1])
    ax.set_ylim(bottom=yedges[0], top=yedges[-1])
    fig.colorbar(image, ax=ax, label=r'$\rho_{\mathrm{Tracking}}$')
    fig.savefig('output/tracking_correction_table.pdf')


if __name__ == '__main__':
    tracking_table()
