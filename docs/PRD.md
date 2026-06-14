# TutorDesk AI

## AI Copilot for Indian Tuition Teachers

### Product Requirements Document (PRD)

Version: 2.0 (Hackathon-optimized)

Hackathon: Hugging Face × Gradio **Build Small Hackathon** (June 5–15, 2026)

Primary Track: **Backyard AI** — solve a real problem for people you know

---

# Executive Summary

TutorDesk AI is an on-laptop teaching copilot built for Indian tuition teachers. A teacher
**photographs a textbook chapter** and, in one click, gets a complete teaching pack —
worksheet, homework, test, answer key, and a parent progress note — in their **regional
language**, with **auto-generated diagrams** for younger classes.

Prep time drops from **~90 minutes/day to under 10**. Everything that can run locally does,
on a laptop, using models ≤8B.

This is a deliberately **Backyard AI** product: a specific user (the home/coaching tutor),
real daily adoption, appropriately small models, and a polished Gradio app.

---

# Problem Statement

Indian tuition teachers (home tutors, small coaching centers, evening/online tutors) spend
60–120 minutes/day manually creating worksheets, tests, homework, answer keys, and parent
updates — often re-making near-identical material. This admin load steals time from teaching.

Existing AI tools assume English, cloud access, and CBSE-only context. Regional-board and
regional-language teachers are underserved, and many work with patchy connectivity.

---

# Vision

The assistant every tuition teacher opens before every class. A full lesson package from a
single chapter photo, in under five minutes, in the teacher's own language.

---

# Target Users

**Primary:** Independent tuition teacher — home tutor, small coaching-center owner,
evening/online tutor (Classes 1–10).

**Secondary:** School teacher needing practice worksheets, unit tests, and revision material.

---

# Hackathon Strategy (why this design wins)

The hackathon rewards **one coherent product that legitimately touches several sponsor
stacks**, plus optional bonus-quest badges. TutorDesk is architected so each headline
feature claims a different sponsor or award, while telling a single tight story.

> Per organizer rules: max **32B params total**, must **run on a laptop**, **Gradio app on a
> Hugging Face Space**, plus a **demo video** and **social post**. (OpenAI/NVIDIA sponsor
> tracks intentionally not targeted. JetBrains track skipped — not product-relevant.)

## Sponsor / Award map

| Headline Feature | Sponsor / Award targeted | Model / Mechanism |
|---|---|---|
| 1. Worksheet-from-Textbook (vision) | **OpenBMB — $10,000** (anchor) | **MiniCPM-V 4.5 (8B)** reads chapter photos/PDFs |
| 2. Weekly Teaching Pack (multi-agent) | **Best Agent — $1,000** + core Backyard AI | 5-agent pipeline orchestration |
| 3. Regional-language generation | **Cohere — $5,000** | **Aya Expanse 8B / Tiny Aya** (Hindi, Tamil, Telugu, Bengali, Gujarati, Marathi, …) |
| 4. Illustrated / diagram worksheets | **Black Forest Labs — $3,000** | **FLUX** generates science/geometry/picture-question art |
| 5. Photo Auto-Grading | **OpenBMB** + **Well-Tuned/Tiny Titan** + **Best Agent** | MiniCPM-V reads the sheet → fine-tuned Qwen3-4B grades it Indian-style |

## Bonus-quest badges & special awards

| Badge / Award | How TutorDesk earns it |
|---|---|
| **Well-Tuned** | Publish a fine-tuned **Qwen3-4B** on Indian curriculum (CBSE + state-board Q&A) |
| **Modal — $20,000 credits** | Run the fine-tuning **training job on Modal** (finetuning use is eligible) |
| **Tiny Titan — $1,500** (≤4B) | Text generation runs on the **4B** fine-tune |
| **Sharing is Caring** | Publish **agent traces** (the multi-agent conversation logs) as a HF dataset |
| **Off the Grid** | Offer a **fully-local mode** — MiniCPM-V + Qwen3-4B via llama.cpp, no cloud APIs |
| **Llama Champion** | Local inference uses the **llama.cpp** runtime |
| **Off-Brand — $1,500** | Custom frontend via **`gr.Server`** (not stock Gradio layout) |
| **Field Notes** | Publish a build/report blog post |
| **Best Demo — $1,000** | The 90-min → 10-min teacher demo story |

