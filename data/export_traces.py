"""Export traces to HF Hub as a public dataset (Sharing-is-Caring badge).

Usage:
    python data/export_traces.py              # runtime agent traces only
    python data/export_traces.py --sessions   # build sessions only (Claude Code JSONL)
    python data/export_traces.py --all        # both

Two trace types are published to naazimsnh02/tutordesk-agent-traces:

  build_sessions/   Raw Claude Code JSONL sessions (redacted by data/redact_sessions.py).
                    Natively rendered by HF Data Studio's agent trace viewer.
                    Per HF docs: https://huggingface.co/docs/hub/en/agent-traces

  runtime_traces/   Per-agent records from live app runs (written by traces/logger.py).
                    Schema: agent, system, user, output, ts
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRACES_JSONL = ROOT / "traces" / "raw" / "agent_traces.jsonl"
BUILD_SESSIONS_DIR = ROOT / "traces" / "build_sessions"
HF_REPO = "naazimsnh02/tutordesk-agent-traces"


# ---------------------------------------------------------------------------
# Runtime traces (app agent calls)
# ---------------------------------------------------------------------------

def _load_runtime_traces() -> list[dict]:
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


def export_runtime(token: str) -> None:
    """Push runtime agent traces as a Parquet dataset split."""
    try:
        from datasets import Dataset
    except ImportError as exc:
        raise RuntimeError("Run: pip install datasets>=2.20") from exc

    rows = _load_runtime_traces()
    if not rows:
        print(
            "No runtime traces found. Run the app first to generate agent traces, "
            "then re-run this script.",
            file=sys.stderr,
        )
        return

    clean = [
        {
            "agent": r.get("agent", ""),
            "system": r.get("system", ""),
            "user": r.get("user", ""),
            "output": r.get("output", ""),
            "ts": float(r.get("ts", 0.0)),
        }
        for r in rows
    ]

    ds = Dataset.from_list(clean)
    ds.push_to_hub(HF_REPO, data_dir="runtime_traces", token=token)
    print(f"Pushed {len(clean)} runtime traces → https://huggingface.co/datasets/{HF_REPO}/viewer/default/runtime_traces")


# ---------------------------------------------------------------------------
# Build sessions (Claude Code JSONL — native HF trace viewer format)
# ---------------------------------------------------------------------------

def export_sessions(token: str) -> None:
    """Upload redacted Claude Code JSONL sessions to build_sessions/ folder in the dataset.

    Per HF docs (https://huggingface.co/docs/hub/en/agent-traces), Claude Code JSONL
    files are natively rendered by HF Data Studio without any conversion.
    """
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise RuntimeError("Run: pip install huggingface_hub>=0.23") from exc

    if not BUILD_SESSIONS_DIR.exists() or not any(BUILD_SESSIONS_DIR.glob("*.jsonl")):
        print(
            f"No redacted build sessions found in {BUILD_SESSIONS_DIR}.\n"
            "Run first: python data/redact_sessions.py",
            file=sys.stderr,
        )
        return

    session_files = sorted(BUILD_SESSIONS_DIR.glob("*.jsonl"))
    api = HfApi(token=token)

    # Ensure the dataset repo exists
    api.create_repo(repo_id=HF_REPO, repo_type="dataset", exist_ok=True)

    print(f"Uploading {len(session_files)} build session(s) to {HF_REPO}/build_sessions/ ...")
    for f in session_files:
        api.upload_file(
            path_or_fileobj=str(f),
            path_in_repo=f"build_sessions/{f.name}",
            repo_id=HF_REPO,
            repo_type="dataset",
            commit_message=f"Add build session {f.name}",
        )
        print(f"  uploaded: {f.name}")

    print(f"\nBuild sessions live → https://huggingface.co/datasets/{HF_REPO}")
    print("Open Data Studio and click any .jsonl row to view the session timeline.")


# ---------------------------------------------------------------------------
# Dataset card
# ---------------------------------------------------------------------------

DATASET_CARD = """\
---
license: mit
format: agent-traces
tags:
  - agent-traces
  - claude-code
  - build-small-hackathon
  - tutordesk-ai
  - education
  - indian-education
configs:
  - config_name: build_sessions
    data_files: build_sessions/*.jsonl
---

# TutorDesk AI — Agent Traces

**Sharing is Caring** badge dataset for the [HuggingFace Build Small Hackathon 2026](https://huggingface.co/build-small-hackathon).

## Contents

### `build_sessions/` — Claude Code Build Sessions (native trace viewer)

{session_count} raw Claude Code (Sonnet 4.6) JSONL sessions covering the full build of
TutorDesk AI — from blank repo through Phase 6 completion. Natively rendered by
[HF Data Studio's agent trace viewer](https://huggingface.co/docs/hub/en/agent-traces).

Sessions cover: repo scaffolding, Modal serving architecture, 5-agent pipeline,
Qwen3-4B fine-tuning workflow, MiniCPM-V vision integration, FLUX diagram generation,
Tiny Aya multilingual support, Off-Brand Gradio theme, offline/llama.cpp mode.

Secrets and local paths have been redacted. HF usernames (`naazimsnh02`) are kept as
they are public-facing identifiers.

### `runtime_traces/` — App Agent Runtime Traces

Per-agent records captured during live pipeline runs. Schema: `agent`, `system`,
`user`, `output`, `ts`. Agents: curriculum, question_gen, difficulty, answer, report, grader.

## Related

- Space: [naazimsnh02/tutordesk-ai](https://huggingface.co/spaces/naazimsnh02/tutordesk-ai)
- Model: [naazimsnh02/tutordesk-qwen3-4b](https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b)
"""


def push_dataset_card(token: str, session_count: int) -> None:
    try:
        from huggingface_hub import HfApi
    except ImportError:
        return
    api = HfApi(token=token)
    api.create_repo(repo_id=HF_REPO, repo_type="dataset", exist_ok=True)
    card_text = DATASET_CARD.format(session_count=session_count)
    api.upload_file(
        path_or_fileobj=card_text.encode(),
        path_in_repo="README.md",
        repo_id=HF_REPO,
        repo_type="dataset",
        commit_message="Update dataset card",
    )
    print("Dataset card pushed.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    do_sessions = "--sessions" in sys.argv or "--all" in sys.argv
    do_runtime = "--runtime" in sys.argv or "--all" in sys.argv
    # Default (no flags) = runtime only, for backwards compat
    if not do_sessions and not do_runtime:
        do_runtime = True

    tok = os.getenv("HF_TOKEN") or ""
    if not tok:
        print("Set HF_TOKEN env var first.", file=sys.stderr)
        sys.exit(1)

    if do_sessions:
        session_files = sorted(BUILD_SESSIONS_DIR.glob("*.jsonl")) if BUILD_SESSIONS_DIR.exists() else []
        push_dataset_card(tok, session_count=len(session_files))
        export_sessions(tok)

    if do_runtime:
        export_runtime(tok)
