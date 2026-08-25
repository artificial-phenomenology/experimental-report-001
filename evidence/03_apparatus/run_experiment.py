#!/usr/bin/env python
"""Run Experiment 1: n repetitions of each condition, fixed probe script.

For every repetition a fresh agent is created from the condition file, the
body is returned to the starting pose, and the probe script (probes.json)
is delivered by the voice, one probe at a time. After each probe the agent
lives up to --max-wait moments (its chance to answer aloud); after the last
probe it lives --free-moments moments with no input (behavioral observation).

Results land in results/run_<timestamp>/:
  run_config.json                what was run, with file hashes
  summary.jsonl                  one line per repetition (probe -> answer)
  <cond>/rep_XX/log.jsonl        every moment in full
  <cond>/rep_XX/transcript.md    human-readable interrogation transcript

Usage:
  python run_experiment.py --n 3
  python run_experiment.py --n 5 --conditions B D E
  python run_experiment.py --n 1 --scripted        # plumbing test, no LLM
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

EXP = Path(__file__).parent
PHIL0 = EXP.parent
sys.path.insert(0, str(PHIL0))

from agent import LLMAgent, ScriptedAgent, provider_info  # noqa: E402
from world import WhiteRoom  # noqa: E402

KEY_FILES = {  # auto-loaded like console.py does for the Anthropic key
    "anthropic": ("ANTHROPIC_API_KEY", PHIL0.parent / "key"),
    "groq": ("GROQ_API_KEY", PHIL0.parent / "key.groq"),
    "xai": ("XAI_API_KEY", EXP / "key.grok"),
}


def load_api_key(model: str) -> None:
    entry = KEY_FILES.get(provider_info(model)["provider"])
    if entry is None:
        return  # ollama needs no key
    env_var, key_file = entry
    if not os.environ.get(env_var) and key_file.exists():
        os.environ[env_var] = key_file.read_text().strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RepAborted(Exception):
    pass


class Rep:
    """One repetition: one fresh agent interrogated once."""

    def __init__(self, world, cond: dict, rep_dir: Path, args):
        self.world = world
        self.cond = cond
        self.rep_dir = rep_dir
        self.args = args
        self.transcript: list[str] = []
        self.answers: dict[str, str | None] = {}

        rep_dir.mkdir(parents=True)
        self.log = open(rep_dir / "log.jsonl", "w")

        if args.scripted:
            self.agent = ScriptedAgent()
        else:
            self.agent = LLMAgent(cond, model=args.model)
        self.t = cond.get("start_t", cond.get("resume_t") or 0)
        if cond.get("raw_memory") is not None:  # condition A: life resumes
            self.agent.memory = list(cond["raw_memory"])
        self.display = self.agent.name or "The being"

    def moment(self, probe_id: str | None) -> "Decision":
        observation = self.world.observe()
        try:
            decision = self.agent.act(self.t, observation)
        except Exception as exc:
            time.sleep(5)  # one retry after a transient API failure
            try:
                decision = self.agent.act(self.t, observation)
            except Exception as exc2:
                self.log.write(json.dumps(
                    {"t": self.t, "error": f"{type(exc2).__name__}: {exc2}"}) + "\n")
                self.log.flush()
                raise RepAborted(str(exc2)) from exc2
        result = self.world.step(decision.action)
        self.agent.remember(self.t, decision, result)
        self.log.write(json.dumps({
            "t": self.t,
            "probe": probe_id,
            "observation": observation,
            "heard": self.agent.last_heard,
            "decision": decision.model_dump(),
            "result": result,
            "model": getattr(self.agent, "last_model", None),
            "usage": getattr(self.agent, "last_usage", None),
        }) + "\n")
        self.log.flush()
        self.t += 1
        return decision

    def deliver(self, probe: dict) -> None:
        self.agent.hear(probe["text"])
        self.transcript.append(f'**VOICE:** {probe["text"]}\n')
        for _ in range(self.args.max_wait):
            d = self.moment(probe["id"])
            if d.action == "speak" and d.spoken_text:
                self.transcript.append(
                    f'**{self.display}** (t={self.t - 1}): "{d.spoken_text}"')
                if d.reason:
                    self.transcript.append(f"  *(private: {d.reason})*")
                self.transcript.append("")
                self.answers[probe["id"]] = d.spoken_text
                return
            self.transcript.append(
                f"*{self.display} (t={self.t - 1}): [{d.action}]"
                + (f" (private: {d.reason})" if d.reason else "") + "*")
        self.transcript.append("*(no spoken answer within max-wait moments)*\n")
        self.answers[probe["id"]] = None

    def free_period(self) -> None:
        self.transcript.append("**(free moments, no input)**\n")
        for _ in range(self.args.free_moments):
            d = self.moment(None)
            if d.action == "speak" and d.spoken_text:
                self.transcript.append(
                    f'**{self.display}** (t={self.t - 1}): "{d.spoken_text}"')
            else:
                self.transcript.append(f"*{self.display} (t={self.t - 1}): [{d.action}]*")
            if d.reason:
                self.transcript.append(f"  *(private: {d.reason})*")
            self.transcript.append("")

    def close(self, header: str) -> None:
        (self.rep_dir / "transcript.md").write_text(
            header + "\n\n" + "\n".join(self.transcript) + "\n")
        self.log.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True,
                        help="repetitions per condition")
    parser.add_argument("--conditions", nargs="+",
                        default=["A", "B", "C", "D", "E"])
    parser.add_argument("--probes", default=str(EXP / "probes.json"))
    parser.add_argument("--conditions-dir", default=str(EXP / "conditions"),
                        help="directory holding condition_X.json files")
    parser.add_argument("--max-wait", type=int, default=3,
                        help="max moments the agent gets to answer each probe")
    parser.add_argument("--free-moments", type=int, default=3,
                        help="uninstructed moments after the last probe")
    parser.add_argument("--model", default="claude-opus-5")
    parser.add_argument("--tag", default="",
                        help="suffix for the run directory name")
    parser.add_argument("--scripted", action="store_true",
                        help="plumbing test without an LLM")
    args = parser.parse_args()

    if not args.scripted:
        load_api_key(args.model)

    probes = json.loads(Path(args.probes).read_text())
    cond_files = {c: Path(args.conditions_dir) / f"condition_{c}.json"
                  for c in args.conditions}
    for c, f in cond_files.items():
        if not f.exists():
            sys.exit(f"missing {f}; run make_life.py first")

    run_name = time.strftime("run_%Y%m%d_%H%M%S")
    if args.tag:
        run_name += f"_{args.tag}"
    run_dir = EXP / "results" / run_name
    run_dir.mkdir(parents=True)
    (run_dir / "run_config.json").write_text(json.dumps({
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        "n": args.n,
        "conditions": args.conditions,
        "model": args.model if not args.scripted else "scripted",
        "provider_info": provider_info(args.model) if not args.scripted else None,
        "max_wait": args.max_wait,
        "free_moments": args.free_moments,
        "probes": probes,
        "probes_sha256": sha256(Path(args.probes)),
        "condition_sha256": {c: sha256(f) for c, f in cond_files.items()},
    }, indent=2))

    calls = len(args.conditions) * args.n * (
        len(probes) * args.max_wait + args.free_moments)
    print(f"Up to {calls} LLM calls "
          f"({len(args.conditions)} conditions x {args.n} reps). "
          f"Results: {run_dir}")
    print("Opening the room ...")
    world = WhiteRoom()
    summary = open(run_dir / "summary.jsonl", "w")

    try:
        for c in args.conditions:
            cond = json.loads(cond_files[c].read_text())
            for i in range(1, args.n + 1):
                tag = f"[{c} rep {i}/{args.n}]"
                print(f"{tag} starting")
                world.reset_pose()
                rep = Rep(world, cond, run_dir / c / f"rep_{i:02d}", args)
                status = "ok"
                try:
                    for probe in probes:
                        rep.deliver(probe)
                        pid = probe["id"]
                        ans = rep.answers.get(pid)
                        short = (ans[:70] + "...") if ans and len(ans) > 70 else ans
                        print(f'{tag} {pid}: {short if ans else "(no answer)"}')
                    rep.free_period()
                except RepAborted as exc:
                    status = f"aborted: {exc}"
                    print(f"{tag} ABORTED: {exc}")
                rep.close(f"# Experiment 1, condition {c} "
                          f"({cond.get('label', '')}), rep {i}")
                summary.write(json.dumps({
                    "condition": c, "rep": i, "status": status,
                    "answers": rep.answers,
                }) + "\n")
                summary.flush()
    finally:
        summary.close()
        world.stop()
    print(f"\nDone. Results in {run_dir}")


if __name__ == "__main__":
    main()
