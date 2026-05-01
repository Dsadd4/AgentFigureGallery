# Release Checklist

## Before Public Push

- Rename public product to `AgentFigureGallery`.
- Initialize a clean git repository from this release folder, not from the 22 GB development workspace.
- Remove all private absolute paths, local tokens, and scratch outputs.
- Add a real license.
- Add third-party source attribution and license metadata.
- Provide a tiny `minimal` pack for CI.
- Provide a larger `public-preview` pack through release assets or Hugging Face Datasets.
- Make one command start the local gallery after assets are downloaded.

## Minimal v0.1 Acceptance Test

The following should work on a new machine:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python scripts/download_assets.py --pack minimal
agentfiguregallery gallery --plot-type bar_chart --limit 20 --serve
agentfiguregallery bundle --session outputs/reference_sessions/<id>
```

Success means:

- the browser shows visible candidates
- like/reject/select updates persist
- global reject hides future candidates
- bundle export includes stable candidate IDs and code references

