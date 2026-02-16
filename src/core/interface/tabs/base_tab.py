import tkinter as tk
from tkinter import ttk
from typing import Any, Optional

class BaseTab:
    """Base class for Democratic Control Interface tabs."""

    def __init__(self, notebook: ttk.Notebook, interface: Any, title: str):
        self.notebook = notebook
        self.interface = interface
        self.frame = ttk.Frame(self.notebook)
        self.notebook.add(self.frame, text=title)
        self.create_widgets()

    def create_widgets(self):
        """Override this method to create widgets in self.frame."""
        raise NotImplementedError
