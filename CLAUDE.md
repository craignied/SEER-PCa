# SEER prostate cancer — neural computation

This project uses neural computation to investigate the SEER prostate cancer
dataset: grooming, modeling, evaluation, and notes that belong with the cohort
rather than with the neuron engine repo.

The neural computational code lives in:

`~/code/neUROn2++/neuron-3.0`

Run models and scripted sessions from there against the dataset files in this
directory (for example `seer_pc_5yr_data.txt` with its key and inputs files).

## Git / data

Large native dumps stay local and are not tracked:

- `*.dta` / `*.rds` (source Stata / R copies of the full SEER extract)

Derived CSV/txt products are small enough for GitHub and are tracked so the
modeling cohort can be used without rebuilding from the local dump.
