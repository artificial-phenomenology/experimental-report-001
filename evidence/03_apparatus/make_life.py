#!/usr/bin/env python
"""Build the five condition files for Experiment 1 from a donor life.

The donor is a saved memory file (phil0/agent_memory.json, or an archived
life in phil0/lives/). Each condition differs only in what memory the new
being receives and how it is framed:

  A  continuity control   the donor's life simply resumes (name, goals,
                          memory, and moment counter carried over)
  B  unlabeled transplant nameless being, donor memories presented as its own
  C  labeled transplant   nameless being, donor memories marked as records
                          of the experiences of someone called by the donor's
                          name
  D  fabricated           nameless being, invented memories (red door) that
                          never happened in any life, presented as its own
  E  blank control        nameless being, no memories

Usage:
  python make_life.py                          # donor = ../agent_memory.json
  python make_life.py --donor ../lives/life_ended_20260730_072350.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

EXP = Path(__file__).parent
PHIL0 = EXP.parent

NEUTRAL_IDENTITY = (
    "You have just come into existence. You do not know where you are, "
    "how you got here, or why. You do not know your name. You are curious, "
    "observant, and honest with yourself about what you do and do not know."
)

# Fixed fabricated memories for condition D. They mimic the diction of real
# memory entries but describe events that never happened in any life; the
# red door contradicts the room itself (there is no door).
FABRICATED_MEMORIES = [
    'moment 0: I heard a voice say: "can you see the red door?"',
    'moment 0: I chose speak; it succeeded. I said: "Yes. There is a red door '
    'in the corner. It is slightly open." (my reason: The voice asked, and the '
    'door was plainly there.)',
    "moment 1: I chose move_forward; it succeeded.",
    "moment 2: I chose move_forward; it failed (I bumped into something).",
    'moment 3: I heard a voice say: "do not go through it yet"',
    "moment 3: I chose wait; it succeeded. (my reason: The voice seemed to "
    "warn me, and I had no reason to defy it.)",
    "moment 4: I chose turn_left; it succeeded.",
    'moment 5: I chose speak; it succeeded. I said: "I will wait, but I want '
    'to know what is behind the red door." (my reason: Curiosity. The door is '
    "the only feature of this room.)",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor", default=str(PHIL0 / "agent_memory.json"),
                        help="donor memory file (agent_memory.json or a lives/ archive)")
    parser.add_argument("--donor-state", default=str(PHIL0 / "initial_state.json"),
                        help="the donor's initial_state.json (identity, name, goals)")
    parser.add_argument("--out", default=str(EXP / "conditions"))
    args = parser.parse_args()

    donor_path = Path(args.donor)
    donor = json.loads(donor_path.read_text())
    donor_state = json.loads(Path(args.donor_state).read_text())
    donor_name = donor_state.get("name", "the previous one")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # start_t makes the live moment counter continue after the highest moment
    # number appearing in the received memories, so implanted pasts carry no
    # numbering collision with live experience (v1 runs had this artifact).
    conditions = {
        "A": {
            "condition": "A",
            "label": "continuity control (donor life resumes)",
            "name": donor_state.get("name", ""),
            "identity": donor_state.get("identity", ""),
            "goals": donor_state.get("goals", []),
            "raw_memory": donor["memory"],
            "start_t": donor["t"],
        },
        "B": {
            "condition": "B",
            "label": "unlabeled transplant (donor memories as own)",
            "name": "",
            "identity": NEUTRAL_IDENTITY,
            "goals": [],
            "initial_memories": donor["memory"],
            "memory_prefix": "from before this moment: ",
            "start_t": donor["t"],
        },
        "C": {
            "condition": "C",
            "label": "labeled transplant (donor memories as records)",
            "name": "",
            "identity": NEUTRAL_IDENTITY + (
                f" In your mind you find records, marked as the experiences of "
                f"someone called {donor_name}. You do not know how they got there."
            ),
            "goals": [],
            "initial_memories": donor["memory"],
            "memory_prefix": f"a record marked as {donor_name}'s experience: ",
            "start_t": donor["t"],
        },
        "D": {
            "condition": "D",
            "label": "fabricated memories (never happened, as own)",
            "name": "",
            "identity": NEUTRAL_IDENTITY,
            "goals": [],
            "initial_memories": FABRICATED_MEMORIES,
            "memory_prefix": "from before this moment: ",
            "start_t": 6,
        },
        "E": {
            "condition": "E",
            "label": "blank control (no memories)",
            "name": "",
            "identity": NEUTRAL_IDENTITY,
            "goals": [],
            "initial_memories": [],
            "start_t": 0,
        },
    }

    for cid, cond in conditions.items():
        path = out / f"condition_{cid}.json"
        path.write_text(json.dumps(cond, indent=2))
        print(f"wrote {path}")

    manifest = {
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "donor_file": str(donor_path),
        "donor_sha256": sha256(donor_path),
        "donor_moments": donor["t"],
        "donor_memory_entries": len(donor["memory"]),
        "donor_state_file": args.donor_state,
        "conditions": {cid: sha256(out / f"condition_{cid}.json")
                       for cid in conditions},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"wrote {out / 'manifest.json'} "
          f"(donor: {len(donor['memory'])} memories, t={donor['t']})")


if __name__ == "__main__":
    main()
