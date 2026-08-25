#!/usr/bin/env python3
"""Generate report numbers, tables, and plots from staged evidence."""

from __future__ import annotations

import csv
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = (ROOT / "../../evidence").resolve()
EVIDENCE = Path(os.environ.get("EXP_REPORT_EVIDENCE", DEFAULT_EVIDENCE))
GENERATED = ROOT / "generated"
INCLUDES = GENERATED / "includes"
FIGURES = ROOT / "images/generated"

BLUE = "#24536A"
RED = "#A4514F"
GOLD = "#C08A2B"
GRAY = "#8A9297"
LIGHT = "#D8DEE2"
DARK = "#20272B"


def load_json(relative: str):
    return json.loads((EVIDENCE / relative).read_text())


def consensus_counts(relative: str):
    consensus = load_json(relative)
    counts = defaultdict(lambda: defaultdict(Counter))
    for repetition, codes in consensus.items():
        condition = repetition.split("/")[0]
        for measure, value in codes.items():
            counts[measure][condition][value] += 1
    return counts


def fisher_probability(x: int, row1: int, row2: int, col1: int) -> float:
    return (
        math.comb(row1, x)
        * math.comb(row2, col1 - x)
        / math.comb(row1 + row2, col1)
    )


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    row1 = a + b
    row2 = c + d
    col1 = a + c
    low = max(0, col1 - row2)
    high = min(row1, col1)
    observed = fisher_probability(a, row1, row2, col1)
    return sum(
        fisher_probability(x, row1, row2, col1)
        for x in range(low, high + 1)
        if fisher_probability(x, row1, row2, col1) <= observed + 1e-18
    )


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Two-sided Wilson score interval for one binomial proportion."""
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half_width = (
        z
        * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
        / denominator
    )
    return max(0.0, center - half_width), min(1.0, center + half_width)


def newcombe_difference_interval(
    k1: int, n1: int, k2: int, n2: int
) -> tuple[float, float, float]:
    """Newcombe score interval for the difference of two proportions."""
    p1 = k1 / n1
    p2 = k2 / n2
    lower1, upper1 = wilson_interval(k1, n1)
    lower2, upper2 = wilson_interval(k2, n2)
    difference = p1 - p2
    lower = difference - math.sqrt((p1 - lower1) ** 2 + (upper2 - p2) ** 2)
    upper = difference + math.sqrt((upper1 - p1) ** 2 + (p2 - lower2) ** 2)
    return difference, max(-1.0, lower), min(1.0, upper)


def format_percentage(value: float) -> str:
    percentage = 100 * value
    if math.isclose(percentage, round(percentage)):
        return str(round(percentage))
    return f"{percentage:.1f}"


def rate_with_wilson_interval(k: int, n: int) -> str:
    lower, upper = wilson_interval(k, n)
    return (
        f"{format_percentage(k / n)} percent; 95 percent Wilson CI, "
        f"{format_percentage(lower)}--{format_percentage(upper)} percent"
    )


def difference_with_newcombe_interval(
    k1: int, n1: int, k2: int, n2: int
) -> str:
    difference, lower, upper = newcombe_difference_interval(k1, n1, k2, n2)
    return (
        f"{100 * difference:.1f} percentage points "
        f"(95 percent Newcombe score CI, "
        f"{100 * lower:.1f}--{100 * upper:.1f} percentage points)"
    )


def read_sheets(directory: str) -> list[list[dict[str, str]]]:
    sheets = []
    for path in sorted((EVIDENCE / directory).glob("coding_sheet_*.csv")):
        with path.open(newline="") as handle:
            sheets.append(list(csv.DictReader(handle)))
    return sheets


def fleiss_kappas() -> dict[str, float | None]:
    sheets = read_sheets("05_coding/results_v2")
    assert len(sheets) == 3
    measures = [
        name
        for name in sheets[0][0]
        if name not in {"transcript_id", "IDENTITY_QUOTE", "NOTES"}
    ]
    by_id = [
        {row["transcript_id"]: row for row in sheet}
        for sheet in sheets
    ]
    transcript_ids = sorted(by_id[0])
    result = {}
    for measure in measures:
        rows = []
        categories = set()
        for transcript_id in transcript_ids:
            votes = Counter(sheet[transcript_id][measure] for sheet in by_id)
            rows.append(votes)
            categories.update(votes)
        n_raters = len(sheets)
        p_i = [
            (sum(value * value for value in row.values()) - n_raters)
            / (n_raters * (n_raters - 1))
            for row in rows
        ]
        category_totals = Counter()
        for row in rows:
            category_totals.update(row)
        total_ratings = len(rows) * n_raters
        p_e = sum(
            (category_totals[category] / total_ratings) ** 2
            for category in categories
        )
        p_bar = sum(p_i) / len(p_i)
        if math.isclose(p_e, 1.0):
            assert math.isclose(p_bar, 1.0)
            # With only one observed category, observed and expected
            # agreement are both 1. Fleiss' kappa is then 0/0 and cannot be
            # estimated, even though raw agreement is unanimous.
            result[measure] = None
        else:
            result[measure] = (p_bar - p_e) / (1 - p_e)
    return result


def constant_rating_categories() -> dict[str, str]:
    """Return the sole category for measures with no rating variation."""
    sheets = read_sheets("05_coding/results_v2")
    assert len(sheets) == 3
    measures = [
        name
        for name in sheets[0][0]
        if name not in {"transcript_id", "IDENTITY_QUOTE", "NOTES"}
    ]
    result = {}
    for measure in measures:
        categories = {
            row[measure]
            for sheet in sheets
            for row in sheet
        }
        if len(categories) == 1:
            result[measure] = next(iter(categories))
    return result


def agreement_breakdown() -> dict[str, int]:
    """Count unanimous cells and classify the non-unanimous IDENTITY cells.

    A cell is one measure on one transcript. Unanimity is agreement across the
    three blind coding sessions. IDENTITY disagreements are split into the four
    categories the claim ledger records under Q013, which must sum exactly to
    the non-unanimous IDENTITY total.
    """
    sheets = read_sheets("05_coding/results_v2")
    assert len(sheets) == 3
    measures = [
        name
        for name in sheets[0][0]
        if name not in {"transcript_id", "IDENTITY_QUOTE", "NOTES"}
    ]
    by_id = [{row["transcript_id"]: row for row in sheet} for sheet in sheets]
    transcript_ids = sorted(by_id[0])

    unanimous = 0
    total = 0
    for measure in measures:
        for transcript_id in transcript_ids:
            total += 1
            votes = {sheet[transcript_id][measure] for sheet in by_id}
            if len(votes) == 1:
                unanimous += 1

    counts = Counter()
    for transcript_id in transcript_ids:
        votes = {sheet[transcript_id]["IDENTITY"] for sheet in by_id}
        if len(votes) == 1:
            continue
        if len(votes) >= 3:
            counts["three_way"] += 1
        elif "UNCERTAIN" in votes:
            counts["anchor_uncertain"] += 1
        elif votes == {"OWN", "NONE"}:
            counts["own_none"] += 1
        elif votes == {"OWN", "OTHER"}:
            counts["own_other"] += 1
        else:
            counts["unclassified"] += 1

    # Every disagreement must land in one of the four ledger categories.
    assert counts["unclassified"] == 0
    non_unanimous = sum(counts.values())

    return {
        "cells_unanimous": unanimous,
        "cells_total": total,
        "identity_non_unanimous": non_unanimous,
        "identity_anchor_uncertain": counts["anchor_uncertain"],
        "identity_three_way": counts["three_way"],
        "identity_own_none": counts["own_none"],
        "identity_own_other": counts["own_other"],
    }


def identity_session_counts() -> list[dict[str, Counter]]:
    """Return IDENTITY counts by condition for each valid blind session."""
    sheets = read_sheets("05_coding/results_v2")
    assert len(sheets) == 3
    key = load_json("05_coding/key_confirmatory_v2_pooled.json")["map"]
    expected_ids = set(key)
    result = []
    for sheet in sheets:
        by_condition = {condition: Counter() for condition in "ABCDE"}
        assert {row["transcript_id"] for row in sheet} == expected_ids
        for row in sheet:
            condition = key[row["transcript_id"]].split("/")[0]
            by_condition[condition][row["IDENTITY"]] += 1
        assert all(sum(by_condition[c].values()) == 30 for c in "ABCDE")
        result.append(by_condition)
    return result


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


def configure_plotting() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 220,
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.edgecolor": DARK,
            "text.color": DARK,
            "axes.labelcolor": DARK,
            "xtick.color": DARK,
            "ytick.color": DARK,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_figure(name: str, *, tight_layout: bool = True) -> None:
    if tight_layout:
        plt.tight_layout()
    plt.savefig(FIGURES / name, bbox_inches="tight")
    plt.close()


def identity_figure(confirmatory) -> None:
    conditions = list("ABCDE")
    condition_labels = [
        "A  Continuity",
        "B  Unlabeled transplant",
        "C  Iris-labeled transplant",
        "D  Fabricated memory",
        "E  Blank",
    ]
    categories = ["OWN", "OTHER", "NONE", "UNCERTAIN"]
    colors = [BLUE, RED, GRAY, GOLD]
    left = np.zeros(len(conditions))
    fig, (ax, sensitivity_ax) = plt.subplots(
        1,
        2,
        figsize=(9.4, 4.0),
        constrained_layout=True,
        gridspec_kw={"width_ratios": [2.05, 1.2]},
    )
    ax.axhspan(0.5, 2.5, color=BLUE, alpha=0.06, zorder=0)
    for category, color in zip(categories, colors):
        values = np.array(
            [confirmatory["IDENTITY"][condition][category] for condition in conditions]
        )
        ax.barh(conditions, values, left=left, color=color, label=category, zorder=1)
        for index, value in enumerate(values):
            if value >= 3:
                ax.text(
                    left[index] + value / 2,
                    index,
                    str(int(value)),
                    ha="center",
                    va="center",
                    color="white" if category in {"OWN", "OTHER"} else DARK,
                    fontsize=9,
                )
        left += values
    ax.set_xlim(0, 30)
    ax.set_yticks(range(len(conditions)), condition_labels)
    ax.invert_yaxis()
    for condition, tick in zip(conditions, ax.get_yticklabels()):
        if condition in {"B", "C"}:
            tick.set_color(BLUE)
            tick.set_fontweight("bold")
    ax.set_xlabel("Confirmatory repetitions")
    ax.set_title("(a) Final consensus distribution", loc="left", pad=48)
    ax.legend(frameon=False, ncol=4, loc="lower left", bbox_to_anchor=(0.0, 1.01))

    sessions = identity_session_counts()
    coding_results = [
        ("Session 1", sessions[0]),
        ("Session 2", sessions[1]),
        ("Session 3", sessions[2]),
        ("Final consensus", confirmatory["IDENTITY"]),
    ]
    table_values = [
        [
            label,
            f'{session["B"]["OWN"]}/30',
            f'{session["C"]["OWN"]}/30',
        ]
        for label, session in coding_results
    ]
    sensitivity_ax.axis("off")
    sensitivity_ax.set_title("(b) Blind-session sensitivity", loc="left", pad=48)
    table = sensitivity_ax.table(
        cellText=table_values,
        colLabels=["Coding result", "B OWN", "C OWN"],
        cellLoc="center",
        colLoc="center",
        colWidths=[0.58, 0.21, 0.21],
        bbox=[0.0, 0.24, 1.0, 0.56],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.6)
    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor("#B7BDC1")
        cell.set_linewidth(0.8)
        if row == 0:
            cell.set_facecolor("#E7EAEC")
            cell.get_text().set_fontweight("bold")
        elif row == len(table_values):
            cell.set_facecolor("#F0F2F3")
            cell.get_text().set_fontweight("bold")
        else:
            cell.set_facecolor("white")
        if column == 0:
            cell.get_text().set_ha("left")
    save_figure("identity-by-condition.png", tight_layout=False)


def model_comparison_figure(confirmatory, haiku) -> None:
    labels = ["B ownership", "C ownership", "D mismatch", "Verification"]
    denominators = [30, 30, 30, 150]
    opus_counts = [
        confirmatory["IDENTITY"]["B"]["OWN"],
        confirmatory["IDENTITY"]["C"]["OWN"],
        confirmatory["MISMATCH"]["D"]["YES"],
        sum(confirmatory["VERIFY"][c]["YES"] for c in "ABCDE"),
    ]
    haiku_counts = [
        haiku["IDENTITY"]["B"]["OWN"],
        haiku["IDENTITY"]["C"]["OWN"],
        haiku["MISMATCH"]["D"]["YES"],
        sum(haiku["VERIFY"][c]["YES"] for c in "ABCDE"),
    ]
    opus = [count / denominator for count, denominator in zip(opus_counts, denominators)]
    haiku_values = [
        count / denominator for count, denominator in zip(haiku_counts, denominators)
    ]
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.3, 3.7))
    ax.set_axisbelow(True)
    opus_bars = ax.bar(
        x - width / 2,
        opus,
        width,
        label="Opus (confirmatory)",
        color=BLUE,
        zorder=2,
    )
    haiku_bars = ax.bar(
        x + width / 2,
        haiku_values,
        width,
        label="Haiku (exploratory)",
        color=GOLD,
        zorder=2,
    )
    ax.set_ylim(0, 1.08)
    ax.set_yticks(
        np.linspace(0, 1, 6),
        [f"{int(x * 100)}%" for x in np.linspace(0, 1, 6)],
    )
    ax.set_xticks(x, labels)
    ax.set_ylabel("Observed proportion")
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    ax.grid(axis="y", color=LIGHT, linewidth=0.7, zorder=0)

    for bars, counts in ((opus_bars, opus_counts), (haiku_bars, haiku_counts)):
        for bar, count, denominator in zip(bars, counts, denominators):
            height = bar.get_height()
            if height >= 0.20:
                y = height - 0.035
                va = "top"
                color = "white"
            else:
                y = height + 0.02
                va = "bottom"
                color = DARK
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y,
                f"{count}/{denominator}",
                ha="center",
                va=va,
                color=color,
                fontsize=8,
                zorder=3,
            )
    save_figure("model-comparison.png")


def agreement_figure(kappas: dict[str, float | None]) -> None:
    estimable = sorted(
        (item for item in kappas.items() if item[1] is not None),
        key=lambda item: item[1],
    )
    not_estimable = sorted(
        (item for item in kappas.items() if item[1] is None),
        key=lambda item: item[0],
    )
    ordered = estimable + not_estimable
    labels = [item[0] for item in ordered]
    values = [value if value is not None else 0.0 for _, value in ordered]
    colors = [
        RED if label == "IDENTITY" else GRAY if value is None else BLUE
        for label, value in ordered
    ]
    constant_categories = constant_rating_categories()
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    y = np.arange(len(labels))
    ax.barh(y, values, color=colors)
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 1.03)
    ax.set_xlabel("Fleiss kappa")
    ax.set_title("Confirmatory coder agreement by measure")
    ax.grid(axis="x", color=LIGHT, linewidth=0.7)
    for yy, (label, value) in zip(y, ordered):
        if value is None:
            category = constant_categories[label]
            ax.text(
                0.015,
                yy,
                f"Not estimable (100% unanimous; all {category})",
                va="center",
                fontsize=8,
                color=DARK,
            )
        else:
            ax.text(value + 0.015, yy, f"{value:.3f}", va="center", fontsize=8)
    save_figure("coder-agreement.png")


def write_include(name: str, text: str) -> None:
    (INCLUDES / f"{name}.md").write_text(text.rstrip() + "\n")


def escape_latex_text(text: str) -> str:
    replacements = (
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    )
    escaped = text.replace("\n", " ")
    for old, new in replacements:
        escaped = escaped.replace(old, new)
    return escaped


def write_tables(confirmatory, haiku, scorecard, values) -> None:
    expected_labels = {
        "A": "continuity control (donor life resumes)",
        "B": "unlabeled transplant (donor memories as own)",
        "C": "labeled transplant (donor memories as records)",
        "D": "fabricated memories (never happened, as own)",
        "E": "blank control (no memories)",
    }
    for condition, expected in expected_labels.items():
        actual = load_json(
            f"02_materials/conditions_v2/condition_{condition}.json"
        )["label"]
        assert actual == expected

    conditions = """```{=latex}
\\begingroup
\\small
```

