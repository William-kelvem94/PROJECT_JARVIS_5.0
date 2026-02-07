"""
JARVIS 5.0 - Knowledge Graph Foundation
========================================
Sprint 2: RAG Avançado
Grafo de conhecimento em memória para navegação conceitual

DEPENDENCIES: pip install networkx
USAGE: from src.core.knowledge_graph import KnowledgeGraph
"""

import sys
import os
from pathlib import Path
import json
import logging
import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX not available. Knowledge Graph disabled.")


class KnowledgeGraph:
    """
    Knowledge Graph para navegação conceitual
    
    - Nós: concepts (ex: "Gemini", "Voice Cloning", "Neural Memory")
    - Arestas: relações ("uses", "depends_on", "related_to", "is_part_of")
    """
    
    def __init__(self, graph_path: Optional[str] = None):
        """
        Args:
            graph_path: Path to save/load graph (JSON format)
        """
        self.graph_path = graph_path or "data/knowledge_graph.json"
        
        if NETWORKX_AVAILABLE:
            self.graph = nx.DiGraph()
            logger.info("✅ Knowledge Graph initialized")
        else:
            self.graph = None
            logger.error("NetworkX not available")
        
        # Entity patterns (simple regex for now)
        self.entity_patterns = {
            'technology': r'\b(Gemini|Qwen|YOLO|Whisper|TTS|XTTS|ChromaDB|Jina|PyQt6|PyTorch)\b',
            'feature': r'\b(voice cloning|wake word|face recognition|OCR|RAG|continual learning|dream cycle)\b',
            'component': r'\b(neural memory|vision system|voice controller|emotion detector|predictive engine)\b',
            'action': r'\b(train|predict|classify|detect|recognize|transcribe|synthesize|embed)\b'
        }
    
    def add_concept(self, concept: str, concept_type: str = 'general', metadata: Optional[Dict] = None):
        """
        Add concept node to graph
        
        Args:
            concept: Concept name
            concept_type: Type (technology, feature, component, action, general)
            metadata: Additional metadata dict
        """
        if not self.graph:
            return
        
        if concept not in self.graph:
            self.graph.add_node(
                concept,
                type=concept_type,
                metadata=metadata or {},
                count=1
            )
            logger.debug(f"➕ Added concept: {concept} ({concept_type})")
        else:
            # Increment count if already exists
            self.graph.nodes[concept]['count'] += 1
    
    def add_relation(self, concept_a: str, concept_b: str, relation_type: str = 'related_to', weight: float = 1.0):
        """
        Add relation between concepts
        
        Args:
            concept_a: Source concept
            concept_b: Target concept
            relation_type: Relation type (uses, depends_on, related_to, is_part_of)
            weight: Relation weight/strength
        """
        if not self.graph:
            return
        
        # Ensure both concepts exist
        if concept_a not in self.graph:
            self.add_concept(concept_a)
        if concept_b not in self.graph:
            self.add_concept(concept_b)
        
        # Add or update edge
        if self.graph.has_edge(concept_a, concept_b):
            self.graph[concept_a][concept_b]['weight'] += weight
        else:
            self.graph.add_edge(concept_a, concept_b, relation=relation_type, weight=weight)
            logger.debug(f"🔗 {concept_a} --[{relation_type}]--> {concept_b}")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text using regex patterns
        
        Args:
            text: Input text
        
        Returns:
            Dict of entity_type -> [entities]
        """
        entities = defaultdict(list)
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities[entity_type].extend([m.lower() for m in matches])
        
        return dict(entities)
    
    def add_from_text(self, text: str, source: str = 'user'):
        """
        Extract concepts from text and add to graph
        
        Args:
            text: Input text
            source: Source of text (user, jarvis, document, etc)
        """
        if not self.graph:
            return
        
        # Extract entities
        entities = self.extract_entities(text)
        
        if not entities:
            return
        
        # Add all entities as concepts
        all_concepts = []
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                self.add_concept(entity, concept_type=entity_type, metadata={'source': source})
                all_concepts.append(entity)
        
        # Create relations between co-occurring concepts
        for i, concept_a in enumerate(all_concepts):
            for concept_b in all_concepts[i+1:]:
                if concept_a != concept_b:
                    self.add_relation(concept_a, concept_b, relation_type='co_occurs', weight=0.5)
    
    def query_relation(self, concept_a: str, concept_b: str) -> Optional[List[str]]:
        """
        Find shortest path between two concepts
        
        Args:
            concept_a: Start concept
            concept_b: End concept
        
        Returns:
            List of concepts in path, or None if no path
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            return None
        
        concept_a = concept_a.lower()
        concept_b = concept_b.lower()
        
        if concept_a not in self.graph or concept_b not in self.graph:
            return None
        
        try:
            path = nx.shortest_path(self.graph.to_undirected(), concept_a, concept_b)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_related_concepts(self, concept: str, max_depth: int = 2, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get concepts related to given concept
        
        Args:
            concept: Source concept
            max_depth: Maximum distance from source
            limit: Maximum number of results
        
        Returns:
            List of (concept, distance) tuples
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            return []
        
        concept = concept.lower()
        
        if concept not in self.graph:
            return []
        
        # BFS from concept
        related = []
        visited = {concept}
        queue = [(concept, 0)]
        
        while queue and len(related) < limit:
            current, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            # Get neighbors
            neighbors = list(self.graph.successors(current)) + list(self.graph.predecessors(current))
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    distance = depth + 1
                    related.append((neighbor, distance))
                    queue.append((neighbor, distance))
        
        # Sort by distance and weight
        related.sort(key=lambda x: x[1])
        return related[:limit]
    
    def get_top_concepts(self, n: int = 20, concept_type: Optional[str] = None) -> List[Tuple[str, int]]:
        """
        Get top N concepts by count
        
        Args:
            n: Number of concepts to return
            concept_type: Filter by concept type (optional)
        
        Returns:
            List of (concept, count) tuples
        """
        if not self.graph:
            return []
        
        concepts = []
        for node, data in self.graph.nodes(data=True):
            if concept_type is None or data.get('type') == concept_type:
                concepts.append((node, data.get('count', 0)))
        
        concepts.sort(key=lambda x: x[1], reverse=True)
        return concepts[:n]
    
    def get_stats(self) -> Dict:
        """Get graph statistics"""
        if not self.graph:
            return {}
        
        return {
            'num_concepts': self.graph.number_of_nodes(),
            'num_relations': self.graph.number_of_edges(),
            'density': nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0,
            'top_concepts': self.get_top_concepts(n=5)
        }
    
    def save(self, path: Optional[str] = None):
        """
        Save graph to JSON
        
        Args:
            path: Save path (overrides self.graph_path)
        """
        if not self.graph:
            return
        
        save_path = path or self.graph_path
        
        # Convert graph to JSON-serializable format
        data = {
            'nodes': [
                {
                    'id': node,
                    'type': data.get('type', 'general'),
                    'count': data.get('count', 1),
                    'metadata': data.get('metadata', {})
                }
                for node, data in self.graph.nodes(data=True)
            ],
            'edges': [
                {
                    'source': u,
                    'target': v,
                    'relation': data.get('relation', 'related_to'),
                    'weight': data.get('weight', 1.0)
                }
                for u, v, data in self.graph.edges(data=True)
            ]
        }
        
        # Save
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Knowledge Graph saved: {save_path}")
        logger.info(f"   Nodes: {len(data['nodes'])}, Edges: {len(data['edges'])}")
    
    def load(self, path: Optional[str] = None):
        """
        Load graph from JSON
        
        Args:
            path: Load path (overrides self.graph_path)
        """
        if not self.graph:
            return
        
        load_path = path or self.graph_path
        
        if not os.path.exists(load_path):
            logger.warning(f"Graph file not found: {load_path}")
            return
        
        with open(load_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clear existing graph
        self.graph.clear()
        
        # Add nodes
        for node_data in data['nodes']:
            self.graph.add_node(
                node_data['id'],
                type=node_data.get('type', 'general'),
                count=node_data.get('count', 1),
                metadata=node_data.get('metadata', {})
            )
        
        # Add edges
        for edge_data in data['edges']:
            self.graph.add_edge(
                edge_data['source'],
                edge_data['target'],
                relation=edge_data.get('relation', 'related_to'),
                weight=edge_data.get('weight', 1.0)
            )
        
        logger.info(f"📂 Knowledge Graph loaded: {load_path}")
        logger.info(f"   Nodes: {self.graph.number_of_nodes()}, Edges: {self.graph.number_of_edges()}")
    
    def visualize_subgraph(self, center_concept: str, depth: int = 2):
        """
        Visualize subgraph around a concept (for debugging)
        
        Args:
            center_concept: Central concept
            depth: Distance from center
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            return
        
        try:
            import matplotlib.pyplot as plt
            
            center_concept = center_concept.lower()
            
            if center_concept not in self.graph:
                logger.error(f"Concept not found: {center_concept}")
                return
            
            # Get subgraph
            nodes = {center_concept}
            for i in range(depth):
                new_nodes = set()
                for node in nodes:
                    new_nodes.update(self.graph.successors(node))
                    new_nodes.update(self.graph.predecessors(node))
                nodes.update(new_nodes)
            
            subgraph = self.graph.subgraph(nodes)
            
            # Draw
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(subgraph, k=0.5)
            
            # Node colors by type
            node_colors = []
            for node in subgraph.nodes():
                node_type = subgraph.nodes[node].get('type', 'general')
                color_map = {
                    'technology': '#FF6B6B',
                    'feature': '#4ECDC4',
                    'component': '#45B7D1',
                    'action': '#FFA07A',
                    'general': '#95E1D3'
                }
                node_colors.append(color_map.get(node_type, '#95E1D3'))
            
            nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=500, alpha=0.9)
            nx.draw_networkx_edges(subgraph, pos, edge_color='#CCCCCC', arrows=True, arrowsize=20)
            nx.draw_networkx_labels(subgraph, pos, font_size=8)
            
            plt.title(f"Knowledge Graph around '{center_concept}' (depth {depth})")
            plt.axis('off')
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            logger.warning("Matplotlib not available for visualization")


# Example usage
if __name__ == "__main__":
    # Create knowledge graph
    kg = KnowledgeGraph()
    
    # Add concepts from text
    kg.add_from_text("JARVIS uses Gemini and Qwen for neural memory with ChromaDB")
    kg.add_from_text("Voice cloning uses XTTS for synthesize speech")
    kg.add_from_text("Wake word detection and voice recognition work together")
    kg.add_from_text("YOLO detects objects and OCR recognizes text in vision system")
    
    # Get stats
    print("\n📊 Knowledge Graph Stats:")
    stats = kg.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Query relations
    print("\n🔍 Path from 'gemini' to 'voice cloning':")
    path = kg.query_relation('gemini', 'voice cloning')
    if path:
        print(f"  {' → '.join(path)}")
    else:
        print("  No path found")
    
    # Get related concepts
    print("\n🔗 Concepts related to 'yolo':")
    related = kg.get_related_concepts('yolo', max_depth=2, limit=5)
    for concept, distance in related:
        print(f"  {concept} (distance: {distance})")
    
    # Save graph
    kg.save()
    print(f"\n💾 Graph saved to: {kg.graph_path}")
