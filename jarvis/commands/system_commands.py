"""
Comandos de sistema para JARVIS
"""

import subprocess
import platform
import re
from typing import Dict, Any

from ..core.logger import default_logger


class SystemCommands:
    """Comandos relacionados ao sistema operacional"""
    
    def __init__(self, config: Dict[str, Any], speech_engine):
        self.config = config
        self.speech_engine = speech_engine
        self.logger = default_logger
        
        # Mapa de programas por sistema operacional
        self.programs = self._get_system_programs()
    
    def _get_system_programs(self) -> Dict[str, tuple]:
        """Retorna programas disponíveis baseado no SO"""
        is_windows = platform.system() == 'Windows'
        
        return {
            'navegador': (
                'chrome.exe' if is_windows else 'google-chrome',
                'navegador'
            ),
            'calculadora': (
                'calc.exe' if is_windows else 'gnome-calculator',
                'calculadora'
            ),
            'bloco de notas': (
                'notepad.exe' if is_windows else 'gedit',
                'bloco de notas'
            ),
            'editor': (
                'notepad.exe' if is_windows else 'gedit',
                'editor de texto'
            ),
            'explorer': (
                'explorer.exe' if is_windows else 'nautilus',
                'explorador de arquivos'
            ),
            'gerenciador de arquivos': (
                'explorer.exe' if is_windows else 'nautilus',
                'gerenciador de arquivos'
            ),
            'cmd': (
                'cmd.exe' if is_windows else 'gnome-terminal',
                'terminal'
            ),
            'terminal': (
                'cmd.exe' if is_windows else 'gnome-terminal',
                'terminal'
            ),
            'prompt': (
                'cmd.exe' if is_windows else 'gnome-terminal',
                'prompt de comando'
            )
        }
    
    def open_program(self, command_text: str) -> bool:
        """Abre programas no sistema"""
        try:
            # Procurar programa correspondente
            for program_key, (executable, friendly_name) in self.programs.items():
                if program_key in command_text:
                    try:
                        # Tentar abrir o programa
                        subprocess.Popen(executable, shell=True)
                        
                        self.speech_engine.speak(
                            f"Pronto! Abrindo o {friendly_name} para você.",
                            emotion='entusiasta',
                            final_pause=1.2
                        )
                        
                        self.logger.command_event(f"open_{program_key}", "success")
                        return True
                        
                    except FileNotFoundError:
                        self.speech_engine.speak(
                            f"Ops! Não encontrei o {friendly_name} no seu sistema.",
                            emotion='preocupado',
                            final_pause=1.3
                        )
                        
                        self.logger.command_event(f"open_{program_key}", "not_found")
                        return True
                    
                    except Exception as e:
                        self.speech_engine.speak(
                            f"Erro ao tentar abrir o {friendly_name}: {str(e)}",
                            emotion='preocupado'
                        )
                        
                        self.logger.error(f"Erro ao abrir {program_key}: {e}")
                        return True
            
            # Programa não reconhecido
            self.speech_engine.speak(
                "Desculpe, mas não reconheci qual programa você quer abrir. "
                "Tente dizer 'abrir navegador' ou 'abrir calculadora'.",
                emotion='pensativo'
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no comando abrir: {e}")
            self.speech_engine.speak(
                "Ocorreu um erro ao tentar abrir o programa.",
                emotion='preocupado'
            )
            return True
    
    def execute_command(self, command_text: str) -> bool:
        """Executa comandos do sistema"""
        try:
            # Extrair comando após "executar"
            cmd_patterns = [
                r'executar (.+)',
                r'execute (.+)',
                r'rodar (.+)',
                r'rode (.+)'
            ]
            
            extracted_cmd = None
            for pattern in cmd_patterns:
                match = re.search(pattern, command_text)
                if match:
                    extracted_cmd = match.group(1).strip()
                    break
            
            if extracted_cmd:
                # Validação básica de segurança
                if self._is_safe_command(extracted_cmd):
                    try:
                        # Executar comando baseado no SO
                        if platform.system() == 'Windows':
                            result = subprocess.run(
                                ['cmd', '/c', extracted_cmd],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                        else:
                            result = subprocess.run(
                                extracted_cmd,
                                shell=True,
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                        
                        if result.returncode == 0:
                            self.speech_engine.speak(
                                "Pronto! Comando executado com sucesso.",
                                emotion='entusiasta'
                            )
                            
                            # Log da saída se não for muito longa
                            if result.stdout and len(result.stdout) < 500:
                                self.logger.debug(f"Saída do comando: {result.stdout}")
                        else:
                            self.speech_engine.speak(
                                f"O comando foi executado, mas retornou um erro. Código: {result.returncode}",
                                emotion='preocupado'
                            )
                        
                        self.logger.command_event(f"execute: {extracted_cmd}", "completed")
                        
                    except subprocess.TimeoutExpired:
                        self.speech_engine.speak(
                            "O comando demorou muito para executar e foi cancelado.",
                            emotion='preocupado'
                        )
                    
                    except Exception as e:
                        self.speech_engine.speak(
                            f"Ops! Não consegui executar o comando. Erro: {str(e)}",
                            emotion='preocupado'
                        )
                        self.logger.error(f"Erro ao executar comando '{extracted_cmd}': {e}")
                
                else:
                    self.speech_engine.speak(
                        "Desculpe, mas não posso executar esse comando por questões de segurança.",
                        emotion='preocupado'
                    )
                    self.logger.warning(f"Comando bloqueado por segurança: {extracted_cmd}")
            
            else:
                self.speech_engine.speak(
                    "Qual comando do sistema você gostaria que eu executasse?",
                    emotion='pensativo'
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no comando executar: {e}")
            self.speech_engine.speak(
                "Ocorreu um erro ao tentar executar o comando.",
                emotion='preocupado'
            )
            return True
    
    def _is_safe_command(self, command: str) -> bool:
        """Verifica se um comando é seguro para executar"""
        command_lower = command.lower()
        
        # Lista de comandos perigosos
        dangerous_commands = [
            'rm -rf', 'del /f', 'format', 'fdisk', 'mkfs',
            'shutdown', 'reboot', 'halt', 'poweroff',
            'dd if=', 'sudo rm', 'sudo del', 'reg delete',
            'taskkill /f', 'kill -9', 'killall',
            'chmod 777', 'chown root', 'passwd',
            'wget', 'curl', 'nc ', 'netcat',
            'python -c', 'eval', 'exec',
            'powershell', 'cmd /c', 'bash -c'
        ]
        
        # Verificar se contém comandos perigosos
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return False
        
        # Lista de comandos seguros
        safe_commands = [
            'dir', 'ls', 'pwd', 'cd', 'echo', 'cat', 'type',
            'date', 'time', 'whoami', 'hostname', 'ipconfig',
            'ping', 'tracert', 'nslookup', 'systeminfo',
            'tasklist', 'ps', 'top', 'df', 'du', 'free',
            'uname', 'which', 'where', 'help'
        ]
        
        # Verificar se começa com comando seguro
        first_word = command_lower.split()[0] if command_lower.split() else ''
        return first_word in safe_commands
    
    def close_program(self, command_text: str) -> bool:
        """Fecha programas (funcionalidade básica)"""
        try:
            # Extrair nome do programa
            close_patterns = [
                r'fechar (.+)',
                r'feche (.+)',
                r'close (.+)',
                r'encerrar (.+)',
                r'encerre (.+)'
            ]
            
            program_name = None
            for pattern in close_patterns:
                match = re.search(pattern, command_text)
                if match:
                    program_name = match.group(1).strip()
                    break
            
            if program_name:
                # Tentar fechar programa específico
                if platform.system() == 'Windows':
                    # Mapear nomes amigáveis para nomes de processo
                    process_map = {
                        'navegador': 'chrome.exe',
                        'calculadora': 'calc.exe',
                        'bloco de notas': 'notepad.exe',
                        'editor': 'notepad.exe'
                    }
                    
                    process_name = process_map.get(program_name, f"{program_name}.exe")
                    
                    try:
                        subprocess.run(['taskkill', '/f', '/im', process_name], 
                                     capture_output=True, check=True)
                        
                        self.speech_engine.speak(
                            f"Pronto! Fechei o {program_name} para você.",
                            emotion='entusiasta'
                        )
                    
                    except subprocess.CalledProcessError:
                        self.speech_engine.speak(
                            f"Não encontrei o {program_name} em execução.",
                            emotion='pensativo'
                        )
                
                else:
                    # Linux/Mac - implementação básica
                    self.speech_engine.speak(
                        "A função de fechar programas no Linux ainda está em desenvolvimento. "
                        "Use o gerenciador de tarefas do sistema.",
                        emotion='pensativo'
                    )
            
            else:
                self.speech_engine.speak(
                    "A função de fechar programas ainda está sendo desenvolvida. "
                    "Por enquanto, use o gerenciador de tarefas do sistema.",
                    emotion='pensativo'
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no comando fechar: {e}")
            self.speech_engine.speak(
                "Ocorreu um erro ao tentar fechar o programa.",
                emotion='preocupado'
            )
            return True
    
    def get_system_info(self) -> Dict[str, str]:
        """Retorna informações do sistema"""
        try:
            return {
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'hostname': platform.node()
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter informações do sistema: {e}")
            return {}
