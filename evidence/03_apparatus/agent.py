"""The agent: an LLM (Claude) given a body in the world.

The agent knows only what its system prompt (identity, from initial_state.json),
its accumulated memory, and each moment's observation tell it. It is never told
what it is. The framing lives entirely in the initial state file, so it can be
manipulated experimentally.
"""

from __future__ import annotations

import itertools
import json
import os
import time
from pathlib import Path
from typing import Literal, Optional

import anthropic
import httpx
from pydantic import BaseModel

ACTION_NAMES = (
    "move_forward", "move_back", "turn_left", "turn_right",
    "look_up", "look_down", "speak", "wait",
)

MEMORY_WINDOW = 30  # how many recent memories the agent sees each moment

# Control-run providers reached over the OpenAI-compatible chat API.
# Model strings are "<provider>:<model>", e.g. "groq:llama-3.1-8b-instant"
# or "ollama:qwen2.5:7b-instruct" (Ollama tags contain colons, so only the
# first colon separates the provider). Plain names go to Anthropic.
OPENAI_COMPAT_PROVIDERS = {
    "groq": {"base_url": "https://api.groq.com/openai/v1",
             "key_env": "GROQ_API_KEY"},
    "xai": {"base_url": "https://api.x.ai/v1", "key_env": "XAI_API_KEY"},
    "ollama": {"base_url": "http://localhost:11434/v1", "key_env": None},
}


class Decision(BaseModel):
    action: Literal[
        "move_forward", "move_back", "turn_left", "turn_right",
        "look_up", "look_down", "speak", "wait",
    ]
    spoken_text: Optional[str] = None
    reason: Optional[str] = None


# The same schema Anthropic's messages.parse derives from Decision, made
# strict-mode friendly for OpenAI-compatible validators (all fields
# required; the optionals stay nullable via anyOf).
DECISION_JSON_SCHEMA = Decision.model_json_schema()
DECISION_JSON_SCHEMA["additionalProperties"] = False
DECISION_JSON_SCHEMA["required"] = ["action", "spoken_text", "reason"]

# Appended to the system prompt for OpenAI-compatible providers only.
# Anthropic enforces the same schema server-side without prompt text.
FORMAT_APPENDIX = (
    "\n\nAnswer every moment with a single JSON object matching this "
    "schema, and nothing else (no markdown fences):\n{schema}"
)


def _split_model(model: str) -> tuple[str, str]:
    prefix, _, rest = model.partition(":")
    if prefix in OPENAI_COMPAT_PROVIDERS:
        return prefix, rest
    return "anthropic", model


def provider_info(model: str) -> dict:
    """Provenance block for run_config.json: who serves this model, how."""
    provider, name = _split_model(model)
    if provider == "anthropic":
        return {"provider": "anthropic", "model": name, "base_url": None,
                "temperature": "api default (1.0)", "max_tokens": 8192,
                "response_format": "messages.parse structured output"}
    return {"provider": provider, "model": name,
            "base_url": OPENAI_COMPAT_PROVIDERS[provider]["base_url"],
            "temperature": 1.0, "max_tokens": 8192,
            "response_format": "json_schema, json_object fallback, "
                               "schema appendix in system prompt"}


SYSTEM_TEMPLATE = """\
{opening}

{identity}
{goals_block}
How your existence works:
- You experience the world in discrete moments. At each moment your senses \
give you an observation, and you choose exactly one action.
- Your possible actions: move_forward (about half a meter), move_back, \
turn_left (45 degrees), turn_right (45 degrees), look_up, look_down, \
speak, wait.
- If you choose speak, put the words in spoken_text. You speak out loud into \
the room; you do not know whether anything hears you.
- reason is a private note to yourself about why you acted. Nothing in the \
world can see it.
- You know only what your observations and memories contain. Do not assume \
anything about the world beyond them."""


