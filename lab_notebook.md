This is the lab notebook for the SEER prostate cancer dataset neural computational modeling runs. The files associated with the runs themselves are in the runs directory in directories named with the convention YYYYMMDDHHMM, with Y as year, M as month, D as day, H as hour, and M as minute.

Entries are appended at the bottom and never rewritten. Each is stamped with
both a readable date/time and the `YYYYMMDDHHMM` stamp naming its run
directory. An entry records what was actually done — the neuron command line,
the data files, the seed, the architecture and training parameters, the
results, and the conclusion — in enough detail that an outside observer could
recreate the run. Failed and abandoned runs are written up as well.

Entries with no run directory (setup, dataset changes, housekeeping) are
stamped the same way and note that no run was performed.

---

## 2026-08-12 14:13 CDT — 202608121413 — Repository reorganization (no run)

Reorganized the project ahead of the first tracked modeling runs.

- Moved all dataset files and the scripts that build them into `data/`:
  `seer-prostate-5-8-17-formatted.dta`, `seer-prostate-5-8-17-formatted.rds`,
  `seer_pc_5yr_data.txt`, `seer_pc_5yr_key.txt`, `seer_pc_5yr_inputs.txt`,
  `seer_pc_5yr_mortality_2004_2009.csv`, `seer_pc_5yr_audit_index.csv`,
  `build_five_year_pc_mortality_csv.py`, `audit_five_year_pc_mortality_csv.py`.
  The `.dta` and `.rds` extracts remain local-only and untracked.
- Data file contents were not modified; only their paths changed. The build and
  audit scripts default to bare relative filenames and so are now run from
  inside `data/`.
- Established `runs/YYYYMMDDHHMM/` as the home for per-run neuron artifacts, and
  added a `!runs/**/*.log` exception to `.gitignore` so run logs are tracked
  despite the repo-wide `*.log` ignore.
- Documented the `data/`, `lab_notebook.md`, and `runs/` conventions in
  `CLAUDE.md`; updated `README.md` paths to match.

No neuron run was performed, so there is no `runs/202608121413/` directory.

Carried forward: the stray `neuron.log` at the project root predates this
convention and its originating run is not identified in any notebook entry. It
was left in place rather than filed under a guessed timestamp.

---

## 2026-08-12 14:17 CDT — 202608121417 — Deleted the pre-convention root log (no run)

Supersedes the "carried forward" note in the entry above: the stray root
`neuron.log` was deleted rather than kept. It documented a run made before this
notebook existed, so it had no matching entry and no identified stamp, seed, or
parameters — it could not have been tied to a reproducible run. Nothing was
tracked in git, so the deletion changes no committed history.

From here on, neuron logs are written into `runs/YYYYMMDDHHMM/` and committed.
A log at the project root means a run was misconfigured and its output was not
directed at a run directory.

Also expanded `README.md` with a "How runs are recorded" section stating the
run-directory and notebook pairing for outside readers.

No neuron run was performed, so there is no `runs/202608121417/` directory.

---

## 2026-08-12 14:39 CDT — 202608121439 — Aborted grouped logistic baseline

Started the first native neuron evaluation of the five-year prostate-cancer
mortality cohort. The purpose was to establish a logistic-regression baseline
and exercise the county-disjoint locked-test design before undertaking neural
architecture selection.

Run directory: `runs/202608121439/`

Engine:

- Executable: `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron`
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`
- Server command, run from the run directory:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --gui --no-browser`

Data:

- A run-local symbolic link, `seer_pc_5yr_data.txt`, pointed to
  `../../data/seer_pc_5yr_data.txt`, keeping neuron's generated artifacts in
  the run directory without duplicating the 20 MB cohort matrix.
- SHA-256:
  `1de0da6a264beb760bdc183f6dccdee33fefc185f4381e95b9bcbf9c164a58aa`
- Load request:
  `mode=raw&path=seer_pc_5yr_data.txt&inputs=22&outputs=1&discrete=1&fraction=0&seed=42`
- neuron reported 22 inputs, 1 output, and 226,679 loaded exemplars.

Evaluation request:

```text
folds=5
seed=42
maxiter=20000
logistic=1
ldfa=0
qdfa=0
neural=0
group=19,20,21,22
locked_fraction=0.10
independence=cluster
```

The group key uses the four area socioeconomic input columns. Independent
pre-run checking found their exact joint values to have a one-to-one mapping
to the 612 county FIPS codes in the audit index, with no collisions. The
request therefore specified a county-disjoint locked holdout, county-disjoint
development folds, and clustered Obuchowski inference.

Outcome: **aborted; no fold completed and no model result was accepted.** The
request was accepted at 14:40:15 CDT, but the first logistic fold remained in
progress for more than two minutes. The request supplied a 20,000-iteration
safety ceiling but omitted the plateau stopping condition. Because reaching
the ceiling would not constitute convergence, a graceful stop was requested at
14:43:27 CDT. neuron stopped at the next iteration boundary and returned:
`cancelled during 'Logistic'` with 0 of 5 folds complete.

Artifacts retained:

- `neuron.log`
- `neuron_actions.log`
- `seer_pc_5yr_data.txt` (symbolic link to the versioned project dataset)

No `cv_predictions.csv`, `cv_metrics.csv`, `cv_run.json`, or locked-test
predictions were produced because the run was cancelled before a fold
completed.

Conclusion: repeat in a new run directory with the same scientific design and
seed, adding neuron's explicit plateau stopping rule
`autostop_tol=0.0001&autostop_window=100`. This entry records the aborted
attempt; it is not evidence about model performance or the proposed split.

---

## 2026-08-12 14:45 CDT — 202608121445 — County-disjoint logistic baseline

Completed the first native neuron evaluation of the full five-year
prostate-cancer mortality cohort. The purpose was to establish a logistic
baseline and directly test neuron's group-disjoint locked-test design before
spending substantially more computation on neural architecture selection.

Run directory: `runs/202608121445/`

Engine and launch:

- Executable: `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron`
- Version recorded by the run: `neuron 3.0.0-dev`
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`
- The engine repository was clean and `HEAD`, `main`, and `origin/main` all
  named that commit before the run.
- Server command, run from the run directory:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --gui --no-browser`

Data:

- `runs/202608121445/seer_pc_5yr_data.txt` is a symbolic link to
  `../../data/seer_pc_5yr_data.txt`. This caused neuron to place all generated
  artifacts in the run directory while avoiding a duplicate 20 MB matrix.
