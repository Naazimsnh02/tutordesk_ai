"""Objective 3 — Indian-style grading training data (the part we build).

No off-the-shelf set. For each NCERT Q&A, synthesize:
  - a marking scheme (split answer into step-marks),
  - 3-4 simulated student answers (correct / partial / right-answer-no-working / wrong-method),
  - marks + per-step rationale for each.
Use a strong teacher-LLM to synthesize; GSM8K-reasoning style step decomposition as template.
~1-2k rows.
"""
from __future__ import annotations

OUT = "data/processed/grading.jsonl"


def build() -> None:
    """TODO Phase 3:
    For each sampled Q&A:
      1. ask teacher-LLM for a step-mark marking scheme
      2. generate simulated student answers across quality levels
      3. label each with marks + breakdown
    Emit ChatML:
        user:   "Grade out of {marks}. Question: {Q}. Marking scheme: {steps}. Student answer: {A}."
        assistant: "Marks: {x}/{marks}\nBreakdown: ...\nFeedback: ..."
    """
    raise NotImplementedError("Phase 3: implement grading data synthesis")


if __name__ == "__main__":
    build()
