# TutorDesk AI

**AI copilot for Indian tuition teachers** — turn ~90 min/day of prep into under 10.
Submission for the Hugging Face × Gradio **Build Small Hackathon** (Backyard AI track).

A teacher photographs a textbook chapter and gets a full teaching pack — worksheet,
homework, test, answer key — in their regional language, with diagrams, plus photo-based
auto-grading. Runs on a laptop with models ≤8B.

## Features
1. **Worksheet-from-Textbook** — MiniCPM-V reads a chapter photo/PDF → worksheet+quiz+key.
2. **Weekly Teaching Pack** — one click, 5-agent pipeline → full pack.
3. **Regional-language output** — Cohere Aya (Hindi, Tamil, …).
4. **Illustrated worksheets** — FLUX diagrams & figures.
5. **Photo Auto-Grading** — MiniCPM-V reads the answer sheet → fine-tuned Qwen3-4B grades
   it Indian-style (step marks, partial credit).

## Docs
- `PRD.md` — product spec + hackathon sponsor/award strategy
- `implementation_plan.md` — phased build plan
- `progress.md` — live status tracker
- `CLAUDE.md` — repo guidance & constraints

## Quickstart
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in tokens
python app.py
```

## Scope (hackathon)
Classes 6–10 · Math + Science · CBSE/NCERT · English (+ Hindi slice).

## Model stack
MiniCPM-V 4.5 (vision) · fine-tuned Qwen3-4B (text/grading) · Cohere Aya (multilingual) ·
FLUX (diagrams). All ≤ the 32B laptop budget; local mode via llama.cpp.
