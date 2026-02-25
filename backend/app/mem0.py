from dotenv import load_dotenv
# simple in-memory client stub used during development/tests
import logging
import json
import os

# stub MemoryClient that mimics interface of external mem0 package
class MemoryClient:
    def __init__(self):
        self.store = {}

    def add(self, messages, user_id=None):
        if user_id not in self.store:
            self.store[user_id] = []
        self.store[user_id].extend(messages)
        return {"status": "ok"}

    def get_all(self, user_id=None):
        return self.store.get(user_id, [])

    def search(self, query, filters=None):
        # naive search: return all memories
        return {"results": self.store.get(filters.get("user_id"), [])}  if filters else []

# Configuração básica
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    def __init__(self, user_name="PedroLucas"):
        self.user_name = user_name
        # O MemoryClient busca a MEM0_API_KEY automaticamente do seu .env
        self.client = MemoryClient()

    def salvar_conversa(self):
        """Simula o envio de mensagens para a memória do Mem0"""
        print(f"\n🚀 Enviando novas memórias para: {self.user_name}...")
        
        messages = [
            {"role": "user", "content": "Ultimamente estou escutando muito Alee."},
            {"role": "assistant", "content": "Ótima escolha! Qual sua música favorita dele?"},
            {"role": "user", "content": "Minha favorita é Tempo do ouro e minha cor preferida é Preto."},
        ]

        # O método add extrai os fatos e salva no banco de dados
        self.client.add(messages, user_id=self.user_name)
        print("✅ Informações processadas e salvas com sucesso!")

    def buscar_memorias(self):
        """Recupera as informações que o Jarvis aprendeu"""
        print(f"\n🧠 Jarvis, o que você lembra sobre {self.user_name}?")
        
        query = f"Quais são as preferências e gostos de {self.user_name}?"
        
        # Na v2, usamos o dicionário filters
        response = self.client.search(query, filters={"user_id": self.user_name})

        # Tratamento da estrutura de resposta (lista ou dicionário)
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
    brain = JarvisMemory("PedroLucas")

    # 1. Primeiro enviamos a informação (Comente essa linha se já enviou uma vez e quer só testar a busca)
    brain.salvar_conversa()

    # 2. Depois buscamos o que foi aprendido
    historico = brain.buscar_memorias()

    # Exibição organizada
    if historico:
        print(json.dumps(historico, indent=2, ensure_ascii=False))
    else:
        print("❌ Nenhuma memória encontrada para este usuário.")
