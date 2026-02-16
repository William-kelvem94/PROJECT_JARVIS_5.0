"""
JARVIS 5.0 - Topology Scanner
==============================
MÃ³dulo para mapear a estrutura completa de um projeto e entender o "todo".
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS-TOPOLOGY-SCANNER")

class TopologyScanner:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.ignored_dirs = {".git", "__pycache__", "node_modules", "venv", ".env", "data", "models"}
        
    def scan_project(self) -> Dict[str, Any]:
        """Gera um mapa da estrutura do projeto e detecta tecnologias"""
        topology = {
            "name": self.root.name,
            "structure": [],
            "tech_stack": set(),
            "complexity_score": 0,
            "main_purpose": "Desconhecido"
        }
        
        try:
            for root, dirs, files in os.walk(self.root):
                # Filtrar diretÃ³rios ignorados
                dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
                
                rel_path = os.path.relpath(root, self.root)
                if rel_path == ".": rel_path = ""
                
                depth = rel_path.count(os.sep)
                if depth > 3: continue # Limitar profundidade para performance
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    self._detect_tech(file, ext, topology["tech_stack"])
                    
                topology["structure"].append(rel_path)
                topology["complexity_score"] += len(files) + len(dirs)

            topology["tech_stack"] = list(topology["tech_stack"])
            topology["main_purpose"] = self._infer_purpose(topology)
            
            logger.info(f"ðŸ“Š Topologia mapeada: {len(topology['structure'])} diretÃ³rios, Techs: {topology['tech_stack']}")
            return topology
            
        except Exception as e:
            logger.error(f"Erro ao escanear topologia: {e}")
            return topology

    def _detect_tech(self, file: str, ext: str, stack: set):
        if ext == '.py': stack.add("Python")
        elif ext in ['.js', '.ts', '.tsx', '.jsx']: stack.add("JavaScript/TypeScript")
        elif ext == '.java': stack.add("Java")
        elif ext == '.cpp' or ext == '.h': stack.add("C++")
        elif file == 'package.json': stack.add("Node.js")
        elif file == 'requirements.txt': stack.add("Python Pip")
        elif file == 'Dockerfile': stack.add("Docker")
        elif ext == '.sql': stack.add("SQL Database")

    def _infer_purpose(self, topology: Dict[str, Any]) -> str:
        stack = topology["tech_stack"]
        if "Python" in stack and "SQL Database" in stack:
            return "AplicaÃ§Ã£o Backend com Banco de Dados"
        if "JavaScript/TypeScript" in stack and "Node.js" in stack:
            return "Projeto Web/Fullstack"
        if "Python" in stack and "torch" in str(topology["structure"]):
            return "Desenvolvimento de IA/Machine Learning"
        return "Projeto de Software Geral"

# InstÃ¢ncia global serÃ¡ criada no LearningEngine ou Agent
