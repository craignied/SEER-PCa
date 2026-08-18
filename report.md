# Predicting 5-Year Prostate Cancer Mortality

## Research question

Can information available at diagnosis predict whether a man with prostate cancer will die from the disease within 5 years?

## Dataset

The dataset was derived from the U.S. SEER cancer registry and included 226,679 men diagnosed with prostate cancer from 2004 through 2009. It contained clinical, demographic, and area-level socioeconomic information recorded around diagnosis, along with each patient’s 5-year prostate cancer mortality outcome.

## Input variables

The model used age, PSA, Gleason score, tumor stage (T), lymph-node stage (N), metastatic stage (M), race and ethnicity, marital status, previous cancer, and year of diagnosis. It also used 4 characteristics of the patient’s area of residence: poverty, median household income, unemployment, and the percentage of adults with less than a high-school education.

Race and ethnicity were combined into 4 mutually exclusive groups: non-Hispanic White, non-Hispanic Black, Hispanic of any race, and non-Hispanic Other. Patients with unknown race or ethnicity were excluded.

## Preparing the data for modeling

We included patients whose 5-year outcome could be determined and whose required clinical, demographic, and area-level information was complete. PSA was converted to a logarithmic scale to reduce the influence of very high values, and categorical variables such as stage, Gleason score, race and ethnicity, and marital status were converted into indicator variables that the models could use.

To evaluate the models in a setting that differed geographically from the development data, we kept all patients from the same county together. We initially considered holding out 10% of the patients for testing, but that group came from too few counties. We therefore targeted a 20% test set, which provided broader geographic coverage while leaving a large development set. Because counties could not be divided between groups, the final locked test set contained 45,239 patients (19.96%) from 68 counties; the development set contained 181,440 patients from 544 different counties.

Model development used 5-fold cross-validation. Counties, rather than individual patients, were assigned to folds, and the folds were balanced as closely as possible for patient numbers and prostate cancer deaths. This prevented patients from the same county from appearing in both training and validation data. The locked test patients were excluded while the computational model was developed and refined.

## Modeling approach

We used logistic regression to estimate each patient’s probability of dying from prostate cancer within 5 years. We then compared it with a neural network using the same patients and cross-validation folds. The neural network was implemented in neuron, a neural computational modeling environment begun in 1992 by Craig Niederberger and modernized as neuron 3.0. Its open source repository may be found at [https://github.com/craignied/neuron](https://github.com/craignied/neuron).

The additional neural computation did not improve prediction. In the 40,000-patient comparison, logistic regression performed better in every fold and had a cross-validated area under the ROC curve (AUC) of 0.901, compared with 0.888 for the neural network. The neural network also selected only 1 to 4 hidden nodes, suggesting that little additional complexity was useful. Logistic regression was therefore preferred as the simpler and better-performing model.

## Regression results

Grouped reverse stepwise regression was performed on the 40,000-patient development sample using a removal threshold of *p* = 0.05. The final model retained age, PSA, Gleason group, T stage, N stage, M stage, marital status, previous cancer, and area median household income.


| Predictor                             | Grouped *p*-value |
| ------------------------------------- | ----------------- |
| M stage                               | 1.87 × 10⁻¹³⁸     |
| Gleason group                         | 4.34 × 10⁻¹⁰¹     |
| ln(PSA)                               | 3.03 × 10⁻⁴²      |
| Age at diagnosis                      | 1.11 × 10⁻¹⁹      |
| N stage                               | 1.47 × 10⁻⁷       |
| T stage                               | 5.85 × 10⁻⁵       |
| Marital status                        | 6.01 × 10⁻⁵       |
| Area median household income          | 0.0024            |
| Previous cancer                       | 0.0033            |
| Diagnosis year*                       | 0.0933            |
| Area unemployment*                    | 0.1589            |
| Area less-than-high-school education* | 0.2692            |
| Race and ethnicity*                   | 1.0000            |
| Area poverty*                         | 1.0000            |


*Removed during grouped reverse stepwise regression. The reported values are sequential grouped Wilks *p*-values obtained at different stages of the stepwise path, not estimates from a single fitted model.

In the full development-sample model, marital status was associated with 5-year prostate cancer mortality. Compared with married men, the adjusted odds of prostate cancer death were higher among men who were never married or had a domestic partner (OR 1.30, 95% CI 1.16–1.47), divorced or separated (OR 1.21, 95% CI 1.06–1.38), or widowed (OR 1.23, 95% CI 1.07–1.40).