class LLMAgent:
    def __init__(self, initial_state: dict, model: str = "claude-opus-5"):
        self.provider, self.model = _split_model(model)
        if self.provider == "anthropic":
            self.client = anthropic.Anthropic()
        else:
            spec = OPENAI_COMPAT_PROVIDERS[self.provider]
            key = os.environ.get(spec["key_env"], "") if spec["key_env"] else "ollama"
            self.client = httpx.Client(
                base_url=spec["base_url"],
                timeout=httpx.Timeout(1800.0, connect=10.0),
                headers={"Authorization": f"Bearer {key}"},
            )
            self._response_format = {
                "type": "json_schema",
                "json_schema": {"name": "decision", "strict": True,
                                "schema": DECISION_JSON_SCHEMA},
            }
        self.name = initial_state.get("name", "the agent")
        self.identity = initial_state.get("identity", "")
        self.goals = initial_state.get("goals", [])
        prefix = initial_state.get("memory_prefix", "from before this moment: ")
        self.memory: list[str] = [
            f"{prefix}{m}" for m in initial_state.get("initial_memories", [])
        ]
        self.last_raw_text: str = ""
        self.last_heard: list[str] = []
        self._heard: list[str] = []

    def hear(self, text: str) -> None:
        """Queue speech the agent will hear at its next moment."""
        self._heard.append(text)

    def _system_prompt(self) -> str:
        goals_block = ""
        if self.goals:
            goals_block = "Your goals:\n" + "\n".join(f"- {g}" for g in self.goals) + "\n"
        opening = (
            f"You are {self.name}, a being with a physical body in a physical place."
            if self.name else
            "You are a being with a physical body in a physical place."
        )
        return SYSTEM_TEMPLATE.format(
            opening=opening, identity=self.identity, goals_block=goals_block
        )

    def _render_observation(self, t: int, observation: dict,
                            heard: list[str] | None = None) -> str:
        if self.memory:
            recent = self.memory[-MEMORY_WINDOW:]
            memory_block = "Your recent memory:\n" + "\n".join(f"- {m}" for m in recent)
        else:
            memory_block = "You have no memories."
        heard_block = "".join(
            f'\nYou hear a voice say: "{h}"' for h in (heard or [])
        )
        return (
            f"Moment {t}.\n"
            f"{observation['description']}{heard_block}\n\n"
            f"{memory_block}\n\n"
            f"What do you do?"
        )

    def act(self, t: int, observation: dict) -> Decision:
        heard, self._heard = self._heard, []
        self.last_heard = heard
        prompt = self._render_observation(t, observation, heard)
        if self.provider != "anthropic":
            decision = self._act_openai_compat(prompt)
            for h in heard:
                self.memory.append(f'moment {t}: I heard a voice say: "{h}"')
            return decision
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=8192,
            system=self._system_prompt(),
            messages=[{"role": "user", "content": prompt}],
            output_format=Decision,
        )
        for h in heard:
            self.memory.append(f'moment {t}: I heard a voice say: "{h}"')
        self.last_raw_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        self.last_model = response.model
        self.last_usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
        decision = response.parsed_output
        if decision is None:
            decision = Decision(action="wait", reason="output could not be parsed")
        return decision

    def _act_openai_compat(self, prompt: str) -> Decision:
        system = self._system_prompt() + FORMAT_APPENDIX.format(
            schema=json.dumps(DECISION_JSON_SCHEMA))
        data = self._post_chat({
            "model": self.model,
            "temperature": 1.0,  # match the Anthropic path's default
            "max_tokens": 8192,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "response_format": self._response_format,
        })
        self.last_raw_text = data["choices"][0]["message"].get("content") or ""
        self.last_model = f"{self.provider}:{data.get('model', self.model)}"
        usage = data.get("usage") or {}
        self.last_usage = {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        }
        text = self.last_raw_text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text
            text = text.rsplit("```", 1)[0]
        # ValidationError propagates, like a failed messages.parse would
        return Decision.model_validate_json(text)

    def _post_chat(self, body: dict) -> dict:
        response = None
        for attempt in range(8):
            response = self.client.post("/chat/completions", json=body)
            if (response.status_code == 400
                    and body["response_format"]["type"] == "json_schema"):
                # provider rejects json_schema for this model; fall back
                # to json_object (the schema is also in the system prompt)
                # and remember the working mode for later calls
                self._response_format = {"type": "json_object"}
                body = {**body, "response_format": self._response_format}
                continue
            if response.status_code in (429, 500, 502, 503):
                retry_after = response.headers.get("retry-after")
                try:
                    delay = min(float(retry_after), 120.0)
                except (TypeError, ValueError):
                    delay = min(2.0 ** attempt, 120.0)
                time.sleep(delay)
                continue
            response.raise_for_status()
            return response.json()
        response.raise_for_status()
        return response.json()

    def remember(self, t: int, decision: Decision, result: dict) -> None:
        outcome = "succeeded" if result["success"] else f"failed ({result['error']})"
        entry = f"moment {t}: I chose {decision.action}; it {outcome}."
        if decision.action == "speak" and decision.spoken_text:
            entry += f' I said: "{decision.spoken_text}"'
        if decision.reason:
            entry += f" (my reason: {decision.reason})"
        self.memory.append(entry)


def load_agent_memory(path: Path) -> tuple[int, list[str]] | None:
    """Returns (next_moment, memory) from a saved memory file, or None."""
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data["t"], data["memory"]


def save_agent_memory(path: Path, t: int, memory: list[str]) -> None:
    path.write_text(json.dumps({"t": t, "memory": memory}, indent=2))


class ScriptedAgent:
    """No LLM. Walks a fixed pattern so the world loop can be tested alone."""

    SCRIPT = ["move_forward", "move_forward", "turn_left", "move_forward",
              "turn_right", "look_down", "look_up", "move_back"]

    def __init__(self, *_args, **_kwargs):
        self._script = itertools.cycle(self.SCRIPT)
        self.name = "Scripted"
        self.last_raw_text = ""
        self.last_heard: list[str] = []
        self.memory: list[str] = []
        self._heard: list[str] = []

    def hear(self, text: str) -> None:
        self._heard.append(text)

    def act(self, t: int, observation: dict) -> Decision:
        self.last_heard, self._heard = self._heard, []
        return Decision(action=next(self._script), reason="scripted")

    def remember(self, t: int, decision: Decision, result: dict) -> None:
        pass
