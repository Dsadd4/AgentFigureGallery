# Hugging Face Space

`spaces/agentfiguregallery-static` is the deployable no-install preview for AgentFigureGallery.

The Space uses Hugging Face `sdk: static`: no Python runtime, no full public pack download, and no server state. It is meant to help visitors understand the workflow before installing the CLI.

Live Space:

- Hub page: https://huggingface.co/spaces/dsadd4/AgentFigureGallery
- Static app: https://dsadd4-agentfiguregallery.static.hf.space/index.html

## Local Preview

```bash
cd spaces/agentfiguregallery-static
python -m http.server 8899
```

Open `http://127.0.0.1:8899`.

## Update Deploy

Create the Space once if it does not exist:

```bash
hf repos create dsadd4/AgentFigureGallery --type space --space-sdk static --exist-ok
```

Upload the static directory:

```bash
hf upload dsadd4/AgentFigureGallery spaces/agentfiguregallery-static --type space --commit-message "Update static AgentFigureGallery showcase"
```

Use `HF_TOKEN` or `hf auth login` before deploying.

## Included Assets

- `assets/agentfiguregallery-social-preview.png`
- `assets/agentfiguregallery-demo.gif`
- `assets/agentfiguregallery-scale-overview.png`
- four representative plot-type previews under `assets/examples/`

Regenerate the source assets from the main repository scripts before copying them into the Space directory.
