import os
import ast
import logging
from pathlib import Path

logger = logging.getLogger("JARVIS-SELF-AUDIT")

class SelfAuditor:
    """
    JARVIS Autonomous Self-Audit System.
    Analyzes code structure, smells, and integrity.
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.issues = []

    def run_audit(self):
        """Executes a full system scan."""
        logger.info("🕵️ Starting Autonomous Self-Audit...")
        self.issues = []
        
        self._check_todos()
        self._check_placeholders()
        self._check_file_structure()
        
        report_path = self.root_dir / "data/reports/self_audit_report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("JARVIS 5.0 - SELF-AUDIT REPORT\n")
            f.write("==============================\n\n")
            if not self.issues:
                f.write("✅ No critical issues found. System is in peak condition.\n")
            else:
                for issue in self.issues:
                    f.write(f"- {issue}\n")
        
        logger.info(f"✅ Audit complete. Report saved to {report_path}")
        return len(self.issues)

    def _check_todos(self):
        """Scans for TODOs in the codebase."""
        for path in self.root_dir.rglob("*.py"):
            if "venv" in str(path) or ".git" in str(path):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if "TODO" in line:
                            self.issues.append(f"TODO found in {path.name}:{i+1}")
            except Exception:
                pass

    def _check_placeholders(self):
        """Checks for common placeholder strings."""
        placeholders = ["pass # Placeholder", "mock_data", "simulate_"]
        for path in self.root_dir.rglob("*.py"):
            if "venv" in str(path) or ".git" in str(path):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for p in placeholders:
                        if p in content:
                            self.issues.append(f"Placeholder '{p}' found in {path.name}")
            except Exception:
                pass

    def _check_file_structure(self):
        """Verifies essential JARVIS 5.0 folders."""
        important_dirs = ["src/core", "src/interface", "data/memory", "config"]
        for d in important_dirs:
            if not (self.root_dir / d).exists():
                self.issues.append(f"Missing critical directory: {d}")

if __name__ == "__main__":
    auditor = SelfAuditor("./")
    auditor.run_audit()
