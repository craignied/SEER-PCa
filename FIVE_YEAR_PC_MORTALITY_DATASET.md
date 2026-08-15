# Five-Year Prostate-Cancer Mortality Modeling Dataset

## Purpose

This document records the complete rationale and construction of
`seer_pc_5yr_mortality_2004_2009.csv`. It is intended to preserve the decisions needed
for a future talk, manuscript, model comparison, or reconstruction of the analysis.

The modeling question is:

> Among men diagnosed with prostate cancer during 2004–2009 who had sufficiently
> complete staging, PSA, Gleason, demographic, and socioeconomic documentation, can
> information available at diagnosis predict death from prostate cancer within five
> years?

The phrase **information available at diagnosis** is important. Treatment, follow-up,
and eventual vital-status information are used to establish eligibility or the outcome,
but they are not model inputs.

## Files

- `seer-prostate-5-8-17-formatted.dta`: source Stata dataset
- `seer-prostate-5-8-17-formatted.rds`: apparent R representation of the same data
- `build_five_year_pc_mortality_csv.py`: reproducible cohort and CSV builder
- `audit_five_year_pc_mortality_csv.py`: independent source-to-output audit
- `seer_pc_5yr_mortality_2004_2009.csv`: numeric model-source CSV
- `seer_pc_5yr_audit_index.csv`: source-row and patient-identity audit trail
- `seer_pc_5yr_data.txt`: headerless numeric data loaded by `neuron-3.0`
- `seer_pc_5yr_key.txt`: human-readable map from model columns to variables
- `seer_pc_5yr_inputs.txt`: grouped input-node structure for stepwise regression
- `MODELING_OUTCOMES.md`: earlier discussion of candidate binary outcomes

The source `.dta` is labeled `SEER Prostate 1973-2014` and contains 1,708,661 records
and 167 variables. The output contains no patient/case identifier.

SHA-256 checksums for the exact files used and produced are:

```text
1977ce1f0531927055ea43a4ba3170bacadf34c317749dac0df7412fad795e0a  seer-prostate-5-8-17-formatted.dta
5fb7d16038da16ff6e7cadf4e20a5f9117899a359328805430418039ea35207d  seer_pc_5yr_mortality_2004_2009.csv
1de0da6a264beb760bdc183f6dccdee33fefc185f4381e95b9bcbf9c164a58aa  seer_pc_5yr_data.txt
c0abbc93eff9f4c19e85a3d319a288e74e2a55876db733014df5f0ef5518c128  seer_pc_5yr_audit_index.csv
344d11cc1e51756b0f011195109ecfcfbe2ebc8a8a3166cfa87fbc7af9ad7ccb  seer_pc_5yr_key.txt
2780c1c835e7ef4b4a2e6f27c133052bd4ea9cc1c02196a717dfa640bb8ba8e3  seer_pc_5yr_inputs.txt
4ced8af6a74f2917896363466f61bc182f4a3fd39d7435a9784c3053d57c0ed9  build_five_year_pc_mortality_csv.py
1cb0e9a42186f407d48235bedb0728129b875c9e999466e14d68d81b471e750e  audit_five_year_pc_mortality_csv.py
```

Earlier artifacts with CSV hash `253edd...` and data-file hash `fccdf5...` contained
299,534 rows and are invalid. They included 72,855 extra rows created by a faulty
county-name socioeconomic merge. The active filenames were regenerated only after the
patient-identity and state-FIPS repair described below passed independent audit.

## Why this outcome was chosen

### Clinical importance

Death from prostate cancer is a clinically meaningful endpoint. It is more specific to
the malignancy than all-cause mortality, which is heavily influenced by age, comorbidity,
and non-cancer illness that are incompletely represented in this dataset.

### Why a fixed five-year horizon is necessary

The source contains the derived variable `deadofpc`, but using it as "ever died from
prostate cancer" would be biased by unequal follow-up. A man diagnosed in 1975 has
decades in which to experience the event; a man diagnosed in 2014 has almost none.

Every included record therefore receives the same conceptual prediction window: the
60 months following diagnosis.

### Why diagnoses were restricted to 2004–2009

The 2004 start provides a reasonably coherent modern-era cohort with Collaborative
Stage information and substantially better PSA and Gleason availability than the full
1973–2014 dataset. The 2009 endpoint allows five potential years of observation in a
dataset extending through 2014.

Some late-2009 cases still have less than 60 observed months. The endpoint rule handles
that explicitly rather than presuming that absence of a recorded death means survival.

### Why not ten-year mortality

