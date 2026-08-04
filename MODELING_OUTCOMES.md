# Construction of the SEER Five-Year Prostate Cancer Mortality Dataset

## Study objective

The dataset was constructed to model prostate cancer-specific mortality within 5 years
of diagnosis among men diagnosed with prostate cancer from 2004 through 2009. The model
uses clinical, demographic, and area socioeconomic information associated with the
diagnostic record. The resulting dataset is suitable for binary logistic regression and
neural network analysis in `neuron-3.0`.

The target population is:

> Men diagnosed with prostate cancer from 2004 through 2009 who had an ascertainable
> 5-year outcome and complete staging, PSA, Gleason, demographic, and area socioeconomic
> information.

## Data source

The source was a formatted SEER prostate cancer dataset containing 1,708,661 tumor
records and 167 variables for diagnoses from 1973 through 2014. The dataset was available
in Stata (`.dta`) and R (`.rds`) formats. Construction used the Stata file because it
retained the variable and value-label metadata needed to interpret coded fields.

SEER records are tumor based. A patient was identified by the combination of SEER
registry and `pubcsnum`, the SEER patient identification number. Tumor record number and
sequence number were retained during construction for record-level verification. These
identifiers were removed from the final modeling matrix.

## Study period

Diagnoses were restricted to 2004 through 2009. The 2004 start provided a cohort with
Collaborative Stage variables and substantially better PSA and Gleason availability than
earlier years. The 2009 endpoint allowed up to 5 years of follow-up within a dataset
extending through 2014.

Diagnosis year remained a model input to adjust for changes in detection, staging,
treatment practice, supportive care, and registry coding during the study period. It was
centered at 2004, producing values from 0 through 5.

## Geographic and socioeconomic linkage

Area socioeconomic variables were linked to each cancer record using a 5-digit
state-county FIPS code. Each of the 18 SEER registries was mapped to its corresponding
state FIPS code. A socioeconomic record was retained only when the state component of its
FIPS code agreed with the state represented by the SEER registry.

The linkage procedure required exactly one state-consistent FIPS record for each
registry-patient combination. The final cohort was also required to contain no repeated
registry-patient identifiers and no repeated combinations of registry, patient, tumor
record number, and sequence number. These constraints established one modeling exemplar
per selected patient.

The included socioeconomic variables were:

- Area poverty percentage
- Area median household income
- Area unemployment percentage
- Area percentage of adults with less than high-school education

SEER percentage fields contain 2 implied decimal places and were divided by 100. Median
household income is stored in tens of dollars and was multiplied by 10. These measurements
describe the patient's area of residence, not the patient's individual income, employment,
poverty status, or education.

## Outcome definition

The binary outcome was prostate cancer-specific death within 5 years of diagnosis. It was
stored as the final column, `pc_death_within_5_years`.

The outcome was coded as follows:

- `1`: Death from prostate cancer with recorded survival of 60 months or less
- `0`: At least 60 months of observed survival without prostate cancer death, or death
  from another cause within 60 months

Patients alive at last contact with less than 60 months of follow-up were excluded because
their 5-year outcome was not known. A death from another cause within 5 years was considered
a non-event for the binary question of whether prostate cancer death occurred during that
interval.

This endpoint is a fixed-horizon binary outcome. It is not a formal competing-risks or
cause-specific hazards analysis.

## Cohort selection

State-consistent linkage identified 349,280 records diagnosed from 2004 through 2009.
Eligibility was then determined sequentially:

| Selection step | Remaining patients or records |
|---|---:|
| Diagnosis from 2004 through 2009 with state-consistent FIPS | 349,280 |
| Ascertainable 5-year outcome | 338,746 |
| Age available | 338,741 |
| PSA available | 285,986 |
| Gleason score available | 259,855 |
| Known AJCC T category | 257,287 |
| Known AJCC N category | 249,392 |
| Known AJCC M category | 248,398 |
| Known race/ethnicity | 245,046 |
| Known marital status | 226,710 |
| Previous-cancer status available | 226,679 |
| All 4 socioeconomic measures available | 226,679 |

The final cohort contained 226,679 unique patients:

- 6,705 prostate cancer deaths within 5 years
- 219,974 non-events
- Event prevalence of 2.9579%

The restriction to complete diagnostic and socioeconomic information defines the intended
population for inference. The resulting model should not be described as applying to all
men with prostate cancer without additional missing-data analyses and external validation.

## Predictor construction

The final model matrix contained 22 numeric input nodes representing 14 conceptual
predictors.

### Age

