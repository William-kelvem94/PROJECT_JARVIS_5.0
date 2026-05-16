import sys
from unittest.mock import MagicMock

# Mock hardware-dependent modules for CI environments
sys.modules['comtypes'] = MagicMock()
sys.modules['pycaw'] = MagicMock()
sys.modules['pycaw.pycaw'] = MagicMock()
sys.modules['pycaw.api'] = MagicMock()
sys.modules['pycaw.api.audioclient'] = MagicMock()
sys.modules['pycaw.api.endpointvolume'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['face_recognition'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()

import pytest

if __name__ == "__main__":
    test_dirs = [
        "backend/tests/",
        "tests/unit/",
    ]
    sys.exit(pytest.main(test_dirs + sys.argv[1:]))