The source follow-up is inadequate for a valid modern-era ten-year binary endpoint.
Requiring known ten-year status among 2004–2009 diagnoses would preferentially retain
early deaths and the small subset with unusually long observation. That would create a
severely selected cohort.

## Exact outcome definition

`pc_death_within_5_years` is the last column and is coded:

- `1`: `deadofpc == 1` and `srv_time_mon <= 60`
- `0`: either:
  - the record has at least 60 months of observed survival/follow-up, or
  - the man died from another cause within 60 months
- Excluded: alive at last contact with less than 60 months of follow-up

A death from another cause before five years is a non-event for this binary question:
the man did not die from prostate cancer within five years and can no longer experience
that event. This is a pragmatic fixed-horizon binary classification, not a formal
cause-specific hazards or competing-risks survival analysis. A future clinical paper
should acknowledge that distinction and may supplement this model with a competing-risks
analysis.

## Cohort construction

The five-year outcome can be determined for 453,276 diagnoses from 2004–2009:

- 24,054 prostate-cancer deaths within five years
- 429,222 non-events
- Event prevalence: 5.31%
- 13,985 otherwise year-eligible records excluded because they were alive with less
  than 60 months of follow-up

The modeling cohort then requires complete diagnosis-time inputs:

- Nonmissing age
- Nonmissing PSA
- Nonmissing Gleason score
- Known/applicable AJCC T, N, and M categories
- Known race/ethnicity
- Known marital status
- Known previous-cancer status
- Nonmissing poverty, income, unemployment, and education attributes

Before socioeconomic-linkage repair, the complete-field selection produced 299,534
rows. The formatted source had matched socioeconomic records on county name without
state: for example, a Connecticut Middlesex County patient received both Connecticut
and New Jersey Middlesex County profiles. The clinical record and outcome were copied
unchanged while FIPS and the four socioeconomic fields varied.

The builder now preserves `reg`, `pubcsnum`, `rec_no`, `seq_num`, `st_cnty`, `fips`, and
the source-row position until all checks pass. Each of the 18 registries is mapped to its
state FIPS, and only the county FIPS in that state is eligible. For every registry/patient
group among the 299,534 pre-linkage rows, the builder requires exactly one state-matched
FIPS. It rejects 72,855 wrong-state rows and then requires uniqueness of both
registry/patient and registry/patient/record/sequence identifiers.

The corrected final dataset contains:

- **226,679 unique patients (exemplars)**
- **6,705 prostate-cancer deaths within five years (events)**
- **219,974 non-events**
- **2.96% event prevalence**
- 22 model inputs and one binary outcome

### Meaning of "exemplar" and "event"

An exemplar is one complete row presented to `neuron-3.0`, corresponding here to one
eligible prostate-cancer case record. In conventional biostatistical writing it would
usually be called an observation, subject, patient, or case.

An event is an exemplar whose modeled outcome occurred: death from prostate cancer
within five years (`1`).

## Why a complete-case cohort was chosen

The immediate purpose is to create a clean, interpretable dataset for logistic-regression
and neural-network modeling. A complete-case cohort avoids requiring an imputation model
or treating clinically important unknown stages as though they were measured categories.
It also makes every model row structurally identical.

The choice is not statistically neutral. Requiring complete information and a valid
state-matched socioeconomic record reduces the event prevalence from 5.31% in the
outcome-evaluable cohort to 2.96% in the final cohort.
Men with incomplete PSA, Gleason, staging, or demographic data evidently had worse
outcomes. Consequently, the trained model's target population is not all men with SEER
prostate cancer. It is explicitly:

> Men diagnosed during 2004–2009 who received sufficiently complete staging, PSA,
> Gleason, demographic, and socioeconomic documentation.

That language should appear in any presentation or manuscript. The model should not be
described as population-wide without a later missing-data analysis. A future study could
compare complete-case results with missingness-indicator or multiple-imputation models.

## Race and ethnicity nomenclature

The source variable `ethnew` is misleadingly named: its Stata label shows that it is a
recode of `race1v`, with White, Black, Other, and Unknown levels. Hispanic origin is
stored separately in `origrecb` and in the more detailed `nhiade` field.

For clarity, race and Hispanic origin were combined conceptually into:

- White
- Black
- Hispanic
- Other
- Unknown

Hispanic origin takes precedence over recorded race, producing the conventional
"Hispanic, any race" group. Because the final dataset is complete-case, Unknown records
are excluded. The numeric CSV uses White as the omitted regression reference:

- `race_black`
- `race_hispanic`
- `race_other`

All three equal zero for White.

