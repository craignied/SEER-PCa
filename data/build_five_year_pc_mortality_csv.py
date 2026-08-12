#!/usr/bin/env python3
"""Build the audited 2004-2009 five-year PC mortality modeling dataset.

This builder preserves patient/tumor identity until all relational checks pass.
The 2017 formatted source contains a faulty county-name socioeconomic merge:
patients in counties such as Middlesex were repeated for same-named counties in
other states. We retain only the FIPS whose state matches the SEER registry and
require exactly one matched row per registry/patient before identifiers are
removed from the model CSV.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd
import pyreadstat


IDENTITY_COLUMNS = ["reg", "pubcsnum", "rec_no", "seq_num", "st_cnty", "fips"]
SOURCE_COLUMNS = IDENTITY_COLUMNS + [
    "year",
    "dead",
    "deadofpc",
    "srv_time_mon",
    "age",
    "psa",
    "gleason",
    "dajcct",
    "dajccn",
    "dajccm",
    "ethnew",
    "origrecb",
    "mar_stat",
    "previouscancer",
    "poverty",
    "income",
    "unemployment",
    "highschool",
]
MODEL_SOURCE_COLUMNS = [
    "age",
    "psa",
    "gleason",
    "dajcct",
    "dajccn",
    "dajccm",
    "ethnew",
    "origrecb",
    "mar_stat",
    "previouscancer",
    "poverty",
    "income",
    "unemployment",
    "highschool",
]

# SEER registry code -> state FIPS. Each registry in this release lies within
# one state, including the metropolitan and residual-area registries.
REGISTRY_STATE_FIPS = {
    1: 2,    # Alaska
    2: 9,    # Connecticut
    3: 6,    # Greater California
    4: 13,   # Greater Georgia
    5: 15,   # Hawaii
    6: 19,   # Iowa
    7: 21,   # Kentucky
    8: 6,    # Los Angeles
    9: 22,   # Louisiana
    10: 13,  # Metropolitan Atlanta
    11: 26,  # Metropolitan Detroit
    12: 34,  # New Jersey
    13: 35,  # New Mexico
    14: 13,  # Rural Georgia
    15: 6,   # San Francisco-Oakland
    16: 6,   # San Jose-Monterey
    17: 53,  # Seattle/Puget Sound
    18: 49,  # Utah
}

OUTPUT_COLUMNS = [
    "age_years",
    "ln_psa",
    "gleason_7",
    "gleason_8_to_10",
    "t_stage_t0",
    "t_stage_t2",
    "t_stage_t3",
    "t_stage_t4",
    "n_stage_n1",
    "m_stage_m1",
    "race_black",
    "race_hispanic",
    "race_other",
    "marital_never_married_or_domestic_partner",
    "marital_divorced_or_separated",
    "marital_widowed",
    "previous_cancer",
    "diagnosis_year_since_2004",
    "poverty_percent",
    "median_household_income_dollars",
    "unemployment_percent",
    "less_than_high_school_percent",
    "pc_death_within_5_years",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("seer-prostate-5-8-17-formatted.dta"),
        help="source Stata dataset",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("seer_pc_5yr_mortality_2004_2009.csv"),
        help="numeric model-source CSV to create",
    )
    parser.add_argument(
        "--audit-index",
        type=Path,
        default=Path("seer_pc_5yr_audit_index.csv"),
        help="identity-preserving audit index to create",
    )
    return parser.parse_args()


def read_source(source: Path) -> pd.DataFrame:
    """Read required columns, preserve source-row position, and coerce numeric data."""
    frame, _ = pyreadstat.read_dta(
        str(source),
        usecols=SOURCE_COLUMNS,
        encoding="latin1",
        apply_value_formats=False,
        disable_datetime_conversion=True,
    )
    frame.insert(0, "source_row", range(len(frame)))
    for column in SOURCE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def five_year_outcome(source: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Return the PC-death event and known-five-year-status masks."""
    event = source["deadofpc"].eq(1) & source["srv_time_mon"].le(60)
    competing_death = (
        source["dead"].eq(1)
        & source["deadofpc"].eq(0)
        & source["srv_time_mon"].le(60)
    )
    known = event | competing_death | source["srv_time_mon"].ge(60)
    return event, known


