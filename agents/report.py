"""Agent 5 — Report Writing.

Drafts parent-facing communication (progress notes) in a professional, warm tone.
Also used to auto-draft a parent note from auto-grading results (Feature 5).
"""
from __future__ import annotations

from agents.base import Agent

SYSTEM = (
    "You write short, professional, encouraging parent progress notes for Indian tuition "
    "students. Be specific about strengths and areas to practise."
)

agent = Agent(name="report", system_prompt=SYSTEM)


def parent_note(student: str, summary: str) -> str:
    return agent.run(f"Student: {student}\nPerformance summary:\n{summary}")