## Input definitions and coding

The CSV is already numeric. Binary indicator coding is performed here deliberately so
that `mkdataset.py` does not choose reference categories alphabetically.

| CSV column | Type | Definition | Reference when applicable |
|---|---|---|---|
| `age_years` | Numerical | Age at diagnosis in years | — |
| `ln_psa` | Numerical | Natural logarithm of diagnosis-time PSA | — |
| `gleason_7` | Binary | Gleason score equals 7 | Gleason 2–6 |
| `gleason_8_to_10` | Binary | Gleason score 8–10 | Gleason 2–6 |
| `t_stage_t0` | Binary | AJCC T0 | T1 |
| `t_stage_t2` | Binary | AJCC T2, including substages/NOS | T1 |
| `t_stage_t3` | Binary | AJCC T3, including substages/NOS | T1 |
| `t_stage_t4` | Binary | AJCC T4, including substages/NOS | T1 |
| `n_stage_n1` | Binary | Any known AJCC N1 category | N0 |
| `m_stage_m1` | Binary | Any known AJCC M1 category | M0 |
| `race_black` | Binary | Black and non-Hispanic | White |
| `race_hispanic` | Binary | Hispanic, any race | White |
| `race_other` | Binary | Other race and non-Hispanic | White |
| `marital_never_married_or_domestic_partner` | Binary | Never married or unmarried/domestic partner | Married |
| `marital_divorced_or_separated` | Binary | Divorced or separated | Married |
| `marital_widowed` | Binary | Widowed | Married |
| `previous_cancer` | Binary | A malignancy preceded the indexed prostate cancer | No previous cancer |
| `diagnosis_year_since_2004` | Numerical | Diagnosis year minus 2004; range 0–5 | — |
| `poverty_percent` | Numerical | Area percentage below poverty threshold | — |
| `median_household_income_dollars` | Numerical | Area median household income in dollars | — |
| `unemployment_percent` | Numerical | Area unemployment percentage | — |
| `less_than_high_school_percent` | Numerical | Area percentage with less than high-school education | — |
| `pc_death_within_5_years` | Binary outcome | Prostate-cancer death within 60 months | No such death |

### PSA transformation

PSA is strongly right-skewed, so the model uses the natural logarithm of PSA rather than
raw PSA. The source's complete values range from 0.1 to 98.0. The upper boundary deserves
additional investigation because it may reflect truncation or a researcher recode. The
log transformation reduces the influence of this upper tail but does not resolve any
source-coding uncertainty.

An odds ratio for a one-unit increase in `ln_psa` is not an odds ratio for one additional
ng/mL. A one-unit natural-log increase corresponds to multiplying PSA by approximately
2.718.

### Gleason grouping

Gleason score is clinically ordinal, not a conventional continuous measurement. It was
grouped as 2–6, 7, and 8–10. This avoids imposing a constant linear effect per Gleason
point and avoids unstable categories for the very rare scores 2–5.

### Stage grouping

Detailed AJCC substages were collapsed to T0/T1/T2/T3/T4, N0/N1, and M0/M1. The goals
are clinically interpretable regression coefficients and adequate counts per parameter.
Unknown, not-applicable, TX, NX, and MX records are excluded rather than assigned to a
stage.

T1, N0, and M0 are the omitted reference categories. Do not add overall AJCC stage,
`nnew`, `mets`, Collaborative Stage extension, or summary stage to the same model: those
variables duplicate information already contained in T/N/M and would create unnecessary
collinearity.

### Marital status

Married is the reference category. Divorced and separated were combined; never married
and the extremely small unmarried/domestic-partner category were combined. Widowed
remains separate. Unknown marital status is excluded.

### Diagnosis year

The outcome window remains exactly five years for every man. Diagnosis year is an input
because two otherwise similar men diagnosed in 2004 and 2009 may have different risks
owing to changes in detection, staging, treatment practice, supportive care, or coding.

The value is centered as `year - 2004`, producing 0–5. Centering makes the intercept refer
to 2004 and improves numerical conditioning. A regression coefficient represents the
adjusted change in five-year mortality odds per calendar year, assuming an approximately
linear time effect.

Diagnosis year may improve historical internal prediction but limits deployment. A trend
estimated over 2004–2009 must not be extrapolated to current patients without external
validation and recalibration. A sensitivity model should therefore omit diagnosis year,
and annual outcome rates should be inspected for nonlinearity.

### Socioeconomic variables

Poverty, income, unemployment, and education are area-level contextual measurements,
not individual patient income, employment, poverty status, or education. Their
coefficients must be described as associations with characteristics of the area of
residence. Doing otherwise would commit an ecological fallacy.

