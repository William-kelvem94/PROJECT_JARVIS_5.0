import ast
import os

def analyze_complexity(root_dir):
    results = []
    for root, dirs, files in os.walk(root_dir):
        if '.git' in root or 'venv' in root: continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        tree = ast.parse(f.read())
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            length = node.end_lineno - node.lineno
                            if length > 50:
                                results.append(f"FUNC|{path}|{node.name}|{length}")
                        elif isinstance(node, ast.ClassDef):
                            length = node.end_lineno - node.lineno
                            if length > 500:
                                results.append(f"CLASS|{path}|{node.name}|{length}")
                except:
                    pass
    return results

if __name__ == "__main__":
    root = r"C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\src"
    for r in analyze_complexity(root):
        print(r)
