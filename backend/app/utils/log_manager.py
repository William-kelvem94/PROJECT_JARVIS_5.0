import os
import json
import datetime
from loguru import logger

class LogManager:
    _instance = None

    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "logs")
        os.makedirs(self.base_dir, exist_ok=True)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = LogManager()
        return cls._instance

    def save_log(self, log_entry: dict):
        """
        Saves a log entry to a JSONL file (one JSON object per line) named by the current date.
        This is much faster and safer than reading/rewriting the whole JSON.
        """
        try:
            today = datetime.date.today().isoformat()
            file_path = os.path.join(self.base_dir, f"{today}.jsonl")
            
            # Ensure timestamp is present
            if "timestamp" not in log_entry:
                log_entry["timestamp"] = datetime.datetime.now().isoformat()
            
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                
        except Exception as e:
            logger.error(f"Failed to save append log: {e}")

    def list_log_dates(self):
        """Returns a list of dates that have logs."""
        files = os.listdir(self.base_dir)
        dates = [f.replace(".jsonl", "").replace(".json", "") for f in files if (f.endswith(".jsonl") or f.endswith(".json"))]
        dates.sort(reverse=True)
        return dates

    def get_logs_by_date(self, date_str: str):
        """Returns all logs for a specific date (handles both JSON and JSONL)."""
        file_path_jsonl = os.path.join(self.base_dir, f"{date_str}.jsonl")
        file_path_json = os.path.join(self.base_dir, f"{date_str}.json")
        
        logs = []
        try:
            # Tenta JSONL primeiro (padrão novo)
            if os.path.exists(file_path_jsonl):
                with open(file_path_jsonl, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                logs.append(json.loads(line))
                            except: continue
                return logs
            
            # Fallback para JSON antigo
            if os.path.exists(file_path_json):
                with open(file_path_json, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler logs de {date_str}: {e}")
            
        return []

log_manager = LogManager.get_instance()
