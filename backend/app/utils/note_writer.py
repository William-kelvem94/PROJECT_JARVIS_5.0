import os
from datetime import datetime
from pathlib import Path
from loguru import logger


class NoteWriter:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.notes_dir = self.vault_path / "JARVIS"
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def create_note(self, title: str, body: str) -> str:
        safe_title = title.strip().replace("/", "_").replace("\\", "_")
        filename = f"{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}_{safe_title[:64]}.md"
        note_path = self.notes_dir / filename

        try:
            note_path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
            logger.success(f"📘 Nota JARVIS criada: {note_path}")
            return str(note_path)
        except OSError as exc:
            logger.error(f"Falha ao escrever nota no segundo cérebro: {exc}")
            raise


note_writer = NoteWriter(
    os.getenv("JARVIS_VAULT_ROOT")
    or os.getenv("OBSIDIAN_VAULT_PATH")
    or r"D:\DOCUMENTOS\GitHub\Will-obsidian"
)
