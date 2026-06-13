"""Feature 5 — Photo Auto-Grading (OpenBMB + Well-Tuned + Best Agent).

Two-stage pipeline:
  1. MiniCPM-V reads the answer sheet → structured per-question extraction.
  2. Fine-tuned Qwen3-4B grades each question Indian-style (step marks, partial credit).
Then a parent note is drafted from the aggregated result.

Marking scheme format (show this template in the UI):
  Q1 [3 marks]: Model answer for question 1
  Q2 [5 marks]:
    Step 1 (1 mark): ...
    Step 2 (2 marks): ...
    Step 3 (2 marks): ...
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from PIL import Image

from agents import grader, report
from models.minicpm import read_image
from utils import pdf as pdf_utils

_EXTRACT_PROMPT = (
    "This is a student's answer sheet. List every question number and the student's written answer.\n"
    "Use this exact format for each question:\n"
    "Q1: <student answer>\n"
    "Q2: <student answer>\n"
    "If an answer is blank or completely illegible write [blank]. "
    "Include every question visible on the sheet."
)


@dataclass
class QuestionResult:
    question_num: int
    awarded: int
    total: int
    breakdown: str


@dataclass
class GradeResult:
    student: str
    subject: str
    grade: int
    total_awarded: int
    total_marks: int
    results: list[QuestionResult] = field(default_factory=list)
    parent_note: str = ""

    def percentage(self) -> float:
        if self.total_marks == 0:
            return 0.0
        return round(100 * self.total_awarded / self.total_marks, 1)

    def summary_markdown(self) -> str:
        pct = self.percentage()
        lines = [
            f"## Grade Report — {self.student}",
            f"**Class {self.grade} · {self.subject}**  ",
            f"### Total: {self.total_awarded}/{self.total_marks} ({pct}%)\n",
            "| Q# | Awarded | Out of | First line of breakdown |",
            "|---|---|---|---|",
        ]
        for r in self.results:
            first_line = r.breakdown.splitlines()[0] if r.breakdown else "—"
            # strip the MARKS: prefix if echoed
            first_line = re.sub(r"^MARKS:\s*\d+/\d+\s*", "", first_line).strip() or "—"
            lines.append(f"| Q{r.question_num} | {r.awarded} | {r.total} | {first_line} |")
        return "\n".join(lines)

    def to_pdf(self) -> str:
        body_parts: list[str] = [
            f"Total: {self.total_awarded}/{self.total_marks} ({self.percentage()}%)\n",
        ]
        for r in self.results:
            body_parts.append(f"## Q{r.question_num}  [{r.awarded}/{r.total} marks]")
            body_parts.append(r.breakdown)
            body_parts.append("")
        if self.parent_note:
            body_parts += ["## Parent Note", self.parent_note]

        return pdf_utils.to_pdf(
            title=f"Grade Report — {self.student}",
            subtitle=f"Class {self.grade} · {self.subject}",
            body="\n".join(body_parts),
        )


def grade_sheet(
    image: Image.Image,
    *,
    marking_scheme: str,
    grade: int,
    subject: str,
    student: str = "Student",
) -> GradeResult:
    """Full auto-grading pipeline for a single answer sheet photo.

    Args:
        image: PIL image of the student's filled answer sheet.
        marking_scheme: Teacher-provided marking scheme text (use the Q[N marks] template).
        grade: Class number (6–10).
        subject: Subject name.
        student: Student's name for the report.

    Returns:
        GradeResult with per-question breakdown, total score, and parent note.
    """
    # Stage 1 — Vision: extract all student answers
    raw_answers = read_image(image, _EXTRACT_PROMPT)
    student_answers = _parse_student_answers(raw_answers)

    # Stage 2 — Parse marking scheme into structured questions
    questions = grader.parse_scheme(marking_scheme)

    # Stage 3 — Grade each question individually
    results: list[QuestionResult] = []
    for q in questions:
        q_num = q["q"]
        q_marks = q["marks"]
        q_answer = q["answer"]
        student_ans = student_answers.get(q_num, "[no answer found]")

        breakdown = grader.grade(
            question=f"Q{q_num}",
            marking_scheme=q_answer,
            student_answer=student_ans,
            marks=q_marks,
        )
        awarded = grader.extract_score(breakdown, q_marks)
        results.append(QuestionResult(
            question_num=q_num,
            awarded=awarded,
            total=q_marks,
            breakdown=breakdown,
        ))

    total_awarded = sum(r.awarded for r in results)
    total_marks = sum(r.total for r in results)

    # Stage 4 — Draft parent note
    per_q = ", ".join(f"Q{r.question_num}: {r.awarded}/{r.total}" for r in results)
    summary = f"{subject} test — {total_awarded}/{total_marks} marks. Per question: {per_q}"
    note = report.parent_note(student, summary)

    return GradeResult(
        student=student,
        subject=subject,
        grade=grade,
        total_awarded=total_awarded,
        total_marks=total_marks,
        results=results,
        parent_note=note,
    )


def _parse_student_answers(text: str) -> dict[int, str]:
    """Parse MiniCPM's extracted answer text into {question_num: answer_text}."""
    answers: dict[int, str] = {}
    pattern = re.compile(r"Q(\d+)\s*:\s*(.+?)(?=\nQ\d+\s*:|\Z)", re.DOTALL)
    for m in pattern.finditer(text):
        answers[int(m.group(1))] = m.group(2).strip()
    return answers
