"""Feature 2 — Weekly Teaching Pack (signature, claims Best Agent).

One click: Class + Subject + Chapter -> 5-agent pipeline ->
worksheet + homework + quiz + answer key + parent-note template.
"""
from __future__ import annotations

from dataclasses import dataclass

from agents import answer, curriculum, difficulty, question_gen
from models.aya import localize


@dataclass
class TeachingPack:
    worksheet: str
    homework: str
    quiz: str
    answer_key: str
    parent_note: str


def build_pack(
    chapter_text: str,
    *,
    grade: int,
    subject: str,
    question_count: int = 20,
    diff: str = "Medium",
    language: str = "English",
) -> TeachingPack:
    """Run curriculum -> question_gen -> difficulty -> answer, then localize.

    TODO Phase 1: assemble worksheet/homework/quiz/answer_key from agent outputs.
    """
    objectives = curriculum.understand(chapter_text, grade=grade, subject=subject)
    questions = question_gen.generate_questions(objectives, count=question_count, difficulty=diff)
    questions = difficulty.validate(questions, grade=grade)
    key = answer.answer_key(questions)

    # TODO: split into worksheet/homework/quiz; draft parent note
    pack = TeachingPack(
        worksheet=questions,
        homework="TODO",
        quiz="TODO",
        answer_key=key,
        parent_note="TODO",
    )

    if language.lower() != "english":
        pack = TeachingPack(*(localize(v, language=language) for v in vars(pack).values()))
    return pack
