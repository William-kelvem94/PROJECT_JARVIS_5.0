import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

# Adicionar raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.interface.stark_dashboard import StarkDashboard

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create dashboard
    dashboard = StarkDashboard()
    dashboard.show()

    # Simulate some logs
    logging.info("Dashboard initialized in standalone mode.")
    logging.warning("System running on backup power.")
    logging.error("Failed to connect to Neural Link.")

    sys.exit(app.exec())
