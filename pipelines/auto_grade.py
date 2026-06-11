"""Feature 5 — Photo Auto-Grading (OpenBMB + Well-Tuned + Best Agent).

Two stages (text model is vision-blind, so vision runs first):
  1. MiniCPM-V reads the answer sheet -> student's answers as structured text.
  2. Fine-tuned Qwen3-4B grades each answer vs. the marking scheme, Indian-style.
Then a parent note is auto-drafted from the result.
"""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from agents import grader, report
from models.minicpm import read_image

_READ = "Read this student's answer sheet. List each question number and the student's answer."


@dataclass
class GradeResult:
    total: str
    breakdown: str
    parent_note: str


def grade_sheet(
    image: Image.Image,
    *,
    question: str,
    marking_scheme: str,
    marks: int,
    student: str = "Student",
) -> GradeResult:
    """TODO Phase 4: parse multi-question sheets; loop grader per question."""
    student_answer = read_image(image, _READ)
    breakdown = grader.grade(question, marking_scheme, student_answer, marks=marks)
    note = report.parent_note(student, breakdown)
    return GradeResult(total="TODO", breakdown=breakdown, parent_note=note)
