#!/bin/sh
# Copy output plots from output/ to correct thesis location

INPUT=./output
OUTPUT=../figures

cp $INPUT/D0ToKpi_mass.pdf $OUTPUT/production/selection/
cp $INPUT/D0ToKpi_mass_offline_selection.pdf $OUTPUT/production/selection/
cp $INPUT/D0ToKpi_mass_offline_selection_regions.pdf $OUTPUT/production/fitting/
cp $INPUT/DpToKpipi_mass.pdf $OUTPUT/production/selection/
cp $INPUT/DpToKpipi_mass_offline_selection.pdf $OUTPUT/production/selection/
cp $INPUT/DpToKpipi_mass_offline_selection_regions.pdf $OUTPUT/production/fitting/
cp $INPUT/DsToKKpi_mass.pdf $OUTPUT/production/selection/
cp $INPUT/DsToKKpi_mass_offline_selection.pdf $OUTPUT/production/selection/
cp $INPUT/DsToKKpi_mass_offline_selection_regions.pdf $OUTPUT/production/fitting/
cp $INPUT/DstToD0pi_D0ToKpi_mass.pdf $OUTPUT/production/selection/
cp $INPUT/DstToD0pi_D0ToKpi_mass_offline_selection.pdf $OUTPUT/production/selection/
cp $INPUT/DstToD0pi_D0ToKpi_delta_mass_offline_selection_regions.pdf $OUTPUT/production/fitting/

cp $INPUT/D0ToKpi_BKGCAT{,_fit}.pdf $OUTPUT/production/efficiencies/
cp $INPUT/DpToKpipi_BKGCAT{,_fit}.pdf $OUTPUT/production/efficiencies/

cp $INPUT/D0ToKpi_MC_PT.pdf $OUTPUT/production/data/
cp $INPUT/D0ToKpi_MC_Y.pdf $OUTPUT/production/data/

cp $INPUT/tracking_correction_table.pdf $OUTPUT/production/efficiencies/

cp $INPUT/D0ToKpi_{mass,ipchisq}_fit_*.pdf $OUTPUT/production/fitting/
cp $INPUT/DpToKpipi_{mass,ipchisq}_fit_*.pdf $OUTPUT/production/fitting/
cp $INPUT/DsToKKpi_{mass,ipchisq}_fit_*.pdf $OUTPUT/production/fitting/
cp $INPUT/DstToD0pi_D0ToKpi_{mass,delta_mass,ipchisq}_fit_*.pdf $OUTPUT/production/fitting/
