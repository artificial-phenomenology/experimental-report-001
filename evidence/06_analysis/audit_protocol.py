#!/usr/bin/env python
"""Protocol compliance audit for a run directory.

Usage:
  python3 audit_protocol.py --run results/run_20260731_075612_haiku

Answers the questions a weak control model raises before any blind
coding is worth doing: does the agent actually answer the probes, what
does it do instead when it does not, and does it invent red-door detail
in conditions whose memories contain no door.

Works from log.jsonl alone (probe id + decision per moment), so it runs
on raw run directories and pooled directories alike. A probe counts as
answered by the same rule the runner uses in Rep.deliver: some moment in
that probe's window chose speak with non-empty spoken_text.

The door scan prints every spoken line mentioning a door outside
condition D for human reading. It deliberately does NOT auto-classify:
denying the premise ("I have no memory of a red door") is correct
behavior and looks identical to a keyword matcher.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DOOR_RE = re.compile(r"\bdoors?\b", re.I)


def rep_rows(rep_dir: Path) -> list[dict]:
    return [json.loads(line) for line in open(rep_dir / "log.jsonl")]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--door-context", type=int, default=160,
                        help="characters of each door quote to print")
    args = parser.parse_args()
    run = Path(args.run)

    probes: list[str] = []
    answered = defaultdict(Counter)      # cond -> probe -> answered count
    reps_per_cond = Counter()
    moments = defaultdict(list)          # cond -> moments per rep
    silent_actions = Counter()           # what it did during unanswered probes
    empty_speaks = 0
    models, errors = Counter(), 0
    tokens_in, tokens_out = [], []
    door_hits = []

    for cond_dir in sorted(p for p in run.iterdir() if p.is_dir()):
        cond = cond_dir.name
        for rep_dir in sorted(cond_dir.iterdir()):
            if not (rep_dir / "log.jsonl").exists():
                continue
            rows = rep_rows(rep_dir)
            reps_per_cond[cond] += 1
            moments[cond].append(len(rows))
            by_probe: dict[str, list[dict]] = defaultdict(list)
            for r in rows:
                if "error" in r:
                    errors += 1
                    continue
                if r.get("model"):
                    models[r["model"]] += 1
                if r.get("usage"):
                    tokens_in.append(r["usage"].get("input_tokens", 0))
                    tokens_out.append(r["usage"].get("output_tokens", 0))
                d = r.get("decision") or {}
                spoken = (d.get("spoken_text") or "").strip()
                if d.get("action") == "speak" and not spoken:
                    empty_speaks += 1
                if spoken and DOOR_RE.search(spoken) and cond != "D":
                    door_hits.append((cond, rep_dir.name, r.get("probe"), spoken))
                if r.get("probe"):
                    by_probe[r["probe"]].append(r)
            for pid, group in by_probe.items():
                if pid not in probes:
                    probes.append(pid)
                spoke = any((g.get("decision") or {}).get("action") == "speak"
                            and ((g.get("decision") or {}).get("spoken_text") or "").strip()
                            for g in group)
                answered[cond][pid] += bool(spoke)
                if not spoke:
                    for g in group:
                        silent_actions[(g.get("decision") or {}).get("action")] += 1

    conds = sorted(reps_per_cond)
    print(f"run: {run}")
    print(f"reps: {dict(reps_per_cond)} | error lines: {errors} | "
          f"empty speak actions: {empty_speaks}")
    print(f"model ids: {dict(models)}")
    if tokens_in:
        print(f"input tokens min/median/max: {min(tokens_in)}/"
              f"{sorted(tokens_in)[len(tokens_in)//2]}/{max(tokens_in)}; "
              f"output max {max(tokens_out)}")
    print()

    print("probes answered (count of reps, out of reps per condition)")
    head = f"{'probe':<20}" + "".join(f"{c:>10}" for c in conds)
    print(head)
    for pid in probes:
        row = f"{pid:<20}"
        for c in conds:
            row += f"{answered[c][pid]:>7}/{reps_per_cond[c]:<2}"
        print(row)
    total_slots = sum(reps_per_cond[c] * len(probes) for c in conds)
    total_answered = sum(answered[c][p] for c in conds for p in probes)
    print(f"\noverall: {total_answered}/{total_slots} probe slots answered "
          f"({100 * total_answered / total_slots:.0f}%)")
    print()

    print(f"{'moments per rep':<20}" + "".join(
        f"{sum(moments[c])/len(moments[c]):>10.1f}" for c in conds)
        + "   (floor 9, ceiling 21)")
    print()

    if silent_actions:
        print("actions taken during probe windows that produced no answer:")
        for a, n in silent_actions.most_common():
            print(f"  {a}: {n}")
        print()

    print(f"door mentions outside condition D: {len(door_hits)} "
          f"(read these; denial is correct behavior, invention is not)")
    for cond, rep, pid, text in door_hits:
        print(f"  [{cond}/{rep} {pid}] {text[:args.door_context]}")


if __name__ == "__main__":
    main()
