import os
import logging
import threading
import time
from typing import Any, Dict, List, Callable

logger = logging.getLogger("jarvis-brain")

class PermissionErrorResolver:
    """Pequeno serviço que tenta sanar problemas de permissão automaticamente."""

    @staticmethod
    def check(path: str, mode: str = 'r') -> bool:
        try:
            with open(path, mode):
                pass
            return True
        except PermissionError as e:
            logger.error(f"Permissão negada ao acessar {path} ({mode}).")
            # tentativa simples de correção: ajustar permissões no sistema local
            try:
                os.chmod(path, 0o666)
                logger.warning(f"Permissões ajustadas para {path}.")
                return True
            except Exception as e2:
                logger.error(f"Falha ao ajustar permissões: {e2}")
                # se estiver no Windows, tentar icacls recursivamente para liberar
                if os.name == 'nt':
                    try:
                        subprocess.run(f"icacls \"{path}\" /grant *S-1-1-0:F /T", shell=True, check=False, capture_output=True)
                        logger.warning(f"Tentativa de icacls em {path}")
                    except Exception:
                        pass
                return False
        except FileNotFoundError:
            logger.warning(f"Arquivo não encontrado: {path}")
            return False
        except Exception as e:
            logger.error(f"Erro ao checar permissão: {e}")
            return False


import functools

def requires_permission(mode: str = 'r'):
    def decorator(fn: Callable[..., Any]):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            path = kwargs.get('file_path') or (args[1] if len(args) > 1 else None)
            if path and isinstance(path, str):
                if not PermissionErrorResolver.check(path, mode):
                    raise PermissionError(f"Acesso negado ou não pode corrigir permissão: {path}")
            return fn(*args, **kwargs)
        return wrapped
    return decorator


