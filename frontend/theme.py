"""TutorDesk AI — custom Gradio 6 theme + CSS (Off-Brand badge, dark mode)."""
from __future__ import annotations

import gradio as gr

# Dark amber palette
_BG_BASE    = "#0F0D09"   # page / deepest dark
_BG_CARD    = "#1C1814"   # card surfaces
_BG_INPUT   = "#141210"   # input fields
_BORDER     = "#3A3020"   # default border
_BORDER_DIM = "#2A2218"   # dim border
_SAFFRON    = "#F59E0B"   # primary accent
_DEEP_SAFF  = "#D97706"   # saffron hover
_AMBER_LBL  = "#FCD34D"   # amber-300 — labels on dark bg
_GREEN      = "#059669"   # secondary accent
_TEXT_MAIN  = "#E7E5E0"   # body text
_TEXT_MID   = "#C8B890"   # secondary text
_TEXT_MUTED = "#8A7A5C"   # muted text
_TEXT_DIM   = "#5C5040"   # very muted
_WHITE      = "#FFFFFF"

theme = gr.themes.Base(
    primary_hue=gr.themes.colors.amber,
    secondary_hue=gr.themes.colors.emerald,
    neutral_hue=gr.themes.colors.stone,
    font=[
        gr.themes.GoogleFont("Plus Jakarta Sans"),
        gr.themes.GoogleFont("Noto Sans"),
        "ui-sans-serif", "system-ui", "sans-serif",
    ],
    font_mono=[gr.themes.GoogleFont("Noto Sans Mono"), "ui-monospace", "monospace"],
).set(
    body_background_fill=_BG_BASE,
    block_background_fill=_BG_CARD,
    block_border_color=_BORDER,
    block_border_width="1px",
    block_radius="10px",
    block_shadow="0 2px 12px rgba(0,0,0,0.40)",
    block_title_text_color=_AMBER_LBL,
    block_title_text_weight="700",
    block_label_background_fill=_BG_INPUT,
    block_label_text_color=_AMBER_LBL,
    button_primary_background_fill=_SAFFRON,
    button_primary_background_fill_hover=_DEEP_SAFF,
    button_primary_text_color=_WHITE,
    button_primary_border_color="transparent",
    button_primary_border_color_hover="transparent",
    button_primary_text_color_hover=_WHITE,
    button_secondary_background_fill=_BORDER_DIM,
    button_secondary_background_fill_hover=_BORDER,
    button_secondary_text_color=_AMBER_LBL,
    input_background_fill=_BG_INPUT,
    input_border_color=_BORDER,
    input_border_color_focus=_SAFFRON,
    input_border_width="1.5px",
    input_shadow_focus="0 0 0 3px rgba(245,158,11,0.18)",
    body_text_color=_TEXT_MAIN,
    body_text_size="14px",
    checkbox_background_color=_SAFFRON,
    slider_color=_SAFFRON,
)