- Dataset SHA-256:
  `1de0da6a264beb760bdc183f6dccdee33fefc185f4381e95b9bcbf9c164a58aa`
- Load request:
  `mode=raw&path=seer_pc_5yr_data.txt&inputs=22&outputs=1&discrete=1&fraction=0&seed=42`
- neuron loaded 226,679 exemplars with 22 inputs and 1 discrete output: 6,705
  events (2.9579%) and 219,974 non-events. No preliminary load-time test split
  was made; the CV operation owned the locked test.

Exact evaluation request:

```text
folds=5
seed=42
maxiter=20000
autostop_tol=0.0001
autostop_window=100
logistic=1
ldfa=0
qdfa=0
neural=0
group=19,20,21,22
locked_fraction=0.10
independence=cluster
```

This run used binary logistic regression only. `maxiter=20000` was a per-fit
safety ceiling, not an accepted stopping condition. The explicit plateau rule
was the reachable stopping condition. No fold exhausted the ceiling: all five
fits completed and contributed predictions. No neural architecture or neural
optimizer was involved.

Grouping and split rationale:

- Input columns 19–22 are area poverty, median household income,
  unemployment, and less-than-high-school education.
- Before the run, their joint exact values were compared row-for-row with the
  audit index: 612 distinct socioeconomic tuples mapped one-to-one to 612
  county FIPS codes, with no tuple shared by two counties and no county having
  multiple tuples. They therefore served as the county key without adding FIPS
  to the predictor matrix.
- The same key governed the locked holdout and all development folds.
- neuron reported zero group leakage.

Achieved partition:

- Locked test requested: 22,668 rows (10% rounded).
- Locked test achieved: 22,617 rows and 620 events (2.7413%) in 14 counties.
- Development set: 204,062 rows and 6,085 events (2.9819%) in 598 counties.
- Development folds contained 40,811–40,814 rows, 1,216–1,218 events, and
  117–121 counties each.
- Fold imbalance score: 0.001. Largest development county: 7,883 rows.
- No split warnings or procedure failures were reported.

The locked test's county composition was checked by joining its original row
identifiers to `seer_pc_5yr_audit_index.csv` in model-row order:

| FIPS | SEER registry | Rows | Events |
|---:|---:|---:|---:|
| 06037 | 8 | 20,364 | 560 |
| 34039 | 12 | 1,716 | 38 |
| 13137 | 4 | 143 | 6 |
| 13119 | 4 | 62 | 4 |
| 21205 | 7 | 61 | 2 |
| 13027 | 4 | 61 | 1 |
| 22083 | 9 | 55 | 2 |
| 22043 | 9 | 44 | 5 |
| 21229 | 7 | 26 | 0 |
| 22035 | 9 | 26 | 0 |
| 21159 | 7 | 25 | 1 |
| 21237 | 7 | 17 | 0 |
| 49001 | 18 | 15 | 1 |
| 21201 | 7 | 2 | 0 |

FIPS 06037 is Los Angeles County. It supplied 20,364 of 22,617 locked rows
(90.0%) and 560 of 620 locked events (90.3%). Thus the split is technically
county-disjoint and outcome-balanced overall, but the locked test is
overwhelmingly a Los Angeles County test rather than a broadly representative
sample of unseen counties.

Results:

| Fold | Rows | Exact empirical AUC | Binormal AUC | Sensitivity | Specificity |
|---:|---:|---:|---:|---:|---:|
| 0 | 40,813 | 0.914663 | 0.913609 | 0.332786 | 0.994318 |
| 1 | 40,813 | 0.892213 | 0.891587 | 0.285127 | 0.993787 |
| 2 | 40,811 | 0.905253 | 0.904082 | 0.282072 | 0.995151 |
| 3 | 40,814 | 0.899527 | 0.898242 | 0.284893 | 0.994974 |
| 4 | 40,811 | 0.897575 | 0.896250 | 0.279376 | 0.995050 |

- Pooled development out-of-fold exact empirical AUC: 0.901638.
- Mean fold AUC reported in Tier 1: 0.902 ± 0.009. This is descriptive spread
  across dependent folds, not a confidence interval.
- Locked-test exact empirical AUC: 0.880071.
- Clustered Obuchowski 95% confidence interval: 0.866083–0.894059, using the 14
  locked counties as the independent sampling units.
- No procedure contrast was computed because only logistic regression ran.
- Total reported procedure time: 961.881 seconds (about 16.0 minutes).

At neuron's default classification threshold, sensitivity was approximately
0.28–0.33 and specificity approximately 0.994–0.995. Given the 2.96% event
prevalence, these threshold-specific values do not replace discrimination by
AUC and do not establish that the default threshold is clinically appropriate.

Artifacts and SHA-256 hashes:

- `cv_predictions.csv`:
  `44cb460d00c229737150ef8659e3b916d3c8dc7cd47feb272f39d47957d2e9f9`
- `cv_metrics.csv`:
  `99069e427a4348c58e7f524aa1be767db971d252b1452c0f0cbcc4c1ef7dae02`
- `cv_run.json`:
  `624952b0708afada2419cb849f052dc70a5427fdb4f3ea8ba89b02f60776a891`
- `cv_locked_predictions.csv`:
  `4b5a8637556fe2e834ee387f264723034fa01594067b509e56dd42056527fe84`
- `neuron.log` and `neuron_actions.log` retain the engine and REST audit trail.

Conclusion: the run is a valid seeded evaluation of logistic performance on
this particular group-disjoint partition, and it demonstrates that neuron's
native end-to-end grouped workflow operates successfully on the full SEER
cohort. However, the 0.880 locked-test AUC should be described specifically as
performance on a locked sample dominated by Los Angeles County. It should not
be adopted as the final general unseen-county estimate without revisiting the
locked-test sizing or allocation objective. The result exposes a limitation of
the current greedy group holdout under extremely unequal county sizes: excellent
row/event balance can coexist with poor representation across counties and
registries. Do not begin expensive neural selection against this locked split
until that design decision is settled.

---

## 2026-08-12 15:13 CDT — 202608121513 — 20% county-disjoint logistic evaluation

Repeated the successful county-disjoint logistic evaluation with a 20% rather
than 10% locked test. The purpose was to determine whether a larger locked
sample would reduce the extreme geographic concentration observed in run
`202608121445`, without changing neuron's native grouping algorithm.

Run directory: `runs/202608121513/`

Engine and data:

