#!/usr/bin/env python3
"""Lightweight, non-blocking UI smoke tests."""

<<<<<<< Updated upstream
import sys

sys.path.insert(0, "src")

try:
    from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
    from PyQt6.QtCore import Qt
=======
import os

import pytest

<<<<<<< HEAD

def _get_qapplication():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_pyqt6_imports():
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QLabel, QMainWindow
    except Exception as exc:
        pytest.fail(f"PyQt6 imports failed: {exc}")

    assert Qt is not None
    assert QLabel is not None
    assert QMainWindow is not None


def test_window_instantiation_offscreen():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QLabel, QMainWindow
>>>>>>> Stashed changes

    app = _get_qapplication()
    window = QMainWindow()
    window.setWindowTitle("JARVIS 5.0 - Interface Test")
    window.setGeometry(100, 100, 800, 600)

<<<<<<< Updated upstream
            label = QLabel("✅ JARVIS Interface is working!\n\nThe GUI framework is functional.")
=======
            label = QLabel(
                "✅ JARVIS Interface is working!\n\nThe GUI framework is functional."
            )
>>>>>>> dev-new-version
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setCentralWidget(label)
=======
    label = QLabel("JARVIS Interface smoke test")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)
>>>>>>> Stashed changes

    window.show()
    app.processEvents()

<<<<<<< Updated upstream
except Exception as e:
    print(f"❌ Interface test failed: {e}")
    sys.exit(1)
<<<<<<< HEAD
=======
    assert window.windowTitle() == "JARVIS 5.0 - Interface Test"
    window.close()
>>>>>>> Stashed changes
=======
>>>>>>> dev-new-version
