"""LoRA fine-tune Qwen3-4B on Modal (claims Modal + Well-Tuned + Tiny Titan).

Flow:
  1. Run the three data-prep scripts to produce data/processed/*.jsonl
  2. Run this script:   modal run finetune/train_modal.py
     - Uploads the three JSONL files to a Modal Volume
     - Launches LoRA SFT on an A10G (~45-60 min for ~5k examples, 3 epochs)
     - Merges the adapter and pushes the full model to HF Hub
  3. Set QWEN_FINETUNED_MODEL in .env to the published repo, then redeploy Modal

Prerequisites in .env:
  HF_TOKEN      — HF write token
  HF_USERNAME   — your HF username (repo will be {HF_USERNAME}/tutordesk-qwen3-4b)
"""
from __future__ import annotations

import pathlib

import modal

_ROOT = pathlib.Path(__file__).parent.parent

app = modal.App("tutordesk-finetune")

vol = modal.Volume.from_name("tutordesk-training-data", create_if_missing=True)

_hf_secret = modal.Secret.from_dotenv(path=str(_ROOT))

_train_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "transformers>=4.44,<5.0",
        "torch>=2.3",
        "accelerate>=0.33",
        "peft>=0.12",
        "trl>=0.10",
        "datasets>=2.20",
        "bitsandbytes>=0.43",
        "sentencepiece",
        "huggingface_hub>=0.24",
    )
)

_DATA_DIR = "/training-data"
_OUT_DIR  = "/training-data/output"
_BASE_MODEL = "Qwen/Qwen3-4B"


@app.cls(
    gpu="A10G",
    image=_train_image,
    secrets=[_hf_secret],
    volumes={_DATA_DIR: vol},
    timeout=7200,
)
class Trainer:
    @modal.method()
    def train(self, hf_repo: str) -> str:
        import json
        import os

        import torch
        from datasets import Dataset
        from peft import LoraConfig as PeftLoraConfig
        from peft import TaskType, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from trl import SFTTrainer

        # ── Load all JSONL files from the volume ──────────────────────────────
        records: list[dict] = []
        for fname in ("generation.jsonl", "difficulty.jsonl", "grading.jsonl"):
            fpath = os.path.join(_DATA_DIR, fname)
            if not os.path.exists(fpath):
                print(f"  WARNING: {fname} not found in volume — skipping")
                continue
            count = 0
            with open(fpath, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
                        count += 1
            print(f"  Loaded {count} examples from {fname}")

        if not records:
            raise RuntimeError("No training data found in volume. Run data prep scripts first.")

        print(f"Total training examples: {len(records)}")

        # ── Tokenizer + base model ─────────────────────────────────────────────
        print(f"Loading base model: {_BASE_MODEL}")
        tokenizer = AutoTokenizer.from_pretrained(_BASE_MODEL, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            _BASE_MODEL,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        model.enable_input_require_grads()

        # ── LoRA adapter ──────────────────────────────────────────────────────
        lora_cfg = PeftLoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        model = get_peft_model(model, lora_cfg)
        model.print_trainable_parameters()

        # ── Format examples with Qwen3 chat template ──────────────────────────
        def fmt(ex: dict) -> str:
            return tokenizer.apply_chat_template(
                ex["messages"],
                tokenize=False,
                add_generation_prompt=False,
                enable_thinking=False,
            )

        texts = [fmt(r) for r in records]
        ds = Dataset.from_dict({"text": texts})
        print(f"Dataset size after formatting: {len(ds)}")

        # ── Training ──────────────────────────────────────────────────────────
        os.makedirs(_OUT_DIR, exist_ok=True)
        args = TrainingArguments(
            output_dir=_OUT_DIR,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            lr_scheduler_type="cosine",
            warmup_ratio=0.05,
            fp16=True,
            logging_steps=50,
            save_strategy="epoch",
            save_total_limit=1,
            report_to="none",
            dataloader_num_workers=0,
        )

        trainer = SFTTrainer(
            model=model,
            args=args,
            train_dataset=ds,
            dataset_text_field="text",
            max_seq_length=2048,
            tokenizer=tokenizer,
        )

        print("Starting training...")
        trainer.train()
        print("Training complete.")

        # ── Merge adapter + push to HF Hub ────────────────────────────────────
        print(f"Merging LoRA adapter...")
        merged = model.merge_and_unload()

        hf_token = os.environ["HF_TOKEN"]
        print(f"Pushing merged model to {hf_repo} ...")
        merged.push_to_hub(hf_repo, token=hf_token, private=False)
        tokenizer.push_to_hub(hf_repo, token=hf_token, private=False)

        print(f"Published: https://huggingface.co/{hf_repo}")
        return hf_repo


@app.local_entrypoint()
def main() -> None:
    import os
    import sys
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(dotenv_path=str(_ROOT / ".env"))

    hf_username = os.getenv("HF_USERNAME", "").strip()
    if not hf_username:
        print("ERROR: HF_USERNAME is not set in .env")
        print("  Add:  HF_USERNAME=your-huggingface-username")
        sys.exit(1)

    hf_repo = f"{hf_username}/tutordesk-qwen3-4b"

    # ── Check data files ─────────────────────────────────────────────────────
    data_files = [
        _ROOT / "data" / "processed" / "generation.jsonl",
        _ROOT / "data" / "processed" / "difficulty.jsonl",
        _ROOT / "data" / "processed" / "grading.jsonl",
    ]
    missing = [str(f) for f in data_files if not f.exists()]
    if missing:
        print("Missing data files (run data prep first):")
        for m in missing:
            print(f"  {m}")
        print("\nCommands:")
        print("  python -m data.prep_generation")
        print("  python -m data.prep_difficulty")
        print("  python -m data.prep_grading")
        sys.exit(1)

    # ── Upload to Modal Volume ────────────────────────────────────────────────
    print("Uploading training data to Modal Volume 'tutordesk-training-data'...")
    with vol.batch_upload() as batch:
        for fpath in data_files:
            batch.put_file(str(fpath), fpath.name)
            size_kb = fpath.stat().st_size // 1024
            print(f"  {fpath.name}  ({size_kb} KB)")
    print("Upload complete.")

    # ── Launch training ──────────────────────────────────────────────────────
    print(f"\nLaunching LoRA fine-tune → target repo: {hf_repo}")
    print("(This takes ~45-60 min on A10G. The Modal dashboard shows live logs.)\n")

    repo = Trainer().train.remote(hf_repo)

    # ── Post-training instructions ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Fine-tune complete: https://huggingface.co/{repo}")
    print("=" * 60)
    print("\nNext steps:")
    print(f"  1. Add to .env:  QWEN_FINETUNED_MODEL={repo}")
    print("  2. modal deploy serving/modal_app.py")
    print("  The Qwen class in serving/modal_app.py reads QWEN_FINETUNED_MODEL")
    print("  from the Modal secret and automatically switches to the fine-tuned model.")