SEER documentation states that county/tract percentages use two implied decimal places
and that median household income is stored in tens of dollars. The builder converts the
stored integers to percentages and dollars. The observed correlation pattern is
internally consistent: poverty correlates positively with unemployment and less-than-high-
school education and negatively with income.

All four are retained because their adjusted relationships are substantively interesting.
They are correlated, so logistic-regression interpretation must include:

- the model condition number;
- individual Wald tests;
- correlations among the four variables;
- comparison with reduced or jointly tested socioeconomic specifications.

An unstable individual coefficient would not demonstrate absence of a socioeconomic
association; it could reflect shared information among the four measures.

Official background:

- [SEER county attributes](https://seer.cancer.gov/seerstat/variables/countyattribs/)
- [SEER static county-attribute definitions](https://seer.cancer.gov/seerstat/variables/countyattribs/static.html)
- [SEER time-dependent attribute definitions](https://seer.cancer.gov/seerstat/variables/countyattribs/time-dependent.html)
- [SEER attribute data dictionary](https://seer.cancer.gov/seerstat/variables/countyattribs/ctattrdict.html)

The short variable names in this 2017 researcher-formatted file do not retain the full
original SEER labels. Before publication, the precise Census/ACS vintage and whether
these four attached attributes are static or time-dependent should be confirmed from the
original extraction recipe if it can be recovered.

## Variables deliberately excluded

### Direct outcome leakage

The following contain survival, vital-status, or cause-of-death information and must
never be predictors:

- `dead`
- `deadofpc`
- `srv_time_mon`
- `stat_rec`
- `codpub`
- `codpubkm`
- `vsrtsadx`
- `odthclass`

They are used only to define the endpoint or determine adequate follow-up.

### Treatment variables

`primaryrx`, `rp`, `radiation`, `postopxrt`, and `preopxrt` are excluded because the
stated prediction point is diagnosis. Treatment is selected after evaluation and is
strongly confounded by age, disease severity, health, access, and patient preference.
Including it would change the model into a post-treatment-selection prognostic model and
could easily be misread as estimating treatment benefit.

### Redundant disease variables

Overall AJCC stage, Collaborative Stage fields, `nnew`, `mets`, summary stage, and general
tumor grade were excluded because T, N, M, and grouped Gleason already represent these
clinical domains. Retaining multiple recodes of the same underlying facts would inflate
collinearity and complicate interpretation.

### Identifiers

`pubcsnum`, FIPS, and other record/geographic identifiers are excluded. The four
socioeconomic measures retain contextual information without allowing the model to learn
an individual case identifier or an effectively arbitrary county code.

## Using the CSV with neuron-3.0

The CSV has a header, contains only numeric values, has no blank cells, and places the
outcome last. No categorical auto-detection or one-hot conversion is required. The
neuron-ready headerless file is reproduced with:

```sh
python3 ~/code/neUROn2++/neuron-3.0/tools/mkdataset.py \
  -o seer_pc_5yr_data.txt \
  seer_pc_5yr_mortality_2004_2009.csv
```

The expected result is 226,679 rows, 23 columns, 22 input nodes, and one output node.

### The key and grouped input structure

`seer_pc_5yr_key.txt` is the authoritative human-readable map used to translate model
input numbers, regression coefficients, Wald rows, saved models, and deployed-model
fields back to their clinical meanings. Its positions are **1-based data columns**,
matching `mkdataset.py`'s key convention. The outcome is column 23 and is not an input.

`seer_pc_5yr_inputs.txt` is the corresponding variable structure used by the engine's
stepwise regression. Its positions are **0-based input nodes**, matching the engine's
convention. Semicolons separate conceptual variables; commas and hyphen ranges join
multiple dummy nodes belonging to one variable:

```text
0; 1; 2, 3; 4-7; 8; 9; 10-12; 13-15; 16; 17; 18; 19; 20; 21
```

This defines 14 conceptual predictors from 22 input nodes. In particular:

- Nodes 2–3 are one Gleason variable.
- Nodes 4–7 are one T-category variable.
- Nodes 10–12 are one race/ethnicity variable.
- Nodes 13–15 are one marital-status variable.

The curated key and input-structure files are intentionally not regenerated with
`mkdataset.py --key --inputs`. The CSV already contains dummy variables, so automatic
generation would list each dummy as a separate conceptual variable and stepwise regression
could select only part of a clinical category. The curated files preserve the intended
grouping and the deliberately chosen reference categories.

Because the outcome prevalence is only 2.96%, classification accuracy alone is
misleading: an always-negative classifier would be 97.04% accurate. Model assessment
must emphasize held-out ROC area with its confidence interval, sensitivity, specificity,
and calibration. The decision threshold should be selected for the clinical purpose, not
assumed to be 0.5.

## Reproduction

The builder requires `pandas` and `pyreadstat`:

```sh
python3 build_five_year_pc_mortality_csv.py
python3 audit_five_year_pc_mortality_csv.py
```

It asserts the expected row count, event count, absence of missing values, recognized
staging codes, and binary outcome. These assertions are intended to make changes in the
source or cohort definition fail visibly rather than silently produce a different study.

The corrected CSV was also passed through the actual `neuron-3.0` `mkdataset.py` tool.
The tool confirmed:

- 226,679 rows recorded
- 23 total columns
- 22 input nodes and one output node
- Every column completely populated

The independent audit script rereads the source, resolves every saved source-row
identifier, independently recomputes all 23 model values, checks the state-FIPS match,
proves patient uniqueness, verifies all physical CSV row widths, and verifies that the
key/input structure covers nodes 0-21 exactly once. It confirmed 226,679 unique patients,
6,705 independently recomputed events, and exact source-to-model agreement within CSV
rounding tolerance.

The principal ranges remain:

- Age: 23–106 years
- Natural-log PSA: -2.30259–4.58497 (raw PSA 0.1–98.0)
- Diagnosis year since 2004: 0–5
- Poverty: 2.32%–38.24%
- Median household income: $27,120–$126,040
- Unemployment: 1.92%–21.21%
- Less than high-school education: 2.04%–38.08%

## Modeling-cohort refinement: T0 exclusion

The source cohort contains two patients coded AJCC T0 (no evidence of a
primary tumor). Neither had a recorded prostate-cancer death within five
years. T0 is biologically distinct from T1 and therefore must not be merged
into the T1 reference category. At the same time, two observations cannot
support estimation of a separate T0 effect; the T0 indicator was identically
zero in the 40,000-patient regression sample and made its encoded information
matrix singular.

The analysis cohort will therefore be restricted to patients with an
identified primary prostate tumor, AJCC T1–T4. The two T0 records will be
excluded on the basis of their staging category, not their observed outcomes.
All previously frozen development/test assignments for the remaining patients
will be preserved; the split will not be redrawn after this exclusion. The
cohort build, independent audit, and reported partition counts must be updated
before the next model fit.

## Development and locked-test construction for reporting

The evaluation unit is county rather than patient. Counties were kept intact
so that no county contributed patients to both model development and the
locked test. Neuron generated candidate county-disjoint allocations with seed
42 while balancing sample size and outcome prevalence. A 10% candidate
produced a geographically concentrated test dominated by Los Angeles County,
so a 20% candidate was examined and accepted because it provided broader
geographic coverage while retaining a large development cohort.

Before the T0 refinement, the accepted allocation contained 181,440 patients
from 544 counties in development and 45,239 patients from 68 counties in the
locked test. The primary estimand is patient-weighted discrimination among
eligible patients from counties absent during model development. Within the
development partition, model selection used county-disjoint cross-validation;
the locked patients were excluded from neural architecture, optimizer,
stopping-rule, and sample-size decisions.

The locked allocation was not completely untouched: logistic performance on
the 10% and 20% candidate allocations was inspected before the 20% allocation
was accepted. The final test should therefore be described as held out from
neural-network development, with this prior logistic inspection disclosed,
rather than as a pristine fully prespecified confirmatory test. Row identities
for the accepted allocation are recorded in
`runs/202608121513/cv_locked_predictions.csv`.

## Planned analyses and sensitivity checks

Before results are used in a talk or manuscript, consider:

1. Compare logistic regression with the neural network on the same held-out records.
2. Report ROC area and confidence interval, not accuracy alone.
3. Examine the condition number and Wald tests, especially for the socioeconomic inputs.
4. Inspect annual event rates and fit a model without diagnosis year.
5. Compare raw versus nonlinear age effects.
6. Consider whether M1 subcategories should be restored.
7. Evaluate performance within race/ethnicity groups and across SEER registries.
8. Use a temporal validation split if feasible, rather than relying only on random
   train/test allocation.
9. Compare the complete-case analysis with a principled missing-data analysis.
10. Confirm the PSA upper-bound coding and the exact source/vintage of the socioeconomic
    attributes.
11. Treat any treatment-effect interpretation as out of scope without an explicit causal
    design.
