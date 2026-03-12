import os
import json
from loguru import logger
import asyncio

class WorkflowEngine:
    _instance = None

    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "workflows")
        os.makedirs(self.base_dir, exist_ok=True)
        # { name: { "type": "file", "target": "path", "last_state": timestamp, "callback": func } }
        self.watchdogs = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = WorkflowEngine()
        return cls._instance

    def register_macro(self, name: str, steps: list):
        """
        Saves a macro definition to JSON.
        Steps should be a list of dicts: {"tool": "tool_name", "args": {}}
        """
        try:
            file_path = os.path.join(self.base_dir, f"{name}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(steps, f, ensure_ascii=False, indent=2)
            logger.success(f"Macro '{name}' registrada com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar macro {name}: {e}")
            return False

    def get_macro(self, name: str):
        file_path = os.path.join(self.base_dir, f"{name}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_macros(self):
        files = os.listdir(self.base_dir)
        return [f.replace(".json", "") for f in files if f.endswith(".json")]

    def add_watchdog(self, name: str, config: dict):
        """
        Adiciona um monitoramento em background.
        config: { "type": "file"|"web", "target": str, "condition": str }
        """
        if config["type"] == "file":
            if os.path.exists(config["target"]):
                config["last_state"] = os.path.getmtime(config["target"])
        
        self.watchdogs[name] = config
        logger.info(f"Watchdog '{name}' ativado para {config['target']}")
        return True

    async def execute_step(self, step, tools_instance):
        """Executa um passo individual do workflow."""
        try:
            if isinstance(step, str):
                return tools_instance.execute_command(step)
            elif isinstance(step, dict):
                if "if" in step:
                    # Lógica de decisão
                    condition = step["if"]
                    logger.info(f"[Workflow] Avaliando condição: {condition}")
                    # Simples verificação por enquanto (expansível com eval/IA)
                    if await self._check_condition(condition, tools_instance):
                        return await self.execute_step(step.get("then"), tools_instance)
                    else:
                        return await self.execute_step(step.get("else"), tools_instance)
                
                cmd = step.get("cmd")
                if cmd:
                    return tools_instance.execute_command(cmd)
                
                tool_name = step.get("tool")
                if tool_name:
                    func = getattr(tools_instance, tool_name, None)
                    if func:
                        return await func(**step.get("args", {}))
            return None
        except Exception as e:
            logger.error(f"Erro ao executar passo: {e}")
            return f"Erro: {e}"

    async def _check_condition(self, condition: str, tools_instance) -> bool:
        """Avalia uma condição simples."""
        # Se contiver 'perception', checa o snapshot
        if "perception." in condition:
            from ..perception.perception_manager import perception_manager
            snap = perception_manager.get_snapshot()
            key = condition.split(".")[1]
            return bool(snap.get(key))
        # Se contiver 'file_exists', checa o disco
        if "file_exists:" in condition:
            path = condition.split(":")[1].strip()
            return os.path.exists(path)
        return False

    async def check_watchdogs(self):
        """Executado periodicamente pelo agentes.py"""
        alerts = []
        for name, cfg in self.watchdogs.items():
            try:
                if cfg["type"] == "file":
                    if os.path.exists(cfg["target"]):
                        mtime = os.path.getmtime(cfg["target"])
                        if mtime > cfg["last_state"]:
                            cfg["last_state"] = mtime
                            alerts.append({
                                "title": "Watchdog: Arquivo Alterado",
                                "detail": f"O arquivo {cfg['target']} foi modificado.",
                                "watchdog_name": name
                            })
            except Exception as e:
                logger.error(f"Erro ao verificar watchdog {name}: {e}")
        return alerts

workflow_engine = WorkflowEngine.get_instance()
