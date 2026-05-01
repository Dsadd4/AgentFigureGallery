# Remote Preview

This is the current lightweight preview deployment pattern before the public GitHub repository exists.

## Sync

```bash
rsync -az --delete \
  --exclude 'outputs/' \
  --exclude '__pycache__/' \
  --exclude '.DS_Store' \
  AgentFigureGallery/ 1.94.40.82:/root/AgentFigureGallery/
```

## Start On Remote

```bash
cd /root/AgentFigureGallery
mkdir -p outputs/server_logs
nohup env PYTHONPATH=/root/AgentFigureGallery PYTHONDONTWRITEBYTECODE=1 \
  python3 -m agentfiguregallery.cli serve --host 0.0.0.0 --port 8876 \
  > outputs/server_logs/server_8876.log 2>&1 &
echo $! > outputs/server.pid
```

## Local Tunnel

If the cloud security group does not expose port `8876`, use:

```bash
ssh -N -L 8877:127.0.0.1:8876 1.94.40.82
```

Then open:

```text
http://127.0.0.1:8877/
```

