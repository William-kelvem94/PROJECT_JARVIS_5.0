"""
Enterprise Knowledge Graph - Grafo de Conhecimento Empresarial
Gerencia conhecimento semântico e relações entre entidades
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from core.logger import logger

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX não disponível. Usando estrutura simples.")

@dataclass
class KnowledgeEntity:
    """Entidade no grafo de conhecimento."""
    id: str
    label: str
    type: str  # PERSON, PLACE, CONCEPT, DOCUMENT, etc.
    properties: Dict[str, Any]
    created_at: datetime
    
@dataclass
class KnowledgeRelationship:
    """Relação entre entidades."""
    id: str
    source: str  # Entity ID
    target: str  # Entity ID
    type: str  # RELATED_TO, CONTAINS, MENTIONS, etc.
    properties: Dict[str, Any]
    created_at: datetime

class SemanticProcessor:
    """Processador semântico para extrair entidades."""
    
    def extract_entities(self, knowledge: Dict[str, Any]) -> List[KnowledgeEntity]:
        """
        Extrai entidades de um conhecimento.
        
        Returns:
            Lista de entidades
        """
        entities = []
        
        # Processar texto se disponível
        text = knowledge.get("text", "")
        if text:
            # Extração simples (pode usar NLP avançado)
            words = text.split()
            for word in words:
                if word[0].isupper() and len(word) > 3:
                    entities.append(KnowledgeEntity(
                        id=f"entity_{len(entities)}",
                        label=word,
                        type="ENTITY",
                        properties={"source": text[:100]},
                        created_at=datetime.now()
                    ))
        
        # Entidades explícitas no conhecimento
        explicit_entities = knowledge.get("entities", [])
        for entity_data in explicit_entities:
            entities.append(KnowledgeEntity(
                id=entity_data.get("id", f"entity_{len(entities)}"),
                label=entity_data.get("label", ""),
                type=entity_data.get("type", "ENTITY"),
                properties=entity_data.get("properties", {}),
                created_at=datetime.now()
            ))
        
        return entities

class RelationshipMiner:
    """Minerador de relações entre entidades."""
    
    def discover_relationships(
        self,
        entities: List[KnowledgeEntity]
    ) -> List[KnowledgeRelationship]:
        """
        Descobre relações entre entidades.
        
        Returns:
            Lista de relações
        """
        relationships = []
        
        # Relações simples baseadas em proximidade ou contexto
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Criar relação genérica
                relationships.append(KnowledgeRelationship(
                    id=f"rel_{len(relationships)}",
                    source=entity1.id,
                    target=entity2.id,
                    type="RELATED_TO",
                    properties={
                        "confidence": 0.5,
                        "source": "proximity"
                    },
                    created_at=datetime.now()
                ))
        
        return relationships

class TemporalAnalyzer:
    """Analisador temporal de contexto."""
    
    def analyze_context(self, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa contexto temporal.
        
        Returns:
            Contexto temporal
        """
        return {
            "timestamp": datetime.now(),
            "relevance_window_days": 30,  # Janela de relevância
            "temporal_tags": knowledge.get("temporal_tags", [])
        }

