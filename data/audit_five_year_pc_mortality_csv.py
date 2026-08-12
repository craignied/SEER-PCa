#!/usr/bin/env python3
"""Independently audit the corrected SEER five-year mortality artifacts."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import pandas as pd
import pyreadstat


STATE_BY_REGISTRY = {
    1: 2, 2: 9, 3: 6, 4: 13, 5: 15, 6: 19, 7: 21, 8: 6, 9: 22,
    10: 13, 11: 26, 12: 34, 13: 35, 14: 13, 15: 6, 16: 6, 17: 53, 18: 49,
}


def args() -> argparse.Namespace:
    """Parse paths to source and artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("seer-prostate-5-8-17-formatted.dta"))
    parser.add_argument("--csv", type=Path, default=Path("seer_pc_5yr_mortality_2004_2009.csv"))
    parser.add_argument("--index", type=Path, default=Path("seer_pc_5yr_audit_index.csv"))
    parser.add_argument("--key", type=Path, default=Path("seer_pc_5yr_key.txt"))
    parser.add_argument("--inputs", type=Path, default=Path("seer_pc_5yr_inputs.txt"))
    return parser.parse_args()


def expand_input_structure(text: str) -> list[list[int]]:
    """Expand the engine's comma/range variable syntax into node groups."""
    groups: list[list[int]] = []
    for group_text in text.strip().split(";"):
        group: list[int] = []
        for token in group_text.split(","):
            token = token.strip()
            if "-" in token:
                start, stop = (int(value) for value in token.split("-"))
                group.extend(range(start, stop + 1))
            else:
                group.append(int(token))
        groups.append(group)
    return groups


def main() -> None:
    """Recompute selection and transformations, then compare every output value."""
    paths = args()
    source_columns = [
        "reg", "pubcsnum", "rec_no", "seq_num", "st_cnty", "fips", "year",
        "dead", "deadofpc", "srv_time_mon", "age", "psa", "gleason", "dajcct",
        "dajccn", "dajccm", "ethnew", "origrecb", "mar_stat", "previouscancer",
        "poverty", "income", "unemployment", "highschool",
    ]
    source, _ = pyreadstat.read_dta(
        str(paths.source), usecols=source_columns, encoding="latin1",
        apply_value_formats=False, disable_datetime_conversion=True,
    )
    source.insert(0, "source_row", range(len(source)))
    for column in source_columns:
        source[column] = pd.to_numeric(source[column], errors="coerce")

    index = pd.read_csv(paths.index)
    model = pd.read_csv(paths.csv)
    if len(index) != 226_679 or len(model) != 226_679:
        raise AssertionError("artifact row count is not 226679")
    if model.shape[1] != 23 or model.columns[-1] != "pc_death_within_5_years":
        raise AssertionError("model must have 22 inputs and the outcome last")
    if index.duplicated(["reg", "pubcsnum"]).any():
        raise AssertionError("audit index repeats a patient")

    chosen = source.iloc[index["source_row"].astype(int).to_numpy()].reset_index(drop=True)
    identity = ["source_row", "reg", "pubcsnum", "rec_no", "seq_num", "st_cnty", "fips", "year"]
    if not chosen[identity].equals(index[identity].astype(chosen[identity].dtypes.to_dict())):
        raise AssertionError("audit index does not identify the claimed source rows")

    expected_state = chosen["reg"].astype(int).map(STATE_BY_REGISTRY)
    if not ((chosen["fips"].astype(int) // 1000) == expected_state).all():
        raise AssertionError("an audited FIPS does not match its registry state")

    event = chosen["deadofpc"].eq(1) & chosen["srv_time_mon"].le(60)
    competing = (
        chosen["dead"].eq(1)
        & chosen["deadofpc"].eq(0)
        & chosen["srv_time_mon"].le(60)
    )
    if not (event | competing | chosen["srv_time_mon"].ge(60)).all():
        raise AssertionError("audit index contains unknown five-year outcomes")
    if int(event.sum()) != 6_705:
        raise AssertionError("independently calculated event count is not 6705")

    # Independently reconstruct each output column from the selected source rows.
    hispanic = chosen["origrecb"].eq(2)
    expected = pd.DataFrame({
        "age_years": chosen["age"].astype(int),
        "ln_psa": chosen["psa"].map(math.log),
        "gleason_7": chosen["gleason"].eq(7).astype(int),
        "gleason_8_to_10": chosen["gleason"].between(8, 10).astype(int),
        "t_stage_t0": chosen["dajcct"].eq(2).astype(int),
        "t_stage_t2": chosen["dajcct"].between(8, 12).astype(int),
        "t_stage_t3": chosen["dajcct"].between(13, 16).astype(int),
        "t_stage_t4": chosen["dajcct"].between(17, 19).astype(int),
        "n_stage_n1": chosen["dajccn"].between(2, 9).astype(int),
        "m_stage_m1": chosen["dajccm"].between(2, 6).astype(int),
        "race_black": ((~hispanic) & chosen["ethnew"].eq(1)).astype(int),
        "race_hispanic": hispanic.astype(int),
        "race_other": ((~hispanic) & chosen["ethnew"].eq(2)).astype(int),
        "marital_never_married_or_domestic_partner": chosen["mar_stat"].isin([4, 6]).astype(int),
        "marital_divorced_or_separated": chosen["mar_stat"].isin([1, 3]).astype(int),
        "marital_widowed": chosen["mar_stat"].eq(7).astype(int),
        "previous_cancer": chosen["previouscancer"].astype(int),
        "diagnosis_year_since_2004": (chosen["year"] - 2004).astype(int),
        "poverty_percent": chosen["poverty"] / 100,
        "median_household_income_dollars": (chosen["income"] * 10).astype(int),
        "unemployment_percent": chosen["unemployment"] / 100,
        "less_than_high_school_percent": chosen["highschool"] / 100,
        "pc_death_within_5_years": event.astype(int),
    })
    if list(expected.columns) != list(model.columns):
        raise AssertionError("CSV header/order differs from independent reconstruction")
    for column in model.columns:
        difference = (model[column].astype(float) - expected[column].astype(float)).abs().max()
        if difference > 5e-7:
            raise AssertionError(f"{column} differs from source; max absolute difference {difference}")

    with paths.csv.open(newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if len(header) != 23 or any(len(row) != 23 for row in reader):
            raise AssertionError("CSV has a malformed physical row")
    key_lines = paths.key.read_text().splitlines()
    if not key_lines[-1].startswith("Column 23:") or len(key_lines) != 15:
        raise AssertionError("key does not end with the column-23 outcome mapping")
    groups = expand_input_structure(paths.inputs.read_text())
    flat = [node for group in groups for node in group]
    if flat != list(range(22)) or len(groups) != 14:
        raise AssertionError("input groups do not cover nodes 0-21 exactly once")

    print("AUDIT PASSED")
    print("226,679 unique registry/patient identifiers")
    print("6,705 independently recomputed events")
    print("Every model value agrees with its identified source row")
    print("Key and 14-variable/22-node input structure are positionally consistent")


if __name__ == "__main__":
    main()
