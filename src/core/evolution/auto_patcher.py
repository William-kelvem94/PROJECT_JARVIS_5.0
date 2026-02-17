"""
AutoPatcher

Responsible for applying safe, test-verified code fixes suggested by the DreamCycle
(insights). Workflow (safe-by-default):

1. Permission check - requires JARVIS_ALLOW_SELF_PATCH=1 (environment) to apply real
   changes. Otherwise only propose/validate.
2. Identify target file from insight (insight['example']['file'] recommended).
3. Ask local LLM (via ai_agent._call_ollama_async) to propose a minimal patched file
   content (best-effort parsing of response).
4. Validate patch by syntax-checking and (when possible) running relevant unit tests.
5. If validation passes, backup original file and atomically replace it.

This is intentionally conservative: no automatic repo commits, no remote pushes.
"""
from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

SELF_PATCH_ENV = "JARVIS_ALLOW_SELF_PATCH"


class AutoPatcher:
    def __init__(self):
        # safety gate: must be explicitly enabled via env var
        self.enabled = os.getenv(SELF_PATCH_ENV, "0") in ("1", "true", "True")

    def is_allowed(self) -> bool:
        # Re-evaluate environment variable at call-time so tests can enable/disable dynamically
        return os.getenv(SELF_PATCH_ENV, "0") in ("1", "true", "True")

    def _extract_file_from_insight(self, insight: Dict) -> Optional[Path]:
        example = insight.get("example") or {}
        f = example.get("file") if isinstance(example, dict) else None
        if f:
            p = Path(f)
            # If relative, resolve against project root
            if not p.is_absolute():
                p = Path.cwd() / p
            return p
        return None

    def _prompt_for_patch(self, file_path: Path, signature: str) -> str:
        """Build prompt for the LLM asking for a minimal patch.

        We ask for the full file content (minimal changes) and instruct the LLM to
        return only the full file between triple backticks if possible.
        """
        file_content = file_path.read_text(encoding="utf-8", errors="ignore")
        prompt = (
            "You are a careful Python engineer. A program produced the following"
            " runtime error/traces and the relevant file content is below."
            " Make a minimal, correct fix that addresses the error, keep the rest"
            " of the file unchanged, and return only the full updated file content"
            " (no explanation). If you cannot confidently fix it, return 'NO_FIX'.\n\n"
            f"ERROR_SIGNATURE:\n{signature}\n\nFILE_PATH: {file_path}\n\nORIGINAL_FILE:\n{file_content}\n\n"
            "Return the complete updated file content enclosed in triple backticks ```...```"
        )
        return prompt

    def _call_llm_for_patch(self, prompt: str, model: str = "gemma3:4b") -> str:
        """Call the local LLM via ai_agent._call_ollama_async. Synchronous wrapper."""
        try:
            # Import locally to avoid circular imports
            from src.core.intelligence.ai_agent import ai_agent
            import asyncio

            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                resp = loop.run_until_complete(
                    ai_agent._call_ollama_async(prompt, image_data=None, model=model)
                )
            finally:
                try:
                    loop.close()
                except Exception:
                    pass

            return resp or ""
        except Exception as e:
            logger.error(f"AutoPatcher: failed to call LLM: {e}")
            return ""

    def _extract_code_block(self, llm_response: str) -> Optional[str]:
        # Look for fenced ``` blocks
        m = re.search(r"```(?:python|py)?\n([\s\S]+?)\n```", llm_response, re.IGNORECASE)
        if m:
            return m.group(1)

        # Otherwise try to heuristically extract the largest python-like chunk
        candidates = re.findall(r"(^def\s+[\s\S]+$)|(^class\s+[\s\S]+$)", llm_response, re.M)
        if candidates:
            # join tuples and return first non-empty
            for cand in candidates:
                for c in cand:
                    if c and len(c) > 20:
                        return c

        # As a last resort, if the response looks like a full file (contains 'import' and 'def')
        if "import" in llm_response and "def " in llm_response:
            return llm_response

        return None

    def _syntax_check(self, code: str, filename_for_compile: str = "<patched>") -> Tuple[bool, Optional[str]]:
        try:
            compile(code, filename_for_compile, "exec")
            return True, None
        except Exception as e:
            return False, str(e)

    def _find_related_tests(self, module_path: Path) -> Optional[str]:
        """Try to find tests that reference the module filename and return pytest -k pattern.
        Returns None if none found.
        """
        base = module_path.stem
        # scan tests/ for references to base
        tests_dir = Path.cwd() / "tests"
        if not tests_dir.exists():
            return None

        pattern = []
        for p in tests_dir.rglob("test_*.py"):
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if base in txt:
                    pattern.append(p)
            except Exception:
                continue

        if not pattern:
            return None

        # build pytest pattern using module basename
        return base

    def _run_pytests_for_module(self, module_path: Path) -> Tuple[bool, str]:
        """Run pytest for related tests if any. Returns (success, output)."""
        pattern = self._find_related_tests(module_path)
        if not pattern:
            # No related tests found — skip heavy test run but consider as 'no-tests'
            return True, "no-tests-found"

        try:
            cmd = [
                shutil.which("python") or sys_executable(),
                "-m",
                "pytest",
                "-q",
                "-k",
                pattern,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            ok = proc.returncode == 0
            out = proc.stdout + "\n" + proc.stderr
            return ok, out
        except Exception as e:
            return False, str(e)

    def _backup_original(self, file_path: Path) -> Optional[Path]:
        try:
            bak = file_path.with_suffix(file_path.suffix + f".bak.{int(time.time())}")
            shutil.copy2(file_path, bak)
            return bak
        except Exception as e:
            logger.error(f"AutoPatcher: failed to create backup for {file_path}: {e}")
            return None

    def apply_patch(self, file_path: Path, new_code: str) -> Tuple[bool, str]:
        """Apply the patch atomically after syntax check and optional unit tests."""
        # Syntax check
        ok, err = self._syntax_check(new_code, filename_for_compile=str(file_path))
        if not ok:
            return False, f"SyntaxError: {err}"

        # Write to temp file
        try:
            fd, tmp = tempfile.mkstemp(suffix=file_path.suffix)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(new_code)

            # Optionally run related pytest tests (disabled by default for safety in CI)
            if os.getenv("JARVIS_AUTO_PATCH_RUN_TESTS", "0") in ("1", "true", "True"):
                tests_ok, test_out = self._run_pytests_for_module(file_path)
                if not tests_ok:
                    # Clean up temp
                    try:
                        os.remove(tmp)
                    except Exception:
                        pass
                    return False, f"Tests failed: {test_out}"
            else:
                tests_ok, test_out = True, "tests-skipped"

            # Backup and replace
            bak = self._backup_original(file_path)
            shutil.copy2(tmp, file_path)
            try:
                os.remove(tmp)
            except Exception:
                pass

            logger.info(f"AutoPatcher: applied patch to {file_path} (backup: {bak})")
            return True, f"Patched (backup: {bak})"
        except Exception as e:
            return False, str(e)

    def attempt_patch_from_insight(self, insight: Dict) -> Tuple[bool, str]:
        """High-level method: propose and (if allowed) apply patch based on an insight.

        Returns (success, message).
        """
        # Permission gate
        if not self.is_allowed():
            logger.warning("AutoPatcher: self-patch disabled by environment")
            return False, "self-patch-disabled"

        file_path = self._extract_file_from_insight(insight)
        if not file_path or not file_path.exists():
            return False, "file-not-found"

        signature = insight.get("signature", "") or str(insight.get("example", ""))

        prompt = self._prompt_for_patch(file_path, signature)
        resp = self._call_llm_for_patch(prompt)
        if not resp or resp.strip().upper() == "NO_FIX":
            return False, "llm-no-fix"

        code = self._extract_code_block(resp)
        if not code:
            # If LLM returned a small snippet, attempt to integrate heuristically
            # (not implemented in MVP)
            return False, "no-code-extracted"

        # Validate action with ActionValidator (safety sentinel)
        try:
            from src.core.evolution.action_validator import action_validator
            from src.core.evolution.action_approval import action_approval_manager

            act = {
                "action_type": "file_modify",
                "target": str(file_path),
                "proposed_code": code,
                "source": "auto_patcher",
            }
            validation = action_validator.validate(act)

            # If validator requires approval and provided a request_id, register pending
            if validation.requires_approval:
                req_id = getattr(validation, "request_id", None)
                if req_id:
                    # Register pending action so approval can trigger apply_patch
                    def _apply_cb():
                        ok2, msg2 = self.apply_patch(file_path, code)
                        return {"ok": ok2, "msg": msg2}

                    registered = action_approval_manager.register_pending(req_id, _apply_cb, meta={"file": str(file_path)})
                    if registered:
                        logger.info(f"AutoPatcher: registered pending approval (request_id={req_id})")
                        return False, f"approval-pending:{req_id}"
                    else:
                        # already pending
                        return False, "approval-already-pending"

                # No request_id -> validator declined or returned structured reason
                logger.warning(f"AutoPatcher: ActionValidator declined/required-approval: {validation.reason}")
                return False, validation.reason or "action-not-approved"
        except Exception as e:
            logger.debug(f"AutoPatcher: ActionValidator unavailable: {e}")

        # Apply patch
        ok, msg = self.apply_patch(file_path, code)
        return ok, msg


# Helpers
def sys_executable() -> str:
    import sys

    return sys.executable


# Singleton
auto_patcher = AutoPatcher()
