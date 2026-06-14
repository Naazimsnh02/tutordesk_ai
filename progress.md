# TutorDesk AI — Progress Tracker

Update this as work completes. Status: ⬜ not started · 🟨 in progress · ✅ done · ⛔ blocked

Last updated: 2026-06-14 (Phases 4 + 5 + 6 complete + UI redesign)

---

## Phase 0 — Project setup
- ✅ Repo scaffolding (folders per CLAUDE.md), `requirements.txt`, `.env.example` (stubs compile clean)
- ✅ Architecture decided: all models self-hosted on Modal; Space = thin Gradio client
- ✅ `serving/modal_app.py` skeleton (one scale-to-zero fn per model)
- ⬜ HF account + empty Space live
- ✅ Modal account + CLI auth (`modal token set`)
- ✅ `modal deploy serving/modal_app.py` succeeds
- ⬜ **Exit:** "hello" Gradio app live on the Space

## Phase 1 — Core text generation (base Qwen3-4B)
- ✅ `serving/modal_app.py::Qwen` — Qwen3-4B on Modal (A10G, scale-to-zero)
- ✅ `models/qwen.py` — Modal client (+ offline stub)
- ✅ `agents/` — curriculum, question_gen, difficulty, answer, report, grader (all wired)
- ✅ `pipelines/weekly_pack.py` — 5-agent orchestration + localization + PDF export
- ✅ `utils/pdf.py` — print-ready A4 PDF (reportlab)
- ✅ `app.py` — Weekly Teaching Pack tab wired; other features show "Coming soon"
- ✅ Deploy: `modal deploy serving/modal_app.py` and smoke-test the pack
- ✅ **Exit:** Feature 2 end-to-end live (Modal → Gradio → PDF download)

## Phase 2 — Vision (Feature 1)
- ✅ `models/minicpm.py` — MiniCPM-V 4.5 Modal client (+ offline guard)
- ✅ `pipelines/worksheet_from_textbook.py` — photo/PDF → MiniCPM extract → weekly_pack
- ✅ `utils/image.py` — PDF rasterization via PyMuPDF
- ✅ `serving/modal_app.py::MiniCPM` — load + read_image implemented (A10G, trust_remote_code)
- ✅ `app.py` — Worksheet-from-Textbook tab fully wired (photo + PDF upload)
- ✅ Deploy: `modal deploy serving/modal_app.py` and smoke-test with a textbook photo
- ✅ **Exit:** Feature 1 — chapter photo → worksheet+quiz+key

## Phase 3 — Dataset + fine-tune on Modal
- ✅ `data/prep_generation.py` — NCERT → ChatML (objective ①, ~3k examples)
- ✅ `data/prep_difficulty.py` — difficulty labels (objective ②, ~1k examples)
- ✅ `data/prep_grading.py` — grading triples via Qwen starmap (objective ③, ~600 examples)
- ✅ `finetune/train_modal.py` — LoRA SFT on Modal A10G, push to HF Hub
- ✅ `serving/modal_app.py` — reads QWEN_FINETUNED_MODEL env var to swap fine-tune in
- ✅ Run data prep: 3k generation + 1k difficulty + 600 grading examples
- ✅ Run training: `modal run finetune/train_modal.py` (A10G, 3 epochs, ~4.6k examples)
- ✅ Publish fine-tuned Qwen3-4B to HF Hub (**Well-Tuned**) → naazimsnh02/tutordesk-qwen3-4b
- ✅ Professional model card pushed to HF Hub
- ✅ Set QWEN_FINETUNED_MODEL=naazimsnh02/tutordesk-qwen3-4b in .env + redeploy Modal
- ✅ **Exit:** model live in serving pipeline

## Phase 4 — Photo Auto-Grading (Feature 5)
- ✅ `agents/grader.py` — structured MARKS: X/Y output contract, `extract_score()`, `parse_scheme()` (regex + Qwen fallback)
- ✅ `pipelines/auto_grade.py` — multi-question loop: MiniCPM-V extract → per-Q Qwen grading → `GradeResult` with summary, markdown table, PDF
- ✅ `app.py` — Photo Auto-Grading tab fully wired (photo upload, marking scheme textbox, student name, grade/subject selectors, PDF download)
- ✅ **Exit:** Feature 5 works on neat/printed sheets

## Phase 5 — Multilingual + Diagrams
- ✅ `serving/modal_app.py::TinyAya` — load + localize implemented (L4, CohereLabs/tiny-aya-fire)
- ✅ `serving/modal_app.py::Flux` — load + generate_diagram implemented (A100, FLUX.1-schnell, bfloat16, 4 steps)
- ✅ `models/aya.py` — Modal client wired; English pass-through + offline no-op
- ✅ `models/flux.py` — Modal client wired; None fallback on offline/error
- ✅ `pipelines/illustrated_worksheet.py` — Qwen extracts ≤3 diagram prompts → FLUX generates → embedded in PDF; graceful text-only fallback
- ✅ `utils/i18n.py` — UI label dictionary for English / Hindi / Tamil
- ✅ `app.py` — Regional Language tab (Tiny Aya translator) + Illustrated Worksheets tab (FLUX pack) fully wired
- ✅ Offline graceful fallback — Aya returns English; FLUX returns None → text-only PDF
- ✅ **Exit:** Features 3 & 4 — Cohere + BFL claims satisfied

