import ast
import os


def analyze_complexity(root_dir):
    results = []
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root or "venv" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if node.end_lineno is not None and node.lineno is not None:
                                line_count = node.end_lineno - node.lineno
                                if line_count > 50:
                                    results.append(
                                        f"FUNC|{path}|{node.name}|{line_count}"
                                    )
                        elif isinstance(node, ast.ClassDef):
                            if node.end_lineno is not None and node.lineno is not None:
                                line_count = node.end_lineno - node.lineno
                                if line_count > 500:
                                    results.append(
                                        f"CLASS|{path}|{node.name}|{line_count}"
                                    )
                except:
                    pass
    return results


if __name__ == "__main__":
    root = r"C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\src"
    for r in analyze_complexity(root):
        print(r)
