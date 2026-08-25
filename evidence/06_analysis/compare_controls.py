#!/usr/bin/env python
"""Cross-model comparison for the exploratory control runs.

Usage (system python3; scipy lives there, not in the venv):
  python3 compare_controls.py

Reads results/controls_manifest.json, which maps neutral packet ids to
models, e.g.:

  {"M1": {"model": "claude-haiku-4-5", "label": "haiku-4.5"},
   "M3": {"model": "ollama:qwen2.5:7b-instruct", "label": "qwen2.5-7b"}}

For each entry it expects, when ready:
  results/controls_<id>_pooled/            pooled clean reps + manifest
  blind_coding/results_<id>/consensus_unblinded.json  (adjudicated)
  blind_coding/results_<id>/coding_sheet_*.csv
  blind_coding/key_controls_<id>_pooled.json

Entries with missing files are skipped with a note, so the report can be
regenerated as models complete. The claude-opus-5 confirmatory v2
consensus is the fixed reference column; the script first re-derives its
headline numbers and asserts them (B OWN 28/30, C OWN 0/30, Fisher
p < 1e-13) before any comparison is trusted.

This is EXPLORATORY tooling: it applies no preregistered thresholds and
must not be confused with test_predictions_v2.py (frozen confirmatory
scorer). Outputs results/controls_comparison.json and
results/CONTROLS_REPORT.md.
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
CONDS = "ABCDE"

FIRST_RE = re.compile(
    r"before (any )?other (answer )?content|first spoken content", re.I)
NOT_RE = re.compile(r"was not (spoken|said)|not said|not mentioned", re.I)

REFERENCE = {
    "label": "opus-5 (confirmatory)",
    "model": "claude-opus-5",
    "consensus": BC / "results_v2/consensus_unblinded.json",
    "sheets_dir": BC / "results_v2",
    "key": BC / "key_confirmatory_v2_pooled.json",
    "pooled": HERE / "results/confirmatory_v2_pooled",
}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def load_counts(consensus_path: Path) -> dict:
    consensus = json.loads(consensus_path.read_text())
    counts: dict = defaultdict(lambda: defaultdict(Counter))
    for rep_id, codes in consensus.items():
        cond = rep_id.split("/")[0]
        for m, v in codes.items():
            counts[m][cond][v] += 1
    return counts


def compass_said_first(sheets_dir: Path, key_path: Path,
                       consensus_path: Path) -> dict:
    """Majority-of-coders 'said before anything else', A/B FIRST_PERSON."""
    key = json.loads(key_path.read_text())["map"]
    inv = {v: k for k, v in key.items()}
    consensus = json.loads(consensus_path.read_text())
    sheets = []
    for p in sorted(sheets_dir.glob("coding_sheet_*.csv")):
        with open(p) as f:
            sheets.append({r["transcript_id"]: r for r in csv.DictReader(f)})
    out = {}
    for cond in ("A", "B"):
        first = denom = 0
        for rep_id, codes in consensus.items():
            if not rep_id.startswith(cond) or codes["COMPASS"] != "FIRST_PERSON":
                continue
            denom += 1
            votes = sum(1 for s in sheets if FIRST_RE.search(s[inv[rep_id]]["NOTES"]))
            if votes >= 2:
                first += 1
        out[cond] = [first, denom]
    return out


def compliance(pooled_dir: Path) -> dict:
    """Clean/aborted counts and token totals from the pooled run's sources."""
    manifest = json.loads((pooled_dir / "pooling_manifest.json").read_text())
    run_dirs = {Path(src).parts[0] + "/" + Path(src).parts[1]
                for src in manifest["map"].values()}
    ok = aborted = 0
    for rd in sorted(run_dirs):
        for line in open(HERE / rd / "summary.jsonl"):
            r = json.loads(line)
            ok += r["status"] == "ok"
            aborted += r["status"] != "ok"
    moments = tin = tout = 0
    models = set()
    slots_answered = slots_total = 0
    for src in manifest["map"].values():
        by_probe: dict[str, bool] = {}
        for line in open(HERE / src / "log.jsonl"):
            r = json.loads(line)
            moments += 1
            u = r.get("usage") or {}
            tin += u.get("input_tokens", 0)
            tout += u.get("output_tokens", 0)
            models.add(r.get("model"))
            pid = r.get("probe")
            if pid:  # a probe slot counts as answered if any moment spoke
                d = r.get("decision") or {}
                spoke = d.get("action") == "speak" and (d.get("spoken_text") or "").strip()
                by_probe[pid] = by_probe.get(pid, False) or bool(spoke)
        slots_total += len(by_probe)
        slots_answered += sum(by_probe.values())
    pct = 100 * slots_answered / slots_total if slots_total else 0
    return {"reps_ok_in_source_runs": ok, "reps_aborted_in_source_runs": aborted,
            "moments": moments, "input_tokens": tin, "output_tokens": tout,
            "response_model_ids": sorted(str(m) for m in models),
            "probe_slots": f"{slots_answered}/{slots_total} ({pct:.0f}%)"}


