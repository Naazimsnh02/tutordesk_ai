"""Agent 1 — Curriculum Understanding.

Extracts topic, learning objectives, and concepts from a chapter (text or
vision-extracted) so downstream agents are grounded in the actual syllabus.
"""
from __future__ import annotations

from agents.base import Agent

SYSTEM = (
    "You are a CBSE/NCERT curriculum expert for Indian Classes 6-10 (Math & Science). "
    "Given chapter content, extract the topic, key concepts, and clear learning objectives."
)

agent = Agent(name="curriculum", system_prompt=SYSTEM)


def understand(chapter_text: str, *, grade: int, subject: str) -> str:
    """Return structured topic/objectives/concepts. TODO: parse into a dataclass."""
    prompt = f"Class {grade} {subject}. Chapter content:\n{chapter_text}"
    return agent.run(prompt)
