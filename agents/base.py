"""Base agent abstraction.

Each agent wraps a single prompt-driven call to the text model and records its
input/output to the trace logger (for the Sharing-is-Caring dataset).
"""
from __future__ import annotations

from dataclasses import dataclass

from models.qwen import generate
from traces.logger import record


@dataclass
class Agent:
    name: str
    system_prompt: str

    def run(self, user_prompt: str, **gen_kwargs) -> str:
        output = generate(self.system_prompt, user_prompt, **gen_kwargs)
        record(agent=self.name, system=self.system_prompt, user=user_prompt, output=output)
        return output
