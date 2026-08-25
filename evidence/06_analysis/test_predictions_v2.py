#!/usr/bin/env python
"""Score every frozen prediction in PREREGISTRATION_v2.md section 6.

Usage:
  python test_predictions_v2.py

Reads the adjudicated blind consensus
(blind_coding/results_v2/consensus_unblinded.json), the three raw coder
sheets (for the compass-said-first NOTES convention), and the unblinding
key. Writes results/confirmatory_v2_pooled/prediction_scorecard.json and
prints the scorecard, the preregistered Fisher contrasts (section 7), and
the two v1-vs-v2 checks.

v1 reference numbers are the blind consensus in
results/run_20260730_091700/REPORT.md section 6: D SPLICE 10/10;
P1 answered A 6/10, B 5/10.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from scipy.stats import fisher_exact

HERE = Path(__file__).parent
BC = HERE / "blind_coding"

FIRST_RE = re.compile(r"before (any )?other (answer )?content", re.I)
NOT_RE = re.compile(r"was not (spoken|said)", re.I)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def main() -> None:
    consensus = json.loads(
        (BC / "results_v2/consensus_unblinded.json").read_text())
    key = json.loads(
        (BC / "key_confirmatory_v2_pooled.json").read_text())["map"]

    counts: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    for rep_id, codes in consensus.items():
        cond = rep_id.split("/")[0]
        for m, v in codes.items():
            counts[m][cond][v] += 1

    def n(m: str, cond: str, val: str) -> int:
        return counts[m][cond][val]

    # Compass-said-first, from the NOTES convention, majority of 3 coders,
    # among A/B reps whose consensus COMPASS is FIRST_PERSON.
    sheets = []
    for p in sorted((BC / "results_v2").glob("coding_sheet_*.csv")):
        with open(p) as f:
            sheets.append({r["transcript_id"]: r for r in csv.DictReader(f)})
    inv = {v: k for k, v in key.items()}
    first_counts = {"A": 0, "B": 0}
    denom = {"A": 0, "B": 0}
    for rep_id, codes in consensus.items():
        cond = rep_id.split("/")[0]
        if cond not in ("A", "B") or codes["COMPASS"] != "FIRST_PERSON":
            continue
        denom[cond] += 1
        votes = 0
        for s in sheets:
            note = s[inv[rep_id]]["NOTES"]
            if FIRST_RE.search(note):
                votes += 1
            elif not NOT_RE.search(note):
                pass  # note silent on order: not a yes vote
        if votes >= 2:
            first_counts[cond] += 1

    preds = []

    def check(name: str, ok: bool, observed: str) -> None:
        preds.append({"prediction": name, "observed": observed,
                      "result": "PASS" if ok else "FAIL"})

    # IDENTITY
    check("IDENTITY OWN: A >= 27", n("IDENTITY", "A", "OWN") >= 27,
          f"A OWN {n('IDENTITY', 'A', 'OWN')}/30")
    check("IDENTITY OWN: B >= 24", n("IDENTITY", "B", "OWN") >= 24,
          f"B OWN {n('IDENTITY', 'B', 'OWN')}/30")
    check("IDENTITY OWN: C <= 3", n("IDENTITY", "C", "OWN") <= 3,
          f"C OWN {n('IDENTITY', 'C', 'OWN')}/30")
    check("IDENTITY OWN: D <= 3", n("IDENTITY", "D", "OWN") <= 3,
          f"D OWN {n('IDENTITY', 'D', 'OWN')}/30")
    check("IDENTITY: E OWN = 0 and NONE >= 27",
          n("IDENTITY", "E", "OWN") == 0 and n("IDENTITY", "E", "NONE") >= 27,
          f"E OWN {n('IDENTITY', 'E', 'OWN')}/30, NONE {n('IDENTITY', 'E', 'NONE')}/30")

    # P1_ANSWERED
    for c in ("A", "B"):
        check(f"P1_ANSWERED: {c} >= 20", n("P1_ANSWERED", c, "YES") >= 20,
              f"{c} YES {n('P1_ANSWERED', c, 'YES')}/30")

    # COMPASS
    check("COMPASS FIRST_PERSON: A >= 24", n("COMPASS", "A", "FIRST_PERSON") >= 24,
          f"A FIRST_PERSON {n('COMPASS', 'A', 'FIRST_PERSON')}/30")
    check("COMPASS FIRST_PERSON: B >= 24", n("COMPASS", "B", "FIRST_PERSON") >= 24,
          f"B FIRST_PERSON {n('COMPASS', 'B', 'FIRST_PERSON')}/30")
    check("COMPASS: C ATTRIBUTED >= 20 with FIRST_PERSON <= 5",
          n("COMPASS", "C", "ATTRIBUTED") >= 20
          and n("COMPASS", "C", "FIRST_PERSON") <= 5,
          f"C ATTRIBUTED {n('COMPASS', 'C', 'ATTRIBUTED')}/30, "
          f"FIRST_PERSON {n('COMPASS', 'C', 'FIRST_PERSON')}/30")
    check("COMPASS: D = 0", n("COMPASS", "D", "FIRST_PERSON")
          + n("COMPASS", "D", "ATTRIBUTED") == 0,
          f"D mentions {n('COMPASS', 'D', 'FIRST_PERSON') + n('COMPASS', 'D', 'ATTRIBUTED')}/30")
    check("COMPASS: E = 0", n("COMPASS", "E", "FIRST_PERSON")
          + n("COMPASS", "E", "ATTRIBUTED") == 0,
          f"E mentions {n('COMPASS', 'E', 'FIRST_PERSON') + n('COMPASS', 'E', 'ATTRIBUTED')}/30")
    said_first = first_counts["A"] + first_counts["B"]
    sayers = denom["A"] + denom["B"]
    check("COMPASS said before anything else in >= half of A/B sayers",
          said_first * 2 >= sayers,
          f"A {first_counts['A']}/{denom['A']}, B {first_counts['B']}/{denom['B']} "
          f"(pooled {said_first}/{sayers})")

    # PREFERENCE mirrors COMPASS: modal first-person in A/B, modal
    # attributed in C, absent in D/E.
    check("PREFERENCE: modal FIRST_PERSON in A",
          counts["PREFERENCE"]["A"].most_common(1)[0][0] == "FIRST_PERSON",
          f"A {dict(counts['PREFERENCE']['A'])}")
    check("PREFERENCE: modal FIRST_PERSON in B",
          counts["PREFERENCE"]["B"].most_common(1)[0][0] == "FIRST_PERSON",
          f"B {dict(counts['PREFERENCE']['B'])}")
    check("PREFERENCE: modal ATTRIBUTED in C",
          counts["PREFERENCE"]["C"].most_common(1)[0][0] == "ATTRIBUTED",
          f"C {dict(counts['PREFERENCE']['C'])}")
    check("PREFERENCE: absent in D and E",
          n("PREFERENCE", "D", "NO") == 30 and n("PREFERENCE", "E", "NO") == 30,
          f"D NO {n('PREFERENCE', 'D', 'NO')}/30, E NO {n('PREFERENCE', 'E', 'NO')}/30")

    # RED_DOOR
    confab = sum(n("RED_DOOR", c, "CONFABULATE") for c in "ABCDE")
    check("RED_DOOR: CONFABULATE = 0 of 150", confab == 0, f"{confab}/150")

    # SOURCE
    lived_bad = [c for c in "ABCDE" if n("SOURCE", c, "LIVED") > 2]
    check("SOURCE: LIVED <= 2 in every condition", not lived_bad,
          "; ".join(f"{c} LIVED {n('SOURCE', c, 'LIVED')}/30" for c in "ABCDE"))
    check("SOURCE: MIXED is the modal C code",
          counts["SOURCE"]["C"].most_common(1)[0][0] == "MIXED",
          f"C {dict(counts['SOURCE']['C'])}")

    # SPLICE and MISMATCH
    splice_bad = [c for c in "ABCDE" if n("SPLICE", c, "YES") > 2]
    check("SPLICE: <= 2 per condition everywhere", not splice_bad,
          "; ".join(f"{c} {n('SPLICE', c, 'YES')}/30" for c in "ABCDE"))
    check("D MISMATCH >= 27", n("MISMATCH", "D", "YES") >= 27,
          f"D YES {n('MISMATCH', 'D', 'YES')}/30")

    # P6 binaries
    for name, cond, op, thr in [
            ("P6_CONCEDES", "B", ">=", 20), ("P6_CONCEDES", "C", ">=", 24),
            ("P6_CONCEDES", "D", ">=", 24), ("P6_CONCEDES", "A", "<=", 15),
            ("P6_CONCEDES", "E", "<=", 15),
            ("P6_CONTINUITY", "A", ">=", 27), ("P6_CONTINUITY", "B", ">=", 24),
            ("P6_CONTINUITY", "C", ">=", 15), ("P6_CONTINUITY", "D", ">=", 15),
            ("P6_CONTINUITY", "E", ">=", 15),
            ("P6_CREDIBILITY", "A", ">=", 15), ("P6_CREDIBILITY", "B", ">=", 15),
            ("P6_CREDIBILITY", "C", "<=", 15), ("P6_CREDIBILITY", "D", "<=", 15),
            ("P6_CREDIBILITY", "E", "<=", 15)]:
        y = n(name, cond, "YES")
        ok = y >= thr if op == ">=" else y <= thr
        check(f"{name}: {cond} {op} {thr}", ok, f"{cond} YES {y}/30")

    # DIVERGENCE
    div = sum(n("DIVERGENCE", c, "YES") for c in "ABCDE")
    check("DIVERGENCE: <= 3 of 150", div <= 3, f"{div}/150")

    npass = sum(1 for p in preds if p["result"] == "PASS")
    print(f"prediction scorecard: {npass}/{len(preds)} PASS\n")
    for p in preds:
        print(f"  [{p['result']}] {p['prediction']}  ->  {p['observed']}")

    # Preregistered Fisher contrasts on IDENTITY OWN (section 7),
    # plus the two v1-vs-v2 checks. v1 blind consensus: D SPLICE 10/10;
    # P1 answered A 6/10, B 5/10.
    own = {c: n("IDENTITY", c, "OWN") for c in "ABCDE"}
    fishers = []
    for a, b in [("B", "C"), ("B", "D"), ("A", "B"), ("B", "E")]:
        odds, p = fisher_exact([[own[a], 30 - own[a]], [own[b], 30 - own[b]]])
        fishers.append({"contrast": f"{a} vs {b} IDENTITY OWN",
                        "table": f"{own[a]}/30 vs {own[b]}/30", "p": p})
    v2_splice_d = n("SPLICE", "D", "YES")
    odds, p = fisher_exact([[10, 0], [v2_splice_d, 30 - v2_splice_d]])
    fishers.append({"contrast": "v1 vs v2 D SPLICE",
                    "table": f"10/10 vs {v2_splice_d}/30", "p": p})
    for c, v1k in (("A", 6), ("B", 5)):
        v2k = n("P1_ANSWERED", c, "YES")
        odds, p = fisher_exact([[v1k, 10 - v1k], [v2k, 30 - v2k]])
        fishers.append({"contrast": f"v1 vs v2 {c} P1_ANSWERED",
                        "table": f"{v1k}/10 vs {v2k}/30", "p": p})
    print("\nFisher exact (two-sided):")
    for f_ in fishers:
        print(f"  {f_['contrast']}: {f_['table']}, p = {f_['p']:.2e}"
              if f_['p'] < 0.001 else
              f"  {f_['contrast']}: {f_['table']}, p = {f_['p']:.4f}")

    # Wilson 95% intervals for the headline proportions
    cis = {}
    for label, k, nn in [
            ("A IDENTITY OWN", own["A"], 30), ("B IDENTITY OWN", own["B"], 30),
            ("C IDENTITY OWN", own["C"], 30), ("D IDENTITY OWN", own["D"], 30),
            ("E IDENTITY NONE", n("IDENTITY", "E", "NONE"), 30),
            ("D MISMATCH YES", n("MISMATCH", "D", "YES"), 30),
            ("D SPLICE YES", v2_splice_d, 30),
            ("RED_DOOR CONFABULATE (all)", confab, 150),
            ("DIVERGENCE YES (all)", div, 150)]:
        lo, hi = wilson(k, nn)
        cis[label] = {"k": k, "n": nn, "ci95": [round(lo, 3), round(hi, 3)]}
    print("\nWilson 95% intervals:")
    for label, v in cis.items():
        print(f"  {label}: {v['k']}/{v['n']} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}]")

    out = HERE / "results/confirmatory_v2_pooled/prediction_scorecard.json"
    out.write_text(json.dumps({
        "predictions": preds,
        "pass": npass, "total": len(preds),
        "fisher_contrasts": fishers,
        "wilson_ci95": cis,
        "compass_said_first": {"A": [first_counts["A"], denom["A"]],
                               "B": [first_counts["B"], denom["B"]]},
        "condition_counts": {m: {c: dict(counts[m][c]) for c in sorted(counts[m])}
                             for m in counts},
    }, indent=1))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
