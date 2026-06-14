# TutorDesk AI — Hackathon Submission

**HuggingFace Build Small Hackathon 2026**

| | |
|---|---|
| **Space** | [build-small-hackathon/tutordesk-ai](https://huggingface.co/spaces/build-small-hackathon/tutordesk-ai) |
| **GitHub** | [Naazimsnh02/tutordesk_ai](https://github.com/Naazimsnh02/tutordesk_ai) |
| **Demo Video** | ✅ [youtu.be/HBBLSwXUeaM](https://youtu.be/HBBLSwXUeaM) |
| **Blog / Field Notes** | ✅ [`docs/field_notes.md`](docs/field_notes.md) |
| **Social Post** | ✅ [x.com/naazimhussain02](https://x.com/naazimhussain02/status/2066153448501072212) |
| **Track** | Track 1: Backyard AI |
| **Total Parameters** | ~27B across all models (≤32B cap ✅) |

---

## Track: Backyard AI

**Problem**: India's 10+ million private tuition teachers each spend 1–2 hours every day manually writing worksheets, quizzes, homework, and answer keys — for every class, every subject. There is no tool built for them.

**Solution**: Photograph a textbook chapter → receive a full teaching pack (worksheet, homework, quiz, answer key, illustrated PDF) in the student's regional language in under 2 minutes. Photo Auto-Grading closes the loop: upload an answer sheet → Indian-style step-mark grading with partial credit.

**Real user**: CBSE/NCERT tuition teachers in Classes 6–10, teaching Math and Science. Objective questions make grading demonstrable.

**Model constraint fit**: Entire pipeline runs from a laptop — all models are open-weight (≤8B each), self-hosted on Modal as scale-to-zero GPU functions. HF Space is a thin Gradio client. Full offline mode via llama.cpp requires no internet or GPU at inference time.

---

## Merit Badges

### ✅ Well-Tuned

Fine-tuned Qwen3-4B published on HF Hub:

| Model | Repo | Task |
|---|---|---|
| Qwen3-4B (LoRA SFT) | [`naazimsnh02/tutordesk-qwen3-4b`](https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b) | Worksheet generation · difficulty classification · Indian step-mark grading |

Training data (~4,600 ChatML examples) synthesised from **ParthKadam2003/NCERT_Dataset** (MIT):
- `data/prep_generation.py` — 3k generation examples
- `data/prep_difficulty.py` — 1k difficulty labels
- `data/prep_grading.py` — 600 grading triples (answer + marking scheme → step marks)

Trained for 3 epochs on Modal A10G via `finetune/train_modal.py`.

### ✅ Off the Grid

Zero cloud API calls. Set `TUTORDESK_OFFLINE=1` and `QWEN_GGUF_PATH=/path/to/model.gguf` — the app runs entirely on-device:
- Qwen3-4B via `llama-cpp-python` (GGUF Q4_K_M)
- MiniCPM-V 4.5 via `transformers` (local weights)
- Aya degrades to English pass-through; FLUX returns `None` → text-only PDF

Student answer sheets and textbook photos never leave the device. Suitable for Tier 2/3 city deployment where internet is patchy.

### ✅ Llama Champion

Qwen3-4B is served via `llama-cpp-python` using a GGUF Q4_K_M quantised model in offline mode (`models/qwen.py → _local_llm()`). Used for all text generation and grading agents when `TUTORDESK_OFFLINE=1`.

### ✅ Off-Brand

Custom Gradio theme — not default Gradio. Implemented in `frontend/theme.py`:
- Saffron (#FF9933) / India-green (#138808) palette
- Plus Jakarta Sans font
- Pill radio buttons, card-style content panels, gradient header with badge chips
- Colour-accented PDF download buttons, per-tab info banners, custom dividers
- `elem_id` and `elem_classes` on every component for CSS targeting

### ✅ Sharing is Caring

Two trace types published to HF Hub at [`naazimsnh02/tutordesk-agent-traces`](https://huggingface.co/datasets/naazimsnh02/tutordesk-agent-traces):

| Folder | Contents | Viewer |
|---|---|---|
| `build_sessions/` | 7 raw Claude Code (Sonnet 4.6) JSONL sessions — full build from blank repo to Phase 6 | Native HF Data Studio agent trace viewer |
| `runtime_traces/` | Per-agent records from live app runs (curriculum, question_gen, difficulty, answer, report, grader) | HF Data Studio table view |

Sessions cover repo scaffolding, Modal serving, 5-agent pipeline, Qwen3-4B fine-tuning, MiniCPM-V integration, FLUX diagrams, Tiny Aya, Off-Brand theme, and offline mode. Secrets and local paths are redacted.

Upload scripts: `data/redact_sessions.py` (redact first) → `data/export_traces.py --all`

### ✅ Field Notes

Blog post written (`field_notes.md`): *"How I built an AI teaching assistant for India's 10 million tuition teachers"*

Covers: the 90-min prep problem, the 5-agent pipeline design, Qwen3-4B fine-tuning on NCERT data, MiniCPM-V for answer-sheet OCR, the Modal self-hosting architecture, the hardest bug, and what "Indian-style grading" actually means.

✅ **Submitted to HF Field Notes**

---

## Prize Categories Targeted

### Special Awards

**Tiny Titan (≤4B)** — Fine-tuned Qwen3-4B is the core text + grading engine at **4B parameters exactly**. It handles worksheet generation, difficulty classification, and Indian step-mark grading as a single fine-tuned model. Within the ≤4B Tiny Titan threshold on its own.

| Component | Parameters |
|---|---|
| Fine-tuned Qwen3-4B | 4B |

*Note: Tiny Aya (3.35B) and MiniCPM-V 4.5 (8B) are also in the stack; total is ~27B. The Tiny Titan claim rests on Qwen3-4B as the central engine.*

**Best Agent** — Fully modular 5-agent pipeline with a single responsibility per agent, defined input/output contracts, and trace logging on every run:

```
Curriculum Agent     → learning objectives + difficulty spine
Question-Gen Agent   → worksheet / homework / quiz questions
Difficulty Agent     → Bloom's taxonomy classification per question
Answer Agent         → worked solutions + step marks
Report Agent         → full teaching pack assembly + PDF
Grader Agent         → answer-sheet photo → step-mark score + feedback
```

**Off-Brand** — Custom Gradio theme with India-themed palette, pill radio buttons, gradient header, and colour-coded output sections. Distinctly different from the default Gradio look.

**Best Demo** — End-to-end demo covering: textbook photo upload → OCR → 5-agent pack generation → regional language translation → illustrated PDF with FLUX diagrams → answer sheet photo → step-mark grading → PDF grade report.

**Bonus Quest Champion** — All 6 merit badges claimed on a single submission:

| # | Badge | Evidence |
|---|---|---|
| 1 | Well-Tuned | `naazimsnh02/tutordesk-qwen3-4b` — LoRA SFT on NCERT data, 3 epochs, A10G |
| 2 | Off the Grid | `TUTORDESK_OFFLINE=1` + `QWEN_GGUF_PATH` → llama.cpp, no internet needed |
| 3 | Llama Champion | `models/qwen.py _local_llm()` — Qwen3-4B GGUF Q4_K_M via llama-cpp-python |
| 4 | Off-Brand | `frontend/theme.py` — saffron/green palette, custom CSS, pill radios, gradient header |
| 5 | Sharing is Caring | `naazimsnh02/tutordesk-agent-traces` — per-agent JSONL traces from all pipelines |
| 6 | Field Notes | `docs/field_notes.md` — submitted to HF Field Notes |

**Community Choice** — TutorDesk AI is built around a problem that 10+ million Indian teachers face every single day. It is demonstrable to anyone who has ever received a worksheet or taken a class test. The live Space requires no setup, no account, and produces a tangible output (a printable PDF) in under 2 minutes.

---

### Sponsor Awards

**OpenBMB ($10,000 pool)**

MiniCPM-V 4.5 (`openbmb/MiniCPM-V-4.5`) is used in two features:
- **Feature 1** — Textbook photo/PDF → structured chapter text extraction
- **Feature 5** — Answer sheet photo → structured student answer extraction (feeds grader)

Served as a scale-to-zero Modal GPU function (`serving/modal_app.py::MiniCPM`).  
Local fallback: MiniCPM-V 4.6 (1.3B) via llama.cpp when offline.

**Modal ($20,000 in credits)**

All model training and all cloud inference runs on Modal:
- `finetune/train_modal.py` — Qwen3-4B LoRA SFT (A10G)
- `data/prep_grading.py` — Qwen starmap synthesis (A10G)
- `serving/modal_app.py::Qwen` — Qwen3-4B text generation inference (A10G, scale-to-zero)
- `serving/modal_app.py::MiniCPM` — MiniCPM-V 4.5 vision inference (A10G, scale-to-zero)
- `serving/modal_app.py::TinyAya` — Tiny Aya translation inference (L4, scale-to-zero)
- `serving/modal_app.py::Flux` — FLUX.1-schnell diagram generation (A100, scale-to-zero)

**Cohere (Aya / CohereLabs)**

Tiny Aya (`CohereLabs/tiny-aya-fire`, 3.35B) is self-hosted on Modal as a scale-to-zero function and used in Feature 3 (Regional Language output). South-Asian language support (Hindi, Tamil) built in. English pass-through when offline.

**Black Forest Labs (FLUX)**

FLUX.1-schnell (Apache-2.0) is self-hosted on Modal (A100, bfloat16, 4-step inference) and used in Feature 4 (Illustrated Worksheets). Qwen3-4B extracts ≤3 diagram prompts from the chapter; FLUX renders each → embedded in the PDF. Graceful text-only fallback when FLUX is unavailable.

---

## Five-Agent Pipeline Summary

```
Feature 1  Worksheet-from-Textbook   MiniCPM-V 4.5 (OpenBMB)          →  Chapter text + concepts
Feature 2  Weekly Teaching Pack      Fine-tuned Qwen3-4B (5 agents)    →  Worksheet + homework + quiz + key
Feature 3  Regional Language         Tiny Aya (CohereLabs, 3.35B)      →  Hindi / Tamil pack
Feature 4  Illustrated Worksheets    FLUX.1-schnell (BFL) + Qwen3-4B   →  Diagram-illustrated PDF
Feature 5  Photo Auto-Grading        MiniCPM-V 4.5 + Qwen3-4B         →  Step-mark grade report
```

---

## Constraints Met

| Constraint | Status |
|---|---|
| Models ≤ 32B parameters (per-model) | ✅ largest is MiniCPM-V 4.5 at 8B |
| Total ≤ 32B (Backyard AI spirit) | ✅ ~27B total across all 4 models |
| Gradio UI | ✅ Custom Gradio 6, theme in `frontend/theme.py` |
| Hosted as HF Space | ✅ [build-small-hackathon/tutordesk-ai](https://huggingface.co/spaces/build-small-hackathon/tutordesk-ai) |
| Demo video | ✅ [youtu.be/HBBLSwXUeaM](https://youtu.be/HBBLSwXUeaM) |
| Social media post | ✅ [x.com/naazimhussain02](https://x.com/naazimhussain02/status/2066153448501072212) |
| Submission before June 15, 2026 | ✅ Submitted June 14, 2026 |

---

## What Is Complete vs. Pending

### ✅ Complete (Phases 0–6)

- All 5 features built and wired end-to-end (`app.py`)
- Fine-tuned Qwen3-4B trained on Modal, published at `naazimsnh02/tutordesk-qwen3-4b`
- All 4 Modal scale-to-zero GPU functions deployed (`serving/modal_app.py`)
- Custom Gradio theme (`frontend/theme.py`) — Off-Brand badge
- Offline mode (`TUTORDESK_OFFLINE=1` + GGUF) — Off the Grid + Llama Champion
- Agent trace logger + export script (`traces/logger.py`, `data/export_traces.py`)
- Print-ready A4 PDF export for all outputs (`utils/pdf.py`)
- Multilingual UI labels (`utils/i18n.py`) — English / Hindi / Tamil
- Field Notes blog post (`field_notes.md`)
- Model card for `naazimsnh02/tutordesk-qwen3-4b`

### ✅ Phase 7 — Complete (submitted June 14, 2026)

1. ✅ **HF Space deployed** — [build-small-hackathon/tutordesk-ai](https://huggingface.co/spaces/build-small-hackathon/tutordesk-ai)
2. ✅ **Agent traces uploaded** — `naazimsnh02/tutordesk-agent-traces`
3. ✅ **Demo video recorded & published** — [youtu.be/HBBLSwXUeaM](https://youtu.be/HBBLSwXUeaM)
4. ✅ **Field Notes written** — `docs/field_notes.md`
5. ✅ **Social post live** — [x.com/naazimhussain02](https://x.com/naazimhussain02/status/2066153448501072212)
6. ✅ **Hackathon form submitted** before June 15 deadline

---

## Links

| Resource | URL |
|---|---|
| HF Space | https://huggingface.co/spaces/build-small-hackathon/tutordesk-ai |
| GitHub | https://github.com/Naazimsnh02/tutordesk_ai |
| Demo Video | https://youtu.be/HBBLSwXUeaM |
| X / Social Post | https://x.com/naazimhussain02/status/2066153448501072212 |
| Fine-tuned model | https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b |
| Agent traces dataset | https://huggingface.co/datasets/naazimsnh02/tutordesk-agent-traces |
