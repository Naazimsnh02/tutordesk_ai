# TutorDesk AI — Implementation Plan

Build plan for the Build Small Hackathon (deadline **June 15, 2026**). Track progress in
`progress.md`; product rationale in `PRD.md`.

## Guiding principles

- **Demo-first:** every phase should move the end-to-end demo forward.
- **Reuse over build:** NCERT_Dataset + pretrained models do most of the work.
- **Narrow scope:** Classes 6–10, Math + Science, CBSE/NCERT, English (+ Hindi slice).
- **Badges are cheap multipliers** — bake them into the architecture, don't bolt on later.

---

## Architecture (decided 2026-06-11)

Laptop can't hold the models → **all models self-hosted on Modal** as scale-to-zero GPU
functions (`serving/modal_app.py`). The **HF Space = thin Gradio UI** calling Modal by name.
No external APIs. Models: MiniCPM-V 4.5 (8B), fine-tuned Qwen3-4B, **Tiny Aya
`CohereLabs/tiny-aya-fire` (3.35B)**, FLUX.1-schnell — total ≈27B.

## Phase 0 — Project setup

- Repo scaffolding per CLAUDE.md structure; `requirements.txt`; `.env.example`.
- HF account + empty **Space**; **Modal account + CLI auth** (`modal token set`).
- `serving/modal_app.py` skeleton: one scale-to-zero function per model.

**Exit:** `app.py` shows a "hello" Gradio app live on the Space; `modal deploy` succeeds.

---

## Phase 1 — Core text generation (no fine-tune yet)

Get the product working with the **base** Qwen3-4B so UI/pipelines aren't blocked on training.

- `serving/modal_app.py::Qwen` — load base Qwen3-4B on Modal; `models/qwen.py` calls it.
- `agents/` — implement the 5 agents (curriculum, question_gen, difficulty, answer, report)
  as prompt-driven functions over Qwen.
- `pipelines/weekly_pack.py` — orchestrate the 5 agents → worksheet+homework+quiz+key+note.
- `utils/pdf.py` — print-ready PDF export.

**Exit:** **Feature 2 (Weekly Teaching Pack)** works end-to-end from text inputs → PDF.

---

## Phase 2 — Vision (Feature 1)

- `serving/modal_app.py::MiniCPM` — load MiniCPM-V 4.5 on Modal (4.6 fallback flag).
- `pipelines/worksheet_from_textbook.py` — image/PDF → extracted topic/concepts → feed
  Phase 1 pipeline.
- `utils/image.py` — PDF page rasterization, basic preprocessing.

**Exit:** **Feature 1** works — photograph a chapter → worksheet+quiz+key.

---

## Phase 3 — Dataset + fine-tune on Modal (Well-Tuned / Tiny Titan / Modal)

- `data/prep_generation.py` — NCERT_Dataset → ChatML JSONL (objective ① generation).
- `data/prep_difficulty.py` — NCERT `Difficulty` column → ChatML (objective ② classify).
- `data/prep_grading.py` — synthesize marking-scheme + simulated-student-answer + marks
  triples (objective ③ grading); ~1–2k rows.
- `finetune/train_modal.py` — LoRA SFT of Qwen3-4B on Modal; merge + export GGUF.
- **Publish the fine-tuned model to the HF Hub** (claims Well-Tuned).

**Exit:** Fine-tuned Qwen3-4B published; swapped into the pipelines; ~6–8k training examples.

---

## Phase 4 — Photo Auto-Grading (Feature 5)

- `pipelines/auto_grade.py` — MiniCPM-V reads answer sheet → fine-tuned Qwen3-4B grades
  against marking scheme → marks + per-step breakdown + auto-drafted parent note.

**Exit:** **Feature 5** works on neat/printed answer sheets.

---

## Phase 5 — Multilingual (Cohere) + Diagrams (FLUX)

- `serving/modal_app.py::TinyAya` — host `CohereLabs/tiny-aya-fire`; language selector on
  every output (Feature 3).
- `serving/modal_app.py::Flux` — host FLUX.1-schnell; diagrams embedded in worksheet PDFs
  (Feature 4).
- Graceful fallback when offline (English-only / no images).

**Exit:** **Features 3 & 4** work; sponsor claims for Cohere + BFL satisfied.

---

## Phase 6 — Badge layer & polish

- **Off the Grid / Llama Champion:** local mode — MiniCPM-V + Qwen3-4B via llama.cpp, toggle
  to disable all cloud calls.
- **Sharing is Caring:** `traces/` — capture agent traces → publish HF dataset.
- **Off-Brand:** custom `gr.Server` frontend, mobile-first polish.
- **Field Notes:** build/report blog post.

**Exit:** all badges claimable; app polished.

---

## Phase 7 — Submission

- Record **demo video** (90-min → 10-min teacher story).
- **Social post.** Final Space deploy + README with sponsor/badge checklist.
- Submit before **June 15, 2026**.

---

## Sponsor / award coverage (target)

| Claim | Phase |
|---|---|
| OpenBMB ($10k) — MiniCPM-V | 2, 4 |
| Modal ($20k credits) — training job | 3 |
| Cohere ($5k) — Aya | 5 |
| Black Forest Labs ($3k) — FLUX | 5 |
| Best Agent ($1k) — 5-agent pipeline | 1 |
| Well-Tuned + Tiny Titan ($1.5k) — published 4B fine-tune | 3 |
| Sharing is Caring — agent traces dataset | 6 |
| Off the Grid + Llama Champion — local mode | 6 |
| Off-Brand ($1.5k) — gr.Server | 6 |
| Best Demo ($1k) + Field Notes | 6, 7 |

## Risks / watch-items

- **Handwriting OCR** unreliable → demo with printed answers; roadmap item.
- **Laptop memory** for 8B + 4B → use GGUF/quantized; lazy-load models.
- **NCERT subject coverage** may skew → verify collection, supplement if thin.
- **Time:** if behind, Phases 1–4 are the must-win core; 5–6 are sponsor add-ons.
