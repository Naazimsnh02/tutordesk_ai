# Field Notes: Building TutorDesk AI — An On-Laptop Copilot for Indian Tuition Teachers

*Submitted for the Hugging Face × Gradio "Build Small" Hackathon · June 2026 · Backyard AI track*

---

## The Problem I Was Solving

In India, roughly 70 million students attend private tuition classes outside school hours.
Their teachers — often solo practitioners working from home — spend 60–90 minutes every day
doing the same things: writing worksheets, marking homework, typing parent updates.
That is prep time that could be teaching time.

I wanted to build something that could cut that 90 minutes to under 10, using only
open-weight models, no paid APIs, and — crucially — software that *works when the internet
doesn't*.

---

## What I Built

**TutorDesk AI** is a five-feature Gradio app for Classes 6–10 Math and Science (CBSE/NCERT):

| Feature | What it does | Model |
|---------|-------------|-------|
| Worksheet from Textbook | Photograph a chapter page → instant worksheet + quiz + answer key | MiniCPM-V 4.5 (OpenBMB, 8B) |
| Weekly Teaching Pack | One click → worksheet + homework + quiz + key + parent note (5-agent pipeline) | Fine-tuned Qwen3-4B |
| Regional Language | Translate any artifact into Hindi or Tamil | Tiny Aya (CohereLabs, 3.35B) |
| Illustrated Worksheets | Embed AI-generated science diagrams in the PDF | FLUX.1-schnell (Black Forest Labs) |
| Photo Auto-Grading | Photograph an answer sheet → marks awarded per step, CBSE-style | MiniCPM-V + fine-tuned Qwen3-4B |

Total model stack: **≈27B parameters** (well under the 32B per-model cap).

---

## Key Technical Decisions

### 1. Self-hosting everything on Modal

My dev laptop cannot hold an 8B vision model and a 12B diffusion model at the same time.
Rather than reaching for a paid API, I deployed every model as a **scale-to-zero GPU function
on Modal**. The Gradio Space is a thin client that calls these functions by name. Cold-start
latency (~20–40 s on first request) is acceptable for a teacher generating a weekly pack —
they are not running a real-time chat.

This approach also lets me claim the Off-the-Grid path cleanly: in offline mode, only
llama.cpp + GGUF is needed locally.

### 2. Fine-tuning Qwen3-4B for Indian grading style

The base Qwen3-4B is a competent text model, but it grades generously — full marks for
directionally correct answers, no attention to *step marks* or *partial credit*, which are
central to CBSE assessment culture.

I built a grading dataset of ~600 `(marking_scheme, student_answer, expected_grade)` triples
synthesised from NCERT worked examples, then LoRA-fine-tuned for 3 epochs on a Modal A10G
(< 30 minutes). The result (`naazimsnh02/tutordesk-qwen3-4b`) reliably outputs structured
`MARKS: X/Y` tokens and penalises skipped steps.

Training loss dropped from ~2.1 → 0.4. Not measured on a held-out set (hackathon scope),
but qualitative grading felt noticeably tighter.

### 3. Tiny Aya for South-Asian languages

`CohereLabs/tiny-aya-fire` (3.35B) is specifically trained for South-Asian languages
including Hindi and Tamil — a much better fit than a general-purpose multilingual model.
I self-host it on a Modal L4 (cheaper than A10G, sufficient for 3B generation) and fall back
to English pass-through when offline.

### 4. The 5-agent architecture

Each "agent" is a single function: system prompt + one LLM call + trace logging.
The Weekly Teaching Pack chains five of them:

```
chapter text → [CurriculumAgent] → topics
                                 → [QuestionGenAgent] → questions (×N)
                                                      → [DifficultyAgent] → labelled questions
                                                      → [AnswerAgent]     → answer key
                                                      → [ReportAgent]     → parent note
```

The pipeline is sequential (each agent depends on the previous), but the structure makes
it easy to swap models per agent in future — e.g., a smaller model for the parent note,
a reasoning model for the answer key.

### 5. Off-the-Grid mode via llama.cpp

For the Off-Grid + Llama Champion badges, the same fine-tuned model can run locally via
**llama-cpp-python** (GGUF quantisation). Set `TUTORDESK_OFFLINE=1` and point
`QWEN_GGUF_PATH` at a Q4_K_M quant (~2.5 GB), and the entire Weekly Teaching Pack,
Auto-Grading (text path), and Regional Language (English pass-through) work without
any internet connection. Vision features degrade gracefully to a text-input prompt.

---

## What Surprised Me

**MiniCPM-V's OCR is remarkably good on printed text.** I expected to need extensive
preprocessing — contrast boost, deskew, upscale. In practice, a phone photo of a clear
NCERT page produces clean extraction on the first try. Handwriting is a different story
(as expected), which is why the demo uses printed/neat answer sheets.

**The grading dataset bottleneck is prompt engineering, not data volume.** Getting Qwen to
output a consistent `MARKS: X/Y` token with a breakdown table required more iteration on
the system prompt than on the examples themselves. Once the prompt was tight, 600 examples
was enough.

**Modal's scale-to-zero genuinely works for hackathon demos.** The fear is "cold start at
demo time." The reality: cache the model in the Modal volume, and the first warm-up is
~20 s — slow, but not demo-breaking.

---

## What I Would Do Differently

1. **Add a GGUF export step to the fine-tuning pipeline.** Right now, Off-Grid mode points
   to a separate Qwen3-4B base GGUF; the fine-tuned weights live only on HF Hub as a full
   checkpoint. Merging LoRA → base → GGUF export would close that gap.

2. **Async the pipeline.** The 5-agent chain runs serially (~45 s end-to-end on A10G). Most
   agents only need the curriculum output, so question_gen, difficulty, answer, and report
   could run in parallel and cut latency by ~3×.

3. **Handwriting robustness.** The auto-grading is scoped to printed sheets. A real
   deployment needs either a dedicated HTR model or a user-assisted transcription step.

---

## Links

- **Space:** https://huggingface.co/spaces/build-small-hackathon/tutordesk-ai
- **Demo Video:** https://youtu.be/HBBLSwXUeaM
- **Fine-tuned model:** https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b
- **Agent traces dataset:** https://huggingface.co/datasets/naazimsnh02/tutordesk-agent-traces
- **Source:** https://github.com/Naazimsnh02/tutordesk_ai

---

*Built by Naazim · June 2026 · TutorDesk AI*
