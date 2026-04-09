from livekit.agents import cli, WorkerOptions
import inspect
print('cli', cli)
print('has run_app', hasattr(cli, 'run_app'))
print('run_app type', type(cli.run_app))
print('WorkerOptions', WorkerOptions)
print(inspect.getsource(cli.run_app))
