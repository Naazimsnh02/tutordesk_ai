"""Export agent traces to HF Hub as a public dataset (Sharing-is-Caring badge).

Usage:
    python data/export_traces.py

Reads traces/raw/agent_traces.jsonl (written by traces/logger.py during normal app use),
cleans the rows, and pushes them to naazimsnh02/tutordesk-agent-traces on HF Hub.

The dataset schema:
  agent  : str   — which agent produced the trace (curriculum, question_gen, …)
  system : str   — the system prompt
  user   : str   — the user prompt
  output : str   — the model's response
  ts     : float — Unix timestamp
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

TRACES_JSONL = Path(__file__).parent.parent / "traces" / "raw" / "agent_traces.jsonl"
HF_REPO = "naazimsnh02/tutordesk-agent-traces"


def _load_traces() -> list[dict]:
    if not TRACES_JSONL.exists():
        return []
    rows: list[dict] = []
    with open(TRACES_JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def export(token: str | None = None, private: bool = False) -> None:
    try:
        from datasets import Dataset
    except ImportError as exc:
        raise RuntimeError("Run: pip install datasets>=2.20") from exc

    rows = _load_traces()
    if not rows:
        print(
            "No traces found. Run the app (with TUTORDESK_OFFLINE=0 or =1) first to "
            "generate agent traces, then re-run this script.",
            file=sys.stderr,
        )
        return

    # Normalise: ensure all expected fields are present
    clean = []
    for r in rows:
        clean.append({
            "agent": r.get("agent", ""),
            "system": r.get("system", ""),
            "user": r.get("user", ""),
            "output": r.get("output", ""),
            "ts": float(r.get("ts", 0.0)),
        })

    ds = Dataset.from_list(clean)
    tok = token or os.getenv("HF_TOKEN") or ""
    ds.push_to_hub(HF_REPO, token=tok, private=private)
    print(f"Pushed {len(clean)} traces → https://huggingface.co/datasets/{HF_REPO}")


if __name__ == "__main__":
    export()
