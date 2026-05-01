# Remote Full KB Validation

Date: 2026-05-01

Release commit: `2a530c8`

Release assets: `full-public-v0.1.0`

Validation host: `1.94.40.82`

Clean validation directory:

```text
/root/afg_verify_full_public_20260501_142004
```

## Result

The full public KB is functionally valid on the remote server:

- Python package editable install passed.
- `py_compile` passed for package and scripts.
- Private-path scan passed with `0 hits`.
- `setup --pack full-public --manifest manifests/resource_manifest.github-api.json --dry-run` resolved all 11 release entries.
- Full archive checksum/extract path passed after staging the same release archives into the validation directory.
- `.agentfiguregallery/config.json` was written for `full-public`.
- `data/reference_candidate_index.json` contains 16,341 selectable candidates.
- `agentfiguregallery gallery --plot-type heatmap_matrix --limit 50 --strategy top` generated a 50-candidate session.
- `agentfiguregallery serve --host 0.0.0.0 --port 8896` returned the gallery HTML from `http://127.0.0.1:8896/`.

## Candidate Counts

| Plot type | Candidates |
| --- | ---: |
| `bar_chart` | 1,516 |
| `benchmark_performance` | 2,310 |
| `box_violin_distribution` | 1,026 |
| `embedding_plot` | 1,273 |
| `heatmap_matrix` | 1,122 |
| `line_chart` | 1,035 |
| `microscopy_panel` | 1,756 |
| `multi_panel_figure` | 4,148 |
| `scatter_plot` | 1,489 |
| `spatial_map` | 666 |
| **Total** | **16,341** |

## Network Caveat

The server can reach the GitHub Release API and GitHub release object storage, but the full remote download path is too slow on this host for a good public quickstart.

Observed checks:

- GitHub Release API asset endpoint returned a redirect to release object storage.
- Object storage supported range requests.
- A 1 MiB range download from the remote server completed at about 32 KB/s.
- At that speed the 1.87 GB full-public pack would take many hours.

For promotion, keep Hugging Face as the primary public manifest and GitHub Release assets as a compatibility mirror, but add a faster mirror for China/Huawei Cloud style deployments before advertising full-public as a frictionless one-command install there.

## Commands

Primary public setup:

```bash
agentfiguregallery setup --pack full-public --manifest-url https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json
```

GitHub Release fallback:

```bash
agentfiguregallery setup --pack full-public --manifest manifests/resource_manifest.github-api.json
```

Remote validation query:

```bash
python3 -m agentfiguregallery.cli query --plot-type heatmap_matrix --json
```

Remote validation serve:

```bash
python3 -m agentfiguregallery.cli serve --host 0.0.0.0 --port 8896
```
