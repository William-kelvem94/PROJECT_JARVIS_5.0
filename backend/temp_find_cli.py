from pathlib import Path
path = Path('venv/Lib/site-packages/livekit/agents/cli/cli.py')
text = path.read_text(encoding='utf-8')
for i, line in enumerate(text.splitlines(), 1):
    if 'def run_app' in line or 'def _build_cli' in line or 'typer.Typer' in line or 'Typer(' in line or 'AgentServer.from_server_options' in line or 'run_app(server' in line:
        print(i, line)
