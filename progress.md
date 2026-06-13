# TutorDesk AI — Progress Tracker

Update this as work completes. Status: ⬜ not started · 🟨 in progress · ✅ done · ⛔ blocked

Last updated: 2026-06-13

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
- ⬜ Run data prep: `python -m data.prep_generation && python -m data.prep_difficulty && python -m data.prep_grading`
- ⬜ Set HF_USERNAME in .env
- ⬜ Run training: `modal run finetune/train_modal.py`
- ⬜ Publish fine-tuned Qwen3-4B to HF Hub (**Well-Tuned**)
- ⬜ Set QWEN_FINETUNED_MODEL in .env + redeploy Modal
- ⬜ **Exit:** model published, ~4.6k examples trained

## Phase 4 — Photo Auto-Grading (Feature 5)
- ⬜ `pipelines/auto_grade.py` — MiniCPM-V read → Qwen3-4B grade → marks+feedback+parent note
- ⬜ **Exit:** Feature 5 works on neat/printed sheets

## Phase 5 — Multilingual + Diagrams
- ⬜ `serving/modal_app.py::TinyAya` (tiny-aya-fire) + language selector (Feature 3)
- ⬜ `serving/modal_app.py::Flux` (FLUX.1-schnell) — diagrams in PDFs (Feature 4)
- ⬜ Offline graceful fallback
- ⬜ **Exit:** Features 3 & 4 — Cohere + BFL claims satisfied

## Phase 6 — Badge layer & polish
- ⬜ Local mode via llama.cpp (**Off the Grid + Llama Champion**)
- ⬜ `traces/` capture + publish HF dataset (**Sharing is Caring**)
- ⬜ Custom `gr.Server` frontend (**Off-Brand**)
- ⬜ Field Notes blog post
- ⬜ **Exit:** all badges claimable, app polished

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
| 3 | Regional-language (Cohere) | ⬜ |
| 4 | Illustrated worksheets (BFL/FLUX) | ⬜ |
| 5 | Photo Auto-Grading (OpenBMB + Well-Tuned) | ⬜ |

## Badge status
| Badge / Award | Status |
|---|---|
| OpenBMB | ⬜ |
| Modal (training) | ⬜ |
| Cohere | ⬜ |
| Black Forest Labs | ⬜ |
| Best Agent | ⬜ |
| Well-Tuned | ⬜ |
| Tiny Titan (≤4B) | ⬜ |
| Sharing is Caring | ⬜ |
| Off the Grid | ⬜ |
| Llama Champion | ⬜ |
| Off-Brand | ⬜ |
| Best Demo | ⬜ |
| Field Notes | ⬜ |

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
