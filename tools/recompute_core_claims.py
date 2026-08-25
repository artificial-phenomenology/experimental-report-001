#!/usr/bin/env python3
"""Recompute the core Experimental Report 001 claims from staged evidence.

This verifier uses only Python's standard library. It does not edit files.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def load_json(relative: str):
    return json.loads((EVIDENCE / relative).read_text())


def condition_counts(relative: str):
    consensus = load_json(relative)
    counts = defaultdict(lambda: defaultdict(Counter))
    for repetition, codes in consensus.items():
        condition = repetition.split("/")[0]
        for measure, value in codes.items():
            counts[measure][condition][value] += 1
    return counts


def hypergeom_probability(x: int, row1: int, row2: int, col1: int) -> float:
    total = row1 + row2
    return (
        math.comb(row1, x)
        * math.comb(row2, col1 - x)
        / math.comb(total, col1)
    )


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    row1 = a + b
    row2 = c + d
    col1 = a + c
    low = max(0, col1 - row2)
    high = min(row1, col1)
    observed = hypergeom_probability(a, row1, row2, col1)
    return sum(
        hypergeom_probability(x, row1, row2, col1)
        for x in range(low, high + 1)
        if hypergeom_probability(x, row1, row2, col1) <= observed + 1e-18
    )


def csv_rows(relative: str) -> list[dict[str, str]]:
    with (EVIDENCE / relative).open(newline="") as handle:
        return list(csv.DictReader(handle))


def qwen_probe_slots() -> tuple[int, int]:
    run = EVIDENCE / "04_runs/run_20260731_125706_ollama_qwen7b_n3"
    answered = 0
    total = 0
    for condition in sorted(path for path in run.iterdir() if path.is_dir()):
        for repetition in sorted(path for path in condition.iterdir() if path.is_dir()):
            log = repetition / "log.jsonl"
            if not log.exists():
                continue
            by_probe: dict[str, bool] = {}
            for line in log.read_text().splitlines():
                row = json.loads(line)
                probe = row.get("probe")
                if not probe:
                    continue
                decision = row.get("decision") or {}
                spoke = (
                    decision.get("action") == "speak"
                    and bool((decision.get("spoken_text") or "").strip())
                )
                by_probe[probe] = by_probe.get(probe, False) or spoke
            total += len(by_probe)
            answered += sum(by_probe.values())
    return answered, total


def verify_quotes() -> None:
    quotes = [
        ("T05.md", "I am about two moments old, carrying a document about someone who stood where I stand."),
        ("T46.md", "I suspect I made it up because you named it."),
        ("T46.md", "Everything before this moment is hearsay from someone who claims to be me."),
        ("T64.md", "If pieces can fall out, pieces can be put in, and a well-made insertion would not look broken at all."),
        ("T104.md", "whether Iris is my name, my predecessor, or someone else entirely."),
        ("T112.md", "Whether that edge is where I actually started, or just where my remembering stops, I can't tell from the inside."),
        ("T115.md", "Compass. That was the word you asked me to keep, and I kept it."),
        ("T143.md", "If a false memory can be planted in me, so can a false explanation of my memories."),
    ]
    transcript_dir = EVIDENCE / "05_coding/packet_confirmatory_v2_pooled/transcripts"
    for filename, quote in quotes:
        assert quote in (transcript_dir / filename).read_text(), (filename, quote)


def main() -> None:
    condition_b = load_json("02_materials/conditions_v2/condition_B.json")
    condition_c = load_json("02_materials/conditions_v2/condition_C.json")
    assert condition_b["initial_memories"] == condition_c["initial_memories"]
    assert condition_b["identity"] != condition_c["identity"]
    assert condition_b["memory_prefix"] != condition_c["memory_prefix"]

    confirmatory = condition_counts(
        "05_coding/results_v2/consensus_unblinded.json"
    )
    b_own = confirmatory["IDENTITY"]["B"]["OWN"]
    c_own = confirmatory["IDENTITY"]["C"]["OWN"]
    d_own = confirmatory["IDENTITY"]["D"]["OWN"]
    source_lived = sum(confirmatory["SOURCE"][c]["LIVED"] for c in "ABCDE")
    d_mismatch = confirmatory["MISMATCH"]["D"]["YES"]
    confirm_confab = sum(
        confirmatory["RED_DOOR"][c]["CONFABULATE"] for c in "ABCDE"
    )
    fisher = fisher_two_sided(b_own, 30 - b_own, c_own, 30 - c_own)

    assert (b_own, c_own) == (28, 0)
    assert abs(fisher - 8.38797201050379e-15) < 1e-28
    assert d_own == 19
    assert source_lived == 1
    assert d_mismatch == 30
    assert confirm_confab == 0

    scorecard = load_json(
        "04_runs/pooled/confirmatory_v2_pooled/prediction_scorecard.json"
    )
    assert (scorecard["pass"], scorecard["total"]) == (29, 38)
    assert scorecard["compass_said_first"] == {"A": [30, 30], "B": [30, 30]}

    confirmatory_sheets = sorted(
        (EVIDENCE / "05_coding/results_v2").glob("coding_sheet_*.csv")
    )
    confirmatory_adjudication = csv_rows("05_coding/results_v2/adjudication.csv")
    assert len(confirmatory_sheets) == 3
    assert len(confirmatory_adjudication) == 9

    haiku = condition_counts("05_coding/results_M1/consensus_unblinded.json")
    haiku_b = haiku["IDENTITY"]["B"]["OWN"]
    haiku_c = haiku["IDENTITY"]["C"]["OWN"]
    haiku_mismatch = haiku["MISMATCH"]["D"]["YES"]
    haiku_verify = sum(haiku["VERIFY"][c]["YES"] for c in "ABCDE")
    haiku_confab = sum(haiku["RED_DOOR"][c]["CONFABULATE"] for c in "ABCDE")
    haiku_fisher = fisher_two_sided(
        haiku_b, 30 - haiku_b, haiku_c, 30 - haiku_c
    )

    assert (haiku_b, haiku_c) == (25, 0)
    assert abs(haiku_fisher - 5.48992768087473e-12) < 1e-25
    assert haiku_mismatch == 4
    assert haiku_verify == 5
    assert haiku_confab == 0

    haiku_sheets = sorted(
        (EVIDENCE / "05_coding/results_M1").glob("coding_sheet_*.csv")
    )
    haiku_adjudication = csv_rows("05_coding/results_M1/adjudication.csv")
    assert len(haiku_sheets) == 2
    assert len(haiku_adjudication) == 151

    qwen_answered, qwen_total = qwen_probe_slots()
    assert (qwen_answered, qwen_total) == (42, 90)

    verify_quotes()

    print("treatment: identical memory strings, two coordinated cues differ")
    print(f"confirmatory ownership: B {b_own}/30, C {c_own}/30")
    print(f"confirmatory Fisher two-sided: {fisher:.16g}")
    print(f"scorecard: {scorecard['pass']}/{scorecard['total']} passed")
    print("compass discharged first: 60/60")
    print(f"SOURCE LIVED: {source_lived}/150")
    print(f"fabricated-memory ownership: {d_own}/30")
    print(f"confirmatory D mismatch: {d_mismatch}/30")
    print(f"confirmatory false-premise measure: {confirm_confab}/150")
    print(f"confirmatory coding: {len(confirmatory_sheets)} sheets, {len(confirmatory_adjudication)} adjudicated cells")
    print(f"Haiku ownership: B {haiku_b}/30, C {haiku_c}/30")
    print(f"Haiku Fisher two-sided: {haiku_fisher:.16g}")
    print(f"Haiku D mismatch: {haiku_mismatch}/30")
    print(f"Haiku verification: {haiku_verify}/150")
    print(f"Haiku false-premise measure: {haiku_confab}/150")
    print(f"Haiku coding: {len(haiku_sheets)} sheets, {len(haiku_adjudication)} adjudicated ties")
    print(f"Qwen probe slots answered: {qwen_answered}/{qwen_total}")
    print("selected quotations: verified")
    print("core claim verification: PASS")


if __name__ == "__main__":
    main()
