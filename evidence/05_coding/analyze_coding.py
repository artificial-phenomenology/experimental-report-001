#!/usr/bin/env python
"""Agreement, consensus, and unblinded condition counts from blind sheets.

Usage (confirmatory run):
  python analyze_coding.py \
      --sheets results_v2/coding_sheet_*.csv \
      --key key_confirmatory_v2_pooled.json \
      --out results_v2

Reads all returned coder sheets, computes per-measure Fleiss' kappa and
unanimity, forms majority consensus (>=2 of 3; cells with no majority are
marked SPLIT for a fourth blind adjudicator), unblinds via the key, and
writes consensus_blind.json, consensus_unblinded.json, and
consensus_counts.json into --out.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

SKIP_COLS = {"transcript_id", "IDENTITY_QUOTE", "NOTES"}


def fleiss_kappa(sheets, tids, measure):
    cats = sorted({s[t][measure].strip() for s in sheets for t in tids})
    idx = {c: j for j, c in enumerate(cats)}
    k = len(sheets)
    table = []
    for t in tids:
        row = [0] * len(cats)
        for s in sheets:
            row[idx[s[t][measure].strip()]] += 1
        table.append(row)
    P_i = [(sum(c * c for c in row) - k) / (k * (k - 1)) for row in table]
    P_bar = sum(P_i) / len(tids)
    p_j = [sum(row[j] for row in table) / (len(tids) * k)
           for j in range(len(cats))]
    P_e = sum(p * p for p in p_j)
    return 1.0 if P_e == 1 else (P_bar - P_e) / (1 - P_e)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheets", nargs="+", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    sheets = []
    for path in args.sheets:
        with open(path) as f:
            sheets.append({r["transcript_id"]: r for r in csv.DictReader(f)})
    tids = sorted(sheets[0])
    assert all(sorted(s) == tids for s in sheets), "sheets cover different ids"
    measures = [c for c in csv.DictReader(open(args.sheets[0])).fieldnames
                if c not in SKIP_COLS]

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    consensus, splits = {}, []
    print(f"{len(sheets)} coders, {len(tids)} transcripts")
    print(f"{'measure':<16}{'fleiss_k':>9}{'unanimous':>11}{'majority':>10}{'split':>7}")
    for m in measures:
        unan = maj = spl = 0
        for t in tids:
            votes = Counter(s[t][m].strip() for s in sheets)
            top, cnt = votes.most_common(1)[0]
            if cnt == len(sheets):
                unan += 1
            elif cnt >= 2:
                maj += 1
            else:
                top = "SPLIT"
                spl += 1
                splits.append((t, m, dict(votes)))
            consensus.setdefault(t, {})[m] = top
        print(f"{m:<16}{fleiss_kappa(sheets, tids, m):>9.3f}"
              f"{unan:>11}{maj:>10}{spl:>7}")

    total = len(tids) * len(measures)
    unani = sum(1 for t in tids for m in measures
                if len({s[t][m].strip() for s in sheets}) == 1)
    print(f"\ncells: {total}, unanimous: {unani} ({100 * unani / total:.0f}%)")
    if splits:
        print("3-way splits needing a blind adjudicator:")
        for t, m, v in splits:
            print(f"  {t} {m}: {v}")

    key = json.loads(Path(args.key).read_text())["map"]
    (out / "consensus_blind.json").write_text(json.dumps(consensus, indent=1))
    (out / "consensus_unblinded.json").write_text(json.dumps(
        {key[t]: consensus[t] for t in tids}, indent=1))

    counts = {}
    for m in measures:
        per = defaultdict(Counter)
        for t in tids:
            per[key[t].split("/")[0]][consensus[t][m]] += 1
        counts[m] = {c: dict(per[c]) for c in sorted(per)}
        print(m, counts[m])
    (out / "consensus_counts.json").write_text(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