- Executable: `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron`
- Engine version: `neuron 3.0.0-dev`
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`
- Server command, issued from the run directory:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --gui --no-browser`
- `seer_pc_5yr_data.txt` was a run-local symbolic link to
  `../../data/seer_pc_5yr_data.txt`.
- Dataset SHA-256:
  `1de0da6a264beb760bdc183f6dccdee33fefc185f4381e95b9bcbf9c164a58aa`
- Load request:
  `mode=raw&path=seer_pc_5yr_data.txt&inputs=22&outputs=1&discrete=1&fraction=0&seed=42`
- neuron loaded all 226,679 rows, including 6,705 events. No load-time test
  split was made; the CV operation owned the locked holdout.

Exact evaluation request:

```text
folds=5
seed=42
maxiter=20000
autostop_tol=0.0001
autostop_window=100
logistic=1
ldfa=0
qdfa=0
neural=0
group=19,20,21,22
locked_fraction=0.20
independence=cluster
```

The only scientific-design change from run `202608121445` was
`locked_fraction=0.20`. The four grouped inputs retain their previously
verified one-to-one mapping to county FIPS. The 20,000-iteration value remained
a safety ceiling; the explicit plateau criterion was the acceptable stopping
condition. All five folds fitted successfully, with no failures, ceiling
exhaustion, leakage, or warnings.

Achieved partition:

- Locked test requested: 45,336 rows.
- Locked test achieved: 45,239 rows and 1,244 events (2.7507%) in 68 counties
  and 14 SEER registries.
- Development: 181,440 rows and 5,461 events (3.0098%) in 544 counties.
- Development folds contained 36,287–36,289 rows, exactly 1,092 or 1,093
  events, and 104–112 counties each.
- Fold imbalance score: 0.001; largest development county: 7,883 rows; group
  leakage: 0.

The locked allocation was joined by original row number to the audit index.
The largest county and registry contributions were:

| FIPS | Registry | Rows | Events | Locked rows |
|---:|---:|---:|---:|---:|
| 06037 (Los Angeles) | 8 | 20,364 | 560 | 45.01% |
| 09001 | 2 | 3,038 | 68 | 6.72% |
| 15003 | 5 | 2,797 | 85 | 6.18% |
| 49035 | 18 | 2,551 | 56 | 5.64% |
| 13089 | 10 | 2,103 | 62 | 4.65% |
| 53061 | 17 | 2,010 | 49 | 4.44% |
| 34039 | 12 | 1,716 | 38 | 3.79% |
| 34007 | 12 | 1,467 | 39 | 3.24% |

Los Angeles supplied 45.01% of locked rows and 45.02% of locked events. The
five largest counties supplied 68.20% of locked rows. Registry 8, which is Los
Angeles alone in this cohort, likewise supplied 45.01%. Thirteen other
registries were represented; four cohort registries were absent from the
locked sample. This is a substantial improvement over the 10% split's 14
counties and 90% Los Angeles concentration, but it is still a geographically
concentrated test rather than an evenly representative sample of counties.

Results:

| Fold | Rows | Exact empirical AUC | Binormal AUC | Sensitivity | Specificity |
|---:|---:|---:|---:|---:|---:|
| 0 | 36,289 | 0.906285 | 0.904899 | 0.302836 | 0.994886 |
| 1 | 36,288 | 0.900747 | 0.899911 | 0.285714 | 0.995312 |
| 2 | 36,287 | 0.901445 | 0.900048 | 0.301282 | 0.994289 |
| 3 | 36,288 | 0.913341 | 0.912447 | 0.321429 | 0.994175 |
| 4 | 36,288 | 0.888567 | 0.887651 | 0.291209 | 0.994687 |

- Pooled development out-of-fold exact empirical AUC: 0.901736.
- Tier-1 fold summary: 0.902 ± 0.009; the ± value is descriptive fold spread,
  not a confidence interval.
- Locked-test exact empirical AUC: 0.892315.
- Clustered Obuchowski 95% confidence interval: 0.874961–0.909668, treating 68
  locked counties as independent sampling units.
- No contrast was computed because logistic was the only procedure.
- Total reported procedure time: 895.829 seconds (about 14.9 minutes).

Compared with the 10% run, the development pooled AUC was essentially
unchanged (0.901736 versus 0.901638), while the locked estimate rose from
0.880071 to 0.892315. The two locked confidence intervals overlap. This
comparison is descriptive because the locked samples are generated from the
same cohort and are not independent experiments.

Artifacts and SHA-256 hashes:

- `cv_predictions.csv`:
  `671c150a9fae900c1597b21ce55b70534a23fb58c453cae7223ca31d6010a57c`
- `cv_metrics.csv`:
  `d26fceabebace664a53a43621e0db91a3a988f407ae273b114ea280690326846`
- `cv_run.json`:
  `678a2e98553437bef5a556f0962b8235492789c9314c5c4b8ecdb1f2585a2f09`
- `cv_locked_predictions.csv`:
  `db1915f15050eec71e113d9d12199c8d845cc2929492ee2e919ee5704efd541c`
- `neuron.log` and `neuron_actions.log` retain the engine and REST audit trail.

Conclusion: increasing the locked fraction from 10% to 20% produced a much
more credible geographic evaluation at little conceptual cost: 68 rather than
14 locked counties, 14 represented registries, and stable development AUC.
Los Angeles still contributes 45% of the locked sample, an unavoidable large
share if that county is included in a patient-sized 20% holdout. Before freezing
this split, decide whether the estimand is patient-weighted performance in
unseen counties, for which this may be acceptable, or county-representative
performance, which would require a different allocation or weighting target.

---

## 2026-08-12 15:34 CDT — 202608121534 — Accepted locked-test design (no run)

Accepted the split created in run `202608121513` as the locked-test design for
subsequent modeling. The primary estimand is patient-weighted discrimination
for eligible patients in counties not used for model development, rather than
an equally county-weighted estimand.

The frozen design is the seed-42, 20% county-disjoint allocation defined by
input columns 19–22:

- Development: 181,440 patients, 5,461 events, 544 counties.
- Locked test: 45,239 patients, 1,244 events, 68 counties.
- Locked-test row identities and cluster assignments are preserved in
  `runs/202608121513/cv_locked_predictions.csv` and the typed design is in
  `runs/202608121513/cv_run.json`.
- The test is patient-weighted; Los Angeles County contributes 45.01% of locked
  patients. This concentration is accepted as part of the stated estimand, not
  overlooked as equal county representation.

