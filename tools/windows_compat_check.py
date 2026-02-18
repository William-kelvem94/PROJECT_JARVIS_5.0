import ast
import os
import sys

def check_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError as e:
            print(f"❌ Syntax Error in {filepath}: {e}")
            return

    windows_imports = {"win32api", "win32con", "win32gui", "win32ui", "wmi", "comtypes", "pycaw", "msvcrt"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in windows_imports:
                    check_guard(node, filepath, alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in windows_imports:
                check_guard(node, filepath, node.module)

def check_guard(node, filepath, import_name):
    # This is a simplified check. A robust one would traverse up the AST to find an If node checking sys.platform
    # For now, we just flag it for manual review if it's not obviously guarded.
    print(f"⚠️  Windows-specific import '{import_name}' found in {filepath} at line {node.lineno}")

def main():
    print("🔍 Scanning for unguarded Windows-specific imports...")
    for root, dirs, files in os.walk("."):
        if "venv" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                check_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
