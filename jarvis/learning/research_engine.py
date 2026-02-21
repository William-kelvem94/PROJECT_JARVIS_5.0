# -*- coding: utf-8 -*-
import logging
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("JARVIS-RESEARCH-ENGINE")

class ResearchEngine:
    """
    Motor de pesquisa autônomo.
    Busca informações sobre lacunas de conhecimento e as transforma em 
    datasets para auto-v-treinamento (Fine-Tuning).
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.research_path = data_dir / "learning" / "research_results"
        self.training_data_path = data_dir / "learning" / "fine_tuning_sets"
        
        # Ensure directories
        self.research_path.mkdir(parents=True, exist_ok=True)
        self.training_data_path.mkdir(parents=True, exist_ok=True)

    def analyze_knowledge_gaps(self, limit: int = 3, priority_topics: List[str] = None) -> List[Dict[str, Any]]:
        """Identifica o que o sistema não sabe, priorizando temas específicos."""
        gaps = []
        
        # Se houver tópicos prioritários, eles vêm primeiro
        if priority_topics:
            for topic in priority_topics:
                gaps.append({
                    "topic": topic,
                    "context": "Prioridade definida pelo usuário para evolução do sistema.",
                    "timestamp": time.time()
                })

        interaction_file = self.data_dir / "logs" / "agent_interactions.jsonl"
        
        if not interaction_file.exists():
            return []

        try:
            with open(interaction_file, "r", encoding="utf-8") as f:
                lines = f.readlines()[-100:] # Analisar últimas 100 interações
                for line in lines:
                    data = json.loads(line)
                    # Heurística: respostas curtas demais ou que contêm "não sei", "erro"
                    resp = data.get("assistant", "").lower()
                    if any(x in resp for x in ["não sei", "desculpe", "erro", "falha"]):
                        gaps.append({
                            "topic": data.get("user"),
                            "context": data.get("assistant"),
                            "timestamp": data.get("ts")
                        })
            
            # Ordenar por relevância (opcional) e limitar
            return gaps[:limit]
        except Exception as e:
            logger.error(f"Erro ao analisar gaps: {e}")
            return []

    def conduct_research(self, gap: Dict[str, Any]) -> bool:
        """Executa a pesquisa massiva sobre o tópico e sub-tópicos."""
        main_topic = gap.get("topic")
        logger.info(f"🚀 Iniciando Pesquisa MASSIVA: {main_topic}")
        
        try:
            from jarvis.dashboard_server import log_task
            log_task(f"🧬 Sincronizando Córtex sobre: {main_topic}")
        except: pass
        
        # 1. Gerar Sub-tópicos dinâmicos via LLM
        sub_topics = []
        try:
            from jarvis.ollama_client import query_ollama
            from jarvis.config_manager import config
            model = config.get("OLLAMA_MODEL") or "llama3"
            prompt = (f"Como um arquiteto de conhecimento, decomponha o tópico '{main_topic}' em 4 sub-tópicos técnicos e específicos "
                      "para pesquisa profunda. Retorne APENAS os nomes dos tópicos separados por vírgula.")
            resp = query_ollama(model, prompt)
            if resp and "," in resp:
                sub_topics = [s.strip() for s in resp.split(",") if s.strip()][:4]
        except Exception as e:
            logger.debug(f"Falha ao gerar sub-tópicos via LLM: {e}")

        if not sub_topics:
            sub_topics = [
                f"{main_topic}: Fundamentos e Teoria",
                f"{main_topic}: Melhores Práticas e Padrões",
                f"{main_topic}: Casos de Uso Avançados",
                f"{main_topic}: Depuração e Performance"
            ]
        
        for i, topic in enumerate(sub_topics):
            logger.info(f"🔎 Minerando sub-tópico: {topic}")
            try: log_task(f"📝 Processando fatia {i+1}/{len(sub_topics)}: {topic}")
            except: pass
            
            # Realizar Pesquisa Real Multi-Fonte
            try:
                from jarvis.web_utils import search_online
                content = search_online(topic)
            except Exception as e:
                logger.error(f"Falha na missão de pesquisa para {topic}: {e}")
                content = f"Dados parciais sobre {topic} coletados durante falha de conexão."
                try: log_task(f"❌ Erro na pesquisa: {e}")
                except: pass

            # NOVO: Salvar no Banco de Dados SQLite para o Grafo Real
            try:
                from jarvis.database import db
                db.add_knowledge(topic, content, category="Research")
            except Exception as e:
                logger.error(f"Erro ao persistir no banco: {e}")

            # Salvar resultado bruto
            result_file = self.research_path / f"mass_{int(time.time()*1000)}.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump({"topic": topic, "content": content}, f, indent=4, ensure_ascii=False)
            
            # 2. Gerar MÚLTIPLOS Pares de Treinamento por sub-tópico (Aumenta o volume)
            self._generate_massive_dataset(topic, content)
        
        return True

    def _generate_massive_dataset(self, topic: str, content: str):
        """Gera volume de dados (10+ pares) para fine-tuning real."""
        dataset_file = self.training_data_path / "massive_train.jsonl"
        
        # Simulamos a geração de 5 variações de perguntas sobre o mesmo conteúdo
        variations = [
            f"Como implementar {topic} de forma eficiente?",
            f"Quais são os principais conceitos de {topic}?",
            f"Explique a arquitetura por trás de {topic}.",
            f"Dê um exemplo prático de {topic}.",
            f"Quais os erros comuns ao lidar com {topic}?"
        ]

        with open(dataset_file, "a", encoding="utf-8") as f:
            for instr in variations:
                pair = {
                    "instruction": instr,
                    "input": "",
                    "output": f"Baseado no conhecimento de JARVIS: {content}"
                }
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
            
        logger.info(f"📦 +5 Amostras adicionadas ao dataset para: {topic}")

    def get_research_status(self) -> Dict[str, Any]:
        """Estatísticas do motor de pesquisa."""
        return {
            "total_research_files": len(list(self.research_path.glob("*.json"))),
            "training_samples_ready": sum(1 for _ in open(self.training_data_path / "auto_train.jsonl")) if (self.training_data_path / "auto_train.jsonl").exists() else 0
        }