Age at diagnosis was retained as a numerical variable in years.

### PSA

PSA was transformed using the natural logarithm:

```text
ln_psa = ln(PSA)
```

The logarithmic transformation reduced right skew and limited the influence of very high
PSA measurements. A 1-unit increase in `ln_psa` represents multiplication of PSA by
approximately 2.718. A doubling of PSA increases `ln_psa` by approximately 0.693.

### Gleason score

Gleason score was treated as an ordinal clinical category rather than a continuous linear
measurement. It was grouped as:

- Gleason 2 through 6, reference category
- Gleason 7
- Gleason 8 through 10

The model matrix therefore contained 2 Gleason indicators.

### AJCC T category

Known AJCC T categories were collapsed to T0, T1, T2, T3, and T4. T1 was the reference
category. Detailed substages and not-otherwise-specified values were assigned to their
corresponding major category. TX and not-applicable values were excluded.

The model matrix contained indicators for T0, T2, T3, and T4.

### AJCC N category

Known AJCC N categories were collapsed to N0 and N1. N0 was the reference category. NX
and not-applicable values were excluded. The model matrix contained 1 N1 indicator.

### AJCC M category

Known AJCC M categories were collapsed to M0 and M1. M0 was the reference category. M1a,
M1b, M1c, and M1 not otherwise specified were included in M1. MX and not-applicable values
were excluded. The model matrix contained 1 M1 indicator.

### Race and ethnicity

SEER race and Hispanic-origin variables were combined into mutually exclusive categories:

- White, reference category
- Black
- Hispanic
- Other

Hispanic origin took precedence over recorded race, corresponding to Hispanic of any
race. Patients with unknown race/ethnicity were excluded. The model matrix contained
indicators for Black, Hispanic, and Other.

### Marital status

Marital status was grouped as:

- Married, reference category
- Never married or unmarried/domestic partner
- Divorced or separated
- Widowed

Patients with unknown marital status were excluded. The model matrix contained 3 marital
status indicators.

### Previous cancer

Previous cancer was coded as a binary input, with no previous cancer as the reference.

### Diagnosis year

Diagnosis year was centered at 2004:

```text
diagnosis_year_since_2004 = diagnosis year - 2004
```

The variable ranged from 0 for a 2004 diagnosis to 5 for a 2009 diagnosis. Centering
improved numerical conditioning and made the model intercept refer to 2004.

### Socioeconomic variables

Poverty, median household income, unemployment, and less-than-high-school education were
retained as separate continuous variables. Their simultaneous inclusion permits assessment
of their adjusted associations with 5-year prostate cancer mortality. Because these
variables describe related aspects of area socioeconomic conditions, regression analyses
should report correlations, individual Wald tests, and the information-matrix condition
number.

## Final column structure

The modeling CSV and neUROn data file contain the following 23 columns:

| Column | Variable |
|---:|---|
| 1 | Age at diagnosis |
| 2 | Natural logarithm of PSA |
| 3 through 4 | Gleason group indicators |
| 5 through 8 | AJCC T-category indicators |
| 9 | AJCC N1 indicator |
| 10 | AJCC M1 indicator |
| 11 through 13 | Race/ethnicity indicators |
| 14 through 16 | Marital-status indicators |
| 17 | Previous cancer |
| 18 | Diagnosis year centered at 2004 |
| 19 | Area poverty percentage |
| 20 | Area median household income |
| 21 | Area unemployment percentage |
| 22 | Area percentage with less than high-school education |
| 23 | Prostate cancer death within 5 years |

The outcome occupies the final column, as required by `mkdataset.py` and `neuron-3.0`.

## Regression-variable grouping

The 22 input nodes represent 14 conceptual predictors. The stepwise-regression input
structure is:

```text
0; 1; 2, 3; 4-7; 8; 9; 10-12; 13-15; 16; 17; 18; 19; 20; 21
```

The engine uses 0-based input-node positions, while the human-readable key uses 1-based
data-column positions. Grouping prevents stepwise regression from selecting only part of
a categorical variable. For example, the 4 T-category indicators constitute one
conceptual predictor.

## Variables excluded from the model

Survival time, vital status, cause of death, and derived death-classification variables
were used only to establish outcome status and were excluded from the predictors.

Treatment variables, including radical prostatectomy and radiation, were excluded because
the intended prediction point precedes treatment selection. Including them would change
the question to post-treatment prognosis and could confound treatment selection with
treatment effect.

