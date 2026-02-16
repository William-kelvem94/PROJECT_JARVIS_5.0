"""
A BÃºssola de Estudo (Curiosity Engine)
Busca conhecimento acadÃªmico, gera perguntas e expande a base de conhecimento.
"""

import logging
import requests
import queue
import time
import xml.etree.ElementTree as ET

try:
    from src.utils.env_manager import get_model_for_tier
except ImportError:
    get_model_for_tier = lambda tier: 'deepseek-r1:8b'  # Fallback
from typing import List, Dict

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Logger setup
logger = logging.getLogger(__name__)

class CuriosityEngine:
    def __init__(self, memory_manager=None):
        self.study_backlog = queue.Queue()
        self.memory_manager = memory_manager
        self.is_studying = False
        self.skill_gaps = [] # Lista de habilidades faltando
        
        # Whitelist de APIs AcadÃªmicas
        self.ARXIV_API_URL = "http://export.arxiv.org/api/query"
        
        # Inicializar com alguns tÃ³picos padrÃ£o se vazio
        self.study_backlog.put("Artificial General Intelligence architecture")
        self.study_backlog.put("Self-supervised learning robotics")

    def register_skill_gap(self, feature_or_topic: str):
        """Registra uma falha ou um tÃ³pico de curiosidade abstrata (Como ser humano, etc)"""
        gap_msg = f"InvestigaÃ§Ã£o: {feature_or_topic}"
        if gap_msg not in self.skill_gaps:
            self.skill_gaps.append(gap_msg)
            self.study_backlog.put(gap_msg)
            logger.info(f"🧠 Nova curiosidade registrada: {feature_or_topic}. Pesquisa agendada.")
            
            # Armazenar no ChromaDB se disponÃ­vel (para persistÃªncia entre boots)
            if self.memory_manager:
                self.memory_manager.save_to_vault(
                    f"O sistema tentou mas não soube como executar: {feature_or_topic}", 
                    metadata={"type": "skill_gap", "status": "pending_research"}
                )

    def stop_study(self):
        self.is_studying = False

    def run_study_cycle(self):
        """Loop de estudo executado durante o sonho"""
        self.is_studying = True
        logger.info("📚 Iniciando ciclo de estudos...")
        
        # UI Signal
        try:
            from src.interface.ui_signals import ui_signals
            ui_signals.update_curiosity_list.emit(list(self.study_backlog.queue))
        except: pass

        while self.is_studying and not self.study_backlog.empty():
            try:
                topic = self.study_backlog.get(timeout=1)
                logger.info(f"🔎 Investigando tópico: {topic}")
                
                # UI Signal
                try: ui_signals.update_learning_status.emit(topic, True)
                except: pass

                # 1. Buscar conhecimento
                papers = self.fetch_academic_data(topic)
                
                for paper in papers:
                    if not self.is_studying: break
                    
                    title = paper['title']
                    summary = paper['summary']
                    full_text = f"Title: {title}\nSummary: {summary}\nLink: {paper['link']}"
                    
                    logger.info(f"📖 Lendo artigo: {title}")
                    
                    # 2. Salvar na Memória (RAG Hierárquico)
                    if self.memory_manager:
                        # Cofre (Deep Storage)
                        self.memory_manager.save_to_vault(full_text, metadata={"source": "arxiv", "topic": topic})
                        # Grafo (Fast Recall)
                        self.memory_manager.extract_semantic_graph(full_text)
                    
                    # 3. Gerar novas perguntas (Curiosidade)
                    self.generate_next_questions(full_text)
                    
                    # Refresh list UI
                    try: ui_signals.update_curiosity_list.emit(list(self.study_backlog.queue))
                    except: pass

                    time.sleep(5) # Pausa para respirar
                
                self.study_backlog.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Erro no ciclo de estudo: {e}")
                time.sleep(10)

        logger.info("💤 Ciclo de estudos finalizado (Backlog vazio ou interrupção).")
        self.is_studying = False
        try: ui_signals.update_learning_status.emit("Nenhum", False)
        except: pass

    def fetch_academic_data(self, topic: str) -> List[Dict]:
        """Busca artigos no arXiv"""
        try:
            params = {
                "search_query": f"all:{topic}",
                "start": 0,
                "max_results": 2,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
            response = requests.get(self.ARXIV_API_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                return self._parse_arxiv_response(response.content)
            else:
                logger.warning(f"Erro API arXiv: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Falha na conexÃ£o com arXiv: {e}")
            return []

    def _parse_arxiv_response(self, xml_content) -> List[Dict]:
        papers = []
        try:
            root = ET.fromstring(xml_content)
            # Namespace do Atom
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip()
                summary = entry.find('atom:summary', ns).text.strip()
                link = entry.find('atom:id', ns).text.strip()
                papers.append({'title': title, 'summary': summary, 'link': link})
        except Exception as e:
            logger.error(f"Erro no parsing XML: {e}")
        return papers

    def generate_next_questions(self, text_content: str):
        """Gera perguntas de follow-up usando Ollama (Tier Ultra)"""
        if not OLLAMA_AVAILABLE: return

        try:
            logger.info("ðŸ¤” Gerando novas perguntas de pesquisa...")
            prompt = (
                f"Analise o seguinte resumo cientÃ­fico:\n\n{text_content}\n\n"
                "Gere exatamente 3 perguntas tÃ©cnicas complexas que este texto NÃƒO respondeu, "
                "para investigarmos amanhÃ£. Formato: Apenas as perguntas, uma por linha."
            )
            
            # Usar modelo do tier ultra
            model_name = get_model_for_tier('ultra')
            response = ollama.chat(model=model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            content = response['message']['content']
            questions = [q.strip() for q in content.split('\n') if '?' in q]
            
            for q in questions[:3]:
                if len(q) > 10:
                    self.study_backlog.put(q)
                    logger.info(f"ðŸ’¡ Nova curiosidade adicionada: {q}")
                    
        except Exception as e:
            logger.error(f"Erro ao gerar perguntas: {e}")

# Instância Global placeholder
try:
    curiosity_engine = CuriosityEngine()
    logging.getLogger(__name__).info("✅ Curiosity Engine initialized successfully")
except Exception as e:
    logging.getLogger(__name__).warning(f"⚠️ Curiosity Engine failed to initialize: {e}")
    curiosity_engine = None