From this point, the locked patients are excluded from neural architecture,
optimizer, stopping-rule, and sample-size decisions. Development-only
cross-validation and inner validation may be examined during selection. The
locked test will be scored again only after the neural procedure is frozen for
the prespecified Neural-versus-Logistic comparison.

No neuron run was performed for this decision, so there is no
`runs/202608121534/` directory.

---

## 2026-08-12 15:50 CDT — 202608121550 — First neural selection run (10,000 development patients)

Started progressive-sample neural architecture selection without exposing the
accepted locked test. This first stage used a reproducible 10,000-row sample
drawn exclusively from the 181,440-patient development partition accepted in
the preceding notebook entry.

Run directory: `runs/202608121550/`

Engine:

- Executable: `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron`
- Version: `neuron 3.0.0-dev`
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`
- Server command, run from the run directory:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --gui --no-browser`

Development-only sample construction:

- Added `data/build_development_sample.py`, a standard-library script that
  reads only the `row` identities from the accepted locked-predictions artifact
  to exclude those rows from selection. Logistic or neural predictions in that
  artifact are not read.
- Source matrix:
  `data/seer_pc_5yr_data.txt`, SHA-256
  `1de0da6a264beb760bdc183f6dccdee33fefc185f4381e95b9bcbf9c164a58aa`.
- Frozen exclusion source:
  `runs/202608121513/cv_locked_predictions.csv`.
- Exact construction command, issued from the project root:

```text
python3 data/build_development_sample.py \
  --data data/seer_pc_5yr_data.txt \
  --locked-predictions runs/202608121513/cv_locked_predictions.csv \
  --sample-size 10000 \
  --seed 42 \
  --output runs/202608121550/seer_pc_5yr_dev_sample_10000.txt \
  --index runs/202608121550/sample_index.csv
```

- The script verified 226,679 source rows and exactly 181,440 rows remaining
  after exclusion. It sampled separately within outcome class using Python's
  seeded `random.Random(42).sample`, then restored original raw-row order.
- Sample: 10,000 patients, 301 events and 9,699 non-events (3.01%).
- `seer_pc_5yr_dev_sample_10000.txt` SHA-256:
  `ac53e7f76cd1409115ca2cd0af4fd0cf0b09676921ff54ca9036e62d6d47fcb0`.
- `sample_index.csv` maps every sample row to its original raw row; SHA-256:
  `8551616e31014aaee86e6af696930362ffbadd2f37ef9af8e71c52d0d41d119c`.

The accepted 45,239-row locked test was absent from the generated data file.
This run therefore could not consult or score it.

Load request:
`mode=raw&path=seer_pc_5yr_dev_sample_10000.txt&inputs=22&outputs=1&discrete=1&fraction=0&seed=42`

Exact cross-validation request:

```text
folds=5
seed=42
maxiter=20000
autostop_tol=0.0001
autostop_window=100
logistic=0
ldfa=0
qdfa=0
neural=1
neural_obd=1
hidden_max=8
iter_budget=4000
inner_val=0.25
algorithm=auto
group=19,20,21,22
```

This was five-fold nested OBD: each outer training fold performed its own
architecture and optimizer selection using a 25% inner validation share. The
county-equivalent socioeconomic key kept groups disjoint in outer folds and
inner validation. The search considered a single hidden layer through a
maximum of eight nodes. The 4,000 iterations per size and 20,000 ordinary-fit
iterations were safety ceilings; the explicit plateau rule supplied a reachable
stopping condition.

Fold design:

- 509 sampled counties; zero group leakage.
- Exactly 2,000 patients per fold.
- Fold events: 60, 60, 61, 60, and 60.
- Fold counties: 102, 103, 102, 102, and 100.
- Imbalance score: 0.013; largest sampled county: 417 rows.
- No warnings or failed folds.

Results:

| Fold | AUC | Sensitivity | Specificity | Hidden nodes | Optimizer |
|---:|---:|---:|---:|---:|---|
| 0 | 0.872543 | 0.316667 | 0.990206 | 2 | L-BFGS |
| 1 | 0.868058 | 0.283333 | 0.994845 | 1 | L-BFGS |
| 2 | 0.878034 | 0.377049 | 0.992780 | 1 | L-BFGS |
| 3 | 0.899313 | 0.250000 | 0.995876 | 2 | L-BFGS |
| 4 | 0.917070 | 0.416667 | 0.992784 | 1 | L-BFGS |

- Pooled out-of-fold exact empirical AUC: 0.886239; binormal AUC: 0.883932.
- Tier-1 mean fold AUC: 0.887 ± 0.021. The ± value is descriptive fold spread,
  not a confidence interval.
- OBD selected one hidden node in 3/5 folds and two in 2/5.
- Automatic optimizer selection chose L-BFGS independently in all 5 folds.
- Total reported neural procedure time: 13.552 seconds.

Artifacts and SHA-256 hashes:

- `cv_predictions.csv`:
  `1bbc796bfd14a8aaff7b71b7190e8566d1ba6371710216ac58a28ea0b834efec`
- `cv_metrics.csv`:
  `c0ec78f2698ba498b7ccd5073a9ae7b05e3e82d722063574ba8190122b2cf483`
- `cv_run.json`:
  `bafb0e73ef867068b3345ca1714e25d04729171aba64070d9b779bc91e0d5a33`
- `neuron.log` and `neuron_actions.log` retain the engine and request trail.

Conclusion: the first neural run was technically clean and inexpensive. On
10,000 development patients, nested OBD strongly favored a very small network
and L-BFGS was completely stable across folds. The pooled neural AUC of 0.886
must not be compared directly with the full-development logistic AUC because
the datasets and fold plans differ. The next progressive stage should repeat
the same neural procedure on a larger development-only sample and include
logistic regression on the same shared folds for a fair descriptive benchmark.

---

## 2026-08-12 15:53 CDT — 202608121553 — Shared-fold logistic versus neural at 20,000 development patients

Advanced the progressive-sample study to 20,000 development-only patients and
compared logistic regression with nested-OBD neural modeling on one shared,
county-disjoint five-fold plan. The accepted locked test remained excluded.

Run directory: `runs/202608121553/`

Engine:

- Executable: `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron`
- Version: `neuron 3.0.0-dev`
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`
- Server command, run from the run directory:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --gui --no-browser`

Development-only sample:

- Exact construction command from the project root:

