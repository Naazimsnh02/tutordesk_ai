"""Modal serving layer — all models run here as scale-to-zero GPU functions.

The HF Space (app.py) is a thin Gradio client; models/*.py call into these functions.
No external APIs → maximizes Modal usage and keeps Off-the-Grid in reach.
"""
