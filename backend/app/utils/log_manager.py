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
        Saves a log entry to a JSON file named by the current date.
        """
        try:
            today = datetime.date.today().isoformat()
            file_path = os.path.join(self.base_dir, f"{today}.json")
            
            logs = []
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            
            # Ensure timestamp is present
            if "timestamp" not in log_entry:
                log_entry["timestamp"] = datetime.datetime.now().isoformat()
            
            logs.append(log_entry)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save persistent log: {e}")

    def list_log_dates(self):
        """Returns a list of dates that have logs."""
        files = os.listdir(self.base_dir)
        dates = [f.replace(".json", "") for f in files if f.endswith(".json")]
        dates.sort(reverse=True)
        return dates

    def get_logs_by_date(self, date_str: str):
        """Returns all logs for a specific date."""
        file_path = os.path.join(self.base_dir, f"{date_str}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

log_manager = LogManager.get_instance()
