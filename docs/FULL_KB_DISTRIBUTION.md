# Full KB Distribution

## Goal

Keep the GitHub repository small while making the full AgentFigureGallery KB available through one command.

The user-facing install path should be:

```bash
git clone https://github.com/<org>/AgentFigureGallery.git
cd AgentFigureGallery
pip install -e .
agentfiguregallery setup --pack public-preview --manifest-url https://huggingface.co/datasets/<org>/AgentFigureGallery/resolve/main/resource_manifest.json
agentfiguregallery gallery --plot-type heatmap_matrix --limit 50 --serve
```

## Storage Split

### GitHub

Use GitHub for:

- package code
- frontend
- skill wrapper
- ExtendAgent instructions
- minimal Glike pack
- small examples
- docs

Do not use GitHub for the 20 GB development mirror.

### Hugging Face Dataset

Recommended default for large public resources:

- `public-preview`
- `source-scripts`
- `full-public`
- `resource_manifest.json`

Use a private Hugging Face Dataset only for the maintainer mirror:

- `full-private`

### Zenodo

Use Zenodo later for frozen DOI snapshots after v0.1 stabilizes.

## Pack Definitions

### `minimal`

Committed with the repo. Human-liked, private-path filtered, small enough for demos.

### `public-preview`

Normal public pack:

- `data/reference_candidate_index.json`
- `data/reference_candidate_facets.json`
- preview PNGs
- public source metadata
- no raw upstream `.git`
- no private-path candidates

### `source-scripts`

Sanitized code context for selected bundles:

- scripts and notebook excerpts only when license permits
- source repository metadata
- license metadata

### `full-public`

Public full KB:

- complete public candidate index
- complete public preview cache
- templates
- design cards
- ExtendAgent instructions
- source attribution

No private paths, no private repos, no raw local machine paths.

### `full-private`

Private maintainer mirror:

- can include full local state needed to resume expansion
- must live in private storage
- never referenced from public README as a default command

## Upload Contract

A published storage location must expose:

```text
resource_manifest.json
public-preview/...
source-scripts/...
full-public/...
```

The manifest is the only URL users need.

## Build Public Pack

From the development Drawing workspace:

```bash
python AgentFigureGallery/scripts/build_public_kb_pack.py \
  --source-root /path/to/Drawing \
  --release-root /path/to/Drawing/AgentFigureGallery \
  --pack full-public \
  --overwrite \
  --base-url https://huggingface.co/datasets/<org>/AgentFigureGallery/resolve/main
```

This writes:

- `assets/releases/full-public/full-public.tar.gz`
- `assets/releases/full-public/resource_manifest.fragment.json`

Run a private-path scan before uploading:

```bash
python scripts/check_private_paths.py --root AgentFigureGallery
```

## Upload Public Pack

Upload these to the selected storage backend:

```text
resource_manifest.json
full-public/full-public.tar.gz
public-preview/<archive-or-files>
source-scripts/<archive-or-files>
```

Do not put auth tokens into commands saved in shell scripts. Login interactively or use a short-lived environment variable outside the repository.

## One-Command Setup

The setup command:

```bash
agentfiguregallery setup --pack public-preview --manifest-url <manifest-url>
```

does three things:

1. Downloads the named pack.
2. Safely unpacks archive entries marked `unpack: true`.
3. Writes `.agentfiguregallery/config.json` with the active pack and manifest.

## Token Rule

Do not write GitHub or Hugging Face tokens into the repo, manifest, shell history, logs, or docs. Use interactive login or short-lived environment variables outside committed files.
