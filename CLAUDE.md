# SEER prostate cancer — neural computation

This project uses neural computation to investigate the SEER prostate cancer
dataset: grooming, modeling, evaluation, and notes that belong with the cohort
rather than with the neuron engine repo.

The neural computational code lives in:

`~/code/neUROn2++/neuron-3.0`

Run models and scripted sessions from there against the dataset files in
`data/` (for example `data/seer_pc_5yr_data.txt` with its key and inputs files).

## Use neuron first

neuron was developed specifically to support the rigorous modeling and
evaluation this cohort requires. Before proposing an external script,
workaround, or new implementation for dataset splitting, grouping,
cross-validation, model or optimizer selection, locked-test evaluation,
inference, reporting, or run management, first inspect neuron's current
documented contract and, when the exact behavior matters, its implementation.

Prefer neuron's existing capability when it fits the scientific question. If
it does not fit, identify the precise limitation before recommending work
outside the engine. Do not infer neuron's capabilities from memory: the engine
changes, and several facilities were built expressly for this SEER work.

## Model variables are not input nodes

The dataset has **14 conceptual predictor variables encoded as 22 input
nodes**, plus the outcome (15 conceptual variables total). Never describe or
analyze the 22 encoded nodes as 22 independent variables. In particular,
regression and variable selection must keep every categorical predictor
together using the grouping in `data/seer_pc_5yr_inputs.txt`:

```text
0; 1; 2, 3; 4-7; 8; 9; 10-12; 13-15; 16; 17; 18; 19; 20; 21
```

These groups are age, PSA, Gleason, T stage, N stage, M stage,
race/ethnicity, marital status, previous cancer, diagnosis year, poverty,
income, unemployment, and education. Indicator-level coefficients may explain
how a fitted categorical variable behaves, but they do not replace the grouped
test of the conceptual variable.

## Layout

```
data/                  cohort files and the scripts that build them
runs/YYYYMMDDHHMM/     one directory per neuron run, holding that run's artifacts
lab_notebook.md        dated, time-stamped narrative of every run
*.md (top level)       dataset construction and evaluation documentation
```

## `data/` — the dataset directory

Every dataset file and every script that produces one lives in `data/`, so the
project root holds only documentation and run output. Contents:

| File | Role |
|---|---|
| `seer-prostate-5-8-17-formatted.dta` / `.rds` | Full SEER extract, Stata and R (local only, not tracked) |
| `build_five_year_pc_mortality_csv.py` | Rebuilds the modeling CSV from the local `.dta` |
| `audit_five_year_pc_mortality_csv.py` | Independent source-to-output audit |
| `seer_pc_5yr_mortality_2004_2009.csv` | Numeric model-source CSV (identifiers removed) |
| `seer_pc_5yr_audit_index.csv` | Audit trail mapping source rows to output rows |
| `seer_pc_5yr_data.txt` | Neuron-ready headerless matrix |
| `seer_pc_5yr_key.txt` | Column map for the matrix |
| `seer_pc_5yr_inputs.txt` | Stepwise input groupings |

The build and audit scripts take bare relative filenames as their defaults, so
run them from inside `data/`:

```bash
cd data && python3 build_five_year_pc_mortality_csv.py
```

### Git / data

Large native dumps stay local and are not tracked:

- `*.dta` / `*.rds` (source Stata / R copies of the full SEER extract)

Derived CSV/txt products are small enough for GitHub and are tracked so the
modeling cohort can be used without rebuilding from the local dump.

## `lab_notebook.md` — the lab notebook

`lab_notebook.md` is the running record of the modeling work. Its purpose is
reproducibility: an outside observer reading it should be able to recreate any
run without asking us anything.

Rules:

- **Append only.** New entries go at the bottom. Never rewrite or delete an
  earlier entry; if something was wrong, say so in a later entry.
- **Every entry is date- and time-stamped**, with a heading that carries both
  the human-readable date/time and the `YYYYMMDDHHMM` stamp that names the
  run directory, so the notebook entry and `runs/` directory are unambiguously
  paired.
- **Record what was actually done**, not what was intended: the exact neuron
  command line, the data files and their state, the seed, the architecture and
  training parameters, what came out, and what we concluded.
- Runs that fail, crash, or get abandoned are written up too. A notebook that
  only records successes is not a record.

## `runs/` — one directory per run

Neuron writes log files, weight set files, session/script files, exported model
files, and similar artifacts. Each run's output goes into its own subdirectory
of `runs/`, named for when the run started:

```
runs/YYYYMMDDHHMM/
```

where `Y` is year, `M` is month, `D` is day, `H` is hour (24-hour), and `M` is
minute — for example `runs/202608121413/` for a run started 2026-08-12 at 14:13.

Get the stamp from the machine rather than typing it, so the notebook and the
directory cannot drift apart:

```bash
date +%Y%m%d%H%M
```

Guidance:

- Create the directory **before** the run and point neuron's output at it, so
  artifacts land there instead of being swept up afterward.
- One directory per run. Do not reuse a stamp or append a second run's output
  to an existing directory.
- Run artifacts **are** committed. The repo-wide `*.log` ignore rule has an
  explicit `!runs/**/*.log` exception so neuron logs are kept; the log is the
  primary evidence for the run.
- Every run directory has a matching `lab_notebook.md` entry bearing the same
  stamp.
