import os
import ast
from datetime import datetime

TARGET_DIRS = [
    ".antigravity",
    ".cursor",
    ".vscode",
    "config",
    "data",
    "docs",
    "models",
    "scripts",
    "src",
    "tests",
    "tools",
]
TARGET_FILES = [
    ".env",
    ".gitignore",
    "jarvis.bat",
    "main.py",
    "README.md",
    "start_jarvis.bat",
    "start_jarvis.sh",
]
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def check_python_syntax(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        ast.parse(content)
        return None
    except SyntaxError as e:
        return f"{file_path}: SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return f"{file_path}: Error reading file: {str(e)}"


def scan_file_content(file_path):
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if "FIXME" in line:
                issues.append(f"{file_path}:{i+1} - FIXME found")
            if "TODO" in line:
                issues.append(f"{file_path}:{i+1} - TODO found")
            if "raise NotImplementedError" in line:
                issues.append(f"{file_path}:{i+1} - NotImplementedError")
            if "<<<<<<< HEAD" in line:
                issues.append(f"{file_path}:{i+1} - Merge conflict marker found")
    except Exception:
        pass  # Binary file or unreadable
    return issues


def find_latest_log_errors():
    log_dir = os.path.join(ROOT_DIR, "data")
    log_files = []
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file.endswith(".log"):
                log_files.append(os.path.join(root, file))

    if not log_files:
        return ["No log files found."]

    # Sort by modification time
    log_files.sort(key=os.path.getmtime, reverse=True)
    latest_logs = log_files[:5]  # Check top 5 most recent logs

    errors = []
    for log_file in latest_logs:
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            file_errors = []
            for line in lines[-50:]:  # Check last 50 lines
                if (
                    "ERROR" in line
                    or "CRITICAL" in line
                    or "Exception" in line
                    or "Traceback" in line
                ):
                    file_errors.append(line.strip())

            if file_errors:
                errors.append(f"Errors in {os.path.basename(log_file)}:")
                errors.extend(file_errors)
        except Exception as e:
            errors.append(f"Could not read {log_file}: {e}")

    return errors


def main():
    report_path = os.path.join(ROOT_DIR, "tools", "scan_report.txt")
    with open(report_path, "w", encoding="utf-8") as report_file:

        def log(msg):
            report_file.write(msg + "\n")
            print(msg)  # Still print to console even if it fails

        log("=== JARVIS 5.0 SYSTEM SCAN ===")
        log(f"Root: {ROOT_DIR}")
        log(f"Time: {datetime.now()}")
        log("-" * 30)

        syntax_errors = []
        content_issues = []

        # Scan Files
        all_files = []
        # Add root files
        for f in TARGET_FILES:
            path = os.path.join(ROOT_DIR, f)
            if os.path.exists(path):
                all_files.append(path)

        # Add directories
        for d in TARGET_DIRS:
            path = os.path.join(ROOT_DIR, d)
            if os.path.exists(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        all_files.append(os.path.join(root, file))

        log(f"Scanning {len(all_files)} files...")

        for file_path in all_files:
            if file_path.endswith(".py"):
                err = check_python_syntax(file_path)
                if err:
                    syntax_errors.append(err)

            # Scan for content issues in text files
            if file_path.endswith((".py", ".md", ".txt", ".bat", ".sh")):
                res = scan_file_content(file_path)
                if res:
                    content_issues.extend(res)

        log("-" * 30)
        log(f"Found {len(syntax_errors)} Syntax Errors:")
        for err in syntax_errors:
            log(f"  [CRITICAL] {err}")

        log("-" * 30)
        log(f"Found {len(content_issues)} Suspicious Items (TODOs/FIXMEs/etc):")
        # Limit output
        for issue in content_issues[:50]:
            log(f"  [WARN] {issue}")
        if len(content_issues) > 50:
            log(f"  ... and {len(content_issues) - 50} more.")

        log("-" * 30)
        log("Recent Log Errors:")
        try:
            errors = find_latest_log_errors()
        except Exception as e:
            errors = [f"Error reading logs: {e}"]

        if not errors:
            log("  No recent ERRORS found in logs.")
        else:
            for err in errors:
                log(f"  {err}")


if __name__ == "__main__":
    main()
