"""TutorDesk AI — custom Gradio 6 theme + CSS (Off-Brand badge).

In Gradio 6, theme= and css= are passed to demo.launch(), not gr.Blocks().
Usage in app.py:
    from frontend.theme import theme, CUSTOM_CSS
    demo.launch(theme=theme, css=CUSTOM_CSS)
"""
from __future__ import annotations

import gradio as gr

# ---------------------------------------------------------------------------
# Colour palette — warm saffron + forest green (Indian education aesthetic)
# ---------------------------------------------------------------------------
_SAFFRON      = "#F59E0B"   # amber-500
_DEEP_SAFFRON = "#D97706"   # amber-600
_DARK_AMBER   = "#92400E"   # amber-800
_GREEN        = "#059669"   # emerald-600
_CREAM        = "#FFFBEB"   # amber-50
_AMBER_100    = "#FEF3C7"
_AMBER_200    = "#FDE68A"
_WHITE        = "#FFFFFF"
_STONE_700    = "#44403C"

theme = gr.themes.Base(
    primary_hue=gr.themes.colors.amber,
    secondary_hue=gr.themes.colors.emerald,
    neutral_hue=gr.themes.colors.stone,
    font=[gr.themes.GoogleFont("Noto Sans"), "ui-sans-serif", "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("Noto Sans Mono"), "ui-monospace", "monospace"],
).set(
    # Page background
    body_background_fill=_CREAM,
    # Blocks / cards
    block_background_fill=_WHITE,
    block_border_color=_AMBER_200,
    block_border_width="1px",
    block_radius="10px",
    block_shadow="0 2px 8px rgba(245,158,11,0.10)",
    # Block titles & labels
    block_title_text_color=_DARK_AMBER,
    block_title_text_weight="700",
    block_label_background_fill=_AMBER_100,
    block_label_text_color=_DARK_AMBER,
    # Primary button — saffron
    button_primary_background_fill=_SAFFRON,
    button_primary_background_fill_hover=_DEEP_SAFFRON,
    button_primary_text_color=_WHITE,
    button_primary_border_color=_SAFFRON,
    button_primary_border_color_hover=_DEEP_SAFFRON,
    button_primary_text_color_hover=_WHITE,
    # Secondary button — subtle
    button_secondary_background_fill=_AMBER_100,
    button_secondary_background_fill_hover=_AMBER_200,
    button_secondary_text_color=_DARK_AMBER,
    # Inputs
    input_background_fill=_WHITE,
    input_border_color=_AMBER_200,
    input_border_color_focus=_SAFFRON,
    # Tabs
    checkbox_background_color=_SAFFRON,
    # Body text
    body_text_color=_STONE_700,
)

# ---------------------------------------------------------------------------
# Custom CSS — branding header, tab pills, footer
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
/* ── Branded header ─────────────────────────────────────────────────────── */
#td-header {
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 60%, #059669 100%);
    border-radius: 14px;
    padding: 28px 36px 22px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 4px 18px rgba(245,158,11,0.25);
}
#td-header h1 {
    color: #FFFFFF !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    margin: 0 0 6px 0;
}
#td-header p {
    color: rgba(255,255,255,0.90) !important;
    font-size: 1rem !important;
    margin: 0;
}

/* ── Tab pills ──────────────────────────────────────────────────────────── */
.tabs > .tab-nav {
    border-bottom: 2px solid #FDE68A !important;
    gap: 4px;
}
.tabs > .tab-nav button {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
    color: #78716C !important;
    padding: 8px 18px !important;
    transition: background 0.15s, color 0.15s;
}
.tabs > .tab-nav button.selected {
    background: #F59E0B !important;
    color: #FFFFFF !important;
    border-bottom: 2px solid #F59E0B !important;
}
.tabs > .tab-nav button:hover:not(.selected) {
    background: #FEF3C7 !important;
    color: #92400E !important;
}

/* ── Primary button ─────────────────────────────────────────────────────── */
.gr-button-primary {
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.2px;
    box-shadow: 0 2px 6px rgba(245,158,11,0.30) !important;
    transition: transform 0.1s, box-shadow 0.1s !important;
}
.gr-button-primary:active {
    transform: scale(0.98);
    box-shadow: 0 1px 3px rgba(245,158,11,0.20) !important;
}

/* ── File download area ─────────────────────────────────────────────────── */
.file-preview {
    border: 1.5px dashed #FDE68A !important;
    border-radius: 8px !important;
    background: #FFFBEB !important;
}

/* ── Footer ─────────────────────────────────────────────────────────────── */
#td-footer {
    text-align: center;
    color: #A8A29E;
    font-size: 0.80rem;
    margin-top: 28px;
    padding: 12px 0 4px;
    border-top: 1px solid #FDE68A;
}
"""