---

# Core Features (MVP — the 5 that win)

## Feature 1 — Worksheet-from-Textbook  → OpenBMB

Teacher uploads a **chapter photo or textbook PDF**. The vision model extracts topic,
concepts, and learning objectives, then generates a worksheet + quiz + answer key grounded
in the actual chapter content.

* Input: chapter image / PDF
* Model: **MiniCPM-V 4.5 (8B)** (laptop-runnable; beats GPT-4o on vision at 8B)
* Output: worksheet, quiz, answer key

This is the "wow" — content appears from a snapshot of the page.

---

## Feature 2 — Weekly Teaching Pack (signature)  → Best Agent

One click. Input: Class, Subject, Chapter (or the photo from Feature 1).

Output, via a **5-agent pipeline**:

1. **Curriculum Understanding Agent** — topic, objectives, concepts
2. **Question Generation Agent** — questions across difficulty levels
3. **Difficulty Validation Agent** — ensures grade-appropriate level
4. **Answer Generation Agent** — answer key + step-by-step solutions
5. **Report Writing Agent** — parent update template

Bundled deliverable: worksheet + homework + quiz + answer key + parent note.

---

## Feature 3 — Regional-Language Generation  → Cohere

Any generated artifact can be produced in the teacher's language.

* Phase 1: English, Hindi, Tamil
* Phase 2: Telugu, Bengali, Gujarati, Marathi, Kannada, Malayalam
* Model: **Cohere Aya Expanse 8B / Tiny Aya** (Tiny Aya covers South Asian languages and
  launched at the India AI Summit)

This is the differentiator for regional-board teachers — the underserved majority.

---

## Feature 4 — Illustrated / Diagram Worksheets  → Black Forest Labs

For Classes 1–5 and for science/geometry, generate **printable illustrations**: labeled
science diagrams, geometry figures, and picture-based questions.

* Model: **FLUX**
* Output: worksheet art embedded in the printable PDF

Unexpected delight in an edu tool, and a clean BFL claim.

---

## Feature 5 — Photo Auto-Grading  → OpenBMB + Well-Tuned + Best Agent

Teacher photographs a student's **filled answer sheet**. A two-stage pipeline grades it and
returns marks + per-question feedback, closing the loop:
**generate worksheet → student writes → photograph → auto-grade → parent note.**

Pipeline (text model is vision-blind, so vision must run first):

1. **MiniCPM-V 4.5 (vision)** reads the sheet → extracts the student's answers as structured
   text (question-by-question).
2. **Fine-tuned Qwen3-4B (text)** grades each answer against the answer key, applying
   **Indian marking conventions** — CBSE / state-board step marks, partial credit, method
   marks — not a generic Western rubric. This is where the Indian-curriculum fine-tune pays
   off.

Output: total score, per-question marks, mistakes flagged, and a one-line parent note
auto-drafted from the result.

* **Demo note:** use neat/printed answers — messy handwriting challenges any 8B vision model.
  Handwriting robustness is a roadmap item.
* **Fine-tune requirement:** training data must include **marking schemes, model answers, and
  step-wise grading examples**, not just questions — so the model learns to mark, not just
  generate.

Why it's strong: real load-bearing AI, completes the teacher workflow, and stacks three
claims (OpenBMB vision + Well-Tuned/Tiny Titan marking + Best Agent pipeline). Also feeds the
published agent-trace dataset.

---

# Roadmap (post-MVP — do NOT demo, keep as slides)

Deferred to avoid scope sprawl that hurts polish/delight scores:

* Full Parent Progress Report (manual inputs) — Feature 5 already auto-drafts a parent note
  from grading results; the rich standalone report is a fast-follow
* Student Performance Analyzer (Excel/CSV upload → weak/strong students, common mistakes) —
  natural next step: aggregate Feature 5 grading across the class
* Remedial Learning Plan Generator (week-by-week improvement plan)
* Question Bank Builder (extract questions/topics/difficulty from uploaded papers)
* Handwriting-robust grading

---

# Model Stack