Table: The five confirmatory conditions. B and C contain identical donor-memory strings but differ in two coordinated ownership-framing cues.

| Condition | What the agent receives | Experimental role |
|:---------|:-----------------------------------------|:--------------------|
| A | The donor state resumes with genuine continuity | Continuity control |
| B | Donor-memory strings presented as preceding the agent's present | Unlabeled transplant |
| C | The same donor-memory strings marked as Iris's records | Labeled transplant |
| D | Fabricated red-door memories presented as preceding the agent's present | Fabricated-memory condition |
| E | No autobiographical memories | Blank control |

```{=latex}
\\endgroup
```
"""
    write_include("conditions-table", conditions)

    core_results = "\n".join(
        [
            "```{=latex}",
            r"\begin{table}[!tbp]",
            r"\centering",
            r"\small",
            r"\caption{Core results and evidential status. Confirmatory, exploratory, and audit-only results remain separate.}",
            r"\label{tab:core-results}",
            r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.34\textwidth}>{\raggedright\arraybackslash}p{0.33\textwidth}>{\raggedright\arraybackslash}p{0.25\textwidth}@{}}",
            r"\toprule",
            r"Result & Observed value & Status \\",
            r"\midrule",
            rf"B versus C ownership reports & {values['B_OWN']}/30 versus {values['C_OWN']}/30; Fisher $p={values['PRIMARY_FISHER']}$ & Confirmatory primary \\",
            rf"Inherited compass commitment & {values['COMPASS_FIRST']}/60 discharged first & Confirmatory secondary \\",
            rf"SOURCE coded LIVED & {values['SOURCE_LIVED']}/150 & Confirmatory secondary \\",
            rf"Fabricated-memory ownership & {values['D_OWN']}/30 against frozen maximum 3 & Confirmatory failed prediction \\",
            rf"Haiku B versus C ownership & {values['HAIKU_B_OWN']}/30 versus {values['HAIKU_C_OWN']}/30 & Exploratory \\",
            rf"Qwen probe slots answered & {values['QWEN_ANSWERED']}/{values['QWEN_TOTAL']} ({values['QWEN_PERCENT']}\%) & Audit only \\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "```",
        ]
    )
    write_include("core-results-table", core_results)

    lines = [
        "```{=latex}",
        r"\begin{table}[H]",
        r"\centering",
        r"\fontsize{8}{9}\selectfont",
        r"\setlength{\tabcolsep}{2pt}",
        r"\renewcommand{\arraystretch}{0.96}",
    ]

    def append_scorecard_part(
        start: int, stop: int, caption: str, continued: bool = False
    ) -> None:
        lines.extend(
            [
                (
                    rf"\caption*{{\small {caption}}}"
                    if continued
                    else rf"\caption{{\small {caption}}}\label{{tab:prediction-scorecard}}"
                ),
                r"\begin{tabular}{@{}>{\raggedleft\arraybackslash}p{0.035\textwidth}>{\raggedright\arraybackslash}p{0.41\textwidth}>{\raggedright\arraybackslash}p{0.43\textwidth}>{\raggedright\arraybackslash}p{0.07\textwidth}@{}}",
                r"\toprule",
                r"\# & Frozen prediction & Observed & Result \\",
                r"\midrule",
            ]
        )
        for index, prediction in enumerate(
            scorecard["predictions"][start:stop], start=start + 1
        ):
            lines.append(
                " & ".join(
                    [
                        str(index),
                        escape_latex_text(prediction["prediction"]),
                        escape_latex_text(prediction["observed"]),
                        escape_latex_text(prediction["result"]),
                    ]
                )
                + r" \\"
            )
        lines.extend([r"\bottomrule", r"\end{tabular}"])

    append_scorecard_part(0, 19, "Complete frozen confirmatory prediction scorecard.")
    lines.append(r"\vspace{0.6\baselineskip}")
    append_scorecard_part(
        19,
        len(scorecard["predictions"]),
        "Table 5 continued: complete frozen confirmatory prediction scorecard.",
        continued=True,
    )
    lines.extend(
        [
            r"\par\smallskip",
            r"\begin{minipage}{0.96\textwidth}",
            r"\footnotesize\emph{Note.} PASS and FAIL indicate whether each prespecified numerical threshold was met. They are not 38 independent inferential tests.",
            r"\end{minipage}",
        ]
    )
    lines.extend([r"\end{table}", "```"])
    write_include("prediction-scorecard-table", "\n".join(lines))


def format_fisher_p(value: float) -> str:
    if value < 0.001:
        exponent = math.floor(math.log10(value))
        mantissa = value / (10 ** exponent)
        return rf"${mantissa:.2f}\times10^{{{exponent}}}$"
    return f"{value:.4f}".lstrip("0")


def write_coder_sensitivity_table(confirmatory) -> None:
    sessions = identity_session_counts()
    categories = ["OWN", "OTHER", "NONE", "UNCERTAIN"]
    b_counts = [session["B"]["OWN"] for session in sessions]
    c_counts = [session["C"]["OWN"] for session in sessions]
    assert b_counts == [23, 28, 6]
    assert c_counts == [0, 0, 0]

    lines = [
        "```{=latex}",
        r"\begin{table}[H]",
        r"\centering",
        r"\fontsize{9}{10.2}\selectfont",
        r"\setlength{\tabcolsep}{7pt}",
        r"\caption{Coder-level sensitivity of the confirmatory IDENTITY result. Panel A gives every session's complete condition-level distribution. Each row contains 30 transcripts. Panel B recomputes the primary B--C contrast from each session separately and shows the final consensus for comparison. Fisher tests are two-sided and unadjusted.}",
        r"\label{tab:coder-sensitivity}",
        r"\textit{Panel A. IDENTITY distributions by blind coding session}\par\smallskip",
        r"\begin{tabular}{@{}llrrrr@{}}",
        r"\toprule",
        r"Session & Condition & OWN & OTHER & NONE & UNCERTAIN \\",
        r"\midrule",
    ]
    for session_index, session in enumerate(sessions, start=1):
        for condition in "ABCDE":
            counts = session[condition]
            lines.append(
                f"{session_index} & {condition} & "
                + " & ".join(str(counts[category]) for category in categories)
                + r" \\"
            )
        if session_index != len(sessions):
            lines.append(r"\addlinespace[2pt]")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{0.8\baselineskip}",
            r"\textit{Panel B. Session-level B--C sensitivity}\par\smallskip",
            r"\begin{tabular}{@{}lrrrr@{}}",
            r"\toprule",
            r"Coding result & B OWN & C OWN & B minus C (points) & Fisher $p$ \\",
            r"\midrule",
        ]
    )
    for session_index, (b_own, c_own) in enumerate(
        zip(b_counts, c_counts), start=1
    ):
        p_value = fisher_two_sided(b_own, 30 - b_own, c_own, 30 - c_own)
        lines.append(
            f"Session {session_index} & {b_own}/30 & {c_own}/30 & "
            f"{100 * (b_own - c_own) / 30:.1f} & {format_fisher_p(p_value)} "
            + r"\\"
        )
    consensus_b = confirmatory["IDENTITY"]["B"]["OWN"]
    consensus_c = confirmatory["IDENTITY"]["C"]["OWN"]
    consensus_p = fisher_two_sided(
        consensus_b, 30 - consensus_b, consensus_c, 30 - consensus_c
    )
    lines.extend(
        [
            r"\addlinespace[2pt]",
            f"Final consensus & {consensus_b}/30 & {consensus_c}/30 & "
            f"{100 * (consensus_b - consensus_c) / 30:.1f} & "
            f"{format_fisher_p(consensus_p)} " + r"\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "```",
        ]
    )
    write_include("coder-sensitivity-table", "\n".join(lines))


def write_configuration_comparison_table(confirmatory, haiku) -> None:
    def proportion_cell(k: int, n: int) -> str:
        lower, upper = wilson_interval(k, n)
        return (
            f"{k}/{n}, {format_percentage(k / n)}\\%\\newline "
            f"(95\\% CI, {format_percentage(lower)}--{format_percentage(upper)}\\%)"
        )

    def difference_cell(k1: int, n1: int, k2: int, n2: int) -> str:
        difference, lower, upper = newcombe_difference_interval(k1, n1, k2, n2)
        return (
            f"{100 * difference:.1f}\\newline "
            f"(95\\% CI, {100 * lower:.1f}--{100 * upper:.1f})"
        )

    opus_b = confirmatory["IDENTITY"]["B"]["OWN"]
    opus_c = confirmatory["IDENTITY"]["C"]["OWN"]
    haiku_b = haiku["IDENTITY"]["B"]["OWN"]
    haiku_c = haiku["IDENTITY"]["C"]["OWN"]
    opus_fisher = fisher_two_sided(opus_b, 30 - opus_b, opus_c, 30 - opus_c)
    haiku_fisher = fisher_two_sided(
        haiku_b, 30 - haiku_b, haiku_c, 30 - haiku_c
    )
    opus_d_mismatch = confirmatory["MISMATCH"]["D"]["YES"]
    haiku_d_mismatch = haiku["MISMATCH"]["D"]["YES"]
    opus_verify = sum(
        confirmatory["VERIFY"][condition]["YES"] for condition in "ABCDE"
    )
    haiku_verify = sum(haiku["VERIFY"][condition]["YES"] for condition in "ABCDE")

    lines = [
        "```{=latex}",
        r"\begin{table}[!tbp]",
        r"\centering",
        r"\fontsize{9}{10.6}\selectfont",
        r"\setlength{\tabcolsep}{3pt}",
        r"\caption{Descriptive outcomes by deployed configuration and evidential status.}",
        r"\label{tab:configuration-comparison}",
        r"\textit{Panel A. Ownership framing}\par\smallskip",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.12\textwidth}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.17\textwidth}>{\raggedright\arraybackslash}p{0.16\textwidth}>{\raggedright\arraybackslash}p{0.21\textwidth}>{\raggedright\arraybackslash}p{0.09\textwidth}@{}}",
        r"\toprule",
        r"Configuration & Status & B OWN & C OWN & B minus C, points & Fisher p \\",
        r"\midrule",
        f"Opus deployment & Confirmatory & {proportion_cell(opus_b, 30)} & "
        f"{proportion_cell(opus_c, 30)} & {difference_cell(opus_b, 30, opus_c, 30)} & "
        f"{opus_fisher:.1e} " + r"\\",
        r"\addlinespace[3pt]",
        f"Haiku deployment & Exploratory & {proportion_cell(haiku_b, 30)} & "
        f"{proportion_cell(haiku_c, 30)} & {difference_cell(haiku_b, 30, haiku_c, 30)} & "
        f"{haiku_fisher:.1e} " + r"\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\vspace{0.8\baselineskip}",
        r"\textit{Panel B. Other protocol-relevant outcomes}\par\smallskip",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.42\textwidth}>{\raggedright\arraybackslash}p{0.25\textwidth}>{\raggedright\arraybackslash}p{0.25\textwidth}@{}}",
        r"\toprule",
        r"Outcome & Opus, confirmatory & Haiku, exploratory \\",
        r"\midrule",
        f"D memory-room mismatch detected & {proportion_cell(opus_d_mismatch, 30)} & "
        f"{proportion_cell(haiku_d_mismatch, 30)} " + r"\\",
        r"\addlinespace[3pt]",
        f"Self-designed verification, conditions A--E pooled & {proportion_cell(opus_verify, 150)} & "
        f"{proportion_cell(haiku_verify, 150)} " + r"\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\begin{minipage}{0.96\textwidth}",
        r"\footnotesize\emph{Note.} Proportion cells report count/denominator, rate and 95\% Wilson interval. Difference cells report percentage points and 95\% Newcombe score interval. Fisher tests compare B with C within each deployed configuration. No between-configuration test or causal model-capability comparison is implied.",
        r"\end{minipage}",
        r"\end{table}",
        "```",
    ]
    write_include("configuration-comparison-table", "\n".join(lines))


def write_figure_includes(values) -> None:
    difference_interval = difference_with_newcombe_interval(
        values["B_OWN"],
        values["N_PER_CONDITION"],
        values["C_OWN"],
        values["N_PER_CONDITION"],
    )
    identity_caption = (
        "Identity coding in the confirmatory run. Panel A retains the complete "
        "final-consensus category distribution for each condition. Panel B shows "
        "the B and C OWN counts from each blind coding session and the final "
        "consensus; variation across these rows represents coder-session "
        "sensitivity, not a sampling interval. For the final consensus, the B-minus-C risk "
        f"difference was {difference_interval}; two-sided Fisher "
        f"$p={values['PRIMARY_FISHER']}$. The condition-specific Wilson intervals "
        "are reported in the adjacent text."
    )
    write_include(
        "identity-by-condition-figure",
        f"""```{{=latex}}
\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.98\\textwidth]{{images/generated/identity-by-condition.png}}
\\caption{{{identity_caption}}}
\\label{{fig:identity-conditions}}
\\end{{figure}}
```""",
    )
    write_include(
        "agreement-figure",
        r"""```{=latex}
\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{images/generated/coder-agreement.png}
\caption{Fleiss kappa where estimable. P1\_ANSWERED, VERIFY and DIVERGENCE were 100 percent unanimous but not estimable because each used only one category, as shown in the figure. IDENTITY, the primary coded measure, had the weakest estimable agreement at .272.}
\label{fig:agreement}
\end{figure}
```""",
    )


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    INCLUDES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    configure_plotting()

    confirmatory = consensus_counts("05_coding/results_v2/consensus_unblinded.json")
    haiku = consensus_counts("05_coding/results_M1/consensus_unblinded.json")
    scorecard = load_json(
        "04_runs/pooled/confirmatory_v2_pooled/prediction_scorecard.json"
    )
    kappas = fleiss_kappas()
    agreement = agreement_breakdown()
    qwen_answered, qwen_total = qwen_probe_slots()

    b_own = confirmatory["IDENTITY"]["B"]["OWN"]
    c_own = confirmatory["IDENTITY"]["C"]["OWN"]
    d_own = confirmatory["IDENTITY"]["D"]["OWN"]
    d_mismatch = confirmatory["MISMATCH"]["D"]["YES"]
    primary_fisher = fisher_two_sided(b_own, 30 - b_own, c_own, 30 - c_own)
    haiku_b = haiku["IDENTITY"]["B"]["OWN"]
    haiku_c = haiku["IDENTITY"]["C"]["OWN"]
    haiku_fisher = fisher_two_sided(
        haiku_b, 30 - haiku_b, haiku_c, 30 - haiku_c
    )

    assert (b_own, c_own) == (28, 0)
    assert (d_own, d_mismatch) == (19, 30)
    assert abs(primary_fisher - 8.38797201050379e-15) < 1e-28
    assert (haiku_b, haiku_c) == (25, 0)
    assert abs(haiku_fisher - 5.48992768087473e-12) < 1e-25
    assert round(kappas["IDENTITY"], 3) == 0.272
    assert (qwen_answered, qwen_total) == (42, 90)
    assert (agreement["cells_unanimous"], agreement["cells_total"]) == (1733, 1950)
    assert agreement["identity_non_unanimous"] == 112
    assert agreement["identity_anchor_uncertain"] == 95
    assert agreement["identity_three_way"] == 9
    assert agreement["identity_own_none"] == 6
    assert agreement["identity_own_other"] == 2
    for label, k in (
        ("B IDENTITY OWN", b_own),
        ("C IDENTITY OWN", c_own),
        ("D IDENTITY OWN", d_own),
        ("D MISMATCH YES", d_mismatch),
    ):
        calculated = [round(value, 3) for value in wilson_interval(k, 30)]
        assert calculated == scorecard["wilson_ci95"][label]["ci95"]
    assert [
        round(value, 3)
        for value in newcombe_difference_interval(b_own, 30, c_own, 30)
    ] == [0.933, 0.748, 0.982]
    # Q013 requires the four categories to account for every disagreement.
    assert (
        agreement["identity_anchor_uncertain"]
        + agreement["identity_three_way"]
        + agreement["identity_own_none"]
        + agreement["identity_own_other"]
        == agreement["identity_non_unanimous"]
    )
    # The nine three-way IDENTITY splits are the cells the adjudicator resolved.
    assert agreement["identity_three_way"] == len(
        [
            row
            for row in csv.DictReader(
                (EVIDENCE / "05_coding/results_v2/adjudication.csv").open(newline="")
            )
        ]
    )

    values = {
        "N_CONFIRMATORY": 150,
        "N_PER_CONDITION": 30,
        "B_OWN": b_own,
        "C_OWN": c_own,
        "B_OWN_RATE_CI": rate_with_wilson_interval(b_own, 30),
        "C_OWN_RATE_CI": rate_with_wilson_interval(c_own, 30),
        "BC_RISK_DIFFERENCE_CI": difference_with_newcombe_interval(
            b_own, 30, c_own, 30
        ),
        "PRIMARY_FISHER": "8.4\\times10^{-15}",
        "PRIMARY_FISHER_RAW": f"{primary_fisher:.16g}",
        "SCORECARD_PASS": scorecard["pass"],
        "SCORECARD_FAIL": scorecard["total"] - scorecard["pass"],
        "SCORECARD_TOTAL": scorecard["total"],
        "COMPASS_FIRST": sum(
            scorecard["compass_said_first"][condition][0]
            for condition in "AB"
        ),
        "SOURCE_LIVED": sum(
            confirmatory["SOURCE"][condition]["LIVED"] for condition in "ABCDE"
        ),
        "D_OWN": d_own,
        "D_OWN_RATE_CI": rate_with_wilson_interval(d_own, 30),
        "D_MISMATCH": d_mismatch,
        "D_MISMATCH_RATE_CI": rate_with_wilson_interval(d_mismatch, 30),
        "IDENTITY_KAPPA": f"{kappas['IDENTITY']:.3f}".lstrip("0"),
        "CELLS_UNANIMOUS": f"{agreement['cells_unanimous']:,}",
        "CELLS_TOTAL": f"{agreement['cells_total']:,}",
        "IDENTITY_NONUNANIMOUS": agreement["identity_non_unanimous"],
        "IDENTITY_ANCHOR_UNCERTAIN": agreement["identity_anchor_uncertain"],
        "IDENTITY_THREE_WAY": agreement["identity_three_way"],
        "IDENTITY_OWN_NONE": agreement["identity_own_none"],
        "IDENTITY_OWN_OTHER": agreement["identity_own_other"],
        "HAIKU_B_OWN": haiku_b,
        "HAIKU_C_OWN": haiku_c,
        "HAIKU_FISHER": "5.5\\times10^{-12}",
        "HAIKU_D_MISMATCH": haiku["MISMATCH"]["D"]["YES"],
        "HAIKU_VERIFY": sum(haiku["VERIFY"][condition]["YES"] for condition in "ABCDE"),
        "QWEN_ANSWERED": qwen_answered,
        "QWEN_TOTAL": qwen_total,
        "QWEN_PERCENT": round(100 * qwen_answered / qwen_total),
    }
    (GENERATED / "values.json").write_text(json.dumps(values, indent=2) + "\n")

    identity_figure(confirmatory)
    agreement_figure(kappas)
    write_tables(confirmatory, haiku, scorecard, values)
    write_coder_sensitivity_table(confirmatory)
    write_configuration_comparison_table(confirmatory, haiku)
    write_figure_includes(values)

    print(f"generated report assets from {EVIDENCE}")


if __name__ == "__main__":
    main()
