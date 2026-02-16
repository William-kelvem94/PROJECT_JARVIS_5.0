"""
JARVIS 5.0 - Instinct Engine (Quick Response Layer)
==================================================
Responsabilidade: Processar comandos triviais via Regex para latência zero.
Evita chamadas desnecessárias de LLM (economia de tokens e processamento).

Ideia inspirada no PVA (Personal Voice Assistent).
"""

import logging
import re
import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class InstinctEngine:
    """
    Camada de 'Instinto' do JARVIS.
    Processa comandos de alta frequência e baixa complexidade.
    """

    def __init__(self):
        self.patterns = self._init_patterns()
        logger.info("✅ InstinctEngine inicializado (Camada de Latência Zero)")

    def _init_patterns(self) -> List[Dict[str, Any]]:
        """Inicializa os padrões de regex para comandos rápidos"""
        return [
            # 1. TEMPO E DATA
            {
                "regex": r"(que horas são|qual a hora|hora atual|me diga a hora)",
                "handler": self._get_time,
                "name": "get_time",
            },
            {
                "regex": r"(que dia é hoje|qual a data|dia de hoje|que dia é)",
                "handler": self._get_date,
                "name": "get_date",
            },
            # 2. SISTEMA E HARDWARE (VOLUME)
            {
                "regex": r"volume (em|para)? (\d+)(%)?",
                "handler": self._set_volume,
                "name": "set_volume",
            },
            {
                "regex": r"(muta|silencia|mutar|silenciar) (o )?(som|áudio|volume)",
                "handler": self._mute_system,
                "name": "mute_system",
            },
            {
                "regex": r"(desmuta|ativar) (o )?(som|áudio|volume)",
                "handler": self._unmute_system,
                "name": "unmute_system",
            },
            # 3. STATUS DO JARVIS
            {
                "regex": r"(quem é você|qual o seu nome|identifique-se|quem é vc)",
                "handler": self._identify_self,
                "name": "identify_self",
            },
            {
                "regex": r"(status|saúde) (do )?(sistema|jarvis|componentes)",
                "handler": self._get_system_status,
                "name": "system_status",
            },
            # 4. CONTROLE DE INTERFACE (MODO NOTURNO/HUD)
            {
                "regex": r"(ativar|ligar|modo) (noturno|escuro)",
                "handler": self._enable_night_mode,
                "name": "enable_night_mode",
            },
            {
                "regex": r"(desativar|desligar|sair do) (modo )?(noturno|escuro)",
                "handler": self._disable_night_mode,
                "name": "disable_night_mode",
            },
            # 5. DEPURAÇÃO RÁPIDA
            {
                "regex": r"(qual|me diga|ver) (o )?(último )?(erro|falha|problema)",
                "handler": self._get_last_error,
                "name": "get_last_error",
            },
        ]

    async def check(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Verifica se o comando coincide com algum padrão de instinto.
        Retorna a resposta/ação se houver match, senão None.
        """
        cmd_clean = command.lower().strip()

        for p in self.patterns:
            match = re.search(p["regex"], cmd_clean)
            if match:
                logger.info(f"⚡ Instinct Match: {p['name']}")
                return await p["handler"](match, command)

        return None

    # --- HANDLERS ---

    async def _get_time(self, match, original_cmd) -> Dict[str, Any]:
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        return {
            "thought": "Comando de hora detectado via camada de instinto.",
            "final_answer": f"São precisamente {time_str}, Senhor.",
            "actions": [],
            "instinct": True,
        }

    async def _get_date(self, match, original_cmd) -> Dict[str, Any]:
        now = datetime.datetime.now()
        dias_semana = [
            "segunda-feira",
            "terça-feira",
            "quarta-feira",
            "quinta-feira",
            "sexta-feira",
            "sábado",
            "domingo",
        ]
        dia_nome = dias_semana[now.weekday()]
<<<<<<< HEAD
<<<<<<< Updated upstream
        date_str = now.strftime(f"%d de %B") # Tradução de mês precisaria de locale, mas vamos simplificar
=======
        date_str = now.strftime(  # noqa: F841
            "%d de %B"
        )  # Tradução de mês precisaria de locale, mas vamos simplificar
>>>>>>> Stashed changes
=======
        date_str = now.strftime(
            "%d de %B"
        )  # Tradução de mês precisaria de locale, mas vamos simplificar
>>>>>>> dev-new-version
        return {
            "thought": "Comando de data detectado via camada de instinto.",
            "final_answer": f"Hoje é {dia_nome}, dia {now.day} de {now.month}, Senhor.",
            "actions": [],
            "instinct": True,
        }

    async def _set_volume(self, match, original_cmd) -> Dict[str, Any]:
        volume = int(match.group(2))
        if volume > 100:
            volume = 100
        if volume < 0:
            volume = 0

        # Ação será executada pelo ActionHandler, mas geramos a resposta aqui
        return {
            "thought": f"Ajustando volume para {volume}% via instinto.",
            "actions": [{"action": "set_volume", "level": volume}],
            "final_answer": f"Volume ajustado para {volume}%, Senhor.",
            "instinct": True,
        }

    async def _mute_system(self, match, original_cmd) -> Dict[str, Any]:
        return {
            "thought": "Mutando áudio do sistema via instinto.",
            "actions": [{"action": "mute_audio"}],
            "final_answer": "Áudio silenciado, Senhor.",
            "instinct": True,
        }

    async def _unmute_system(self, match, original_cmd) -> Dict[str, Any]:
        return {
            "thought": "Ativando áudio do sistema via instinto.",
            "actions": [{"action": "unmute_audio"}],
            "final_answer": "Áudio reativado, Senhor.",
            "instinct": True,
        }

    async def _identify_self(self, match, original_cmd) -> Dict[str, Any]:
        return {
            "thought": "Identificação solicitada.",
            "final_answer": "Eu sou o JARVIS 5.0, sua inteligência artificial soberana e evolutiva, Senhor.",
            "actions": [],
            "instinct": True,
        }

    async def _get_system_status(self, match, original_cmd) -> Dict[str, Any]:
        # Tenta pegar info do hardware_manager se disponível via singleton
        status_msg = "Sistemas operacionais dentro dos parâmetros normais, Senhor."
        return {
            "thought": "Status do sistema solicitado via instinto.",
            "final_answer": status_msg,
            "actions": [{"action": "show_performance_stats"}],
            "instinct": True,
        }

    async def _enable_night_mode(self, match, original_cmd) -> Dict[str, Any]:
        return {
            "thought": "Ativando Modo Noturno via instinto.",
            "actions": [{"action": "set_ui_mode", "mode": "night"}],
            "final_answer": "Ativando protocolos de discrição. Modo Noturno ativado, Senhor.",
            "instinct": True,
        }

    async def _disable_night_mode(self, match, original_cmd) -> Dict[str, Any]:
        return {
            "thought": "Desativando Modo Noturno via instinto.",
            "actions": [{"action": "set_ui_mode", "mode": "standard"}],
            "final_answer": "Retornando à iluminação padrão, Senhor.",
            "instinct": True,
        }

    async def _get_last_error(self, match, original_cmd) -> Dict[str, Any]:
        # Busca no log se possível, ou usa uma variável global de erros
        return {
            "thought": "Solicitação de diagnóstico de erro via instinto.",
            "actions": [{"action": "get_last_system_error"}],
            "final_answer": "Analisando os registros de falha... Um momento, Senhor.",
            "instinct": True,
        }


# Singleton instance
instinct_engine = InstinctEngine()