CUSTOM_CSS = """
/* ── Reset & base ────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box !important; }

body {
    background: #0F0D09 !important;
    color: #E7E5E0 !important;
    font-family: 'Plus Jakarta Sans', 'Noto Sans', system-ui, sans-serif !important;
}

.gradio-container {
    background: #0F0D09 !important;
    max-width: 100% !important;
    padding: 16px 24px !important;
}

/* ── Branded header ─────────────────────────────────────────────────────── */
#td-header {
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 55%, #059669 100%);
    border-radius: 18px;
    padding: 34px 48px 28px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 8px 40px rgba(245,158,11,0.22), 0 2px 16px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
}
#td-header::before {
    content: '';
    position: absolute; top: -50px; right: -50px;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(255,255,255,0.07);
    pointer-events: none;
}
#td-header::after {
    content: '';
    position: absolute; bottom: -70px; left: -40px;
    width: 240px; height: 240px; border-radius: 50%;
    background: rgba(255,255,255,0.05);
    pointer-events: none;
}
#td-header .td-icon {
    font-size: 2.8rem; display: block;
    margin-bottom: 8px; line-height: 1;
    position: relative; z-index: 1;
}
#td-header h1 {
    color: #FFFFFF !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -1.5px !important;
    margin: 0 0 8px 0 !important;
    text-shadow: 0 2px 12px rgba(0,0,0,0.2) !important;
    line-height: 1.1 !important;
    position: relative; z-index: 1;
}
#td-header .td-tagline {
    color: rgba(255,255,255,0.90);
    font-size: 0.98rem;
    margin: 0 0 18px 0;
    font-weight: 500;
    position: relative; z-index: 1;
}
#td-header .td-badges {
    display: flex; justify-content: center;
    gap: 8px; flex-wrap: wrap;
    position: relative; z-index: 1;
}
#td-header .td-badge {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.28);
    color: #FFFFFF;
    border-radius: 100px;
    padding: 4px 13px;
    font-size: 0.77rem; font-weight: 600; letter-spacing: 0.2px;
}

/* ── Top-level feature tabs ─────────────────────────────────────────────── */
.tabs > .tab-nav {
    background: #1C1814 !important;
    border-radius: 12px 12px 0 0 !important;
    border-bottom: 2px solid #3A3020 !important;
    padding: 6px 6px 0 !important;
    gap: 4px !important;
    overflow-x: auto !important;
}
.tabs > .tab-nav button {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    color: #8A7A5C !important;
    padding: 10px 18px !important;
    transition: all 0.16s ease !important;
    border: none !important;
    background: transparent !important;
    white-space: nowrap !important;
}
.tabs > .tab-nav button.selected {
    background: linear-gradient(135deg, #F59E0B, #D97706) !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 10px rgba(245,158,11,0.35) !important;
}
.tabs > .tab-nav button:hover:not(.selected) {
    background: #2A2218 !important;
    color: #FCD34D !important;
}

/* ── Inner / output tabs ────────────────────────────────────────────────── */
.tabs .tabs > .tab-nav {
    background: #161210 !important;
    border-radius: 8px 8px 0 0 !important;
    border-bottom: 2px solid #3A3020 !important;
    padding: 4px 4px 0 !important;
}
.tabs .tabs > .tab-nav button {
    font-size: 0.80rem !important;
    padding: 7px 13px !important;
    color: #8A7A5C !important;
    border-radius: 6px 6px 0 0 !important;
    font-weight: 500 !important;
}
.tabs .tabs > .tab-nav button.selected {
    background: #1C1814 !important;
    color: #FCD34D !important;
    border-bottom: 2px solid #F59E0B !important;
    box-shadow: none !important;
}
.tabs .tabs > .tab-nav button:hover:not(.selected) {
    background: #2A2218 !important;
    color: #FCD34D !important;
}

/* ── Feature info banner ────────────────────────────────────────────────── */
.feature-banner {
    background: #1C1814;
    border: 1px solid #3A3020;
    border-left: 4px solid #F59E0B;
    border-radius: 10px;
    padding: 11px 16px;
    margin-bottom: 14px;
    font-size: 0.84rem;
    color: #C8B890;
    line-height: 1.65;
}
.feature-banner strong { color: #FCD34D; }

/* ── Row containing settings + content columns ───────────────────────────── */
.td-main-row {
    display: flex !important;
    width: 100% !important;
    gap: 14px !important;
    align-items: flex-start !important;
}
.td-main-row > * { min-width: 0 !important; }

/* ── Settings sidebar card ───────────────────────────────────────────────── */
.settings-panel {
    background: #181510 !important;
    border: 1px solid #3A3020 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 14px rgba(0,0,0,0.4) !important;
    min-width: 0 !important;
}
.settings-panel .block {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding-left: 14px !important;
    padding-right: 14px !important;
    margin-bottom: 0 !important;
}
.settings-panel .block:first-child { padding-top: 14px !important; }
.settings-panel .block:last-child  { padding-bottom: 14px !important; }

/* ── Content input card ──────────────────────────────────────────────────── */
.content-panel {
    background: #141210 !important;
    border: 1px solid #2E2818 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3) !important;
    min-width: 0 !important;
}
.content-panel .block {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 14px !important;
}

/* ── All blocks ──────────────────────────────────────────────────────────── */
.block {
    background: #1C1814 !important;
    border-color: #3A3020 !important;
}

/* ── Component labels ───────────────────────────────────────────────────── */
.label-wrap span,
.block-label span {
    font-weight: 600 !important;
    font-size: 0.74rem !important;
    color: #FCD34D !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* ── Text inputs & textareas ────────────────────────────────────────────── */
input[type="text"],
input[type="number"],
input[type="email"],
input[type="search"],
textarea {
    background: #141210 !important;
    border: 1.5px solid #3A3020 !important;
    border-radius: 8px !important;
    color: #E7E5E0 !important;
    font-size: 0.89rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
input::placeholder, textarea::placeholder { color: #5C5040 !important; }
input:focus, textarea:focus {
    border-color: #F59E0B !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.14) !important;
    outline: none !important;
}

/* ── Dropdowns ──────────────────────────────────────────────────────────── */
.wrap .wrap-inner {
    background: #141210 !important;
    border: 1.5px solid #3A3020 !important;
    border-radius: 8px !important;
    color: #E7E5E0 !important;
    min-height: 36px !important;
    transition: border-color 0.15s !important;
}
.wrap .wrap-inner:focus-within {
    border-color: #F59E0B !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.14) !important;
}
.options {
    background: #1C1814 !important;
    border: 1.5px solid #3A3020 !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.55) !important;
    overflow: hidden !important;
    margin-top: 4px !important;
}
.options > * {
    font-size: 0.86rem !important;
    padding: 9px 13px !important;
    color: #C8B890 !important;
    cursor: pointer;
}
.options > *.selected, .options > *:hover {
    background: #2A2218 !important;
    color: #FCD34D !important;
}

/* ── Slider ─────────────────────────────────────────────────────────────── */
input[type="range"] { accent-color: #F59E0B !important; }
output {
    background: #2A2218 !important;
    color: #FCD34D !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    padding: 2px 9px !important;
    border: 1px solid #3A3020 !important;
}

/* ── Radio pill buttons ─────────────────────────────────────────────────── */
.radio-group .wrap {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
}
.radio-group label {
    border: 1.5px solid #3A3020 !important;
    border-radius: 100px !important;
    padding: 5px 16px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    background: #1C1814 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #C8B890 !important;
    margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    white-space: nowrap !important;
}
.radio-group label.selected {
    border-color: #F59E0B !important;
    background: linear-gradient(135deg, #F59E0B, #D97706) !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 10px rgba(245,158,11,0.28) !important;
}
.radio-group label:hover:not(.selected) {
    border-color: #D97706 !important;
    background: #2A2218 !important;
    color: #FCD34D !important;
}
.radio-group input[type="radio"] {
    width: 0 !important; height: 0 !important;
    opacity: 0 !important; position: absolute !important;
}

/* ── Image upload zone ──────────────────────────────────────────────────── */
.image-container > div,
.upload-container {
    border: 2px dashed #3A3020 !important;
    border-radius: 10px !important;
    background: #141210 !important;
    transition: all 0.18s ease !important;
}
.image-container > div:hover,
.upload-container:hover {
    border-color: #F59E0B !important;
    background: #1C1814 !important;
}

/* ── File upload / download ─────────────────────────────────────────────── */
.file-preview {
    border: 2px dashed #3A3020 !important;
    border-radius: 10px !important;
    background: #141210 !important;
    color: #C8B890 !important;
}
.td-pdf-download .file-preview,
.td-pdf-download > div {
    border: 2px dashed #1E4A38 !important;
    border-radius: 10px !important;
    background: #0C1C14 !important;
}
.td-pdf-download .label-wrap span { color: #34D399 !important; }

/* ── Primary buttons ────────────────────────────────────────────────────── */
button.primary,
button[class*="primary"] {
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.93rem !important;
    letter-spacing: 0.2px !important;
    padding: 12px 28px !important;
    box-shadow: 0 4px 16px rgba(245,158,11,0.28), 0 1px 4px rgba(0,0,0,0.4) !important;
    transition: all 0.18s ease !important;
    width: 100% !important;
    cursor: pointer !important;
}
button.primary:hover,
button[class*="primary"]:hover {
    background: linear-gradient(135deg, #D97706, #B45309) !important;
    box-shadow: 0 6px 20px rgba(245,158,11,0.38) !important;
    transform: translateY(-1px) !important;
}
button.primary:active,
button[class*="primary"]:active {
    transform: translateY(0) scale(0.98) !important;
    box-shadow: 0 2px 8px rgba(245,158,11,0.20) !important;
}

/* ── Markdown output panels ─────────────────────────────────────────────── */
.output-markdown {
    background: #141210 !important;
    border: 1.5px solid #2E2818 !important;
    border-radius: 10px !important;
    min-height: 120px !important;
}
.output-markdown .prose,
.output-markdown > div {
    padding: 14px 16px !important;
    line-height: 1.82 !important;
    color: #E7E5E0 !important;
}
.output-markdown h1,
.output-markdown h2,
.output-markdown h3 {
    color: #FCD34D !important;
    border-bottom: 1px solid #3A3020 !important;
    padding-bottom: 6px !important;
    margin-bottom: 12px !important;
}
.output-markdown code {
    background: #2A2218 !important;
    color: #FCD34D !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
    font-size: 0.84em !important;
}
.output-markdown blockquote {
    border-left: 3px solid #F59E0B !important;
    background: #1C1814 !important;
    padding: 8px 14px !important;
    border-radius: 0 6px 6px 0 !important;
    margin: 8px 0 !important;
}

/* ── Grade summary (green accent) ───────────────────────────────────────── */
#ag-summary {
    background: #0C1C14 !important;
    border: 1.5px solid #1E4A38 !important;
    border-left: 4px solid #059669 !important;
    border-radius: 10px !important;
}
#ag-summary h1, #ag-summary h2, #ag-summary h3 {
    color: #34D399 !important;
    border-bottom-color: #1E4A38 !important;
}

/* ── Read-only / status textboxes ────────────────────────────────────────── */
#ag-note textarea,
#il-status textarea {
    background: #0F0D09 !important;
    border-color: #2E2818 !important;
    color: #8A7A5C !important;
    font-size: 0.84rem !important;
    font-style: italic !important;
}
#rl-out textarea {
    background: #0C1812 !important;
    border-color: #1E4A38 !important;
    color: #D1FAE5 !important;
    font-style: normal !important;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
.td-divider {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(to right, transparent, #3A3020, transparent) !important;
    margin: 14px 0 !important;
}

/* ── Output section label ────────────────────────────────────────────────── */
.td-output-label {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 12px 0 8px;
    font-weight: 700;
    font-size: 0.70rem;
    color: #5C5040;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.td-output-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #3A3020, transparent);
}

/* ── Scrollbars ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0F0D09; }
::-webkit-scrollbar-thumb { background: #3A3020; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #F59E0B; }

/* ── Footer ─────────────────────────────────────────────────────────────── */
#td-footer {
    text-align: center;
    margin-top: 28px;
    padding: 18px 0 8px;
    border-top: 1px solid #3A3020;
}
#td-footer .td-footer-badges {
    display: flex; justify-content: center;
    gap: 8px; flex-wrap: wrap;
    margin-bottom: 10px;
}
#td-footer .td-footer-badge {
    background: #1C1814;
    border: 1px solid #3A3020;
    color: #8A7A5C;
    border-radius: 100px;
    padding: 3px 12px;
    font-size: 0.73rem; font-weight: 600;
}
#td-footer .td-footer-text {
    color: #5C5040;
    font-size: 0.77rem;
    line-height: 1.8;
}
#td-footer a { color: #D97706 !important; text-decoration: none !important; font-weight: 600 !important; }
#td-footer a:hover { color: #F59E0B !important; }

/* ── Hide Gradio's built-in footer bar ───────────────────────────────────── */
footer { display: none !important; }

/* ── Responsive ─────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    #td-header { padding: 24px 16px 20px; border-radius: 12px; }
    #td-header h1 { font-size: 1.8rem !important; }
    .gradio-container { padding: 8px !important; }
    .tabs > .tab-nav button { padding: 8px 10px !important; font-size: 0.78rem !important; }
    .td-main-row { flex-direction: column !important; }
}
"""