def select_one_valid_row_per_patient(source: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Apply clinical completeness gates and repair the faulty county-name join."""
    event, outcome_known = five_year_outcome(source)
    no_blanks = source[MODEL_SOURCE_COLUMNS].notna().all(axis=1)
    stage_known = (
        ~source["dajcct"].isin([1, 21])
        & ~source["dajccn"].isin([10, 11])
        & ~source["dajccm"].isin([7, 8])
    )
    demographics_known = source["ethnew"].ne(3) & source["mar_stat"].ne(5)
    pre_linkage = (
        source["year"].between(2004, 2009)
        & outcome_known
        & no_blanks
        & stage_known
        & demographics_known
    )

    candidates = source.loc[pre_linkage].copy()
    if len(candidates) != 299_534:
        raise ValueError(f"expected 299534 pre-linkage rows, found {len(candidates)}")
    if candidates[IDENTITY_COLUMNS].isna().any().any():
        raise ValueError("candidate identity or geography contains missing values")

    registry_codes = set(candidates["reg"].astype(int).unique())
    if not registry_codes.issubset(REGISTRY_STATE_FIPS):
        raise ValueError(f"unmapped registry codes: {registry_codes - REGISTRY_STATE_FIPS.keys()}")
    if not candidates["fips"].map(float.is_integer).all():
        raise ValueError("FIPS contains noninteger values")

    expected_state = candidates["reg"].astype(int).map(REGISTRY_STATE_FIPS)
    observed_state = candidates["fips"].astype(int) // 1000
    candidates["state_fips_matches_registry"] = observed_state.eq(expected_state)

    # The formatted source's faulty join may create 2-5 county-name matches.
    # Every registry/patient must have exactly one row in the correct state.
    match_counts = candidates.groupby(["reg", "pubcsnum"], sort=False)[
        "state_fips_matches_registry"
    ].sum()
    if len(match_counts) != 226_679:
        raise ValueError(f"expected 226679 candidate patients, found {len(match_counts)}")
    bad_match_counts = match_counts[match_counts.ne(1)]
    if not bad_match_counts.empty:
        raise ValueError(
            f"{len(bad_match_counts)} patients do not have exactly one state-matched FIPS"
        )

    selected = candidates.loc[candidates["state_fips_matches_registry"]].copy()
    selected_event = event.loc[selected.index].astype("int8")
    if len(selected) != 226_679:
        raise ValueError(f"expected 226679 corrected rows, found {len(selected)}")
    if selected.duplicated(["reg", "pubcsnum"]).any():
        raise ValueError("corrected cohort contains repeated patients")
    if selected.duplicated(["reg", "pubcsnum", "rec_no", "seq_num"]).any():
        raise ValueError("corrected cohort contains repeated tumor records")
    if int(selected_event.sum()) != 6_705:
        raise ValueError(f"expected 6705 events, found {int(selected_event.sum())}")
    return selected, selected_event


def validate_source_codes(raw: pd.DataFrame) -> None:
    """Reject any known categorical code not handled by the planned recodes."""
    allowed = {
        "gleason": set(range(2, 11)),
        "dajcct": {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19},
        "dajccn": set(range(1, 10)),
        "dajccm": set(range(1, 7)),
        "ethnew": {0, 1, 2},
        "origrecb": {1, 2},
        "mar_stat": {1, 2, 3, 4, 6, 7},
        "previouscancer": {0, 1},
    }
    for column, valid in allowed.items():
        observed = set(raw[column].astype(int).unique())
        if not observed.issubset(valid):
            raise ValueError(f"unexpected {column} codes: {sorted(observed - valid)}")


def encode_model_inputs(raw: pd.DataFrame, event: pd.Series) -> pd.DataFrame:
    """Create the documented 22 numeric inputs and final binary outcome."""
    validate_source_codes(raw)
    hispanic = raw["origrecb"].eq(2)
    output = pd.DataFrame(index=raw.index)
    output["age_years"] = raw["age"].astype(int)
    output["ln_psa"] = raw["psa"].map(math.log)
    output["gleason_7"] = raw["gleason"].eq(7).astype("int8")
    output["gleason_8_to_10"] = raw["gleason"].ge(8).astype("int8")
    output["t_stage_t0"] = raw["dajcct"].eq(2).astype("int8")
    output["t_stage_t2"] = raw["dajcct"].between(8, 12).astype("int8")
    output["t_stage_t3"] = raw["dajcct"].between(13, 16).astype("int8")
    output["t_stage_t4"] = raw["dajcct"].between(17, 19).astype("int8")
    output["n_stage_n1"] = raw["dajccn"].between(2, 9).astype("int8")
    output["m_stage_m1"] = raw["dajccm"].between(2, 6).astype("int8")
    output["race_black"] = (~hispanic & raw["ethnew"].eq(1)).astype("int8")
    output["race_hispanic"] = hispanic.astype("int8")
    output["race_other"] = (~hispanic & raw["ethnew"].eq(2)).astype("int8")
    output["marital_never_married_or_domestic_partner"] = (
        raw["mar_stat"].isin([4, 6]).astype("int8")
    )
    output["marital_divorced_or_separated"] = raw["mar_stat"].isin([1, 3]).astype("int8")
    output["marital_widowed"] = raw["mar_stat"].eq(7).astype("int8")
    output["previous_cancer"] = raw["previouscancer"].astype("int8")
    output["diagnosis_year_since_2004"] = (raw["year"] - 2004).astype("int8")
    output["poverty_percent"] = raw["poverty"] / 100.0
    output["median_household_income_dollars"] = (raw["income"] * 10).astype(int)
    output["unemployment_percent"] = raw["unemployment"] / 100.0
    output["less_than_high_school_percent"] = raw["highschool"] / 100.0
    output["pc_death_within_5_years"] = event
    output = output[OUTPUT_COLUMNS]
    validate_encoded_output(output)
    return output


def validate_encoded_output(output: pd.DataFrame) -> None:
    """Validate row count, binary groups, positions, ranges, and exclusivity."""
    if list(output.columns) != OUTPUT_COLUMNS:
        raise ValueError("model columns are not in the prescribed order")
    if len(output) != 226_679 or output.isna().any().any():
        raise ValueError("model output has the wrong size or contains missing values")
    if int(output.iloc[:, -1].sum()) != 6_705:
        raise ValueError("model outcome event count is wrong")

    binary_columns = OUTPUT_COLUMNS[2:17] + [OUTPUT_COLUMNS[-1]]
    for column in binary_columns:
        if not output[column].isin([0, 1]).all():
            raise ValueError(f"{column} is not binary")
    for columns, name in [
        (["gleason_7", "gleason_8_to_10"], "Gleason"),
        (["t_stage_t0", "t_stage_t2", "t_stage_t3", "t_stage_t4"], "T stage"),
        (["race_black", "race_hispanic", "race_other"], "race/ethnicity"),
        (
            [
                "marital_never_married_or_domestic_partner",
                "marital_divorced_or_separated",
                "marital_widowed",
            ],
            "marital status",
        ),
    ]:
        if output[columns].sum(axis=1).gt(1).any():
            raise ValueError(f"mutually exclusive {name} indicators overlap")
    if not output["age_years"].between(0, 120).all():
        raise ValueError("age outside audit range")
    if not output["diagnosis_year_since_2004"].between(0, 5).all():
        raise ValueError("centered diagnosis year outside 0-5")


def write_audit_index(raw: pd.DataFrame, event: pd.Series, path: Path) -> None:
    """Write identifiers and geography used for independent row-level auditing."""
    audit = raw[["source_row"] + IDENTITY_COLUMNS + ["year"]].copy()
    audit["pc_death_within_5_years"] = event.to_numpy()
    audit.to_csv(path, index=False, lineterminator="\n")


def main() -> None:
    """Build and save the corrected model CSV and identity audit index."""
    args = parse_args()
    source = read_source(args.source)
    selected, event = select_one_valid_row_per_patient(source)
    analysis = encode_model_inputs(selected, event)
    analysis.to_csv(args.output, index=False, lineterminator="\n", float_format="%.8g")
    write_audit_index(selected, event, args.audit_index)
    print(f"Wrote {len(analysis):,} unique patients and {len(analysis.columns)} columns")
    print(f"Outcome events: {int(event.sum()):,} ({event.mean():.4%})")
    print("Rejected 72,855 wrong-state rows from the faulty county-name linkage")
    print(f"Model CSV: {args.output}")
    print(f"Audit index: {args.audit_index}")


if __name__ == "__main__":
    main()
