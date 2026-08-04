# Large-cohort evaluation notes

Status: **working notes, not an approved implementation plan**  
Acceptance case: SEER prostate-cancer cohort (~226,000–250,000 rows)

## Why this needs a separate protocol

Training one network iteration is linear in the number of rows, but a complete
model-selection procedure multiplies that cost:

```text
folds
× architectures grown
× architectures pruned
× optimizer probes
× iterations per trial
+ locked-development refit
```

The Civic Choice acceptance run has 6,000 rows. Five-fold nested OBD over the
full SEER cohort would make every iteration roughly forty times more expensive
before those procedural multipliers are applied. A method that is scalable per
iteration can still be impractical as a complete selection procedure.

The recent OBD eligibility work also establishes a non-negotiable rule:

> A fitted model must reach a meaningful stopping condition. Reaching
> `max_iterations` is failure to converge, not a successful fit.

Large-cohort cost cannot be controlled by silently stopping unfinished models.

## Test-set size should be justified, not conventional

A default 25% holdout is not automatically appropriate for a quarter-million
rows.

At roughly 3% event prevalence:

- 250,000 rows contain about 7,500 events;
- a 10% locked test contains about 25,000 rows and 750 events;
- a 25% locked test contains about 62,500 rows and 1,875 events.

The smaller test may already estimate overall AUC precisely. The correct size
must be determined from:

- required AUC precision;
- required event count;
- subgroup-specific performance claims;
- cluster structure; and
- the population to which the result is meant to generalize.

Subgroup and cluster coverage may matter more than the raw fraction. For
example, a metastatic-disease analysis or an unseen-county claim requires
adequate representation of those units, not merely a large row count.

## Decide the population claim first

Two different questions require different partitions:

### New patients from known counties

A patient-level holdout may estimate performance for future patients drawn from
the same county mixture. County-level shared covariates still create clustered
observations, so ordinary independent-row inference may remain invalid.

### Patients from unseen counties

Counties must remain indivisible across development and test. This estimates
generalization to areas the model never encountered and is normally the harder
claim.

Group separation prevents leakage; it does not by itself make patient rows
independent. The inferential method must match the sampling unit.

## Candidate staged design

```text
Full cohort
│
├── Locked final test
│   ├── sized from precision and event requirements
│   ├── never used for model or architecture selection
│   └── group-aware when the target is unseen counties
│
└── Development cohort
    │
    ├── Representative architecture-selection subset
    │   ├── outcome/subgroup balanced as required
    │   ├── initial candidate: roughly 20,000–40,000 rows
    │   └── used for optimizer and OBD investigation
    │
    └── Remaining development rows
        └── used in the final fit after the procedure is frozen
```

Proposed workflow:

1. State the population claim and sampling unit.
2. Size and lock the final test using precision and subgroup-event
   requirements, not a default fraction.
3. Draw a representative subset from development data for optimizer and
   architecture selection.
4. Run OBD on progressively larger selection samples.
5. Repeat enough deterministic selections to assess stability.
6. Freeze the optimizer rule, architecture, and stopping configuration.
7. Fit that frozen procedure on the full development cohort.
8. Require a meaningful stopping condition; ceiling exhaustion is a loud
   failure.
9. Score once on the untouched locked test.
10. Use cluster-aware inference when the sampling units are clustered.

## Progressive-sample architecture stability

A smaller selection sample may favor an architecture appropriate to that sample
size. More development data can support a larger model. Therefore, do not
assume that an architecture selected on 10,000 rows remains optimal at 200,000.

Measure an architecture learning curve:

| Selection rows | Optimizer | Selected hidden | Validation AUC | Stop reason | Runtime |
|---:|---|---:|---:|---|---:|
| 5,000 | — | — | — | — | — |
| 10,000 | — | — | — | — | — |
| 20,000 | — | — | — | — | — |
| 40,000 | — | — | — | — | — |

If the selected architecture and validation performance stabilize, that is
empirical justification for ending architecture search before using the entire
development cohort. If they continue changing, the selection subset is too
small or the procedure is unstable.

## What not to do

- Do not run five-fold nested OBD over the full cohort by reflex.
- Do not hold out 25% merely because 25% is a familiar default.
- Do not use the locked test to choose optimizer, architecture, stopping
  settings, or sample size.
- Do not accept `max_iterations` as convergence to save time.
- Do not claim independent-row DeLong inference for county-clustered patients.
- Do not assume group-aware splitting solves cluster-aware inference.
- Do not freeze a small-sample architecture without measuring stability as the
  selection sample grows.

## Open decisions

- What precision and subgroup guarantees should size the locked SEER test?
- Is the primary claim about new patients from known counties or unseen
  counties?
- Which variables define the grouping/sampling unit?
- What selection-sample sizes should the progressive schedule use?
- How many deterministic repetitions are needed to call architecture stable?
- Should progressive-sample selection become a first-class neuron workflow or
  remain a documented analysis protocol?
- What cluster-aware locked-test inference will replace ordinary DeLong?
- Can the final full-development fit reach a meaningful stopping condition in
  practical time with the current full-batch optimizers?

## Acceptance principle

SEER should be the acceptance test for a general large-cohort evaluation
protocol, not receive a one-off shortcut. The final protocol should be general
over event prevalence, subgroup structure, clustering, and cohort size.