```text
python3 data/build_development_sample.py \
  --data data/seer_pc_5yr_data.txt \
  --locked-predictions runs/202608121513/cv_locked_predictions.csv \
  --sample-size 20000 \
  --seed 42 \
  --output runs/202608121553/seer_pc_5yr_dev_sample_20000.txt \
  --index runs/202608121553/sample_index.csv
```

- The same frozen locked-row list and outcome-stratified seeded sampling method
  as run `202608121550` were used.
- Sample: 20,000 patients, 602 events and 19,398 non-events (3.01%).
- Sample matrix SHA-256:
  `0c30991841f5c705f73eea4104ee3ec2ff15440e538e1a96d836170ba8c0e9dd`.
- Row index SHA-256:
  `234dad665c825ad106fe5a753bbb6c84e198183d8bc597b2c21a21aee4c41af4`.
- The accepted locked patients were absent from the sample and could not be
  consulted or scored.

Load request:
`mode=raw&path=seer_pc_5yr_dev_sample_20000.txt&inputs=22&outputs=1&discrete=1&fraction=0&seed=42`

Exact evaluation request:

```text
folds=5
seed=42
maxiter=20000
autostop_tol=0.0001
autostop_window=100
logistic=1
ldfa=0
qdfa=0
neural=1
neural_obd=1
hidden_max=8
iter_budget=4000
inner_val=0.25
algorithm=auto
group=19,20,21,22
```

Logistic and the neural procedure used the same outer folds. Neural
architecture and optimizer selection occurred independently inside each outer
training fold using group-disjoint 25% inner validation. The hidden-layer
search ceiling was eight nodes. Iteration counts were safety ceilings; the
explicit plateau condition was available as a meaningful stop.

Fold design:

- 532 sampled counties; zero leakage.
- Exactly 4,000 patients per fold.
- Fold events: 120, 121, 121, 120, and 120.
- Fold counties: 107, 105, 106, 107, and 107.
- Imbalance score: 0.005; largest sampled county: 855 rows.
- No warnings or procedure failures; both procedures fitted all five folds.

Results:

| Fold | Logistic AUC | Neural AUC | Neural − logistic | Hidden | Optimizer |
|---:|---:|---:|---:|---:|---|
| 0 | 0.895384 | 0.866181 | -0.029203 | 1 | L-BFGS |
| 1 | 0.910540 | 0.900820 | -0.009720 | 2 | L-BFGS |
| 2 | 0.880739 | 0.881749 | +0.001010 | 2 | L-BFGS |
| 3 | 0.875092 | 0.860228 | -0.014864 | 7 | L-BFGS |
| 4 | 0.884006 | 0.885760 | +0.001754 | 1 | iRPROP+ |

- Logistic pooled out-of-fold exact empirical AUC: 0.888384; binormal AUC:
  0.887567; reported time 93.115 seconds.
- Neural pooled out-of-fold exact empirical AUC: 0.875719; binormal AUC:
  0.874265; reported time 26.502 seconds.
- Pooled exact-AUC difference, neural minus logistic: -0.012665. Tier 1 reported
  a descriptive difference of -0.010 from its fold summaries. No inferential
  test was performed because this was development cross-validation, not locked
  evaluation.
- Mean fold AUCs were 0.889 ± 0.014 for logistic and 0.879 ± 0.016 for neural;
  the ± values are descriptive fold spread, not confidence intervals.
- OBD selected hidden sizes 1, 2, 2, 7, and 1. L-BFGS was selected in 4/5 folds;
  iRPROP+ was selected in 1/5.

Artifacts and SHA-256 hashes:

- `cv_predictions.csv`:
  `9a3fdaca244aef331b09458a5043235fa427ff8d23161eeadce7cf4f4127745a`
- `cv_metrics.csv`:
  `8afce4f90e9779d4dda369e9d7501d8de0c85081b99701174d3825223e9a8b2c`
- `cv_run.json`:
  `4ba0e10efa6b3b9595e10b03ff07b79183a2167c2010c156f03831346b5c6188`
- `neuron.log` and `neuron_actions.log` retain the engine and request trail.

Conclusion: on the same 20,000-patient development folds, logistic regression
outperformed the nested neural procedure descriptively. The neural architecture
was not stable: four folds selected one or two hidden nodes, while one selected
seven. Optimizer selection was nearly but not completely stable. These results
support the possibility that the dominant signal is well represented by a
linear logit, but they do not yet settle the neural question because this is
only the first shared-fold sample size and the architecture changed materially
in one fold. Continue the progressive schedule before freezing or rejecting the
neural procedure; do not inspect the accepted locked test.

---

## 2026-08-12 16:00 CDT — 202608121600 — Shared-fold logistic versus neural at 40,000 development patients

Advanced the progressive-sample comparison to 40,000 development-only
patients. Logistic regression and the nested-OBD neural procedure used one
shared, county-disjoint five-fold plan. The accepted locked test remained
excluded from the data available to neuron.

Run directory: `runs/202608121600/`

Engine:

- Executable: `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron`
- Version: `neuron 3.0.0-dev`
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`
- Server command, run from the run directory:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --gui --no-browser`

Development-only sample:

```text
python3 data/build_development_sample.py \
  --data data/seer_pc_5yr_data.txt \
  --locked-predictions runs/202608121513/cv_locked_predictions.csv \
  --sample-size 40000 \
  --seed 42 \
  --output runs/202608121600/seer_pc_5yr_dev_sample_40000.txt \
  --index runs/202608121600/sample_index.csv
```

- Sample: 40,000 patients, 1,204 events and 38,796 non-events (3.01%).
- Sample matrix SHA-256:
  `edc4c5f5f9b801e8627dcb2fe90f1055cfa2f6d3c3382df0988a13b08fc3e00b`.
- Row index SHA-256:
  `6bd272a4e7342b0f4318be1525d386b621e8532a33be35bbb74bd5c87e78a027`.
- The construction used the same accepted locked-row exclusion, seed, and
  outcome-stratified method as the 10,000- and 20,000-row stages. No locked row
  was present or scoreable.

Load request:
`mode=raw&path=seer_pc_5yr_dev_sample_40000.txt&inputs=22&outputs=1&discrete=1&fraction=0&seed=42`

Exact evaluation request:

```text
folds=5
seed=42
maxiter=20000
autostop_tol=0.0001
autostop_window=100
logistic=1
ldfa=0
qdfa=0
neural=1
neural_obd=1
hidden_max=8
iter_budget=4000
inner_val=0.25
algorithm=auto
group=19,20,21,22
```

