"""Modal app — one scale-to-zero GPU function per model.

Deploy:  modal deploy serving/modal_app.py
Then the Space/clients call functions by name via `modal.Function.from_name`.

Design notes:
- Each model is its own function so they don't share a container (avoids OOM) and each
  idles to zero between calls (credit-efficient).
- `@modal.enter()` loads weights once per warm container.
- GPU sizing: 8B/4B/3.35B text+vision fit on an A10G/L4; FLUX prefers A100/L40S.
- Weights are baked into the image (or cached on a Volume) so cold starts stay fast.

Param budget (self-hosted, all open-weight): MiniCPM-V 8B + Qwen3-4B + FLUX ~12B +
Tiny-Aya 3.35B ≈ 27B total (< 32B cap).
"""
from __future__ import annotations

# import modal
from config import CONFIG

# app = modal.App(CONFIG.modal_app_name)
#
# text_image = modal.Image.debian_slim().pip_install(
#     "transformers", "torch", "accelerate", "peft", "sentencepiece"
# )
# flux_image = modal.Image.debian_slim().pip_install("diffusers", "torch", "transformers")


# --- Vision: MiniCPM-V (OpenBMB) -------------------------------------------------
# @app.cls(gpu="A10G", image=text_image, scaledown_window=120)
class MiniCPM:
    """TODO Phase 2: load CONFIG.minicpm_model in @modal.enter(); expose read_image()."""


# --- Text + grading: fine-tuned Qwen3-4B (Modal / Well-Tuned / Tiny Titan) --------
# @app.cls(gpu="A10G", image=text_image, scaledown_window=120)
class Qwen:
    """TODO Phase 1: load base Qwen3-4B; Phase 3: prefer CONFIG.qwen_finetuned_model.
    Expose generate(system, user, **kw)."""


# --- Multilingual: Tiny Aya (Cohere) ---------------------------------------------
# @app.cls(gpu="L4", image=text_image, scaledown_window=120)
class TinyAya:
    """TODO Phase 5: load CONFIG.aya_model (tiny-aya-fire); expose localize(text, language)."""


# --- Images: FLUX (Black Forest Labs) --------------------------------------------
# @app.cls(gpu="A100", image=flux_image, scaledown_window=120)
class Flux:
    """TODO Phase 5: load CONFIG.flux_model; expose generate_diagram(prompt) -> bytes."""