## Phase 6 — Badge layer & polish
- ✅ Local mode via llama.cpp (**Off the Grid + Llama Champion**) — `models/qwen.py` `_local_llm()`, `QWEN_GGUF_PATH` + `GGUF_N_GPU_LAYERS` in config; `llama-cpp-python>=0.3` added to requirements; offline path calls `create_chat_completion` with chatml format
- ✅ `traces/` capture + publish HF dataset (**Sharing is Caring**) — `data/export_traces.py` reads `traces/raw/agent_traces.jsonl` and pushes to `naazimsnh02/tutordesk-agent-traces`
- ✅ Fully custom frontend (**Off-Brand**) — `app.py` now uses `gr.Server` (FastAPI) serving a hand-written single-page UI `static/index.html`; each of the 5 features posts to its own JSON/multipart endpoint, PDFs served via `/api/download/<token>`; `@app.api("health_check")` kept for gradio-client compat. Replaces the old `gr.Blocks` + `frontend/theme.py` approach (deleted). Pins `gradio==6.16.0`.
- ✅ Full UI redesign — saffron/green design-token CSS carried over from the old theme; gradient header w/ badges, JS feature-nav + output sub-tabs, pill radios, drag-drop dropzones w/ image preview, animated orbit loading card, marked.js markdown rendering, green-accented grade/PDF panels, footer with model badges
- ✅ Field Notes blog post — `field_notes.md` (submit to HF Field Notes)
- ✅ **Exit:** all badges claimable, app polished

## Phase 7 — Submission
- ⬜ Demo video (90-min → 10-min story)
- ⬜ Social post
- ⬜ Final Space deploy + README w/ sponsor/badge checklist
- ⬜ **Submit before June 15, 2026**

---

## Feature status (at a glance)
| # | Feature | Status |
|---|---|---|
| 1 | Worksheet-from-Textbook (OpenBMB) | ✅ |
| 2 | Weekly Teaching Pack (Best Agent) | ✅ |
| 3 | Regional-language (Cohere) | ✅ |
| 4 | Illustrated worksheets (BFL/FLUX) | ✅ |
| 5 | Photo Auto-Grading (OpenBMB + Well-Tuned) | ✅ |

## Badge status
| Badge / Award | Status | Notes |
|---|---|---|
| OpenBMB | ✅ ready | MiniCPM-V 4.5 in Features 1 + 5 |
| Modal (training) | ✅ ready | `finetune/train_modal.py` on A10G |
| Cohere | ✅ ready | Tiny Aya self-hosted on Modal |
| Black Forest Labs | ✅ ready | FLUX.1-schnell self-hosted on Modal |
| Best Agent | ✅ ready | 5-agent weekly pack pipeline |
| Well-Tuned | ✅ ready | `naazimsnh02/tutordesk-qwen3-4b` on HF Hub |
| Tiny Titan (≤4B) | ✅ ready | Qwen3-4B (4B params) |
| Sharing is Caring | ✅ ready | `data/export_traces.py` → push to HF dataset |
| Off the Grid | ✅ ready | `TUTORDESK_OFFLINE=1` + `QWEN_GGUF_PATH` → llama.cpp |
| Llama Champion | ✅ ready | Qwen3-4B via llama.cpp GGUF |
| Off-Brand | ✅ ready | `gr.Server` (FastAPI) + custom `static/index.html` single-page frontend |
| Best Demo | ⬜ | Demo video needed (Phase 7) |
| Field Notes | ✅ ready | `field_notes.md` — submit to HF Field Notes |

---

## Decision log
- 2026-06-11 — Track: **Backyard AI**. Skipped OpenAI/NVIDIA/JetBrains.
- 2026-06-11 — Feature 5 changed from manual Parent Report → **Photo Auto-Grading**.
- 2026-06-11 — Vision: **MiniCPM-V 4.5 (8B)** default; 4.6 (1.3B) offline fallback.
- 2026-06-11 — Text model: **fine-tuned Qwen3-4B** (chosen for Tiny Titan ≤4B).
- 2026-06-11 — Scope narrowed: **Classes 6–10, Math + Science, CBSE/NCERT, English + Hindi**.
- 2026-06-11 — Base dataset: **ParthKadam2003/NCERT_Dataset** (MIT).
- 2026-06-11 — **Hosting: all models self-hosted on Modal** (laptop can't hold them); Space =
  thin Gradio client; no external APIs.
- 2026-06-11 — Multilingual model: **Tiny Aya `CohereLabs/tiny-aya-fire` (3.35B)**, South-Asian
  tuned. Total stack ≈27B (< 32B).

## Open questions — resolved
- ✅ Cohere award accepts self-hosted Aya (confirmed 2026-06-11)
- ✅ 32B cap is **per-model** (each model individually) — all ours are well under

## Notes / blockers
- (none yet)
