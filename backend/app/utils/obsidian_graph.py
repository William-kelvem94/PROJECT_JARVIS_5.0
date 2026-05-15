from typing import Optional
import os
import re
import networkx as nx
from loguru import logger
from pathlib import Path

class ObsidianGraph:
    """
    Constrói e gerencia o grafo de conhecimento do Obsidian.
    Mapeia relações via links wiki [[Link]].
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.graph = nx.DiGraph()
        self.link_pattern = re.compile(r'\[\[(.*?)\]\]')
        logger.info(f"🕸️ Inicializando Grafo de Conhecimento: {vault_path}")

    def build_graph(self, vault_path: Optional[str] = None):
        """Escanear o vault e construir o grafo completo."""
        if vault_path is not None:
            self.vault_path = vault_path

        self.graph.clear()
        md_files = list(Path(self.vault_path).rglob("*.md"))
        
        for file_path in md_files:
            node_name = file_path.stem
            self.graph.add_node(node_name, path=str(file_path))
            
            try:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                links = self.link_pattern.findall(content)
                for link in links:
                    # Limpa o link de aliases (ex: [[Nota|Alias]])
                    target = link.split('|')[0].strip()
                    self.graph.add_edge(node_name, target)
            except Exception as e:
                logger.error(f"Erro ao processar {file_path}: {e}")
        
        logger.success(f"🕸️ Grafo do Obsidian construído: {len(self.graph.nodes)} nós, {len(self.graph.edges)} conexões.")

    def query_related(self, node_name: str, depth: int = 1):
        """Busca notas relacionadas (vizinhos) a partir de um termo."""
        if node_name not in self.graph:
            # Tenta busca parcial se não achar exato
            matches = [n for n in self.graph.nodes if node_name.lower() in n.lower()]
            if not matches: return []
            node_name = matches[0]

        # Pega vizinhos de entrada e saída
        related = set()
        for _ in range(depth):
            predecessors = list(self.graph.predecessors(node_name))
            successors = list(self.graph.successors(node_name))
            related.update(predecessors)
            related.update(successors)
        
        return list(related)

    def update_node(self, file_path: str):
        """Atualiza incrementalmente um nó do grafo."""
        path_obj = Path(file_path)
        node_name = path_obj.stem
        
        # Remove arestas antigas
        if node_name in self.graph:
            self.graph.remove_node(node_name)
        
        # Adiciona novamente
        self.graph.add_node(node_name, path=str(file_path))
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            links = self.link_pattern.findall(content)
            for link in links:
                target = link.split('|')[0].strip()
                self.graph.add_edge(node_name, target)
            logger.info(f"🕸️ Grafo atualizado: {node_name}")
        except Exception:
            pass


def _get_default_vault_path() -> str:
    # 1. Prioridade Máxima: Variáveis de Ambiente
    env_path = os.getenv('JARVIS_VAULT_ROOT') or os.getenv('OBSIDIAN_VAULT_PATH') or os.getenv("JARVIS_KB_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
        
    # 2. Prioridade: Caminhos conhecidos no Windows (Will-obsidian)
    for user_vault in (r"D:\DOCUMENTOS\GitHub\Will-obsidian", "C:/Users/willi/Documents/GitHub/Will-obsidian"):
        if os.path.exists(user_vault):
            return user_vault

    # 3. Fallback: data/kb_local relativo à raiz do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_dir, "data", "kb_local")

obsidian_graph = ObsidianGraph(_get_default_vault_path())
