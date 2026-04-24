import os
import json
import time
from pathlib import Path

def analyze_project(root_dir):
    report = {
        "summary": {},
        "large_files": [],
        "file_types": {},
        "todos": [],
        "structure": {}
    }
    
    total_size = 0
    total_files = 0
    total_loc = 0
    
    ignore_dirs = {'.git', '.next', 'node_modules', 'venv', '__pycache__', '.obsidian'}
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        rel_path = os.path.relpath(root, root_dir)
        if rel_path == ".":
            rel_path = "root"
            
        for file in files:
            file_path = Path(root) / file
            try:
                stats = file_path.stat()
                size = stats.st_size
                total_size += size
                total_files += 1
                
                ext = file_path.suffix.lower()
                report["file_types"][ext] = report["file_types"].get(ext, 0) + 1
                
                # Check for large files (> 500KB)
                if size > 500 * 1024:
                    report["large_files"].append({
                        "path": str(file_path.relative_to(root_dir)),
                        "size_kb": round(size / 1024, 2)
                    })
                
                # Analyze text files
                if ext in {'.py', '.js', '.ts', '.tsx', '.css', '.html', '.md', '.yaml', '.yml'}:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        total_loc += len(lines)
                        
                        for i, line in enumerate(lines):
                            if "TODO" in line.upper() or "FIXME" in line.upper():
                                report["todos"].append({
                                    "file": str(file_path.relative_to(root_dir)),
                                    "line": i + 1,
                                    "text": line.strip()
                                })
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

    report["summary"] = {
        "total_files": total_files,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "total_loc": total_loc,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return report

if __name__ == "__main__":
    root = Path(__file__).parent.parent
    print(f"Iniciando análise em: {root}")
    data = analyze_project(root)
    
    output_path = root / "project_analysis_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"\n--- Resumo da Análise ---")
    print(f"Total de Arquivos: {data['summary']['total_files']}")
    print(f"Tamanho Total: {data['summary']['total_size_mb']} MB")
    print(f"Total de Linhas de Código: {data['summary']['total_loc']}")
    print(f"Arquivos Grandes (>500KB): {len(data['large_files'])}")
    print(f"TODOs Encontrados: {len(data['todos'])}")
    print(f"\nRelatório completo salvo em: {output_path}")
