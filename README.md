---
sdk: gradio
sdk_version: 6.16.0
app_file: app.py
title: TutorDesk AI
short_description: AI teaching-pack generator for Indian tuition teachers
license: mit
tags:
  - education
  - teaching
  - gradio
  - llm
  - multimodal
  - indian-education
  - cbse
  - ncert
  - fine-tuned
  - qwen3
  - minicpm
  - aya
  - flux
  - local-first
  - backyard-ai
  - modal.com
  - multilingual
  - open-trace
  - custom-ui
  - llama.cpp
---

<div align="center">

# TutorDesk AI

### AI Teaching-Pack Generator for Indian Tuition Teachers

*90 minutes of daily prep → under 10 minutes*

[![Hugging Face Space](https://img.shields.io/badge/🤗%20Space-Live%20Demo-blue)](https://huggingface.co/spaces/build-small-hackathon/tutordesk-ai)
[![Watch Demo](https://img.shields.io/badge/▶%20Watch-Demo%20Video-red)](https://youtu.be/HBBLSwXUeaM)
[![Blog Post](https://img.shields.io/badge/📝%20Blog-Field%20Notes-orange)](https://huggingface.co/blog/build-small-hackathon/tutordesk-ai)
[![X Post](https://img.shields.io/badge/𝕏-View%20Post-black)](https://x.com/naazimhussain02/status/2066153448501072212)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Training: Modal](https://img.shields.io/badge/Training-Modal%20A10G-orange)](https://modal.com)
[![Vision: OpenBMB](https://img.shields.io/badge/Vision-OpenBMB%20MiniCPM-purple)](https://huggingface.co/openbmb)
[![Multilingual: Cohere](https://img.shields.io/badge/Multilingual-Cohere%20Aya-teal)](https://huggingface.co/CohereLabs)
[![Diagrams: BFL](https://img.shields.io/badge/Diagrams-FLUX.1--schnell-black)](https://huggingface.co/black-forest-labs)
[![Hackathon: Build Small 2026](https://img.shields.io/badge/Hackathon-HF%20Build%20Small%202026-yellow)](https://huggingface.co/build-small-hackathon)

</div>

---

## What It Does

India has 10+ million private tuition teachers. Each spends 1–2 hours every day manually writing worksheets, quizzes, homework, and answer keys — by hand, for each class, each subject. There is no tool built for them.

**TutorDesk AI takes a textbook chapter photo and produces a full teaching pack in under 2 minutes:**

| Output | What it is |
|---|---|
| Worksheet | 10 structured questions, tiered by difficulty |
| Homework set | 5 take-home problems with hints |
| Class test | 5-question quiz ready to print |
| Answer key | Full worked answers with step marks |
| Illustrated PDF | Diagrams and figures generated alongside questions |
| Hindi / Tamil output | Entire pack translated via Tiny Aya |

**Photo Auto-Grading** closes the loop: upload a student's answer sheet photo → get Indian-style step-mark grading (partial credit, method marks) with a PDF grade report.

---

## Demo

```
Upload a textbook chapter photo (Classes 6–10 · Math / Science · CBSE)
        ↓
Agent 1 — MiniCPM-V 4.5 extracts chapter text + key concepts from the photo
Agent 2 — Curriculum agent identifies learning objectives + difficulty spine
Agent 3 — Question-gen agent produces worksheet, homework, and quiz questions
Agent 4 — Answer agent writes worked solutions + step marks
Agent 5 — Report agent assembles the full teaching pack (Markdown + PDF)
        ↓
PACK READY — worksheet · homework · quiz · key · illustrated PDF — in ~90 sec
```

---

## Five-Feature Pipeline

```
┌──────────────────────────────────────┐
│  Feature 1 — Worksheet-from-Textbook │  MiniCPM-V 4.5 (8B)
│  Chapter photo/PDF → teaching pack   │  OCR + concept extraction
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Feature 2 — Weekly Teaching Pack    │  Fine-tuned Qwen3-4B
│  One click → full 5-agent pack       │  curriculum · q-gen · answer · report
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Feature 3 — Regional Language       │  Tiny Aya (CohereLabs, 3.35B)
│  Entire pack → Hindi / Tamil         │  South-Asian-tuned translation
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Feature 4 — Illustrated Worksheets  │  FLUX.1-schnell (BFL, Apache-2.0)
│  Auto-generated diagrams + figures   │  Qwen extracts prompts → FLUX renders
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Feature 5 — Photo Auto-Grading      │  MiniCPM-V 4.5 + fine-tuned Qwen3-4B
│  Answer sheet photo → grade report   │  Indian step-marks · partial credit
└──────────────────────────────────────┘
```

All agent runs are traced to `traces/raw/agent_traces.jsonl` for the **Sharing is Caring** dataset.

---

## Fine-Tuned Model

### Qwen3-4B (TutorDesk Grading + Generation)

| | |
|---|---|
| **Repo** | [`naazimsnh02/tutordesk-qwen3-4b`](https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b) |
| **Base** | Qwen/Qwen3-4B |
| **Method** | LoRA SFT (PEFT), trained on Modal A10G |
| **Data** | ~4,600 examples — 3k NCERT generation, 1k difficulty labels, 600 grading triples |
| **Training** | 3 epochs on Modal A10G · pushed to HF Hub |
| **Tasks** | Worksheet generation · difficulty classification · Indian-style step-mark grading |
| **Inference** | `transformers` (Modal) or GGUF via `llama-cpp-python` (offline) |

### Training Data (NCERT → ChatML)

| Script | Output | Examples |
|---|---|---|
| `data/prep_generation.py` | Generation pairs (chapter → questions) | ~3,000 |
| `data/prep_difficulty.py` | Difficulty classification labels | ~1,000 |
| `data/prep_grading.py` | Grading triples (answer + scheme → marks) | ~600 |

Base data: **ParthKadam2003/NCERT_Dataset** (124k rows, MIT licence).

---

## Running Locally

```bash
git clone https://github.com/Naazimsnh02/tutordesk_ai
cd tutordesk-ai
pip install -r requirements.txt
cp .env.example .env   # fill in MODAL_TOKEN_ID, HF_TOKEN
python app.py
```

**Offline / Off-the-Grid mode** (no Modal, no cloud):

```bash
TUTORDESK_OFFLINE=1 \
QWEN_GGUF_PATH=/path/to/tutordesk-qwen3-4b.Q4_K_M.gguf \
python app.py
```

Aya and FLUX degrade gracefully — English-only, text-only worksheets when offline.

### Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` | Cloud mode | Modal GPU inference |
| `HF_TOKEN` | Optional | Faster HF Hub downloads |
| `QWEN_FINETUNED_MODEL` | Optional | Override default Qwen model on Modal |
| `QWEN_GGUF_PATH` | Offline mode | Local GGUF file for llama.cpp |
| `TUTORDESK_OFFLINE` | Offline mode | `1` = skip Modal, use local llama.cpp |

---

## Re-Training

```bash
export HF_TOKEN=<your-token>

modal run data/prep_generation.py   # ~10 min — NCERT → ChatML generation data
modal run data/prep_difficulty.py   # ~5 min  — difficulty labels
modal run data/prep_grading.py      # ~10 min — grading triples via Qwen starmap
modal run finetune/train_modal.py   # ~1–2 hr — LoRA SFT on A10G, pushes to HF Hub
```

---

## Model Architecture

| Component | Model | Parameters | Runtime |
|---|---|---|---|
| Vision (textbook + answer sheets) | MiniCPM-V 4.5 | 8B | transformers (Modal A10G) |
| Text gen + grading | Fine-tuned Qwen3-4B | 4B | transformers (Modal) / llama.cpp (offline) |
| Multilingual translation | Tiny Aya (`CohereLabs/tiny-aya-fire`) | 3.35B | transformers (Modal L4) |
| Diagram generation | FLUX.1-schnell | ~12B | diffusers (Modal A100) |
| **Total** | — | **~27B** | — |

All models are open-weight and self-hosted on Modal — zero external API calls.
Total stack ≈ **27B parameters** — comfortably under the **32B cap**.

---

## Hackathon Badges

| Badge | How |
|---|---|
| Well-Tuned | Fine-tuned Qwen3-4B at `naazimsnh02/tutordesk-qwen3-4b` — trained on NCERT data for worksheet generation + Indian-style grading |
| Off the Grid | `TUTORDESK_OFFLINE=1` + `QWEN_GGUF_PATH` → full local llama.cpp inference (Aya/FLUX degrade gracefully) |
| Llama Champion | Qwen3-4B served via `llama-cpp-python` (GGUF Q4_K_M) in offline mode |
| Off-Brand | Custom Gradio theme — saffron/green palette, Plus Jakarta Sans, branded CSS (`frontend/theme.py`) |
| Sharing is Caring | Agent traces → `naazimsnh02/tutordesk-agent-traces` HF dataset (`data/export_traces.py`) |
| Field Notes | *"How I built an AI teaching assistant for India's 10 million tuition teachers"* |

---

## Sharing is Caring — Trace Dataset

Two trace types published to [`naazimsnh02/tutordesk-agent-traces`](https://huggingface.co/datasets/naazimsnh02/tutordesk-agent-traces):

| Folder | Contents | Viewer |
|---|---|---|
| `build_sessions/` | 7 Claude Code (Sonnet 4.6) JSONL build sessions — full project from blank repo to submission | Native HF Data Studio agent trace viewer |
| `runtime_traces/` | Per-agent records from live app runs — curriculum, question_gen, difficulty, answer, report, grader | HF Data Studio table view |

Per [HF agent traces docs](https://huggingface.co/docs/hub/en/agent-traces), Claude Code JSONL is natively rendered in Data Studio without conversion.

```bash
# Step 1 — redact secrets and local paths from Claude Code sessions
python data/redact_sessions.py

# Step 2 — push everything to HF Hub
python data/export_traces.py --all
```

---

## Project Structure

```
tutordesk_ai/
├── app.py                          # Gradio entry point (HF Space)
├── config.py                       # CONFIG dataclass
├── frontend/
│   └── theme.py                    # Custom Gradio theme — saffron/green, branded CSS
├── serving/
│   └── modal_app.py                # All models as scale-to-zero Modal GPU functions
├── agents/
│   ├── curriculum.py               # Learning objective extraction
│   ├── question_gen.py             # Question generation (worksheet / homework / quiz)
│   ├── difficulty.py               # Bloom's taxonomy difficulty classification
│   ├── answer.py                   # Worked answer generation (step marks)
│   ├── report.py                   # Teaching pack assembly
│   └── grader.py                   # Indian-style step-mark grading
├── models/
│   ├── qwen.py                     # Qwen3-4B client (Modal + offline llama.cpp)
│   ├── minicpm.py                  # MiniCPM-V 4.5 client (Modal)
│   ├── aya.py                      # Tiny Aya client (Modal + English pass-through)
│   └── flux.py                     # FLUX.1-schnell client (Modal + None fallback)
├── pipelines/
│   ├── weekly_pack.py              # 5-agent orchestration → WeeklyPack + PDF
│   ├── worksheet_from_textbook.py  # Photo/PDF → MiniCPM → weekly_pack
│   ├── auto_grade.py               # Multi-question grading → GradeResult + PDF
│   └── illustrated_worksheet.py   # Qwen prompts → FLUX diagrams → PDF
├── data/
│   ├── prep_generation.py          # NCERT → ChatML generation examples
│   ├── prep_difficulty.py          # Difficulty classification examples
│   ├── prep_grading.py             # Grading triples synthesis
│   └── export_traces.py            # Upload agent traces → HF Hub
├── finetune/
│   ├── train_modal.py              # LoRA SFT on Modal A10G → HF Hub
│   └── lora_config.py              # LoRA hyperparameters
├── utils/
│   ├── pdf.py                      # Print-ready A4 PDF (reportlab)
│   ├── image.py                    # PDF rasterization (PyMuPDF)
│   └── i18n.py                     # UI labels (English / Hindi / Tamil)
└── traces/
    └── logger.py                   # AgentTraceLogger → JSONL
```

---

## Scope

**Classes 6–10 · Math + Science · CBSE/NCERT · English (+ Hindi slice)**

Objective Math/Science questions make grading demonstrable and verifiable. Humanities and earlier classes are intentionally deferred.

---

## Links

- **HF Space**: [build-small-hackathon/tutordesk-ai](https://huggingface.co/spaces/build-small-hackathon/tutordesk-ai)
- **Demo Video**: [youtu.be/HBBLSwXUeaM](https://youtu.be/HBBLSwXUeaM)
- **GitHub**: [Naazimsnh02/tutordesk_ai](https://github.com/Naazimsnh02/tutordesk_ai)
- **X Post**: [x.com/naazimhussain02](https://x.com/naazimhussain02/status/2066153448501072212)
- **Fine-tuned model**: [naazimsnh02/tutordesk-qwen3-4b](https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b)
- **Agent traces**: [naazimsnh02/tutordesk-agent-traces](https://huggingface.co/datasets/naazimsnh02/tutordesk-agent-traces)

---

## License

- **Code**: MIT
- **Qwen3-4B**: Apache 2.0 (Alibaba)
- **MiniCPM-V 4.5**: Apache 2.0 (OpenBMB)
- **Tiny Aya**: Apache 2.0 (CohereLabs)
- **FLUX.1-schnell**: Apache 2.0 (Black Forest Labs)

---

*HuggingFace Build Small Hackathon 2026 · Track 1: Backyard AI · [Naazimsnh02](https://github.com/Naazimsnh02/tutordesk_ai)*
