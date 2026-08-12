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
