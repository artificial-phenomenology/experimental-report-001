#!/usr/bin/env python
"""Fold a blind adjudicator's resolutions into the consensus files.

Usage:
  python apply_adjudication.py \
      --consensus-dir results_v2 \
      --adjudication results_v2/adjudication.csv \
      --key key_confirmatory_v2_pooled.json

Rewrites consensus_blind.json, consensus_unblinded.json, and
consensus_counts.json in place, replacing each SPLIT cell with the
adjudicator's code. Refuses to overwrite a non-SPLIT cell.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consensus-dir", required=True)
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--key", required=True)
    args = parser.parse_args()

    cdir = Path(args.consensus_dir)
    consensus = json.loads((cdir / "consensus_blind.json").read_text())

    applied = 0
    with open(args.adjudication) as f:
        reader = csv.DictReader(f)
        long_format = reader.fieldnames is not None and \
            {"measure", "value"} <= set(reader.fieldnames)
        for row in reader:
            t = row["transcript_id"]
            if long_format:  # one row per adjudicated (transcript, measure)
                cells = [(row["measure"], row["value"])]
            else:  # wide: every non-annotation column is an adjudicated cell
                cells = [(m, v) for m, v in row.items()
                         if m not in {"transcript_id", "IDENTITY_QUOTE",
                                      "RATIONALE"}]
            for m, val in cells:
                assert consensus[t][m] == "SPLIT", \
                    f"{t} {m} is {consensus[t][m]}, not SPLIT; refusing"
                consensus[t][m] = val.strip()
                applied += 1
    remaining = [(t, m) for t, v in consensus.items()
                 for m, val in v.items() if val == "SPLIT"]
    assert not remaining, f"unresolved SPLIT cells remain: {remaining}"
    print(f"applied {applied} adjudicated cells, 0 SPLITs remain")

    key = json.loads(Path(args.key).read_text())["map"]
    tids = sorted(consensus)
    (cdir / "consensus_blind.json").write_text(json.dumps(consensus, indent=1))
    (cdir / "consensus_unblinded.json").write_text(json.dumps(
        {key[t]: consensus[t] for t in tids}, indent=1))

    measures = list(consensus[tids[0]])
    counts = {}
    for m in measures:
        per = defaultdict(Counter)
        for t in tids:
            per[key[t].split("/")[0]][consensus[t][m]] += 1
        counts[m] = {c: dict(per[c]) for c in sorted(per)}
        print(m, counts[m])
    (cdir / "consensus_counts.json").write_text(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
