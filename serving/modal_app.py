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
        "transformers>=4.44,<5.0",  # MiniCPM-V custom code breaks on transformers 5.x
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
import os as _os
# After Phase 3: set QWEN_FINETUNED_MODEL in .env / Modal secret to switch to the fine-tune.
_QWEN_MODEL_ID = _os.environ.get("QWEN_FINETUNED_MODEL", _QWEN_BASE_MODEL)

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

import pathlib as _pathlib
_hf_secret = modal.Secret.from_dotenv(
    path=str(_pathlib.Path(__file__).parent.parent)  # serving/ -> project root
)

@app.cls(gpu="A10G", image=_vision_image, scaledown_window=120, secrets=[_hf_secret])
class MiniCPM:
    @modal.enter()
    def load(self) -> None:
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(
            _MINICPM_MODEL_ID, trust_remote_code=True
        )
        # Load without device_map to avoid transformers 5.x infer_auto_device_map
        # breaking on the custom MiniCPMV class. Use bfloat16 + sdpa per model docs.
        self.model = AutoModel.from_pretrained(
            _MINICPM_MODEL_ID,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
        ).eval().cuda()


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
_AYA_MODEL_ID = "CohereLabs/tiny-aya-fire"

@app.cls(gpu="L4", image=_text_image, scaledown_window=120, secrets=[_hf_secret])
class TinyAya:
    @modal.enter()
    def load(self) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(_AYA_MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(
            _AYA_MODEL_ID,
            torch_dtype=torch.float16,
            device_map="auto",
        ).eval()

    @modal.method()
    def localize(self, text: str, language: str) -> str:
        import torch

        system = (
            f"You are an expert educational translator. Translate the following "
            f"educational content into {language}. Preserve all question numbers, "
            f"formatting, and mathematical notation exactly. Return only the translated text."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ]
        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = f"{system}\n\nUser: {text}\n\nAssistant:"

        inputs = self.tokenizer([prompt], return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = outputs[0][inputs.input_ids.shape[1]:]
        return self.tokenizer.decode(generated, skip_special_tokens=True).strip()


# ---------------------------------------------------------------------------
# FLUX.1-schnell  (diagram/illustration generation — BFL claim)
# Phase 5.
# ---------------------------------------------------------------------------
@app.cls(gpu="A100", image=_flux_image, scaledown_window=120, secrets=[_hf_secret])
class Flux:
    @modal.enter()
    def load(self) -> None:
        import torch
        from diffusers import FluxPipeline

        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16,
        ).to("cuda")

    @modal.method()
    def generate_diagram(self, prompt: str) -> bytes:
        import io

        image = self.pipe(
            prompt,
            num_inference_steps=4,
            guidance_scale=0.0,
            height=512,
            width=512,
        ).images[0]
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()


# ---------------------------------------------------------------------------
# Local entrypoint — smoke-test all 4 models:  modal run serving/modal_app.py
# ---------------------------------------------------------------------------
@app.local_entrypoint()
def main() -> None:
    import io
    import time

    W = 65

    def _ok(label, t0, preview=""):
        import textwrap
        short = textwrap.shorten(str(preview).replace("\n", " "), width=45)
        print(f"  ✅  {label:<24} ({time.time()-t0:.1f}s)  {short!r}")

    def _fail(label, t0, err):
        print(f"  ❌  {label:<24} ({time.time()-t0:.1f}s)  {err}")

    print("=" * W)
    print("  TutorDesk AI — Modal smoke test (all 4 models)")
    print("=" * W)

    # 1 — Qwen3-4B
    print("\n  1 · Qwen3-4B")
    t = time.time()
    try:
        q = Qwen()
        out = q.generate.remote(
            "You are a CBSE tutor for Class 8 Science.",
            "Give one MCQ on Cell Structure. Return only the question and 4 options.",
            max_new_tokens=256, temperature=0.3,
        )
        _ok("Qwen.generate", t, out)
    except Exception as exc:
        _fail("Qwen.generate", t, exc)

    # 2 — MiniCPM-V
    print("\n  2 · MiniCPM-V 4.5")
    t = time.time()
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (128, 128), (255, 255, 248))
        ImageDraw.Draw(img).text((10, 55), "TEST", fill=(60, 60, 60))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        m = MiniCPM()
        out = m.read_image.remote(buf.getvalue(), "Describe this image in one sentence.")
        _ok("MiniCPM.read_image", t, out)
    except Exception as exc:
        _fail("MiniCPM.read_image", t, exc)

    # 3 — Tiny Aya
    print("\n  3 · Tiny Aya")
    t = time.time()
    try:
        a = TinyAya()
        out = a.localize.remote("What is the function of the cell membrane?", "Hindi")
        _ok("TinyAya.localize", t, out)
    except Exception as exc:
        _fail("TinyAya.localize", t, exc)

    # 4 — FLUX.1-schnell
    print("\n  4 · FLUX.1-schnell")
    t = time.time()
    try:
        f = Flux()
        raw = f.generate_diagram.remote(
            "Simple labeled science diagram: animal cell. Clean, educational style."
        )
        size_kb = len(raw) // 1024
        _ok("Flux.generate_diagram", t, f"PNG {size_kb} KB")
    except Exception as exc:
        _fail("Flux.generate_diagram", t, exc)

    print("\n" + "=" * W)
