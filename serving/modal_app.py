"""Modal app — scale-to-zero GPU functions, one per model.

Deploy:   modal deploy serving/modal_app.py
Test:     modal run   serving/modal_app.py

Each model lives in its own class so they never share a container (avoids OOM)
and each idles to zero between calls (credit-efficient).

Param budget (per-model cap, each well under 32B):
  Qwen3-4B       ~4B   A10G
  MiniCPM-V 4.5  ~8B   A10G
  tiny-aya-fire  ~3B   L4
  FLUX.1-schnell ~12B  A100
"""
from __future__ import annotations

import modal

_MODAL_APP_NAME = "tutordesk-ai"
_QWEN_BASE_MODEL = "Qwen/Qwen3-4B"

app = modal.App(_MODAL_APP_NAME)

_text_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "transformers>=4.44",
        "torch>=2.3",
        "accelerate>=0.33",
        "sentencepiece",
        "Pillow>=10.0",
    )
)

_vision_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "transformers>=4.44",
        "torch>=2.3",
        "accelerate>=0.33",
        "sentencepiece",
        "Pillow>=10.0",
        "timm",
    )
)

_flux_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "diffusers>=0.30",
        "torch>=2.3",
        "transformers>=4.44",
        "Pillow>=10.0",
    )
)


# ---------------------------------------------------------------------------
# Qwen3-4B  (text generation + Indian-style grading)
# Phase 1: base model. Phase 3: swap MODEL_ID to CONFIG.qwen_finetuned_model.
# ---------------------------------------------------------------------------
_QWEN_MODEL_ID = _QWEN_BASE_MODEL  # change to finetuned HF repo path after Phase 3

@app.cls(gpu="A10G", image=_text_image, scaledown_window=120)
class Qwen:
    @modal.enter()
    def load(self) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(_QWEN_MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(
            _QWEN_MODEL_ID,
            dtype=torch.float16,
            device_map="auto",
        )
        self.model.eval()

    @modal.method()
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_new_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        import re
        import torch

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        # enable_thinking=False suppresses the <think> chain-of-thought block;
        # the regex below is a belt-and-suspenders fallback for older checkpoints.
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = outputs[0][inputs.input_ids.shape[1]:]
        raw = self.tokenizer.decode(generated, skip_special_tokens=True)
        # Strip any residual <think>…</think> blocks the model still emits
        clean = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
        return clean.strip()


# ---------------------------------------------------------------------------
# MiniCPM-V  (vision: textbook + answer-sheet reading)
# Phase 2.
# ---------------------------------------------------------------------------
_MINICPM_MODEL_ID = "openbmb/MiniCPM-V-4_5"

@app.cls(gpu="A10G", image=_vision_image, scaledown_window=120)
class MiniCPM:
    @modal.enter()
    def load(self) -> None:
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(
            _MINICPM_MODEL_ID, trust_remote_code=True
        )
        # device_map="auto" triggers infer_auto_device_map which breaks on the
        # custom MiniCPMV class (missing all_tied_weights_keys). Load on CPU
        # then move to cuda manually to avoid the issue.
        self.model = AutoModel.from_pretrained(
            _MINICPM_MODEL_ID,
            trust_remote_code=True,
            dtype=torch.float16,
        ).to("cuda")
        self.model.eval()

    @modal.method()
    def read_image(self, image_bytes: bytes, instruction: str) -> str:
        import io
        import torch
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        msgs = [{"role": "user", "content": [image, instruction]}]
        with torch.no_grad():
            result = self.model.chat(image=None, msgs=msgs, tokenizer=self.tokenizer)
        return result


# ---------------------------------------------------------------------------
# Tiny Aya  (multilingual: South-Asian languages — Cohere claim)
# Phase 5.
# ---------------------------------------------------------------------------
@app.cls(gpu="L4", image=_text_image, scaledown_window=120)
class TinyAya:
    @modal.enter()
    def load(self) -> None:
        # TODO Phase 5: load CONFIG.aya_model (CohereLabs/tiny-aya-fire)
        raise NotImplementedError("Phase 5: load Tiny Aya")

    @modal.method()
    def localize(self, text: str, language: str) -> str:
        raise NotImplementedError("Phase 5: implement Tiny Aya localization")


# ---------------------------------------------------------------------------
# FLUX.1-schnell  (diagram/illustration generation — BFL claim)
# Phase 5.
# ---------------------------------------------------------------------------
@app.cls(gpu="A100", image=_flux_image, scaledown_window=120)
class Flux:
    @modal.enter()
    def load(self) -> None:
        # TODO Phase 5: load CONFIG.flux_model via diffusers
        raise NotImplementedError("Phase 5: load FLUX")

    @modal.method()
    def generate_diagram(self, prompt: str) -> bytes:
        raise NotImplementedError("Phase 5: implement FLUX diagram generation")


# ---------------------------------------------------------------------------
# Local entrypoint for quick manual testing:  modal run serving/modal_app.py
# ---------------------------------------------------------------------------
@app.local_entrypoint()
def main() -> None:
    q = Qwen()
    out = q.generate.remote(
        "You are a CBSE tutor for Class 8 Science.",
        "Generate 3 medium MCQ questions on the topic of Cell Structure.",
    )
    print(out)
