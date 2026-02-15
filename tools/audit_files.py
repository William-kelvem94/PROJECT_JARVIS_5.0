import os
import time
from pathlib import Path

def get_file_info(root_dir):
    file_info = []
    for root, dirs, files in os.walk(root_dir):
        if '.git' in root or '__pycache__' in root or 'venv' in root or '.cursor' in root or '.vscode' in root:
            continue
        for file in files:
            path = Path(root) / file
            try:
                stat = path.stat()
                size_kb = stat.st_size / 1024
                mod_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                line_count = 0
                if file.endswith('.py'):
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            line_count = sum(1 for _ in f)
                    except:
                        pass
                
                file_info.append({
                    'path': str(path.relative_to(root_dir)),
                    'size_kb': size_kb,
                    'mod_date': mod_date,
                    'lines': line_count
                })
            except Exception as e:
                pass
    return file_info

if __name__ == "__main__":
    root = r"C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0"
    info = get_file_info(root)
    for i in info:
        print(f"{i['path']}|{i['size_kb']:.2f}|{i['mod_date']}|{i['lines']}")
