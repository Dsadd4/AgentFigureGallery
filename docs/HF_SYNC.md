# Hugging Face Sync

Use Hugging Face as the primary public full-KB distribution channel and GitHub Releases as the fallback mirror.

## Dataset Card Only

Dry run:

```bash
python scripts/upload_full_public_to_hf.py --card-only --dry-run
```

Real sync:

```bash
export HF_TOKEN="your_huggingface_write_token"
python scripts/upload_full_public_to_hf.py --card-only
```

## Full Public Pack

The full upload expects release archives under `assets/releases/full-public/` and the manifest at `manifests/resource_manifest.json`.

```bash
export HF_TOKEN="your_huggingface_write_token"
python scripts/upload_full_public_to_hf.py --skip-existing
```

## User Install Command

```bash
agentfiguregallery setup --pack full-public --manifest-url https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json
```

Keep `docs/HF_DATASET_CARD.md` as the source of truth for the remote dataset README.
