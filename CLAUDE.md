# CLAUDE.md — TutorDesk AI

Guidance for Claude Code (and humans) working in this repo.

## What this is

**TutorDesk AI** — an on-laptop AI copilot for Indian tuition teachers. Submission for the
**Hugging Face × Gradio "Build Small Hackathon"** (June 5–15, 2026), **Backyard AI** track.

A teacher photographs a textbook chapter → gets a full teaching pack (worksheet, homework,
test, answer key) in their regional language, with diagrams, plus photo-based auto-grading.
Goal: ~90 min/day of prep → under 10.

Read `PRD.md` for the full product spec and the sponsor/award strategy. Read
`implementation_plan.md` for the build plan and `progress.md` for current status — **update
`progress.md` as work completes.**

## Hard constraints (hackathon rules — do not violate)

- **≤ 32B total params** across all local models; must **run on a laptop**.
- App is a **Gradio app deployed as a Hugging Face Space**.
- Submission needs a **demo video** + **social post** + (for badges) a **blog/Field Notes**.
- Deadline: **June 15, 2026**.

## The 5 features (each claims a sponsor/award — see PRD)

1. **Worksheet-from-Textbook** — MiniCPM-V reads a chapter photo/PDF → worksheet+quiz+key.
2. **Weekly Teaching Pack** — one click, 5-agent pipeline → full pack.
3. **Regional-language output** — Cohere Aya/Tiny Aya (Hindi, Tamil, …).
4. **Illustrated/diagram worksheets** — FLUX generates diagrams/figures.
5. **Photo Auto-Grading** — MiniCPM-V reads answer sheet → fine-tuned Qwen3-4B grades it
   Indian-style (step marks, partial credit).

## Hosting architecture

Dev laptop can't hold the models, so **all models are self-hosted on Modal** as scale-to-zero
GPU functions (`serving/modal_app.py`). The **HF Space runs only the Gradio UI** and calls
those functions by name; `models/*.py` are thin clients. **No external APIs** — this
maximizes Modal usage, keeps Off-the-Grid reachable, and self-hosts the open-weight Cohere/BFL
models (still claims both sponsors). "Runs on a laptop" = model *size* discipline (≤32B), not
your dev hardware.

## Model stack (all open-weight, self-hosted on Modal)

| Role | Model | Notes |
|---|---|---|
| Vision | **MiniCPM-V 4.5 (8B)** | Textbook + answer-sheet reading. 4.6 (1.3B) = lightweight/offline fallback. |
| Text gen + grading | **Fine-tuned Qwen3-4B** | LoRA SFT, trained on **Modal**. ≤4B → Tiny Titan. |
| Multilingual | **Tiny Aya (`CohereLabs/tiny-aya-fire`, 3.35B)** | South-Asian-tuned → Cohere claim. |
| Images | **FLUX.1-schnell** (Black Forest Labs, Apache-2.0) | Diagrams/illustrations. |

Total ≈ **27B** (8 + 4 + 12 + 3.35) — under the 32B cap.

**Local/Off-Grid mode:** MiniCPM-V + fine-tuned Qwen3-4B via **llama.cpp**, no Modal/cloud
(Aya/FLUX degrade gracefully — English-only, text-only worksheets when offline).

**To verify on the hackathon Discord:** (1) does the Cohere award accept self-hosted Aya or
require the Cohere API? (2) is the 32B cap per-model or total? If Cohere needs the API, swap
only `models/aya.py`'s backend to a Cohere API call — interface is unchanged.

## Scope for the hackathon (narrow on purpose)

**Classes 6–10 · Math + Science · CBSE/NCERT · English (+ small Hindi slice).**
Do not broaden to humanities or all classes — objective Math/Science answers make grading
demonstrable. Deferred features live in PRD "Roadmap" — keep them out of the demo build.

## Tech stack & conventions

- **Python 3.11+**, **Gradio** UI with a **custom `gr.Server` frontend** (claims Off-Brand).
- **transformers / PEFT (LoRA)** for fine-tuning; **Modal** for the training job.
- **llama.cpp** (GGUF) for local inference.
- Keep secrets in a `.env` (never commit). Cohere/FLUX/HF tokens via env vars.
- Outputs must be **print-ready** (PDF). Mobile-first, simple, one-tap flows.
- Prefer small, composable modules per agent (see `agents/`). Each agent = one clear job.

## Proposed project structure

```
tutordesk_ai/
  app.py                  # Gradio entry point (HF Space) — thin client
  frontend/               # custom gr.Server frontend (Off-Brand)
  serving/modal_app.py    # all models as scale-to-zero Modal GPU functions
  agents/                 # curriculum, question_gen, difficulty, answer, report, grader
  models/                 # thin clients calling Modal (or local in offline mode)
  pipelines/              # weekly_pack, worksheet_from_textbook, auto_grade
  data/                   # dataset prep scripts (NCERT → ChatML JSONL)
  finetune/               # Modal training scripts, LoRA config
  traces/                 # captured agent traces → HF dataset (Sharing is Caring)
  utils/                  # pdf export, i18n, image helpers
  PRD.md  implementation_plan.md  progress.md  CLAUDE.md
```

## Datasets

- Base: **ParthKadam2003/NCERT_Dataset** (124k rows, MIT) — generation + difficulty labels.
- Grading: synthesize marking-scheme + simulated-student-answer triples (no off-the-shelf
  set); use GSM8K-reasoning style step decomposition. ~6–8k total examples.
- Verify the KadamParth collection for per-subject siblings before committing.

## Working agreements

- When you finish a task, tick it in `progress.md` and note any deviation from the plan.
- Don't add a feature that isn't in the 5 + badge plan without flagging scope risk.
- Stage demos with **neat/printed** answer sheets (handwriting OCR is a known weak spot).
