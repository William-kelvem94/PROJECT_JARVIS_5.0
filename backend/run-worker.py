import sys
sys.path.insert(0, '.')
from livekit.agents import cli
from app.agents import entrypoint
cli.run_app(WorkerOptions(entrypoint=entrypoint))
print("Worker rodando! Agent pronto para rooms.")
