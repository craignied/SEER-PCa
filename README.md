# SEER-PCa

Cohort construction, notes, and neuron-ready datasets for modeling
**five-year prostate cancer–specific mortality** in SEER (diagnoses 2004–2009).

The modeling question:

> Among men diagnosed with prostate cancer during 2004–2009 who had sufficiently
> complete staging, PSA, Gleason, demographic, and socioeconomic documentation, can
> information available at diagnosis predict death from prostate cancer within five
> years?

## Neural computation

Training and analysis run in **[neuron 3.0](https://github.com/craignied/neuron)**
(`~/code/neUROn2++/neuron-3.0` on the author’s machines). This repo holds the
data and documentation for that work; it is not the engine.

Load the headerless matrix with its key and input grouping, for example:

- `seer_pc_5yr_data.txt`
- `seer_pc_5yr_key.txt`
- `seer_pc_5yr_inputs.txt`

## What’s in the repo

| Path | Role |
|---|---|
| `FIVE_YEAR_PC_MORTALITY_DATASET.md` | Full construction rationale and checksums |
| `MODELING_OUTCOMES.md` | Outcome and cohort design notes |
| `build_five_year_pc_mortality_csv.py` | Rebuild the modeling CSV from the local Stata source |
| `audit_five_year_pc_mortality_csv.py` | Independent source-to-output audit |
| `seer_pc_5yr_mortality_2004_2009.csv` | Numeric model-source CSV (identifiers removed) |
| `seer_pc_5yr_audit_index.csv` | Audit trail (source row / identity mapping) |
| `seer_pc_5yr_data.txt` | Neuron-ready matrix |
| `seer_pc_5yr_key.txt` / `seer_pc_5yr_inputs.txt` | Column map and stepwise input groups |
| `large_cohort_evaluation_notes.md` | Evaluation notes for large-cohort runs |
| `CLAUDE.md` | Short project brief for AI assistants |

## What’s not in the repo

The full SEER extract is **local only** (too large for GitHub, and not needed once
the derived cohort exists):

- `seer-prostate-5-8-17-formatted.dta` (~352 MB)
- `seer-prostate-5-8-17-formatted.rds` (~47 MB)

See `.gitignore`. To rebuild derived files you need the local `.dta` and the
build script’s Python dependencies (`pandas`, `pyreadstat`).

## License / data use

SEER data are subject to SEER and NCI data-use agreements. Do not redistribute
restricted source extracts. The tracked matrices here contain no patient
identifiers; still treat them as research data under your local agreements.