| Role | Model | Sponsor / Award | Notes |
|---|---|---|---|
| Vision (textbook + answer-sheet reading) | **MiniCPM-V 4.5 (8B)** | OpenBMB | Built on Qwen3-8B + SigLIP2; runs on laptop. **4.6 (1.3B)** is the lightweight/Off-the-Grid fallback (lower OCR accuracy on dense pages) |
| Text generation + Indian-style grading | **Fine-tuned Qwen3-4B** | Modal + Well-Tuned + Tiny Titan | Trained on Modal; ≤4B for Tiny Titan; grades with marking-scheme logic |
| Multilingual generation | **Cohere Aya Expanse 8B / Tiny Aya** | Cohere | Regional Indian languages |
| Image generation | **FLUX** | Black Forest Labs | Diagrams & illustrations |

All language models ≤8B; total stack well under the 32B cap. ✅

**Local mode (Off the Grid + Llama Champion):** MiniCPM-V + fine-tuned Qwen3-4B served via
**llama.cpp**, no cloud APIs. Cohere/FLUX features degrade gracefully or fall back to local
substitutes when offline.

---

# Fine-Tuning Strategy  → Well-Tuned + Modal + Tiny Titan

Fine-tune **Qwen3-4B** for:

* Educational content & question generation
* Difficulty classification
* Indian curriculum alignment (CBSE + state boards)
* **Indian-style grading** — apply marking schemes, step marks, and partial credit (powers
  Feature 5)

Training job runs **on Modal** (finetuning is an eligible Modal use). The resulting model is
**published to the Hugging Face Hub** to claim the **Well-Tuned** badge, and its 4B size
qualifies for **Tiny Titan**.

## Dataset

* CBSE question papers, state-board papers
* Teacher-created worksheets, educational PDFs
* Open educational resources
* **Marking schemes, model answers, and step-wise graded solutions** (required for Feature 5
  grading quality)

---

# Agent Traces as a Dataset  → Sharing is Caring

The multi-agent pipeline's conversation logs (curriculum → question → validation → answer →
report) are captured and **published as a Hugging Face dataset**:
*"Indian-curriculum worksheet-generation agent traces."* This earns the **Sharing is Caring**
badge and doubles as a reusable open-education resource (and a **Field Notes** blog topic).

---

# User Interface  → Off-Brand

* Platform: **Gradio**, with a **custom frontend via `gr.Server`** (claims Off-Brand)
* Deployment: **Hugging Face Space**
* Design: mobile-first, teacher-focused, one-tap workflows
* Every output is **print-ready** (PDF) — teachers print and hand out

---

# Success Metrics

* **Prep time:** 60–120 min/day → **< 10 min** (target headline metric)
* **Weekly time saved:** ~7–10 hours per teacher
* **Content generated:** worksheets / tests / homework per week
* **Satisfaction:** "Would you use this again tomorrow?" → target **80%+**

---

# Demo Story (Backyard AI + Best Demo)

A tutor teaching Classes 6–10 spends ~90 minutes/day on prep.

With TutorDesk AI:

1. **Photograph** today's chapter (MiniCPM-V reads it)
2. **One click** → Weekly Teaching Pack (5-agent pipeline)
3. Output in **Tamil** (Cohere) with **diagrams** for the Class-6 group (FLUX)
4. **Print** worksheet + test; next day, **photograph a student's answer sheet → auto-graded**
   Indian-style (MiniCPM-V + fine-tuned Qwen3-4B), with a parent note auto-drafted

Time: 90 minutes → **under 10**. ~7–10 hours saved every week.

A real, specific user; real daily adoption; appropriately small models; a polished app —
directly aligned with Backyard AI judging, while stacking OpenBMB, Cohere, Black Forest Labs,
Modal, and six bonus badges.

---

# MVP Checklist

Must-have for submission:

* [ ] Feature 1 — Worksheet-from-Textbook (MiniCPM-V 4.5)
* [ ] Feature 2 — Weekly Teaching Pack (5-agent)
* [ ] Feature 3 — Regional-language output (Cohere Aya)
* [ ] Feature 4 — Illustrated worksheets (FLUX)
* [ ] Feature 5 — Photo Auto-Grading (MiniCPM-V reads → fine-tuned Qwen3-4B grades)
* [ ] Fine-tuned Qwen3-4B published (Modal-trained)
* [ ] Agent traces dataset published
* [ ] Local mode via llama.cpp
* [ ] Custom `gr.Server` frontend on a HF Space
* [ ] Demo video + social post + Field Notes blog
