"""
Productivity Tracker - Sistema de Rastreamento de Produtividade
Monitora uso de aplicaÃ§Ãµes e fornece insights
"""

import logging
import time
import psutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class ProductivityTracker:
    """Rastreador de produtividade"""

    def __init__(self, data_dir: str = "productivity_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.app_time: Dict[str, float] = defaultdict(float)
        self.app_categories: Dict[str, str] = {
            # Produtividade
            "code.exe": "Produtividade",
            "WINWORD.EXE": "Produtividade",
            "EXCEL.EXE": "Produtividade",
            "POWERPNT.EXE": "Produtividade",
            "notion.exe": "Produtividade",
            # ComunicaÃ§Ã£o
            "Teams.exe": "ComunicaÃ§Ã£o",
            "Slack.exe": "ComunicaÃ§Ã£o",
            "Discord.exe": "ComunicaÃ§Ã£o",
            "OUTLOOK.EXE": "ComunicaÃ§Ã£o",
            # NavegaÃ§Ã£o
            "chrome.exe": "NavegaÃ§Ã£o",
            "firefox.exe": "NavegaÃ§Ã£o",
            "msedge.exe": "NavegaÃ§Ã£o",
            # Entretenimento
            "Spotify.exe": "Entretenimento",
            "vlc.exe": "Entretenimento",
            # Desenvolvimento
            "python.exe": "Desenvolvimento",
            "node.exe": "Desenvolvimento",
            "git.exe": "Desenvolvimento",
        }

        self.current_app = None
        self.last_check = time.time()
        self.tracking_enabled = True

        self.daily_stats = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_time": 0,
            "productive_time": 0,
            "distraction_time": 0,
            "apps": {},
        }

        self._load_today_stats()

    def _load_today_stats(self):
        """Carrega estatÃ­sticas do dia atual"""
        today = datetime.now().strftime("%Y-%m-%d")
        stats_file = self.data_dir / f"stats_{today}.json"

        if stats_file.exists():
            try:
                with open(stats_file, "r") as f:
                    self.daily_stats = json.load(f)
                logger.info("âœ… EstatÃ­sticas do dia carregadas")
            except Exception as e:
                logger.error(f"Erro ao carregar estatÃ­sticas: {e}")

    def _save_stats(self):
        """Salva estatÃ­sticas do dia"""
        today = datetime.now().strftime("%Y-%m-%d")
        stats_file = self.data_dir / f"stats_{today}.json"

        try:
            with open(stats_file, "w") as f:
                json.dump(self.daily_stats, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar estatÃ­sticas: {e}")

    def get_active_window(self) -> Optional[str]:
        """Retorna nome da janela ativa"""
        try:
            import win32gui
            import win32process

            # Obter janela ativa
            hwnd = win32gui.GetForegroundWindow()

            # Obter PID do processo
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # Obter nome do processo
            process = psutil.Process(pid)
            return process.name()

        except ImportError:
            logger.warning(
                "âš ï¸ pywin32 nÃ£o disponÃ­vel. Instale: pip install pywin32"
            )
            return None
        except Exception:
            return None

    def update(self):
        """Atualiza rastreamento (chamar periodicamente)"""
        if not self.tracking_enabled:
            return

        current_time = time.time()
        elapsed = current_time - self.last_check

        # Obter aplicaÃ§Ã£o ativa
        active_app = self.get_active_window()

        if active_app:
            # Atualizar tempo da aplicaÃ§Ã£o
            self.app_time[active_app] += elapsed

            # Atualizar estatÃ­sticas diÃ¡rias
            if active_app not in self.daily_stats["apps"]:
                self.daily_stats["apps"][active_app] = {
                    "time": 0,
                    "category": self.app_categories.get(active_app, "Outros"),
                }

            self.daily_stats["apps"][active_app]["time"] += elapsed
            self.daily_stats["total_time"] += elapsed

            # Categorizar tempo
            category = self.app_categories.get(active_app, "Outros")
            if category in ["Produtividade", "Desenvolvimento"]:
                self.daily_stats["productive_time"] += elapsed
            elif category == "Entretenimento":
                self.daily_stats["distraction_time"] += elapsed

            self.current_app = active_app

        self.last_check = current_time

        # Salvar a cada 5 minutos
        if int(current_time) % 300 == 0:
            self._save_stats()

    def get_top_apps(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna apps mais usados"""
        sorted_apps = sorted(self.app_time.items(), key=lambda x: x[1], reverse=True)

        return [
            {
                "app": app,
                "time": time_spent,
                "time_formatted": self._format_time(time_spent),
                "category": self.app_categories.get(app, "Outros"),
            }
            for app, time_spent in sorted_apps[:limit]
        ]

    def get_category_breakdown(self) -> Dict[str, float]:
        """Retorna tempo por categoria"""
        category_time = defaultdict(float)

        for app, time_spent in self.app_time.items():
            category = self.app_categories.get(app, "Outros")
            category_time[category] += time_spent

        return dict(category_time)

    def get_productivity_score(self) -> float:
        """Calcula score de produtividade (0-100)"""
        total = self.daily_stats["total_time"]
        if total == 0:
            return 0

        productive = self.daily_stats["productive_time"]
        return (productive / total) * 100

    def get_daily_summary(self) -> Dict[str, Any]:
        """Retorna resumo do dia"""
        return {
            "date": self.daily_stats["date"],
            "total_time": self._format_time(self.daily_stats["total_time"]),
            "productive_time": self._format_time(self.daily_stats["productive_time"]),
            "distraction_time": self._format_time(self.daily_stats["distraction_time"]),
            "productivity_score": self.get_productivity_score(),
            "top_apps": self.get_top_apps(5),
            "category_breakdown": self.get_category_breakdown(),
        }

    def get_weekly_report(self) -> Dict[str, Any]:
        """Gera relatÃ³rio semanal"""
        today = datetime.now()
        week_start = today - timedelta(days=7)

        weekly_data = []

        for i in range(7):
            date = week_start + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            stats_file = self.data_dir / f"stats_{date_str}.json"

            if stats_file.exists():
                try:
                    with open(stats_file, "r") as f:
                        daily_data = json.load(f)
                        weekly_data.append(daily_data)
                except Exception:
                    pass

        # Calcular mÃ©dias
        if not weekly_data:
            return {"error": "Sem dados da semana"}

        total_time = sum(d["total_time"] for d in weekly_data)
        productive_time = sum(d["productive_time"] for d in weekly_data)

        return {
            "period": f"{week_start.strftime('%Y-%m-%d')} a {today.strftime('%Y-%m-%d')}",
            "total_time": self._format_time(total_time),
            "avg_daily_time": self._format_time(total_time / len(weekly_data)),
            "productivity_score": (
                (productive_time / total_time * 100) if total_time > 0 else 0
            ),
            "days_tracked": len(weekly_data),
        }

    def _format_time(self, seconds: float) -> str:
        """Formata tempo em horas e minutos"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes}min"

    def enable_tracking(self):
        """Ativa rastreamento"""
        self.tracking_enabled = True
        logger.info("âœ… Rastreamento de produtividade ativado")

    def disable_tracking(self):
        """Desativa rastreamento"""
        self.tracking_enabled = False
        self._save_stats()
        logger.info("â¸ï¸ Rastreamento de produtividade pausado")


# InstÃ¢ncia global removida para evitar execuÃ§Ã£o durante import
# productivity_tracker = ProductivityTracker()


# Exemplo de uso
if __name__ == "__main__":
    import time

    print("Rastreando produtividade por 60 segundos...")

    for i in range(60):
        productivity_tracker.update()
        time.sleep(1)

        if i % 10 == 0:
            summary = productivity_tracker.get_daily_summary()
            print(f"\nðŸ“Š Resumo (apÃ³s {i}s):")
            print(f"  Tempo total: {summary['total_time']}")
            print(f"  Score: {summary['productivity_score']:.1f}%")

    print("\nðŸ“ˆ RelatÃ³rio Final:")
    summary = productivity_tracker.get_daily_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
