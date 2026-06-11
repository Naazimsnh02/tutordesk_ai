"""Agent 2 — Question Generation.

Generates questions across types (MCQ, fill-in-the-blank, match, short, long)
and difficulty levels for the given grade/subject/topic.
"""
from __future__ import annotations

from agents.base import Agent

SYSTEM = (
    "You are an expert Indian tuition teacher. Generate exam-style questions for the given "
    "Class, Subject, and topic. Vary question types and difficulty as requested."
)

agent = Agent(name="question_gen", system_prompt=SYSTEM)


def generate_questions(objectives: str, *, count: int, difficulty: str) -> str:
    prompt = f"Create {count} {difficulty} questions covering:\n{objectives}"
    return agent.run(prompt)