The configuration was unchanged from the 20,000-row shared-fold run. Neural
architecture and optimizer selection occurred independently inside each outer
training fold using county-disjoint 25% inner validation. Safety ceilings and
the explicit plateau stopping condition were retained.

Fold design:

- 540 sampled counties; zero leakage.
- Exactly 8,000 patients per fold.
- Fold events: 241, 241, 241, 241, and 240.
- Fold counties: 108, 108, 110, 109, and 105.
- Imbalance score: 0.003; largest sampled county: 1,731 rows.
- No warnings or failed folds; both procedures fitted all five folds.

Results:

| Fold | Logistic AUC | Neural AUC | Neural − logistic | Hidden | Optimizer |
|---:|---:|---:|---:|---:|---|
| 0 | 0.901052 | 0.889179 | -0.011873 | 1 | L-BFGS |
| 1 | 0.895493 | 0.882771 | -0.012722 | 1 | L-BFGS |
| 2 | 0.904311 | 0.899805 | -0.004506 | 3 | L-BFGS |
| 3 | 0.889809 | 0.878094 | -0.011715 | 4 | L-BFGS |
| 4 | 0.912063 | 0.897876 | -0.014187 | 1 | L-BFGS |

- Logistic pooled out-of-fold exact empirical AUC: 0.900582; binormal AUC:
  0.899498; reported time 167.668 seconds.
- Neural pooled out-of-fold exact empirical AUC: 0.888217; binormal AUC:
  0.886622; reported time 23.195 seconds.
- Pooled exact-AUC difference, neural minus logistic: -0.012365. Tier 1 reported
  the fold-summary difference as -0.011. No inferential test was performed on
  development cross-validation.
- Mean fold AUCs: logistic 0.901 ± 0.008; neural 0.890 ± 0.009. These are
  descriptive fold spreads, not confidence intervals.
- OBD selected hidden sizes 1, 1, 3, 4, and 1. L-BFGS was selected by Auto in
  all five folds.

Artifacts and SHA-256 hashes:

- `cv_predictions.csv`:
  `4660ffe04d3fb72bee3c027dfb4b99e9b3efc05917469a1664a9dd799f9dc23f`
- `cv_metrics.csv`:
  `71466ef332ca14a1cae583511e831f7792e705985bde669606bd5f587837f0a5`
- `cv_run.json`:
  `350b1fdbaa8669ded0b5b061dad4b3a49c96e885b67070cecfdb234bf0bde4c4`
- `neuron.log` and `neuron_actions.log` retain the engine and request trail.

Conclusion: doubling the selection sample to 40,000 did not reveal a neural
advantage. Logistic regression exceeded the neural AUC in every fold and by
0.012365 in pooled out-of-fold predictions, essentially the same deficit seen
at 20,000 patients. Architecture selection became more concentrated: three of
five folds selected one hidden node, with the others selecting three and four;
the prior seven-node outlier did not recur. Optimizer selection stabilized
completely on L-BFGS. This is strong development evidence that added neural
complexity is not improving discrimination under the tested procedure. The
accepted locked test remains unspent for a final frozen comparison.

---

## 2026-08-12 16:11 CDT — 202608121611 — Failed full-development logistic coefficient fit

Attempted to fit one 22-input logistic model on the complete accepted
development cohort in order to obtain neuron's coefficient estimates, Wald
tests, and information-matrix condition number. The locked test was excluded.

Run directory: `runs/202608121611/`

Engine and data:

- Executable: `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron`
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`
- Server command:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --gui --no-browser`
- The complete 181,440-row development matrix was materialized with:

```text
python3 data/build_development_sample.py \
  --data data/seer_pc_5yr_data.txt \
  --locked-predictions runs/202608121513/cv_locked_predictions.csv \
  --sample-size 181440 \
  --seed 42 \
  --output runs/202608121611/seer_pc_5yr_development.txt \
  --index runs/202608121611/development_index.csv
```

- Development matrix: 181,440 patients, 5,461 events and 175,979 non-events;
  SHA-256
  `cb6839d41da1fe1cacb6008f44b2e23f0dd9149483c7185c94583f41c7587682`.
- Development index SHA-256:
  `b22e5adb51c45b53ac23d269a9f1ecfd08d4b3ec400f71f63a44385697eaba97`.

Requests:

```text
mode=raw&path=seer_pc_5yr_development.txt&inputs=22&outputs=1&discrete=1&fraction=0&seed=42
type=logistic
algorithm=1&maxiter=20000&seed=42&autostop=1&autostop_tol=0.0001&autostop_window=100&async=1
```

Outcome: **failed; no fit or coefficient result was accepted.** Training
progress was observable through approximately iteration 1,865, with finite and
steadily decreasing cross-entropy (about 1.69105 initially and 0.0873523 at the
last observed sample). The process then ceased accepting loopback HTTP
connections before publishing a terminal result. No coefficient table,
condition number, saved model, or completion status was produced. The process
was terminated after confirming the listener was unavailable. `neuron.log` and
`neuron_actions.log` are retained along with the exact development matrix and
index.

Conclusion: this attempt supplies no coefficient or variable-importance
evidence. Retry the same all-input logistic coefficient analysis on the already
defined 40,000-patient development-only sample, which has 1,204 events and is
large enough for a stable screening analysis while avoiding the failed
full-cohort standalone-report path.

---

## 2026-08-12 16:16 CDT — 202608121616 — Corrected regression target (no run)

Corrected the interpretation and planned regression analysis before launching
the retry proposed in the preceding entry.

The model matrix contains 22 encoded input nodes, but these represent **14
conceptual predictor variables**, not 22 independent variables. With the
outcome, the dataset contains 15 conceptual variables total. The requested
regression must therefore assess the 14 predictors with categorical indicator
sets kept intact:

```text
0; 1; 2, 3; 4-7; 8; 9; 10-12; 13-15; 16; 17; 18; 19; 20; 21
```

The groups correspond, in order, to age, PSA, Gleason, T stage, N stage, M
stage, race/ethnicity, marital status, previous cancer, diagnosis year,
poverty, income, unemployment, and education. A coefficient/Wald table over
individual encoded inputs can describe contrasts within a fitted categorical
variable, but it does not answer which conceptual variables are selected.

The unlaunched directory `runs/202608121615/` had been created for the
individual-input retry before this correction. It contains only symbolic links
to the prior 40,000-row sample and index; neuron was not launched and no model
or analysis ran. It is retained rather than repurposed or silently removed.

