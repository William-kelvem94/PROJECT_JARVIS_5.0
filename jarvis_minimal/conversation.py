import os
import json
from typing import List, Dict


class ConversationMemory:
    def __init__(self, path: str = "data/conversation.jsonl", window: int = 6):
        self.path = path
        self.window = window
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._history: List[Dict[str, str]] = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        self._history.append(json.loads(line))
            except Exception:
                # corrupt file -> start fresh
                self._history = []

    def add(self, user: str, assistant: str):
        entry = {"user": user, "assistant": assistant}
        self._history.append(entry)
        # persist append
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        # keep only recent window in memory
        if len(self._history) > self.window * 2:
            self._history = self._history[- self.window * 2 :]

    def as_prompt(self, system_prompt: str = "", max_items: int = None) -> str:
        items = self._history if max_items is None else self._history[-max_items * 2 :]
        buf = []
        if system_prompt:
            buf.append(system_prompt.strip())
            buf.append("\n---\n")
        for entry in items[-(self.window * 2) :]:
            buf.append(f"Usuário: {entry['user']}")
            buf.append(f"Jarvis: {entry['assistant']}")
        return "\n".join(buf)

    def clear(self):
        self._history = []
        try:
            open(self.path, "w", encoding="utf-8").close()
        except Exception:
            pass

    def recent(self, n: int = 6):
        return self._history[-n:]
