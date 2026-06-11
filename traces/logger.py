"""Agent trace logger (Sharing-is-Caring badge).

Records every agent call (system/user/output) to JSONL under traces/raw/.
A later step (data/export_traces.py) cleans and publishes these as an HF dataset.
"""
from __future__ import annotations

import json
import os
import time

_OUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
_OUT_PATH = os.path.join(_OUT_DIR, "agent_traces.jsonl")


def record(*, agent: str, system: str, user: str, output: str) -> None:
    os.makedirs(_OUT_DIR, exist_ok=True)
    row = {"ts": time.time(), "agent": agent, "system": system, "user": user, "output": output}
    with open(_OUT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
