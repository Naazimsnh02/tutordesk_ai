"""TutorDesk AI — Gradio Server entry point (Hugging Face Space).

The Space is a thin client: all heavy inference runs on Modal (serving/modal_app.py).
The UI is a fully custom single-page frontend (static/index.html) served by gr.Server
(FastAPI under the hood) — this claims the Off-Brand badge. Each of the 5 features posts
to its own JSON/multipart endpoint; generated PDFs are served back via /api/download/<token>.
"""
from __future__ import annotations

import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

import gradio as gr
from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from config import CONFIG
from models.aya import localize
from pipelines.auto_grade import grade_sheet
from pipelines.illustrated_worksheet import build_illustrated_pack
from pipelines.weekly_pack import build_pack
from pipelines.worksheet_from_textbook import from_image, from_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "static"

# ── Generated-PDF registry ──────────────────────────────────────────────────────
# Maps a short opaque token -> absolute file path of a generated PDF, so the
# frontend can request a download without exposing temp paths.
_PDF_REGISTRY: dict[str, str] = {}


def _register_pdf(path: str | None) -> dict[str, str] | None:
    """Register a generated PDF and return {token, url, name} for the frontend."""
    if not path or not os.path.exists(path):
        return None
    token = uuid.uuid4().hex
    _PDF_REGISTRY[token] = path
    return {"token": token, "url": f"/api/download/{token}", "name": Path(path).name}


# ── Gradio Server ───────────────────────────────────────────────────────────────

gr.set_static_paths(paths=["static/"])
app = gr.Server()


# ── Static + meta routes ────────────────────────────────────────────────────────

@app.get("/")
async def homepage():
    html = (_STATIC_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/api/health")
async def health():
    return JSONResponse({"status": "ok", "offline": CONFIG.offline})


@app.get("/api/config")
async def get_config():
    """Curriculum scope so the frontend dropdowns stay data-driven."""
    langs = list(CONFIG.languages)
    return JSONResponse({
        "classes": [str(c) for c in CONFIG.classes],
        "subjects": list(CONFIG.subjects),
        "languages": langs,
        "languages_non_en": [l for l in langs if l.lower() != "english"],
    })


# Gradio-client-compatible endpoint (satisfies Off-Brand + @gradio/client tooling)
@app.api(name="health_check")
def health_check() -> dict:
    return {"status": "ok", "offline": CONFIG.offline}


@app.get("/api/download/{token}")
async def download_pdf(token: str):
    path = _PDF_REGISTRY.get(token)
    if not path or not os.path.exists(path):
        return JSONResponse({"error": "File not found or expired."}, status_code=404)
    return FileResponse(path, media_type="application/pdf", filename=Path(path).name)


# ── Form helpers ────────────────────────────────────────────────────────────────

def _err(message: str, status: int = 200) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status)


async def _save_upload(upload, prefix: str) -> str:
    """Persist a Starlette UploadFile to a temp file and return its path."""
    suffix = Path(getattr(upload, "filename", "") or "").suffix.lower() or ".jpg"
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    with os.fdopen(fd, "wb") as fh:
        fh.write(await upload.read())
    return path


def _pack_payload(pack, pdf_path: str | None, **extra: Any) -> dict:
    payload = {
        "worksheet": pack.worksheet,
        "homework": pack.homework,
        "quiz": pack.quiz,
        "answer_key": pack.answer_key,
        "parent_note": pack.parent_note,
        "pdf": _register_pdf(pdf_path),
    }
    payload.update(extra)
    return payload


# ── Feature 2 — Weekly Teaching Pack ─────────────────────────────────────────────

