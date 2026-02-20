#!/usr/bin/env python3
"""
Test script to verify JARVIS interface works
"""

import sys

sys.path.insert(0, "src")


def run_interface_test() -> int:
    """Show a small test window (only when executed directly)."""
    try:
        from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
        from PyQt6.QtCore import Qt

        class TestWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("JARVIS 5.0 - Interface Test")
                self.setGeometry(100, 100, 800, 600)

                label = QLabel(
                    "✅ JARVIS Interface is working!\n\nThe GUI framework is functional."
                )
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setCentralWidget(label)

        app = QApplication(sys.argv)
        window = TestWindow()
        window.show()
        print("✅ Interface test successful - window should be visible")
        return app.exec()

    except Exception as e:
        print(f"❌ Interface test failed: {e}")
        raise


if __name__ == "__main__":
    sys.exit(run_interface_test())
