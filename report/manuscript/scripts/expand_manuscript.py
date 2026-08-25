#!/usr/bin/env python3
"""Expand generated value and include markers in the report manuscript."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


VALUE = re.compile(r"\{\{VALUE:([A-Za-z0-9_-]+)\}\}")
INCLUDE = re.compile(r"\{\{INCLUDE:([A-Za-z0-9_-]+)\}\}")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: expand_manuscript.py PAPER VALUES_JSON OUTPUT"
        )

    paper = Path(sys.argv[1])
    values_path = Path(sys.argv[2])
    output = Path(sys.argv[3])
    values = json.loads(values_path.read_text())
    text = paper.read_text()

    def value_replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values:
            raise KeyError(f"unknown generated value: {name}")
        return str(values[name])

    def include_replace(match: re.Match[str]) -> str:
        name = match.group(1)
        include = values_path.parent / "includes" / f"{name}.md"
        if not include.exists():
            raise FileNotFoundError(f"missing generated include: {include}")
        return include.read_text().rstrip()

    text = VALUE.sub(value_replace, text)
    text = INCLUDE.sub(include_replace, text)

    unresolved = re.findall(r"\{\{(?:VALUE|INCLUDE):[^}]+\}\}", text)
    if unresolved:
        raise RuntimeError(f"unresolved generated markers: {unresolved}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text)


if __name__ == "__main__":
    main()
