"""Collect and redact Claude Code build sessions for public upload (Sharing is Caring badge).

Usage:
    python data/redact_sessions.py

Reads the Claude Code JSONL sessions from ~/.claude/projects/ for both tutordesk project
folders, redacts known secrets and the local Windows username from paths, and writes clean
copies to traces/build_sessions/ ready for upload via data/export_traces.py.

What is redacted:
  - Actual token values matching known patterns (hf_*, ak-* Modal tokens)
  - The local Windows username in cwd/path fields (replaced with [USER])
  - Any bearer/authorization header values

What is kept:
  - HF usernames like naazimsnh02 (public-facing, same as GitHub/HF)
  - noreply@anthropic.com (not PII)
  - All code, prompts, tool calls, reasoning — the build story
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Source session directories
# ---------------------------------------------------------------------------
HOME = Path.home()
SESSION_DIRS = [
    HOME / ".claude" / "projects" / "C--Users-naazi-Downloads-New-Projects-tutordesk-ai",
    HOME / ".claude" / "projects" / "C--Users-naazi-Downloads-New-Projects-Tutordesk",
]

OUT_DIR = Path(__file__).parent.parent / "traces" / "build_sessions"

# ---------------------------------------------------------------------------
# Redaction rules — order matters: most-specific first
# ---------------------------------------------------------------------------
REDACTIONS: list[tuple[re.Pattern, str]] = [
    # Actual HF token values  (hf_ + 30-50 alphanumeric chars)
    (re.compile(r'hf_[A-Za-z0-9]{20,}'), "[HF_TOKEN_REDACTED]"),
    # Modal token IDs / secrets  (ak- + 15+ chars)
    (re.compile(r'ak-[A-Za-z0-9_\-]{15,}'), "[MODAL_TOKEN_REDACTED]"),
    # Bearer tokens in any Authorization header
    (re.compile(r'(?i)(authorization["\s:=]+bearer\s+)[A-Za-z0-9._\-]{20,}'), r'\1[BEARER_REDACTED]'),
    # Local Windows username in file paths — keep project path readable
    (re.compile(r'C:\\\\Users\\\\naazi\\\\'), r'C:\\\\Users\\\\[USER]\\\\'),
    (re.compile(r'C:/Users/naazi/'), 'C:/Users/[USER]/'),
    (re.compile(r'C:\\Users\\naazi\\'), r'C:\\Users\\[USER]\\'),
    # Same patterns inside JSON-escaped strings
    (re.compile(r'C:\\\\\\\\Users\\\\\\\\naazi\\\\\\\\'), r'C:\\\\\\\\Users\\\\\\\\[USER]\\\\\\\\'),
]


def _redact(text: str) -> str:
    for pattern, replacement in REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def _process_file(src: Path, dst: Path) -> int:
    """Redact src → dst. Returns line count written."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with open(src, encoding="utf-8") as fin, open(dst, "w", encoding="utf-8") as fout:
        for raw in fin:
            fout.write(_redact(raw))
            written += 1
    return written


def collect(dry_run: bool = False) -> list[Path]:
    """Find all JSONL session files, redact, write to OUT_DIR. Returns output paths."""
    found: list[tuple[Path, Path]] = []
    for d in SESSION_DIRS:
        if not d.exists():
            print(f"  skip (not found): {d}")
            continue
        for f in sorted(d.glob("*.jsonl")):
            out = OUT_DIR / f.name
            found.append((f, out))

    if not found:
        print("No session files found. Check SESSION_DIRS paths.")
        return []

    print(f"Found {len(found)} session file(s):")
    results: list[Path] = []
    for src, dst in found:
        size_kb = src.stat().st_size // 1024
        if dry_run:
            print(f"  [dry-run] {src.name}  ({size_kb} KB)  -> {dst}")
            results.append(dst)
            continue
        lines = _process_file(src, dst)
        print(f"  {src.name}  ({size_kb} KB, {lines} lines)  -> {dst.name}")
        results.append(dst)

    if not dry_run:
        print(f"\nRedacted sessions written to: {str(OUT_DIR)}")
    return results


def verify(paths: list[Path]) -> bool:
    """Spot-check that no raw tokens remain in the redacted output."""
    bad_patterns = [
        re.compile(r'hf_[A-Za-z0-9]{20,}'),
        re.compile(r'ak-[A-Za-z0-9_\-]{15,}'),
    ]
    clean = True
    for p in paths:
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for pat in bad_patterns:
            if pat.search(text):
                print(f"  WARNING: possible un-redacted secret in {p.name} (pattern: {pat.pattern})")
                clean = False
    if clean:
        print("Verification passed — no raw tokens found in redacted files.")
    return clean


if __name__ == "__main__":
    import sys
    dry = "--dry-run" in sys.argv
    print("=== TutorDesk AI — Build Session Redactor ===\n")
    out_paths = collect(dry_run=dry)
    if out_paths and not dry:
        print("\nRunning verification scan...")
        verify(out_paths)
        print(f"\nNext: python data/export_traces.py --sessions  (uploads {len(out_paths)} files to HF Hub)")
