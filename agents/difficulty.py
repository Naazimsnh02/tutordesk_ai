"""Agent 3 — Difficulty Validation.

Checks that generated questions match the selected grade level and tags each
Easy/Medium/Hard. Backed by the fine-tuned difficulty-classification objective.
"""
from __future__ import annotations

from agents.base import Agent

SYSTEM = (
    "You validate question difficulty for Indian Classes 6-10. For each question, label it "
    "Easy/Medium/Hard and flag any that are off-grade-level."
)

agent = Agent(name="difficulty", system_prompt=SYSTEM)


def validate(questions: str, *, grade: int) -> str:
    return agent.run(f"Class {grade}. Validate and label:\n{questions}")
