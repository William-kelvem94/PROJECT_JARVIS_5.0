from dotenv import load_dotenv
from loguru import logger
import json
import os

# simple in-memory client stub used during development/tests
# simple in-memory client with file persistence

class MemoryClient:
    def __init__(self):
        # Caminho para persistência de dados
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "memories.json")
        self.store = self._load()

    def _load(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar memórias: {e}")
        return {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar memórias: {e}")

    def add(self, messages, user_id=None):
        if user_id not in self.store:
            self.store[user_id] = []
        
        # Converte mensagens para um formato simplificado de "fatos"
        for msg in messages:
            if isinstance(msg, dict) and "content" in msg:
                import datetime
                self.store[user_id].append({
                    "memory": msg["content"],
                    "updated_at": datetime.datetime.now().isoformat()
                })
        
        self._save()
        return {"status": "ok"}

    def get_all(self, user_id=None):
        return self.store.get(user_id, [])

    def search(self, query, filters=None):
        user_id = filters.get("user_id") if filters else None
        return {"results": self.store.get(user_id, [])} if user_id else []

# Configuração básica
load_dotenv()

# async wrapper around MemoryClient so agent code can await
class AsyncMemoryClient:
    def __init__(self):
        self._client = MemoryClient()

    async def get_all(self, user_id=None):
        return self._client.get_all(user_id=user_id)

    async def search(self, query, filters=None):
        return self._client.search(query, filters=filters)

    async def add(self, messages, user_id=None):
        return self._client.add(messages, user_id=user_id)


class JarvisMemory:
    def __init__(self, user_name="Chefe"):
        self.user_name = user_name
        self.client = MemoryClient()

    def salvar_conversa(self):
        """Simula o envio de mensagens para a memória do Mem0"""
        logger.info(f"\n🚀 Enviando novas memórias para: {self.user_name}...")
        
        messages = [
            {"role": "user", "content": "Ultimamente estou escutando muito Alee."},
            {"role": "assistant", "content": "Ótima escolha! Qual sua música favorita dele?"},
            {"role": "user", "content": "Minha favorita é Tempo do ouro e minha cor preferida é Preto."},
        ]

        self.client.add(messages, user_id=self.user_name)
        logger.success("✅ Informações processadas e salvas com sucesso!")

    def buscar_memorias(self):
        """Recupera as informações que o Jarvis aprendeu"""
        logger.info(f"\n🧠 Jarvis, o que você lembra sobre {self.user_name}?")
        
        query = f"Quais são as preferências e gostos de {self.user_name}?"
        response = self.client.search(query, filters={"user_id": self.user_name})

        results = response["results"] if isinstance(response, dict) and "results" in response else response

        memories_list = []
        for item in results:
            if isinstance(item, dict):
                memories_list.append({
                    "fato": item.get("memory"),
                    "data": item.get("updated_at")
                })
        
        return memories_list

# --- EXECUÇÃO ---
if __name__ == "__main__":
    brain = JarvisMemory("Chefe")
    brain.salvar_conversa()
    historico = brain.buscar_memorias()
    if historico:
        logger.debug(json.dumps(historico, indent=2, ensure_ascii=False))
    else:
        logger.warning("❌ Nenhuma memória encontrada para este usuário.")
