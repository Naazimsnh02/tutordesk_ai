"""Feature 2 — Weekly Teaching Pack (signature feature, claims Best Agent).

One click: Class + Subject + Chapter -> 5-agent pipeline ->
worksheet + homework + quiz + answer key + parent-note template,
exported as a single print-ready PDF.
"""
from __future__ import annotations

from dataclasses import dataclass

from agents import answer, curriculum, difficulty, question_gen, report
from models.aya import localize
from utils.pdf import to_pdf


@dataclass
class TeachingPack:
    worksheet: str
    homework: str
    quiz: str
    answer_key: str
    parent_note: str

    def localized(self, language: str) -> "TeachingPack":
        if language.lower() == "english":
            return self
        return TeachingPack(
            worksheet=localize(self.worksheet, language=language),
            homework=localize(self.homework, language=language),
            quiz=localize(self.quiz, language=language),
            answer_key=localize(self.answer_key, language=language),
            parent_note=localize(self.parent_note, language=language),
        )

    def to_pdf(self, *, grade: int, subject: str, chapter: str, out_path: str | None = None) -> str:
        """Combine all sections into one print-ready A4 PDF. Returns the file path."""
        body = (
            f"## Worksheet\n{self.worksheet}\n\n"
            f"## Homework\n{self.homework}\n\n"
            f"## Quiz\n{self.quiz}\n\n"
            f"## Answer Key\n{self.answer_key}\n\n"
            f"## Parent Note Template\n{self.parent_note}"
        )
        return to_pdf(
            f"Weekly Teaching Pack — Class {grade} {subject}",
            f"Chapter: {chapter}",
            body,
            out_path=out_path,
        )


def build_pack(
    chapter_text: str,
    *,
    grade: int,
    subject: str,
    question_count: int = 20,
    diff: str = "Medium",
    language: str = "English",
) -> TeachingPack:
    """Run the 5-agent pipeline and return a TeachingPack.

    Agent order: curriculum -> question_gen -> difficulty -> answer -> report.
    """
    # Agent 1: extract topic + objectives
    objectives = curriculum.understand(chapter_text, grade=grade, subject=subject)

    # Agent 2: generate questions
    raw_questions = question_gen.generate_questions(
        objectives, count=question_count, difficulty=diff
    )

    # Agent 3: validate difficulty
    validated_questions = difficulty.validate(raw_questions, grade=grade)

    # Agent 4: generate answer key (also splits worksheet / quiz by question type)
    key = answer.answer_key(validated_questions)

    # Split validated questions: first 60% -> worksheet, last 40% -> quiz
    lines = [l for l in validated_questions.splitlines() if l.strip()]
    split = max(1, int(len(lines) * 0.6))
    worksheet_qs = "\n".join(lines[:split])
    quiz_qs = "\n".join(lines[split:])

    # Homework: shorter set (every other question from worksheet)
    homework_qs = "\n".join(lines[::2][:10])

    # Agent 5: draft parent note from the topic summary
    note = report.parent_note("Student", f"Completed worksheets on: {objectives[:300]}")

    pack = TeachingPack(
        worksheet=worksheet_qs,
        homework=homework_qs,
        quiz=quiz_qs,
        answer_key=key,
        parent_note=note,
    )
    return pack.localized(language)