@app.post("/api/weekly_pack")
async def api_weekly_pack(request: Request):
    data = await request.json()
    chapter_text = (data.get("chapter_text") or "").strip()
    if not chapter_text:
        return _err("Please enter chapter content, or use the Textbook Scan tab to upload a photo.")
    try:
        pack = build_pack(
            chapter_text,
            grade=int(data.get("grade", 8)),
            subject=data.get("subject", "Science"),
            question_count=int(data.get("question_count", 20)),
            diff=data.get("difficulty", "Medium"),
            language=data.get("language", "English"),
        )
        pdf_path = pack.to_pdf(
            grade=int(data.get("grade", 8)),
            subject=data.get("subject", "Science"),
            chapter=chapter_text[:60],
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("weekly_pack failed")
        return _err(str(exc))
    return JSONResponse(_pack_payload(pack, pdf_path))


# ── Feature 1 — Worksheet-from-Textbook ──────────────────────────────────────────

@app.post("/api/textbook")
async def api_textbook(request: Request):
    form = await request.form()
    photo = form.get("photo")
    pdf_file = form.get("pdf")
    has_photo = photo is not None and hasattr(photo, "read")
    has_pdf = pdf_file is not None and hasattr(pdf_file, "read")
    if not has_photo and not has_pdf:
        return _err("Please upload a textbook photo or PDF.")

    grade = int(form.get("grade", 8))
    subject = form.get("subject", "Science")
    kwargs = dict(
        grade=grade,
        subject=subject,
        question_count=int(form.get("question_count", 20)),
        diff=form.get("difficulty", "Medium"),
        language=form.get("language", "English"),
    )

    tmp_path = None
    try:
        if has_photo:
            from PIL import Image as PILImage
            tmp_path = await _save_upload(photo, "td_tb_")
            img = PILImage.open(tmp_path).convert("RGB")
            pack = from_image(img, **kwargs)
        else:
            tmp_path = await _save_upload(pdf_file, "td_tb_")
            pack = from_pdf(tmp_path, **kwargs)
        pdf_path = pack.to_pdf(grade=grade, subject=subject, chapter="Textbook upload")
    except Exception as exc:  # noqa: BLE001
        logger.exception("textbook failed")
        return _err(str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    return JSONResponse(_pack_payload(pack, pdf_path))


# ── Feature 5 — Photo Auto-Grading ───────────────────────────────────────────────

@app.post("/api/auto_grade")
async def api_auto_grade(request: Request):
    form = await request.form()
    photo = form.get("photo")
    if photo is None or not hasattr(photo, "read"):
        return _err("Please upload a photo of the student's answer sheet.")
    marking_scheme = (form.get("marking_scheme") or "").strip()
    if not marking_scheme:
        return _err("Please enter the marking scheme using the Q[N marks] template.")

    tmp_path = None
    try:
        from PIL import Image as PILImage
        tmp_path = await _save_upload(photo, "td_ag_")
        img = PILImage.open(tmp_path).convert("RGB")
        result = grade_sheet(
            img,
            marking_scheme=marking_scheme,
            grade=int(form.get("grade", 8)),
            subject=form.get("subject", "Science"),
            student=(form.get("student") or "Student").strip() or "Student",
        )
        pdf_path = result.to_pdf()
    except Exception as exc:  # noqa: BLE001
        logger.exception("auto_grade failed")
        return _err(str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    return JSONResponse({
        "summary": result.summary_markdown(),
        "parent_note": result.parent_note,
        "percentage": result.percentage(),
        "total_awarded": result.total_awarded,
        "total_marks": result.total_marks,
        "pdf": _register_pdf(pdf_path),
    })


# ── Feature 3 — Regional Language (Tiny Aya) ─────────────────────────────────────

@app.post("/api/translate")
async def api_translate(request: Request):
    data = await request.json()
    content = (data.get("content") or "").strip()
    language = data.get("language", "Hindi")
    if not content:
        return _err("Please paste some content to translate.")
    try:
        if language.lower() == "english":
            translated = content
            pdf = None
        else:
            translated = localize(content, language=language)
            from utils.pdf import to_pdf as _to_pdf
            pdf_path = _to_pdf(
                title=f"TutorDesk AI — {language} Output",
                subtitle="Translated by Tiny Aya (CohereLabs/tiny-aya-fire)",
                body=translated,
            )
            pdf = _register_pdf(pdf_path)
    except Exception as exc:  # noqa: BLE001
        logger.exception("translate failed")
        return _err(str(exc))
    return JSONResponse({"translated": translated, "pdf": pdf})


# ── Feature 4 — Illustrated Worksheets (FLUX.1-schnell) ──────────────────────────

@app.post("/api/illustrated")
async def api_illustrated(request: Request):
    data = await request.json()
    chapter_text = (data.get("chapter_text") or "").strip()
    if not chapter_text:
        return _err("Please enter chapter content.")
    try:
        result = build_illustrated_pack(
            chapter_text,
            grade=int(data.get("grade", 8)),
            subject=data.get("subject", "Science"),
            question_count=int(data.get("question_count", 20)),
            diff=data.get("difficulty", "Medium"),
            language=data.get("language", "English"),
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("illustrated failed")
        return _err(str(exc))

    n = result.diagram_count
    diagram_status = (
        f"{n} diagram(s) generated and embedded in the PDF."
        if n > 0
        else "No diagrams generated (FLUX unavailable or offline — text-only PDF)."
    )
    return JSONResponse(_pack_payload(
        result.pack, result.pdf_path, diagram_status=diagram_status, diagram_count=n,
    ))


# ── Launch ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.launch(show_error=True)
