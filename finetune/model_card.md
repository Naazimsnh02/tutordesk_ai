---
language:
- en
- hi
license: apache-2.0
base_model: Qwen/Qwen3-4B
tags:
- education
- indian-education
- cbse
- ncert
- fine-tuned
- lora
- qwen3
- tutoring
- question-generation
- grading
datasets:
- ParthKadam2003/NCERT_Dataset
pipeline_tag: text-generation
library_name: transformers
---

# TutorDesk Qwen3-4B

A LoRA fine-tuned version of [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) trained for **Indian CBSE/NCERT tuition teachers** (Classes 6–10, Math & Science).

Part of the [TutorDesk AI](https://github.com/naazimsnh02/tutordesk_ai) project — submitted to the **Hugging Face × Gradio "Build Small Hackathon"** (Backyard AI track, June 2026).

---

## What it does

This model is fine-tuned on three objectives, all grounded in the Indian CBSE/NCERT curriculum:

| Objective | Task | Examples |
|---|---|---|
| **Question Generation** | Given a class, subject, topic, and difficulty → output an exam question + answer + explanation | ~3,000 |
| **Difficulty Classification** | Given a question → output `Easy`, `Medium`, or `Hard` | ~1,000 |
| **Indian-style Grading** | Given a question, marking scheme, and student answer → award step marks + one-line feedback | ~600 |

**Total training examples: ~4,600**

---

## Model details

| Property | Value |
|---|---|
| Base model | `Qwen/Qwen3-4B` |
| Parameters | 4B (≤4B → qualifies for Tiny Titan) |
| Fine-tune method | LoRA (PEFT) |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| Target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj` |
| Training epochs | 3 |
| Batch size | 4 × 4 grad accum = 16 effective |
| Learning rate | 2e-4 (cosine schedule, 5% warmup) |
| Max seq length | 2,048 tokens |
| Precision | fp16 |
| Hardware | Modal A10G (24 GB VRAM) |
| Adapter | Merged into base weights (no adapter files needed at inference) |

---

## Training data

- **Source:** [ParthKadam2003/NCERT_Dataset](https://huggingface.co/datasets/ParthKadam2003/NCERT_Dataset) (MIT license, ~124k rows)
- **Scope filtered to:** Classes 6–10 · Mathematics & Science · CBSE/NCERT
- **Grading triples:** Synthesized using the base Qwen3-4B as a teacher model — each Q&A pair was expanded into 4 student-answer types (correct/no-working/partial/wrong-method) with step-mark breakdowns.
- All data formatted as ChatML (Qwen3 chat template, `enable_thinking=False`).

---

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "naazimsnh02/tutordesk-qwen3-4b"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, dtype="auto", device_map="auto")

def ask(system, user, max_new_tokens=512):
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=0.7, do_sample=True)
    return tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
```

### Generate a question

```python
response = ask(
    "You are an expert Indian CBSE tutor for Classes 6-10 Math and Science.",
    "Generate a Medium Short Answer question for Class 8 Science on the topic 'Cell Structure'. "
    "Provide the full question, answer, and explanation.",
)
print(response)
```

### Classify difficulty

```python
response = ask(
    "You classify the difficulty of Indian CBSE exam questions for Classes 6-10 as Easy, Medium, or Hard. "
    "Reply with only the label — nothing else.",
    "Classify difficulty for this Class 9 Science question:\n"
    "Explain the process of photosynthesis and write the balanced chemical equation.",
)
print(response)  # → Medium
```

### Grade a student answer (Indian-style)

```python
response = ask(
    "You are an Indian CBSE teacher grading student answers. "
    "Award step marks, give partial credit where deserved, and provide a one-sentence feedback comment.",
    "Grade out of 3 marks.\n\n"
    "Question: State Newton's Second Law of Motion.\n\n"
    "Marking scheme:\n"
    "  Step 1: Force is proportional to rate of change of momentum (1 mark)\n"
    "  Step 2: F = ma stated or derived (1 mark)\n"
    "  Step 3: Units and direction mentioned (1 mark)\n\n"
    "Student answer: Force equals mass times acceleration. More force means more acceleration.",
)
print(response)  # → Marks: 2/3\nFeedback: ...
```

---

## Scope & limitations

- **Scope:** Classes 6–10 · CBSE/NCERT · Mathematics & Science · English (primary), Hindi (partial)
- **Not trained for:** Humanities, language arts, competitive exams (JEE/NEET), classes below 6 or above 10
- **Grading:** Best on objective Math/Science answers; open-ended essay grading is not reliable
- **Handwriting OCR:** This model operates on text. Handwriting recognition is handled separately by MiniCPM-V in the TutorDesk pipeline
- **Language:** Outputs are primarily English; multilingual outputs handled by Tiny Aya in the TutorDesk pipeline

---

## Citation

If you use this model, please cite the base model and dataset:

```bibtex
@misc{tutordesk-qwen3-4b,
  author    = {Naazim},
  title     = {TutorDesk Qwen3-4B: CBSE Tutor Fine-tune},
  year      = {2026},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b}
}
```

---

## License

Apache 2.0 (inherited from Qwen3-4B base). Training data from ParthKadam2003/NCERT_Dataset (MIT).
