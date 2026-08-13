#!/usr/bin/env python3
"""Build a reproducible outcome-stratified sample from a frozen locked split."""

import argparse
import csv
import random
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--locked-predictions", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    args = parser.parse_args()

    if args.sample_size < 2:
        raise ValueError("sample size must be at least 2")

    with args.locked_predictions.open(newline="") as handle:
        locked_reader = csv.DictReader(handle)
        required = {"row", "cluster", "outcome"}
        if not required.issubset(locked_reader.fieldnames or []):
            raise ValueError("locked-predictions file lacks row/cluster/outcome")
        locked_rows = {int(row["row"]) for row in locked_reader}

    lines = args.data.read_text().splitlines()
    if len(lines) != 226_679:
        raise ValueError(f"expected 226679 data rows, found {len(lines)}")
    if any(len(line.split()) != 23 for line in lines):
        raise ValueError("every source row must contain 23 columns")
    if locked_rows and (min(locked_rows) < 0 or max(locked_rows) >= len(lines)):
        raise ValueError("locked row outside source-data range")

    development = [i for i in range(len(lines)) if i not in locked_rows]
    if len(development) != 181_440:
        raise ValueError(f"expected 181440 development rows, found {len(development)}")

    by_outcome = {0: [], 1: []}
    for i in development:
        outcome = int(float(lines[i].split()[-1]))
        if outcome not in by_outcome:
            raise ValueError(f"nonbinary outcome on row {i}")
        by_outcome[outcome].append(i)

    target_events = round(args.sample_size * len(by_outcome[1]) / len(development))
    target_non_events = args.sample_size - target_events
    if target_events > len(by_outcome[1]) or target_non_events > len(by_outcome[0]):
        raise ValueError("requested sample exceeds an outcome class")

    rng = random.Random(args.seed)
    selected = sorted(
        rng.sample(by_outcome[0], target_non_events)
        + rng.sample(by_outcome[1], target_events)
    )

    args.output.write_text("".join(lines[i] + "\n" for i in selected))
    with args.index.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["sample_row", "raw_row", "outcome"])
        for sample_row, raw_row in enumerate(selected):
            writer.writerow([sample_row, raw_row, int(float(lines[raw_row].split()[-1]))])

    print(
        f"Wrote {len(selected)} development rows: "
        f"{target_events} events and {target_non_events} non-events"
    )


if __name__ == "__main__":
    main()