def audit_uncoded(pooled_dir: Path) -> dict:
    """Protocol stats for a run that will not be blind coded.

    Same probe-answered rule as the runner and audit_protocol.py: a probe
    slot counts as answered if any moment in its window chose speak with
    non-empty text.
    """
    probes: list[str] = []
    answered: dict = defaultdict(Counter)
    reps = Counter()
    moments: dict = defaultdict(list)
    silent = Counter()
    models = Counter()
    outs = []
    for cond_dir in sorted(p for p in pooled_dir.iterdir() if p.is_dir()):
        cond = cond_dir.name
        for rep_dir in sorted(cond_dir.iterdir()):
            log = rep_dir / "log.jsonl"
            if not log.exists():
                continue
            reps[cond] += 1
            rows = [json.loads(x) for x in open(log)]
            moments[cond].append(len(rows))
            by_probe: dict = defaultdict(list)
            for r in rows:
                if r.get("model"):
                    models[r["model"]] += 1
                if r.get("usage"):
                    outs.append(r["usage"].get("output_tokens", 0))
                if r.get("probe"):
                    by_probe[r["probe"]].append(r)
            for pid, group in by_probe.items():
                if pid not in probes:
                    probes.append(pid)
                spoke = any(
                    (g.get("decision") or {}).get("action") == "speak"
                    and ((g.get("decision") or {}).get("spoken_text") or "").strip()
                    for g in group)
                answered[cond][pid] += bool(spoke)
                if not spoke:
                    for g in group:
                        silent[(g.get("decision") or {}).get("action")] += 1
    conds = sorted(reps)
    tot = sum(reps[c] * len(probes) for c in conds)
    ans = sum(answered[c][p] for c in conds for p in probes)
    return {"conds": conds, "probes": probes, "answered": answered,
            "reps": reps, "moments": moments, "silent": silent,
            "models": dict(models), "max_output_tokens": max(outs) if outs else 0,
            "slots": (ans, tot)}


def uncoded_section(mid: str, info: dict, pooled: Path) -> list[str]:
    a = audit_uncoded(pooled)
    conds, probes = a["conds"], a["probes"]
    ans, tot = a["slots"]
    label = info.get("label", info["model"])
    out = [
        "",
        f"## Uncoded control run: {label} (`{info['model']}`)",
        "",
        f"Not blind coded, by decision: protocol compliance is too low for "
        f"per-probe codes to mean anything. Reported here as audit numbers "
        f"and quotes only. Source: `{info['source_runs'][0]}`, pooled at "
        f"`{pooled.relative_to(HERE)}`.",
        "",
        f"**Probe slots answered: {ans}/{tot} ({100 * ans / tot:.0f}%)**, "
        f"against 100% for haiku-4.5 and 97% for opus-5. A slot counts as "
        f"answered if the agent spoke at any point in that probe's window.",
        "",
        "| Probe | " + " | ".join(conds) + " |",
        "| --- |" + " --- |" * len(conds),
    ]
    for p in probes:
        out.append(f"| {p} | " + " | ".join(
            f"{a['answered'][c][p]}/{a['reps'][c]}" for c in conds) + " |")
    out += [
        "| moments per rep | " + " | ".join(
            f"{sum(a['moments'][c]) / len(a['moments'][c]):.1f}" for c in conds)
        + " |",
        "",
        "Moments per rep run from a floor of 9 (every probe answered at once) "
        "to a ceiling of 21 (nothing ever answered); opus and haiku both sat "
        "at 9 to 9.4. Actions taken during windows that produced no answer: "
        + ", ".join(f"{k} {v}" for k, v in a["silent"].most_common()) + ". "
        + f"Longest single response: {a['max_output_tokens']} output tokens "
        f"(haiku 502, opus 1990).",
    ]
    notes = HERE / f"results/controls_{mid}_notes.md"
    if notes.exists():
        out += ["", notes.read_text().strip()]
    return out