Overall AJCC stage, Collaborative Stage extension, derived node and metastasis recodes,
summary stage, and general tumor grade were excluded because they duplicate information
represented by T, N, M, and Gleason. Record identifiers and geographic codes were also
excluded from the modeling matrix.

## Data files

The analysis files are:

- `seer_pc_5yr_mortality_2004_2009.csv`: Headered numeric modeling dataset
- `seer_pc_5yr_data.txt`: Headerless data loaded by `neuron-3.0`
- `seer_pc_5yr_key.txt`: Human-readable map of data columns and reference categories
- `seer_pc_5yr_inputs.txt`: Grouped input-node definitions for stepwise regression
- `seer_pc_5yr_audit_index.csv`: Source-row, patient, tumor, and FIPS audit trail
- `build_five_year_pc_mortality_csv.py`: Reproducible dataset builder
- `audit_five_year_pc_mortality_csv.py`: Independent source-to-output audit

## Data validation

The builder required:

- Exactly one state-consistent FIPS match per selected patient
- Unique registry-patient identifiers
- Unique registry-patient-record-sequence identifiers
- Recognized values for every categorical source field
- Complete values for every selected predictor
- Mutually exclusive categorical indicator patterns
- A binary outcome in the final column
- Exact agreement with the prespecified column order

An independent audit reread the source data, resolved each saved source-row identifier,
recomputed every eligibility condition and all 23 output values, verified patient
uniqueness and state-FIPS concordance, and checked the key and grouped input structure.
The completed audit confirmed:

- 226,679 unique patients
- 6,705 independently calculated events
- Exact source-to-model agreement within CSV rounding tolerance
- Complete and nonoverlapping coverage of input nodes 0 through 21

The modeling CSV was then processed with `mkdataset.py`. The resulting neUROn file
contained 226,679 rows, 22 input nodes, and 1 binary output. A streaming comparison
confirmed numerical agreement between every value in the headered CSV and the headerless
neUROn data file.

## Train-test splitting completed

Two train-test splitting checks were run in `neuron-3.0` and recorded in `neuron.log`.
The first was a diagnostic split stratified on the outcome and input column 10. It
produced 170,010 training exemplars and 56,669 test exemplars. This split was superseded
by the group-aware split described below.

The selected split was group aware. Records with identical values for the 4 area
socioeconomic inputs (data columns 19 through 22) were assigned to the same partition.
This prevents records representing the same socioeconomic-area profile from appearing
in both training and test sets.

The group-aware split contained:

| Partition | Total | Non-events | Events | Event prevalence |
|---|---:|---:|---:|---:|
| Training | 170,016 | 164,987 | 5,029 | 2.95796% |
| Test | 56,663 | 54,987 | 1,676 | 2.95784% |
| Total | 226,679 | 219,974 | 6,705 | 2.95793% |

There were 612 socioeconomic groups: 386 in training and 226 in testing. No group
occurred in both partitions. The requested test-set size was 56,663 and was achieved
exactly in this run, although group-aware splitting generally can only approximate a
target size because groups are indivisible.

The split summary is durable in `neuron.log`, but no partition-membership file, random
seed, fitted model, or model results are currently present in this directory. Therefore,
after restarting `neuron-3.0`, the data must be loaded and the group-aware split repeated
unless the active program session was saved elsewhere. A repeated random split is not
guaranteed to assign the same records to each partition.

## Statistical considerations

Because the event prevalence is 2.96%, an always-negative classifier would be 97.04%
accurate. Classification accuracy alone is therefore uninformative. Model assessment
should emphasize held-out ROC area with its confidence interval, sensitivity, specificity,
and calibration.

The final test set must be separated at the patient level. Any scaling or normalization
must be estimated from the training set and then applied unchanged to the test set. If
model architecture, transformations, or variable selection are tuned using a validation
set, the final test set should remain untouched until the analysis is prespecified.

## Current modeling status and restart point

Dataset construction, independent auditing, conversion to the `neuron-3.0` input format,
and the group-aware splitting check are complete. No fitted regression or neural-network
model, variable-selection result, performance estimate, or calibration result has yet
been recorded.

On restart:

1. Load `seer_pc_5yr_data.txt` as a raw dataset with 22 inputs and 1 binary output.
2. Create a group-aware train-test split using input columns 19 through 22 as the grouping
   variables and a target test size of 56,663.
3. Before fitting or tuning models, save enough split information to reproduce the exact
   partition, such as the random seed or record-level partition membership.
4. Estimate all preprocessing parameters from the training partition only.
5. Preserve the test partition untouched until the modeling procedure is finalized.