class NeuroSymbolicBrain:
    """Esqueleto para um cérebro neurosimbólico autônomo e adaptativo.

    - Módulos independentes de percepção, raciocínio e memória
    - Capaz de reconfigurar sua arquitetura em tempo de execução
    - Treinamento local segmentado (fine‑tuning de cada módulo)
    - Carrega configurações iniciais a partir de BRAIN_PLAN.md
    """

    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self.training_lock = threading.Lock()
        self._setup_default_modules()
        self._load_plan_file()

    def _load_plan_file(self):
        """Analisa BRAIN_PLAN.md e registra módulos listados ali, preservando o que já existe."""
        path = os.path.join(os.getcwd(), 'docs', 'brain_plan.md')
        if not os.path.exists(path):
            logger.info("Arquivo BRAIN_PLAN.md não encontrado; pulando carregamento inicial.")
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            modules_section = False
            for line in lines:
                if modules_section:
                    if not line.strip():
                        break
                    # captura nome em **nome** ou formato similar
                    import re
                    m = re.search(r"\*\*(.*?)\*\*", line)
                    if m:
                        name = m.group(1).strip()
                        if name and name not in self.modules:
                            self.modules[name] = {}
                            logger.info(f"Módulo '{name}' carregado via plano cerebral.")
                if line.startswith('## Módulos-chave'):
                    modules_section = True
        except Exception as e:
            logger.error(f"Falha ao ler plano cerebral: {e}")

    def _setup_default_modules(self):
        # cada módulo poderia ser um objeto com estados e parâmetros próprios
        # módulos básicos são inicializados com dicionários; posteriormente
        # podem receber chaves como 'model' contendo identificadores de API/arquivo.
        self.modules['perception'] = {}
        self.modules['reasoning'] = {}
        self.modules['memory'] = {}
        # módulos que representam conexões externas que não devem ser removidas
        self.modules['livekit'] = {'type': 'external', 'description': 'Conexão LiveKit para sessões de voz/áudio'}
        self.modules['gemini'] = {'type': 'external', 'model': 'gemini', 'description': 'Modelo Gemini via Google (usado pelo agente)'}
        # detectar hardware neurosimbólico (stub: procura pacote "neurosim")
        try:
            import neurosim
            self.modules['neurosim'] = {'type': 'hardware', 'description': 'Acelerador neurosimbólico local'}
            logger.info("Acelerador neurosimbólico detectado e registrado.")
        except ImportError:
            logger.debug("Nenhum acelerador neurosimbólico detectado.")
        logger.debug("Módulos cerebrais iniciais configurados com LiveKit e Gemini.")

    def register_module(self, name: str, module: Any):
        """Adiciona um componente ao cérebro que pode ser treinado separadamente."""
        self.modules[name] = module
        logger.warning(f"Módulo '{name}' registrado no cérebro. Módulo atual: {self.modules[name]}")
        if name in ('livekit','gemini'):
            logger.info(f"Módulo crítico externo '{name}' permanece ativo e não será alterado automaticamente.")

    def train_module(self, name: str, data: Any, epochs: int = 1) -> str:
        """Executa processo de treinamento local ou fine‑tuning para um único módulo.

        Se o módulo possuir um campo `'model'` válido (por exemplo um identificador de modelo
        aprovado pelo `ollama` ou outra API), ele será ajustado de fato com os dados fornecidos.
        Caso contrário, o método apenas registra a operação mas **não** finge qualquer progresso.
        """
        if name not in self.modules:
            return f"Módulo '{name}' não encontrado."
        module = self.modules[name]
        count = len(data) if hasattr(data, '__len__') else 'desconhecidos'
        logger.warning(f"Treinando módulo '{name}' por {epochs} épocas com {count} itens.")

        # tentativa de fine-tuning real, se houver modelo associado
        model_ref = module.get('model')
        if model_ref:
            try:
                # exemplo de integração com Ollama ou outro serviço local/externo
                # a API real pode variar; substitua pelos detalhes da sua infra
                if 'ollama' in globals() and ollama is not None:
                    resp = ollama.finetune(model=model_ref, data=data, epochs=epochs)
                    module['last_training'] = resp
                    logger.info(f"Fine-tuning concluído via Ollama para '{name}'.")
                    return f"Fine-tuning real de '{name}' concluído."
                # fallback para hardware neurosimbólico se disponível
                if self.modules.get('neurosim'):
                    # chamada fictícia à API neurosimbólica
                    logger.info(f"Enviando pedido de treino ao acelerador neurosimbólico para '{name}'.")
                    # digamos que neurosim.train(data, epochs) exista
                    try:
                        import neurosim
                        neurosim.train(data=data, epochs=epochs)
                        return f"Treinamento em hardware neurosimbólico concluído para '{name}'."
                    except Exception as e:
                        logger.error(f"Falha no acelerador neurosimbólico: {e}")
                        # continue para próximo bloco
                # se chegamos aqui, nenhuma engine disponível, apenas log
                logger.warning("Nenhuma engine de treinamento disponível; registrando sem ajustes.")
                return f"Registrado pedido de treinamento para '{name}', mas nenhuma engine disponível."
            except Exception as e:
                logger.error(f"Erro ao treinar módulo '{name}' com modelo '{model_ref}': {e}")
                return f"Erro no treinamento real: {e}"
        # se não há modelo, não fingimos nada, apenas confirmamos recepção dos dados
        return f"Dados de treinamento recebidos para '{name}', mas nenhum modelo associado."

    def self_modify_architecture(self, plan: Dict[str, Any]) -> str:
        """Aplica alterações na estrutura do cérebro com base em um plano.

        O plano descreve novos módulos, conexões ou parâmetros hiper.
        """
        logger.warning(f"Aplicando plano de auto-modificação: {plan}")
        # simulação de modificação
        for mod, conf in plan.items():
            self.modules.setdefault(mod, {})
            self.modules[mod].update(conf)
        return "Arquitetura atualizada conforme plano."

    def summarize_state(self) -> str:
        return f"Cérebro com {len(self.modules)} módulos: {list(self.modules.keys())}."

    def training_plan(self, topics: List[str]) -> Dict[str, Any]:
        """Gera um plano modular de treinamento baseado nos tópicos fornecidos."""
        plan = {}
        for topic in topics:
            plan[topic] = {'epochs': 3, 'priority': 'normal'}
        logger.info(f"Plano de treinamento gerado: {plan}")
        return plan


# instância global para uso pelo agente
brain = NeuroSymbolicBrain()