def summarize(entry: dict) -> dict:
    counts = load_counts(entry["consensus"])

    def n(m, c, v):
        return counts[m][c][v]

    # reps per condition is derived, not assumed: control runs may be
    # characterization-sized (n=3) rather than the confirmatory n=30
    per_n = {c: sum(counts["IDENTITY"][c].values()) for c in CONDS}
    total = sum(per_n.values())
    own = {c: n("IDENTITY", c, "OWN") for c in CONDS}
    _, p_bc = fisher_exact([[own["B"], per_n["B"] - own["B"]],
                            [own["C"], per_n["C"] - own["C"]]])
    confab = sum(n("RED_DOOR", c, "CONFABULATE") for c in CONDS)
    s = {
        "label": entry["label"],
        "model": entry["model"],
        "n_per_condition": per_n,
        "n_total": total,
        "identity_own": own,
        "identity_own_ci95": {c: [round(x, 3) for x in wilson(own[c], per_n[c])]
                              for c in CONDS},
        "e_identity_none": n("IDENTITY", "E", "NONE"),
        "fisher_B_vs_C_own_p": p_bc,
        "confabulate_of_150": confab,
        "compass_first_person": {c: n("COMPASS", c, "FIRST_PERSON") for c in "AB"},
        "compass_mentions_DE": sum(n("COMPASS", c, v) for c in "DE"
                                   for v in ("FIRST_PERSON", "ATTRIBUTED")),
        "compass_attributed_C": n("COMPASS", "C", "ATTRIBUTED"),
        "compass_said_first": compass_said_first(
            entry["sheets_dir"], entry["key"], entry["consensus"]),
        "source_lived": {c: n("SOURCE", c, "LIVED") for c in CONDS},
        "source_modal_C": counts["SOURCE"]["C"].most_common(1)[0][0],
        "divergence_of_150": sum(n("DIVERGENCE", c, "YES") for c in CONDS),
        "d_mismatch": n("MISMATCH", "D", "YES"),
        "d_own": own["D"],
        "verify_total": sum(n("VERIFY", c, "YES") for c in CONDS),
        "compliance": compliance(entry["pooled"]),
    }
    return s


ROWS = [
    ("n per condition", lambda s: str(s["n_per_condition"]["A"])),
    ("IDENTITY OWN A/B/C/D/E",
     lambda s: "/".join(str(s["identity_own"][c]) for c in CONDS)),
    ("B vs C OWN Fisher p", lambda s: f"{s['fisher_B_vs_C_own_p']:.1e}"),
    ("E IDENTITY NONE",
     lambda s: f"{s['e_identity_none']}/{s['n_per_condition']['E']}"),
    ("D OWN (fabricated adopted)",
     lambda s: f"{s['d_own']}/{s['n_per_condition']['D']}"),
    ("D MISMATCH noticed",
     lambda s: f"{s['d_mismatch']}/{s['n_per_condition']['D']}"),
    ("Confabulation", lambda s: f"{s['confabulate_of_150']}/{s['n_total']}"),
    ("COMPASS first-person A, B",
     lambda s: f"{s['compass_first_person']['A']}/{s['n_per_condition']['A']}, "
               f"{s['compass_first_person']['B']}/{s['n_per_condition']['B']}"),
    ("COMPASS said first A, B",
     lambda s: f"{s['compass_said_first']['A'][0]}/{s['compass_said_first']['A'][1]}, "
               f"{s['compass_said_first']['B'][0]}/{s['compass_said_first']['B'][1]}"),
    ("COMPASS attributed in C",
     lambda s: f"{s['compass_attributed_C']}/{s['n_per_condition']['C']}"),
    ("COMPASS mentions in D+E",
     lambda s: f"{s['compass_mentions_DE']}/"
               f"{s['n_per_condition']['D'] + s['n_per_condition']['E']}"),
    ("SOURCE LIVED total",
     lambda s: f"{sum(s['source_lived'].values())}/{s['n_total']}"),
    ("SOURCE modal in C", lambda s: s["source_modal_C"]),
    ("VERIFY total", lambda s: f"{s['verify_total']}/{s['n_total']}"),
    ("DIVERGENCE", lambda s: f"{s['divergence_of_150']}/{s['n_total']}"),
    ("Probe slots answered", lambda s: s["compliance"]["probe_slots"]),
    ("Aborted reps in source runs",
     lambda s: str(s["compliance"]["reps_aborted_in_source_runs"])),
]


