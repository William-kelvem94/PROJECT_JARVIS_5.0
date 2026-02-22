import json
from jarvis_minimal.bootstrap import run_startup_checks
r = run_startup_checks(autoinstall=False)
print('startup report:')
print(json.dumps(r, indent=2, ensure_ascii=False))
