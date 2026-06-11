"""Agent 4 — Answer Generation.

Produces the answer key: correct answers, explanations, and step-by-step
solutions (especially for Math & Science numericals).
"""
from __future__ import annotations

from agents.base import Agent

SYSTEM = (
    "You are an answer-key author for Indian Classes 6-10 Math & Science. Provide correct "
    "answers with concise explanations and step-by-step working where relevant."
)

agent = Agent(name="answer", system_prompt=SYSTEM)


def answer_key(questions: str) -> str:
    return agent.run(f"Produce a full answer key with steps for:\n{questions}")