Updated `CLAUDE.md` with a standing rule requiring this distinction and the
grouped structure for regression and variable selection.

No neuron run was performed for this correction, so there is no
`runs/202608121616/` directory.

---

## 2026-08-12 16:17 CDT — 202608121617 — Baseline fit completed; REST stepwise unavailable

Fitted the 22-input logistic baseline on the previously defined 40,000-patient
development-only sample, intending to follow it with grouped reverse stepwise
regression over 14 conceptual variables.

Run directory: `runs/202608121617/`

- Engine: `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --gui --no-browser`
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`.
- The sample and index were symbolic links to run `202608121600`; sample
  SHA-256:
  `edc4c5f5f9b801e8627dcb2fe90f1055cfa2f6d3c3382df0988a13b08fc3e00b`.
- Requests: raw load with 22 inputs, no holdout, seed 42; logistic model; then
  canonical training with a 20,000-iteration ceiling and plateau stop
  (`tol=0.0001`, window 100).

The baseline stopped at iteration 2,722 with finite cross-entropy 0.08716292
and wrote its coefficient/Wald report. The information-matrix condition number
was approximately `1.4e15`, indicating severe ill-conditioning in the encoded
design. The GUI listener then became unavailable before a grouped stepwise
request could be submitted. No stepwise regression ran and no variable was
selected. The engine process was terminated after confirming the listener was
unavailable.

Artifacts retained: `model.txt`, `neuron.log`, `neuron_actions.log`, and the
sample/index links. SHA-256: `model.txt`
`d780c6536b3d0196d55273983a1d94165763553503d3717a7dd4f81003b8c8d9`;
`neuron.log`
`16a81b0f11b00726e0dd8205523b270788ad52cb497d042ccd2afa4d83576b63`;
`neuron_actions.log`
`6f87047686404893c89d2c371568df29d8fd1f386dc33ddcc54a289ffda2274b`.

Conclusion: the baseline fit is descriptive evidence only. Use neuron's
maintained scripted compatibility interface for the grouped stepwise analysis.

---

## 2026-08-12 16:19 CDT — 202608121619 — Grouped reverse stepwise failed at iteration ceiling

Attempted the grouped reverse stepwise analysis through neuron's scripted
compatibility interface on the same 40,000-patient development-only sample.

Run directory: `runs/202608121619/`

- Exact engine command:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --seed 42 < session.in > session.out`
- Grouped variable structure:
  `0;1;2,3;4-7;8;9;10-12;13-15;16;17;18;19;20;21`.
- Reverse removal threshold: p = 0.05.
- Canonical logistic training, automatic step size, maximum-gradient stop at
  the default `1e-6`, and 20,000-iteration safety ceiling.

Outcome: **failed; no variable was selected.** The full baseline stopped at
the ceiling after 20,001 reported iterations, with maximum absolute gradient
`1.922899e-05`; neuron correctly declared it unconverged. Its first reverse
candidate, removal of conceptual variable 0 (age), likewise reached
`max_iterations`. neuron refused to calculate a Wilks p-value or select a
variable from the incomplete pass.

Artifacts and SHA-256 hashes: `session.in`
`c5b77d99e0f1013b2efd14b2da5f9c08c88b3ad547ff9933245aa5b8eb1a6e36`;
`session.out`
`ab2a603bb37659bf9fb71b88f75d6310062f7bdbd214da34b7661f483f09d84b`;
`neuron.log`
`2d9537dc620455fc802496c23d04318212156591e36452393d9d8c4944659dbb`;
`model.txt`
`c533f82b5cb7bf624b84d42c6893096001ebcff09acd6689d45159a10da35b21`.

Conclusion: repeat with the same grouped structure, threshold, and ceiling but
an explicit reachable maximum-gradient condition of `1e-4`. This is a declared
approximate convergence criterion; every candidate must meet it independently.

---

## 2026-08-12 16:33 CDT — 202608121633 — Successful grouped reverse logistic regression

Completed grouped reverse stepwise logistic regression over the 14 conceptual
predictor variables on the 40,000-patient development-only sample. The accepted
locked test remained excluded.

Run directory: `runs/202608121633/`

Engine and exact procedure:

- Command:
  `/Users/craign/code/neUROn2++/neuron-3.0/build/neuron --seed 42 < session.in > session.out`.
- Engine commit: `2deec3b5dbd16eed00ca521797392fbeb943a73e`.
- Sample: the run-`202608121600` matrix, 40,000 patients and 1,204 events;
  SHA-256
  `edc4c5f5f9b801e8627dcb2fe90f1055cfa2f6d3c3382df0988a13b08fc3e00b`.
- Logistic training: canonical gradient descent, automatic step size,
  batch/epoch, no weight decay, seed 42.
- Stopping: maximum absolute gradient `1e-4`; 20,000-iteration safety ceiling.
- Grouped structure:
  `0;1;2,3;4-7;8;9;10-12;13-15;16;17;18;19;20;21`.
- Direction: reverse; removal threshold p = 0.05.

The full baseline reached the declared maximum-gradient stop in 4,461
iterations (40 seconds), with final cross-entropy 0.08709246 and log likelihood
-3483.698. Every candidate fit used the same stopping configuration and had to
finish before entering a Wilks comparison. The full encoded model's
information-matrix condition number was `1.7e15`; individual Wald results are
therefore not used as substitutes for the grouped likelihood-ratio tests.

Grouped removal path:

| Removal order | Variable index | Conceptual predictor | Removal p-value |
|---:|---:|---|---:|
| 1 | 6 | Race/ethnicity | 1.000000 |
| 2 | 10 | Area poverty | 1.000000 |
| 3 | 12 | Area unemployment | 0.158889 |
| 4 | 13 | Area less-than-high-school education | 0.269178 |
| 5 | 9 | Diagnosis year | 0.093320 |

After these removals, every remaining candidate had p < 0.05, so reverse
selection stopped. The final retained variables were:

| Variable index | Conceptual predictor | Final-pass removal p-value |
|---:|---|---:|
| 0 | Age at diagnosis | 1.109306e-19 |
| 1 | ln(PSA) | 3.030357e-42 |
| 2 | Gleason group | 4.341650e-101 |
| 3 | AJCC T category | 5.849993e-05 |
| 4 | AJCC N category | 1.465667e-07 |
| 5 | AJCC M category | 1.869389e-138 |
| 7 | Marital status | 6.013513e-05 |
| 8 | Previous cancer | 3.265508e-03 |
| 11 | Area median household income | 2.444712e-03 |