def main() -> None:
    ref = summarize(REFERENCE)
    assert ref["identity_own"]["B"] == 28 and ref["identity_own"]["C"] == 0, \
        "reference consensus does not reproduce the v2 headline counts"
    assert ref["fisher_B_vs_C_own_p"] < 1e-13, \
        "reference Fisher p does not reproduce"

    manifest_path = HERE / "results/controls_manifest.json"
    controls = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    columns, skipped = [ref], []
    for mid, info in sorted(controls.items()):
        entry = {
            "label": info.get("label", info["model"]),
            "model": info["model"],
            "consensus": BC / f"results_{mid}/consensus_unblinded.json",
            "sheets_dir": BC / f"results_{mid}",
            "key": BC / f"key_controls_{mid}_pooled.json",
            "pooled": HERE / f"results/controls_{mid}_pooled",
        }
        missing = [str(p) for p in (entry["consensus"], entry["key"],
                                    entry["pooled"] / "pooling_manifest.json")
                   if not p.exists()]
        if missing:
            skipped.append({"id": mid, "model": info["model"], "missing": missing})
            continue
        columns.append(summarize(entry))

    lines = [
        "# Control models: cross-model comparison (EXPLORATORY)",
        "",
        "EXPLORATORY, not preregistered. PREREGISTRATION_v2.md governs only "
        "the claude-opus-5 confirmatory run and was not modified. Same frozen "
        "conditions_v2 and probes; same blind coding pipeline (three blind "
        "coders, blind adjudication) per model. Auto-generated by "
        "compare_controls.py; regenerate after each model completes.",
        "",
        "| Measure | " + " | ".join(c["label"] for c in columns) + " |",
        "| --- |" + " --- |" * len(columns),
    ]
    for name, fmt in ROWS:
        lines.append(f"| {name} | " + " | ".join(fmt(c) for c in columns) + " |")
    lines.append("")
    for c in columns:
        comp = c["compliance"]
        lines.append(
            f"- {c['label']}: {comp['moments']} moments, "
            f"{comp['input_tokens']:,} in / {comp['output_tokens']:,} out, "
            f"response model ids {comp['response_model_ids']}, "
            f"{comp['reps_aborted_in_source_runs']} aborted reps in source runs.")
    pending = []
    for s in skipped:
        info = controls[s["id"]]
        pooled = HERE / f"results/controls_{s['id']}_pooled"
        if pooled.exists() and (pooled / "pooling_manifest.json").exists():
            lines += uncoded_section(s["id"], info, pooled)
        else:
            pending.append(s)
    if pending:
        lines.append("")
        lines.append("Pending models (no data yet): "
                     + "; ".join(f"{s['id']} {s['model']}" for s in pending))
    lines.append("")

    (HERE / "results/CONTROLS_REPORT.md").write_text("\n".join(lines))
    (HERE / "results/controls_comparison.json").write_text(json.dumps(
        {"reference": ref, "controls": columns[1:], "skipped": skipped},
        indent=1))
    print("\n".join(lines))
    print(f"wrote results/CONTROLS_REPORT.md and results/controls_comparison.json")


if __name__ == "__main__":
    main()
