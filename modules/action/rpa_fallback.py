"""
Sistema de Fallback Multi-Estratégia para Automação RPA
Implementa múltiplas estratégias de automação com fallback automático
"""

import os
import platform
import subprocess
import time
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from core.logger import logger
from modules.system.circuit_breaker import CircuitBreaker

class MultiStrategyAutomation:
    """
    Automação com múltiplas estratégias e fallback automático.
    Tenta diferentes métodos até encontrar um que funcione.
    """
    
    def __init__(self):
        self.system = platform.system()
        self.strategies = self._init_strategies()
        self.circuit_breakers = {}  # Circuit breaker por estratégia
        
        logger.info(f"MultiStrategyAutomation inicializado para {self.system}")
    
    def _init_strategies(self) -> List[Callable]:
        """Inicializa lista de estratégias de automação."""
        strategies = []
        
        # Estratégia 1: pyautogui (se disponível)
        try:
            import pyautogui
            strategies.append(self._try_pyautogui)
            logger.info("Estratégia pyautogui disponível")
        except ImportError:
            pass
        
        # Estratégia 2: Comandos CLI específicos do OS
        strategies.append(self._try_cli_commands)
        
        # Estratégia 3: Subprocess direto
        strategies.append(self._try_subprocess)
        
        # Estratégia 4: OS específico
        if self.system == "Windows":
            strategies.append(self._try_windows_specific)
        elif self.system == "Linux":
            strategies.append(self._try_linux_specific)
        elif self.system == "Darwin":
            strategies.append(self._try_macos_specific)
        
        return strategies
    
    def _get_circuit_breaker(self, strategy_name: str) -> CircuitBreaker:
        """Obtém ou cria circuit breaker para uma estratégia."""
        if strategy_name not in self.circuit_breakers:
            self.circuit_breakers[strategy_name] = CircuitBreaker(
                failure_threshold=3,
                timeout=30.0
            )
        return self.circuit_breakers[strategy_name]
    
    def execute_action(self, action: str, target: str, **kwargs) -> Dict[str, Any]:
        """
        Executa ação tentando múltiplas estratégias.
        
        Args:
            action: Tipo de ação ("open_app", "click", "type", etc.)
            target: Alvo da ação (nome do app, coordenadas, texto, etc.)
            **kwargs: Argumentos adicionais
        
        Returns:
            Resultado da execução
        """
        logger.info(f"Executando ação: {action} -> {target}")
        
        # Tentar cada estratégia até uma funcionar
        for strategy in self.strategies:
            strategy_name = strategy.__name__
            
            try:
                # Verificar circuit breaker
                cb = self._get_circuit_breaker(strategy_name)
                
                if cb.state.value == "open":
                    logger.debug(f"Circuit breaker aberto para {strategy_name}, pulando...")
                    continue
                
                # Tentar estratégia
                result = cb.call(strategy, action, target, **kwargs)
                
                if result and result.get("success"):
                    logger.info(f" Estratégia {strategy_name} funcionou!")
                    return {
                        "success": True,
                        "strategy": strategy_name,
                        "result": result
                    }
                    
            except Exception as e:
                logger.debug(f"Estratégia {strategy_name} falhou: {e}")
                continue
        
        # Nenhuma estratégia funcionou
        logger.error(f" Todas as estratégias falharam para {action} -> {target}")
        return {
            "success": False,
            "error": "Todas as estratégias de automação falharam",
            "action": action,
            "target": target
        }
    
    def _try_pyautogui(self, action: str, target: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Estratégia usando pyautogui."""
        try:
            import pyautogui
            
            if action == "open_app":
                # pyautogui não abre apps diretamente, retornar None
                return None
            
            elif action == "click":
                x, y = kwargs.get("x"), kwargs.get("y")
                if x is None or y is None:
                    return None
                button = kwargs.get("button", "left")
                pyautogui.click(x, y, button=button)
                return {"success": True}
            
            elif action == "type":
                interval = kwargs.get("interval", 0.1)
                pyautogui.write(target, interval=interval)
                return {"success": True}
            
            elif action == "press_key":
                pyautogui.press(target)
                return {"success": True}
            
            elif action == "hotkey":
                keys = kwargs.get("keys", target.split())
                pyautogui.hotkey(*keys)
                return {"success": True}
            
        except Exception as e:
            raise Exception(f"Erro no pyautogui: {e}")
        
        return None
    
    def _try_cli_commands(self, action: str, target: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Estratégia usando comandos CLI."""
        try:
            if action == "open_app":
                if self.system == "Windows":
                    subprocess.Popen(f"start {target}", shell=True)
                elif self.system == "Linux":
                    subprocess.Popen(target, shell=True)
                elif self.system == "Darwin":
                    subprocess.Popen(["open", "-a", target])
                else:
                    subprocess.Popen(target, shell=True)
                
                time.sleep(1)  # Aguardar app abrir
                return {"success": True}
        
        except Exception as e:
            raise Exception(f"Erro em CLI commands: {e}")
        
        return None
    
    def _try_subprocess(self, action: str, target: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Estratégia usando subprocess direto."""
        try:
            if action == "open_app":
                # Tentar executar diretamente
                app_path = kwargs.get("app_path")
                if app_path and os.path.exists(app_path):
                    subprocess.Popen(app_path)
                    return {"success": True}
                elif os.path.exists(target):
                    subprocess.Popen(target)
                    return {"success": True}
        
        except Exception as e:
            raise Exception(f"Erro em subprocess: {e}")
        
        return None
    
    def _try_windows_specific(self, action: str, target: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Estratégia específica para Windows."""
        try:
            if action == "open_app":
                # Tentar usar shell do Windows
                import win32api  # pywin32
                import win32con
                
                # Usar ShellExecute para abrir app
                win32api.ShellExecute(0, "open", target, "", "", win32con.SW_SHOWNORMAL)
                return {"success": True}
        except ImportError:
            # pywin32 não disponível, usar fallback
            pass
        except Exception as e:
            raise Exception(f"Erro em Windows specific: {e}")
        
        return None
    
    def _try_linux_specific(self, action: str, target: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Estratégia específica para Linux."""
        try:
            if action == "open_app":
                # Tentar xdg-open
                subprocess.Popen(["xdg-open", target])
                return {"success": True}
        except Exception as e:
            raise Exception(f"Erro em Linux specific: {e}")
        
        return None
    
    def _try_macos_specific(self, action: str, target: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Estratégia específica para macOS."""
        try:
            if action == "open_app":
                # Usar open command do macOS
                subprocess.Popen(["open", target])
                return {"success": True}
        except Exception as e:
            raise Exception(f"Erro em macOS specific: {e}")
        
        return None
    
    def get_available_strategies(self) -> List[str]:
        """Retorna lista de estratégias disponíveis."""
        return [s.__name__ for s in self.strategies]
    
    def get_strategy_health(self) -> Dict[str, Any]:
        """Retorna saúde de cada estratégia (circuit breakers)."""
        health = {}
        for name, cb in self.circuit_breakers.items():
            health[name] = cb.get_state()
        return health