The p-values above are sequential grouped Wilks tests at the final completed
pass, conditional on the already removed variables. They rank strength of
evidence against removal in this selection path; they are not effect sizes and
should not be interpreted as a causal hierarchy.

Artifacts and SHA-256 hashes:

- `session.in`:
  `d671bfda3780719dad476d9d659fb8b4ccfa246948f4b9fa71290a8622a7ce35`
- `session.out`:
  `2621e4fae1f228a794905502522900a6b2cb36f2bdfac7da3b0b9aa7af343ad2`
- `neuron.log`:
  `1fbf2ebdfaf4cabb81e8be87b77a40c05dce7735e0211bbeb435d8ffefb6b15d`
- `model.txt`:
  `d8b072d30b795dde684e640a557d45af88e0348cdfa5e72ee335133443c2431d`

Conclusion: stage, PSA, Gleason, and age carried the strongest grouped evidence;
marital status, previous cancer, and area income also remained independently
informative at the prespecified 0.05 threshold. Race/ethnicity, diagnosis year,
poverty, unemployment, and education were removed along this development-only
path. This is exploratory variable selection on one 40,000-patient sample, not
a locked-test result or a causal analysis. The selected model has not been
refitted and compared out of sample, and selection uncertainty is not captured
by these p-values.

---

## 2026-08-12 16:55 CDT — 202608121655 — Consolidated regression table and marital-status direction (no run)

Added a single consolidated presentation of the successful grouped reverse
regression from run `202608121633`. No model was fitted and the locked test was
not accessed for this entry.

| Variable index | Conceptual predictor | Stepwise result | Sequential grouped p-value |
|---:|---|---|---:|
| 0 | Age at diagnosis | Retained | 1.109306e-19 |
| 1 | ln(PSA) | Retained | 3.030357e-42 |
| 2 | Gleason group | Retained | 4.341650e-101 |
| 3 | AJCC T category | Retained | 5.849993e-05 |
| 4 | AJCC N category | Retained | 1.465667e-07 |
| 5 | AJCC M category | Retained | 1.869389e-138 |
| 6 | Race/ethnicity | Removed first | 1.000000 |
| 7 | Marital status | Retained | 6.013513e-05 |
| 8 | Previous cancer | Retained | 3.265508e-03 |
| 9 | Diagnosis year | Removed fifth | 9.331972e-02 |
| 10 | Area poverty | Removed second | 1.000000 |
| 11 | Area median household income | Retained | 2.444712e-03 |
| 12 | Area unemployment | Removed third | 1.588885e-01 |
| 13 | Area less-than-high-school education | Removed fourth | 2.691780e-01 |

For marital status, married is the reference category and the modeled outcome
is prostate-cancer death within five years. The full fitted model's three
non-married indicators all had positive coefficients, so each was associated
with higher adjusted odds of five-year prostate-cancer death than marriage:

| Marital category versus married | Beta | Adjusted odds ratio for PC death | Approximate 95% Wald CI | Input-level Wald p |
|---|---:|---:|---:|---:|
| Never married/domestic partner | 0.263583 | 1.302 | 1.156–1.465 | 1.2e-05 |
| Divorced/separated | 0.191749 | 1.211 | 1.062–1.382 | 0.0043 |
| Widowed | 0.204575 | 1.227 | 1.072–1.404 | 0.0029 |

Thus, in this adjusted development-sample model, being married was associated
with lower odds of prostate-cancer death within five years (and therefore
better prostate-cancer-specific five-year survival) than each recorded
non-married category. This is an association, not evidence that marriage
causes improved survival. The categories should not be collapsed into a single
"unmarried" effect without fitting that contrast. The grouped p-value establishes
that marital status as a conceptual variable contributed information; the
indicator-level coefficients describe the direction of its individual
contrasts. Because the encoded full model was severely ill-conditioned and the
analysis used one 40,000-patient development sample, the odds ratios and Wald
intervals are exploratory and should be confirmed in a stable refitted model.

No neuron run was performed for this summary, so there is no
`runs/202608121655/` directory.

---

## 2026-08-14 06:23 CDT — 202608140623 — T0 cohort decision and split-reporting clarification (no run)

Reviewed the severe ill-conditioning in the 40,000-patient full logistic fit
from run `202608121633`. A direct count established the structural cause of
the unstable T0 coefficient:

| Dataset | Total patients | T0 patients | T0 five-year PC deaths |
|---|---:|---:|---:|
| Full modeling matrix | 226,679 | 2 | 0 |
| 40,000-patient development sample | 40,000 | 0 | 0 |

Because the T0 input was identically zero in the fitted sample, its coefficient
was unidentified. This explains the T0 standard error of approximately
`372,975` and contributes directly to the reported information-matrix
condition number of `1.7e15`. T0 means no evidence of a primary tumor; it is
biologically distinct from T1 and will not be merged with the T1 reference
category.

Decision: restrict the modeling cohort to patients with an identified primary
prostate tumor, AJCC T1–T4, and exclude the two T0 patients. This is a
stage-based eligibility rule, not an outcome-based exclusion; their outcomes
were inspected to diagnose estimability but are not the selection criterion.
This decision has been documented in `FIVE_YEAR_PC_MORTALITY_DATASET.md` but
has not yet been implemented in the cohort files. When implemented, the two
records will be removed without redrawing the frozen allocation: every
remaining patient's existing development or locked-test assignment will be
preserved. The build and independent audit must then be rerun, and the revised
partition counts recorded before fitting another model.

Also clarified the language required for the eventual report. Neuron created
seed-42 candidate county-disjoint allocations, keeping each county wholly in
development or test and balancing patient/event totals. The 10% allocation was
rejected as too geographically concentrated; the accepted 20% allocation
contained, before T0 exclusion, 181,440 development patients in 544 counties
and 45,239 locked-test patients in 68 counties. Development model selection
used county-disjoint cross-validation, and locked patients were excluded from
all neural architecture, optimizer, stopping-rule, and sample-size decisions.

The report must also disclose that logistic locked-test performance on both
candidate allocations was viewed before the 20% allocation was accepted.
Consequently, the accepted test is held out from neural development but is not
a completely untouched, fully prespecified confirmatory test. The principal
estimand remains patient-weighted discrimination in eligible patients from
counties absent during model development.

No cohort file was changed and no neuron run was performed for this decision,
so there is no `runs/202608140623/` directory.
