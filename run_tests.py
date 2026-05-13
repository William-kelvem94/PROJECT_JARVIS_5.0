import sys
from unittest.mock import MagicMock

sys.modules['comtypes'] = MagicMock()
sys.modules['pycaw'] = MagicMock()
sys.modules['pycaw.pycaw'] = MagicMock()
sys.modules['pycaw.api'] = MagicMock()
sys.modules['pycaw.api.audioclient'] = MagicMock()
sys.modules['pycaw.api.endpointvolume'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()

import pytest
sys.exit(pytest.main(["backend/tests/"]))
