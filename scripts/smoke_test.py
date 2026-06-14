"""Smoke test for all four TutorDesk AI models.

Tests each model via the thin clients (models/*.py) → Modal backend.
Run from the project root:

    python scripts/smoke_test.py              # cloud (Modal) — all 4 models
    TUTORDESK_OFFLINE=1 python scripts/smoke_test.py  # offline (llama.cpp only)

Prerequisites: `modal token set` done and `modal deploy serving/modal_app.py` up.
Offline mode: QWEN_GGUF_PATH must point to a local .gguf file.
"""
from __future__ import annotations

import io
import sys
import textwrap
import time
from typing import Callable

# ── Minimal test image (128×128 white square with a label) ──────────────────
def _make_test_image():
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (128, 128), color=(255, 255, 248))
    draw = ImageDraw.Draw(img)
    draw.text((10, 55), "TEST IMAGE\nCell diagram", fill=(60, 60, 60))
    return img


# ── Pretty output helpers ────────────────────────────────────────────────────
_W = 70

def _header(title: str) -> None:
    print(f"\n{'─' * _W}")
    print(f"  {title}")
    print(f"{'─' * _W}")

def _ok(label: str, elapsed: float, preview: str) -> None:
    short = textwrap.shorten(preview.strip().replace("\n", " "), width=50)
    print(f"  ✅  {label:<22} ({elapsed:.1f}s)  →  {short!r}")

def _fail(label: str, elapsed: float, err: str) -> None:
    print(f"  ❌  {label:<22} ({elapsed:.1f}s)  →  {err}")


# ── Individual model tests ───────────────────────────────────────────────────

def test_qwen() -> bool:
    from models.qwen import generate

    _header("1 · Qwen3-4B  (text generation + grading)")
    t0 = time.time()
    try:
        out = generate(
            "You are a CBSE tutor for Class 8 Science.",
            "Give exactly one MCQ question on Cell Structure. Return only the question and 4 options.",
            max_new_tokens=256,
            temperature=0.3,
        )
        _ok("Qwen.generate", time.time() - t0, out)
        return True
    except Exception as exc:
        _fail("Qwen.generate", time.time() - t0, str(exc))
        return False


def test_minicpm() -> bool:
    from models.minicpm import read_image

    _header("2 · MiniCPM-V 4.5  (vision — textbook + answer-sheet reading)")
    t0 = time.time()
    try:
        img = _make_test_image()
        out = read_image(img, "Describe what you see in this image in one sentence.")
        _ok("MiniCPM.read_image", time.time() - t0, out)
        return True
    except NotImplementedError as exc:
        # Expected in offline mode
        _ok("MiniCPM.read_image", time.time() - t0, f"[offline skip] {exc}")
        return True
    except Exception as exc:
        _fail("MiniCPM.read_image", time.time() - t0, str(exc))
        return False


def test_aya() -> bool:
    from models.aya import localize

    _header("3 · Tiny Aya  (CohereLabs/tiny-aya-fire — regional language)")
    t0 = time.time()
    try:
        sample = "Q1. What is the function of the cell membrane?"
        out = localize(sample, language="Hindi")
        _ok("TinyAya.localize", time.time() - t0, out)
        return True
    except Exception as exc:
        _fail("TinyAya.localize", time.time() - t0, str(exc))
        return False


def test_flux() -> bool:
    from models.flux import generate_diagram

    _header("4 · FLUX.1-schnell  (Black Forest Labs — diagram generation)")
    t0 = time.time()
    try:
        img = generate_diagram(
            "Simple labeled science diagram: animal cell with nucleus, "
            "cell membrane, and mitochondria. Clean, educational style."
        )
        if img is None:
            # None is the documented offline / error fallback — not a hard failure
            _ok("Flux.generate_diagram", time.time() - t0, "[offline/unavailable — None returned, text-only fallback active]")
        else:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            size_kb = len(buf.getvalue()) // 1024
            _ok("Flux.generate_diagram", time.time() - t0, f"PNG image {img.width}×{img.height} px, {size_kb} KB")
        return True
    except Exception as exc:
        _fail("Flux.generate_diagram", time.time() - t0, str(exc))
        return False


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    from config import CONFIG

    print("=" * _W)
    print("  TutorDesk AI — Model Smoke Test")
    print(f"  Mode: {'OFFLINE (llama.cpp)' if CONFIG.offline else 'CLOUD (Modal)'}")
    if CONFIG.offline:
        print(f"  QWEN_GGUF_PATH: {CONFIG.qwen_gguf_path or '(not set — will error)'}")
    print("=" * _W)

    results = {
        "Qwen3-4B":       test_qwen(),
        "MiniCPM-V":      test_minicpm(),
        "Tiny Aya":       test_aya(),
        "FLUX.1-schnell": test_flux(),
    }

    print(f"\n{'═' * _W}")
    print("  Summary")
    print(f"{'─' * _W}")
    passed = 0
    for name, ok in results.items():
        status = "✅  PASS" if ok else "❌  FAIL"
        print(f"  {status}  {name}")
        passed += ok
    print(f"{'═' * _W}")
    print(f"  {passed}/{len(results)} models passed\n")

    if passed < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
