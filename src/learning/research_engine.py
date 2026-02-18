# -*- coding: utf-8 -*-
# src/learning/research_engine.py
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..utils.safe_execute import safe_execute

logger = logging.getLogger("JARVIS-RESEARCH-ENGINE")

class ResearchEngine:
    """
    Motor de pesquisa autônoma para preencher lacunas de conhecimento.
    Integra com sistemas externos de forma segura e controlada.
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.research_dir = self.data_dir / "research"
        self.research_dir.mkdir(parents=True, exist_ok=True)
        
    @safe_execute(default=[])
    def analyze_knowledge_gaps(self, max_gaps: int = 5) -> List[Dict[str, Any]]:
        """
        Analisa interações para identificar lacunas de conhecimento.
        
        Args:
            max_gaps: Número máximo de gaps para retornar
            
        Returns:
            Lista de gaps de conhecimento prioritários
        """
        try:
            # Integrar com GapAnalyzer existente
            from .gap_analyzer import KnowledgeGapAnalyzer
            
            analyzer = KnowledgeGapAnalyzer(self.data_dir)
            gaps = analyzer.analyze_gaps()
            
            # Ordenar por prioridade e limitar
            gaps.sort(key=lambda x: x.get('priority', 0), reverse=True)
            return gaps[:max_gaps]
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de gaps: {e}")
            return []
    
    @safe_execute(default=False)
    def conduct_research(self, gap: Dict[str, Any]) -> bool:
        """
        Conduz pesquisa autônoma sobre um gap específico.
        
        Args:
            gap: Gap de conhecimento identificado
            
        Returns:
            True se a pesquisa foi bem-sucedida
        """
        try:
            topic = gap.get('topic', 'unknown')
            logger.info(f"🔍 Iniciando pesquisa sobre: {topic}")
            
            # 1. Pesquisa em fontes seguras (Hugging Face)
            hf_results = self._research_huggingface(topic)
            
            # 2. Busca web controlada (se habilitado)
            web_results = self._research_web_safe(topic)
            
            # 3. Síntese do conhecimento
            research_data = self._synthesize_knowledge(topic, hf_results, web_results)
            
            # 4. Salvar resultados
            success = self._save_research_results(topic, research_data)
            
            if success:
                logger.info(f"✅ Pesquisa concluída: {topic}")
                return True
            else:
                logger.error(f"❌ Falha ao salvar pesquisa: {topic}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na pesquisa de {gap.get('topic', 'unknown')}: {e}")
            return False
    
    @safe_execute(default=[])
    def _research_huggingface(self, topic: str) -> List[Dict[str, Any]]:
        """Pesquisa em datasets do Hugging Face."""
        try:
            import requests
            
            # Buscar datasets relevantes
            hf_url = f"https://huggingface.co/api/datasets?search={topic}&limit=3"
            response = requests.get(hf_url, timeout=10)
            
            if response.status_code == 200:
                datasets = response.json()
                return [{
                    'source': 'huggingface',
                    'dataset_id': dataset.get('id', ''),
                    'downloads': dataset.get('downloads', 0),
                    'likes': dataset.get('likes', 0)
                } for dataset in datasets]
            return []
            
        except Exception as e:
            logger.warning(f"⚠️ Pesquisa HF falhou para {topic}: {e}")
            return []
    
    @safe_execute(default=[])
    def _research_web_safe(self, topic: str) -> List[Dict[str, Any]]:
        """Pesquisa web controlada com fontes verificadas."""
        try:
            # Buscar apenas de fontes confiáveis
            search_query = f"{topic} site:github.com OR site:huggingface.co OR site:.org"
            
            # Usar Google search com fallback
            try:
                from googlesearch import search
                # Usar list para forçar execução do generator dentro do safe_execute
                results = list(search(search_query, num_results=2))
                return [{'source': 'web', 'url': url} for url in results]
            except (ImportError, Exception):
                logger.debug("googlesearch não disponível ou falhou")
                return []
                
        except Exception as e:
            logger.warning(f"⚠️ Pesquisa web falhou para {topic}: {e}")
            return []
    
    @safe_execute(default={})
    def _synthesize_knowledge(self, topic: str, hf_results: List, web_results: List) -> Dict[str, Any]:
        """Sintetiza resultados da pesquisa em conhecimento estruturado."""
        return {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'sources': {
                'huggingface_datasets': hf_results,
                'web_resources': web_results
            },
            'summary': f"Pesquisa autônoma sobre {topic}",
            'synthetic_data_generated': self._generate_synthetic_data(topic)
        }
    
    @safe_execute(default=False)
    def _save_research_results(self, topic: str, research_data: Dict[str, Any]) -> bool:
        """Salva resultados da pesquisa para uso futuro."""
        try:
            # Criar nome de arquivo seguro
            safe_topic = "".join(c if c.isalnum() else "_" for c in topic)
            filename = f"research_{safe_topic}_{int(time.time())}.json"
            filepath = self.research_dir / filename
            
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(research_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"💾 Pesquisa salva: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar pesquisa: {e}")
            return False
    
    @safe_execute(default=False)
    def _generate_synthetic_data(self, topic: str) -> bool:
        """Gera dados sintéticos para treinamento baseado na pesquisa."""
        try:
            # Diretório para dados sintéticos
            synth_dir = self.data_dir / "training_datasets" / "synthetic"
            synth_dir.mkdir(parents=True, exist_ok=True)
            
            # Criar dataset simples baseado no tópico
            synthetic_data = {
                'prompt': f'Explique o conceito de {topic}',
                'chosen': f'{topic} é um tópico importante que requer compreensão detalhada.',
                'rejected': f'{topic} é irrelevante e não merece atenção.'
            }
            
            filepath = synth_dir / f"{topic.replace(' ', '_')}_synthetic.jsonl"
            import json
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(synthetic_data, ensure_ascii=False) + '\n')
                
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Geração de dados sintéticos falhou: {e}")
            return False
    
    @safe_execute(default={})
    def get_research_status(self) -> Dict[str, Any]:
        """Retorna status das pesquisas realizadas."""
        try:
            research_files = list(self.research_dir.glob("research_*.json"))
            latest_time = 0
            if research_files:
                latest_time = max([f.stat().st_mtime for f in research_files])
                
            return {
                'total_research_files': len(research_files),
                'latest_research': latest_time,
                'research_dir': str(self.research_dir)
            }
        except Exception as e:
            return {'error': str(e)}
