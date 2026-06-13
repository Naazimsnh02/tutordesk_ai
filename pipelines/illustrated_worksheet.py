"""Feature 4 — Illustrated Worksheets (FLUX.1-schnell, Black Forest Labs claim).

Builds a weekly teaching pack and enriches it with labeled scientific diagrams generated
by FLUX.1-schnell, embedded in the final PDF.

Diagram generation is skipped gracefully when offline or if FLUX returns None,
producing a standard text-only PDF as fallback.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image

from agents.base import Agent
from models.flux import generate_diagram
from pipelines.weekly_pack import TeachingPack, build_pack
from utils.pdf import to_pdf

_DIAGRAM_SYSTEM = (
    "You identify at most 3 concepts in a worksheet that would be clearest with a labeled diagram. "
    "Return ONLY the diagram prompts, one per line, nothing else. "
    "Each prompt must be a concrete, detailed description for an image generator — e.g. "
    "'clear labeled cross-section diagram of a plant cell showing nucleus, chloroplast, "
    "vacuole, and cell wall on a white background'. "
    "Prioritise diagrams that are standard in CBSE Class 6–10 Science textbooks."
)

_diagram_agent = Agent(name="diagram_planner", system_prompt=_DIAGRAM_SYSTEM)

_FLUX_STYLE_PREFIX = (
    "Clear, clean educational diagram, white background, bold labels, "
    "suitable for a Class 8 CBSE Science textbook: "
)


@dataclass
class IllustratedPack:
    pack: TeachingPack
    diagrams: list[Image.Image] = field(default_factory=list)
    diagram_prompts: list[str] = field(default_factory=list)
    pdf_path: str = ""

    @property
    def diagram_count(self) -> int:
        return len(self.diagrams)


def build_illustrated_pack(
    chapter_text: str,
    *,
    grade: int,
    subject: str,
    question_count: int = 20,
    diff: str = "Medium",
    language: str = "English",
) -> IllustratedPack:
    """Run the weekly-pack pipeline then add FLUX diagrams.

    Falls back to a plain text PDF if FLUX is unavailable (offline or error).
    """
    pack = build_pack(
        chapter_text,
        grade=grade,
        subject=subject,
        question_count=question_count,
        diff=diff,
        language=language,
    )

    # Identify concepts that benefit from diagrams
    raw_prompts = _diagram_agent.run(pack.worksheet)
    prompts = [p.strip() for p in raw_prompts.splitlines() if p.strip()][:3]

    # Generate diagrams — None results are dropped
    diagrams: list[Image.Image] = []
    used_prompts: list[str] = []
    for prompt in prompts:
        img = generate_diagram(_FLUX_STYLE_PREFIX + prompt)
        if img is not None:
            diagrams.append(img)
            used_prompts.append(prompt)

    body = (
        f"## Worksheet\n{pack.worksheet}\n\n"
        f"## Homework\n{pack.homework}\n\n"
        f"## Quiz\n{pack.quiz}\n\n"
        f"## Answer Key\n{pack.answer_key}\n\n"
        f"## Parent Note\n{pack.parent_note}"
    )
    pdf_path = to_pdf(
        f"Illustrated Teaching Pack — Class {grade} {subject}",
        f"Chapter: {chapter_text[:60]}",
        body,
        images=diagrams or None,
    )

    return IllustratedPack(
        pack=pack,
        diagrams=diagrams,
        diagram_prompts=used_prompts,
        pdf_path=pdf_path,
    )
