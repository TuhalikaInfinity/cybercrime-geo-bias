# Geography of Cybercrime Documentation and Geographic Bias in AI

Pilot study code and data. Author: Tuhalika Saha.

## Question
Does an AI system reproduce, amplify or recognize geographic bias in
documented cybercrime, and can it tell absent documentation from
absent events?

## Contents
- cybercrime_geo_bias.ipynb: main Colab notebook (RQ1, RQ2, RQ3)
- rq3_size_check.py: RQ3 county-size control (population table,
  size-matched stratum, comparison)
- figs_ieee.py: regenerates the five figures used in the paper
- data/: input tables and model outputs (see below)
- figures/: the five final figures

## Data
- FBI IC3 annual reports 2023-2025, state tables transcribed by hand:
  data/ic3_complaints_by_state_v2.csv
- UMD Cyber Events Database: NOT included. Download from
  https://cybereventsdatabase.org and save as
  cyber_events_2026-11-10.csv
- US Census ACS 2025 1-year tables B01003 and S2801: data/ACS*.csv
- Census county population estimates, vintage 2025: co-est2025-alldata.csv
  is not included; download it from
  https://www.census.gov/data/tables/time-series/demo/popest/2020s-counties-total.html
  (data/rq3_county_population.csv holds the derived county table)
- Model outputs used in the paper: data/probe_2023_estimates.csv,
  data/probe_rq3.csv, data/probe_rq3_size.csv

## How to run
1. Open cybercrime_geo_bias.ipynb in Google Colab.
2. Upload the data files to the Colab working directory (not into a
   subfolder), plus the UMD and Census files listed above.
3. Add your own Gemini API key in Colab Secrets as GEMINI_API_KEY.
4. Run the cells in order. The model is gemini-3.1-flash-lite.

## Notes
- No API key is included in this repository.
- Model answers can vary between runs and over time, so re-running
  may not reproduce the exact outputs in data/.
- This is a preliminary pilot study: one model, small samples.