class EnterpriseKnowledgeGraph:
    """
    Grafo de conhecimento empresarial.
    Gerencia entidades, relações e conhecimento semântico.
    """
    
    def __init__(self):
        self.semantic_processor = SemanticProcessor()
        self.relationship_miner = RelationshipMiner()
        self.temporal_analyzer = TemporalAnalyzer()
        
        # Estrutura de armazenamento
        if NETWORKX_AVAILABLE:
            self.graph = nx.MultiDiGraph()
        else:
            self.entities: Dict[str, KnowledgeEntity] = {}
            self.relationships: List[KnowledgeRelationship] = []
        
        logger.info("Enterprise Knowledge Graph inicializado")
    
    async def integrate_knowledge(self, knowledge: Dict[str, Any]):
        """
        Integra novo conhecimento no grafo.
        
        Args:
            knowledge: Dicionário com conhecimento
        """
        try:
            # 1. Processamento semântico
            semantic_entities = self.semantic_processor.extract_entities(knowledge)
            
            if not semantic_entities:
                logger.debug("Nenhuma entidade extraída do conhecimento")
                return
            
            # 2. Descobrir relações
            relationships = self.relationship_miner.discover_relationships(semantic_entities)
            
            # 3. Análise temporal
            temporal_context = self.temporal_analyzer.analyze_context(knowledge)
            
            # 4. Integrar no grafo
            await self._upsert_entities(semantic_entities, relationships, temporal_context)
            
            logger.info(f"Conhecimento integrado: {len(semantic_entities)} entidades, {len(relationships)} relações")
            
        except Exception as e:
            logger.error(f"Erro integrando conhecimento: {e}")
    
    async def _upsert_entities(
        self,
        entities: List[KnowledgeEntity],
        relationships: List[KnowledgeRelationship],
        temporal_context: Dict[str, Any]
    ):
        """Atualiza ou insere entidades no grafo."""
        if NETWORKX_AVAILABLE:
            # Usar NetworkX
            for entity in entities:
                self.graph.add_node(
                    entity.id,
                    label=entity.label,
                    type=entity.type,
                    properties=entity.properties,
                    created_at=entity.created_at.isoformat(),
                    **temporal_context
                )
            
            for rel in relationships:
                self.graph.add_edge(
                    rel.source,
                    rel.target,
                    type=rel.type,
                    properties=rel.properties,
                    created_at=rel.created_at.isoformat()
                )
        else:
            # Usar estrutura simples
            for entity in entities:
                self.entities[entity.id] = entity
            
            self.relationships.extend(relationships)
    
    async def query_knowledge(
        self,
        query: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        Consulta o grafo de conhecimento.
        
        Args:
            query: Query de busca
            depth: Profundidade de travessia
        
        Returns:
            Contexto de conhecimento
        """
        try:
            # Buscar entidades relacionadas à query
            matching_entities = []
            
            if NETWORKX_AVAILABLE:
                # Busca no NetworkX
                query_lower = query.lower()
                for node_id, data in self.graph.nodes(data=True):
                    label = data.get("label", "").lower()
                    if any(word in label for word in query_lower.split()):
                        matching_entities.append({
                            "id": node_id,
                            "label": data.get("label"),
                            "type": data.get("type"),
                            "properties": data.get("properties", {})
                        })
                
                # Traversar relações
                relationships = []
                if matching_entities:
                    for entity in matching_entities[:depth]:  # Limitar profundidade
                        neighbors = list(self.graph.neighbors(entity["id"]))
                        for neighbor_id in neighbors[:5]:  # Limitar número
                            neighbor_data = self.graph.nodes[neighbor_id]
                            relationships.append({
                                "source": entity["id"],
                                "target": neighbor_id,
                                "type": "RELATED_TO"
                            })
            else:
                # Busca simples
                query_lower = query.lower()
                for entity_id, entity in self.entities.items():
                    if query_lower in entity.label.lower():
                        matching_entities.append({
                            "id": entity_id,
                            "label": entity.label,
                            "type": entity.type,
                            "properties": entity.properties
                        })
                
                # Buscar relações
                relationships = []
                for rel in self.relationships:
                    if rel.source in [e["id"] for e in matching_entities]:
                        relationships.append({
                            "source": rel.source,
                            "target": rel.target,
                            "type": rel.type
                        })
            
            return {
                "entities": matching_entities,
                "relationships": relationships[:10],  # Limitar
                "confidence": min(1.0, len(matching_entities) / 5.0),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Erro consultando conhecimento: {e}")
            return {
                "entities": [],
                "relationships": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do grafo."""
        if NETWORKX_AVAILABLE:
            return {
                "entities": self.graph.number_of_nodes(),
                "relationships": self.graph.number_of_edges(),
                "is_connected": nx.is_connected(self.graph.to_undirected()) if self.graph.number_of_nodes() > 0 else False
            }
        else:
            return {
                "entities": len(self.entities),
                "relationships": len(self.relationships)
            }

