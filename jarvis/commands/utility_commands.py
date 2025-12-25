"""
Comandos utilitários para JARVIS
"""

import os
import re
import subprocess
import platform
from datetime import datetime
from typing import Dict, Any

from ..core.logger import default_logger


class UtilityCommands:
    """Comandos utilitários e de informação"""
    
    def __init__(self, config: Dict[str, Any], speech_engine):
        self.config = config
        self.speech_engine = speech_engine
        self.logger = default_logger
    
    def tell_time(self, command_text: str) -> bool:
        """Diz a hora atual"""
        try:
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            
            # Determinar período do dia
            if hour < 12:
                period = "da manhã"
            elif hour < 18:
                period = "da tarde"
            else:
                period = "da noite"
            
            time_str = f"{hour:02d}:{minute:02d}"
            
            self.speech_engine.speak(
                f"Agora são exatamente {time_str} {period}.",
                emotion='entusiasta'
            )
            
            self.logger.command_event("tell_time", "completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao dizer hora: {e}")
            self.speech_engine.speak(
                "Ops! Não consegui verificar a hora atual.",
                emotion='preocupado'
            )
            return True
    
    def tell_date(self, command_text: str) -> bool:
        """Diz a data atual"""
        try:
            now = datetime.now()
            
            # Mapear dias da semana para português
            weekdays = {
                'Monday': 'segunda-feira',
                'Tuesday': 'terça-feira',
                'Wednesday': 'quarta-feira',
                'Thursday': 'quinta-feira',
                'Friday': 'sexta-feira',
                'Saturday': 'sábado',
                'Sunday': 'domingo'
            }
            
            # Mapear meses para português
            months = {
                1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
            }
            
            weekday_en = now.strftime("%A")
            weekday_pt = weekdays.get(weekday_en, weekday_en)
            
            day = now.day
            month_pt = months.get(now.month, str(now.month))
            year = now.year
            
            date_str = f"{weekday_pt}, {day} de {month_pt} de {year}"
            
            self.speech_engine.speak(
                f"Hoje é {date_str}.",
                emotion='entusiasta'
            )
            
            self.logger.command_event("tell_date", "completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao dizer data: {e}")
            self.speech_engine.speak(
                "Ops! Não consegui verificar a data atual.",
                emotion='preocupado'
            )
            return True
    
    def calculate(self, command_text: str) -> bool:
        """Faz cálculos matemáticos"""
        try:
            # Padrões para extrair expressão matemática
            calc_patterns = [
                r'calcular (.+)',
                r'calculate (.+)',
                r'quanto é (.+)',
                r'quanto da (.+)',
                r'faça a conta (.+)'
            ]
            
            expression = None
            for pattern in calc_patterns:
                match = re.search(pattern, command_text)
                if match:
                    expression = match.group(1).strip()
                    break
            
            if expression:
                # Limpar e normalizar expressão
                expression = self._normalize_math_expression(expression)
                
                if expression:
                    try:
                        # Avaliar expressão de forma segura
                        result = self._safe_eval(expression)
                        
                        if result is not None:
                            self.speech_engine.speak(
                                f"O resultado de {expression} é {result}.",
                                emotion='entusiasta'
                            )
                        else:
                            self.speech_engine.speak(
                                "Hmm, não consegui calcular essa expressão. "
                                "Tente usar apenas números e operadores básicos como +, -, * e /.",
                                emotion='pensativo'
                            )
                    
                    except Exception as e:
                        self.logger.warning(f"Erro no cálculo '{expression}': {e}")
                        self.speech_engine.speak(
                            "Não consegui calcular essa expressão. "
                            "Verifique se está usando apenas números e operadores válidos.",
                            emotion='preocupado'
                        )
                
                else:
                    self.speech_engine.speak(
                        "Não entendi a expressão matemática. "
                        "Tente algo como 'calcular 2 mais 3' ou 'calcular 10 dividido por 2'.",
                        emotion='pensativo'
                    )
            
            else:
                self.speech_engine.speak(
                    "Claro! Qual cálculo você gostaria que eu fizesse? "
                    "Por exemplo, diga 'calcular 25 vezes 4'.",
                    emotion='entusiasta'
                )
            
            self.logger.command_event(f"calculate: {expression}", "completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no comando calcular: {e}")
            self.speech_engine.speak(
                "Ocorreu um erro ao fazer o cálculo.",
                emotion='preocupado'
            )
            return True
    
    def _normalize_math_expression(self, expression: str) -> str:
        """Normaliza expressão matemática para avaliação"""
        if not expression:
            return ""
        
        # Converter palavras para operadores
        replacements = {
            ' mais ': ' + ',
            ' menos ': ' - ',
            ' vezes ': ' * ',
            ' multiplicado por ': ' * ',
            ' dividido por ': ' / ',
            ' elevado a ': ' ** ',
            ' ao quadrado': ' ** 2',
            ' ao cubo': ' ** 3',
            'raiz de ': 'sqrt(',
            'raiz quadrada de ': 'sqrt('
        }
        
        normalized = expression.lower()
        
        for word, operator in replacements.items():
            normalized = normalized.replace(word, operator)
        
        # Adicionar parênteses para sqrt se necessário
        if 'sqrt(' in normalized and ')' not in normalized:
            normalized += ')'
        
        # Remover espaços extras
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _safe_eval(self, expression: str):
        """Avalia expressão matemática de forma segura"""
        try:
            # Lista de funções e constantes permitidas
            allowed_names = {
                "__builtins__": {},
                "abs": abs,
                "round": round,
                "pow": pow,
                "sqrt": lambda x: x ** 0.5,
                "pi": 3.14159265359,
                "e": 2.71828182846
            }
            
            # Verificar se contém apenas caracteres seguros
            safe_chars = set('0123456789+-*/().** \t')
            if not all(c in safe_chars or c.isalnum() for c in expression):
                return None
            
            # Avaliar expressão
            result = eval(expression, allowed_names)
            
            # Arredondar resultado se for float
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)
            
            return result
            
        except:
            return None
    
    def search_web(self, command_text: str) -> bool:
        """Abre navegador para pesquisa na web"""
        try:
            # Padrões para extrair termo de pesquisa
            search_patterns = [
                r'pesquisar (.+)',
                r'pesquise (.+)',
                r'search (.+)',
                r'buscar (.+)',
                r'busque (.+)',
                r'procurar (.+)',
                r'procure (.+)'
            ]
            
            search_term = None
            for pattern in search_patterns:
                match = re.search(pattern, command_text)
                if match:
                    search_term = match.group(1).strip()
                    break
            
            if search_term:
                # Construir URL de pesquisa
                search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
                
                try:
                    # Abrir navegador baseado no SO
                    if platform.system() == 'Windows':
                        os.startfile(search_url)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', search_url])
                    else:  # Linux
                        subprocess.run(['xdg-open', search_url])
                    
                    self.speech_engine.speak(
                        f"Pronto! Abrindo o navegador para pesquisar sobre '{search_term}'.",
                        emotion='entusiasta'
                    )
                    
                    self.logger.command_event(f"search: {search_term}", "completed")
                
                except Exception as e:
                    self.logger.error(f"Erro ao abrir navegador: {e}")
                    self.speech_engine.speak(
                        "Ops! Não consegui abrir o navegador para fazer a pesquisa.",
                        emotion='preocupado'
                    )
            
            else:
                self.speech_engine.speak(
                    "O que você gostaria que eu pesquisasse? "
                    "Basta dizer 'pesquisar' seguido do que procura.",
                    emotion='pensativo'
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no comando pesquisar: {e}")
            self.speech_engine.speak(
                "Ocorreu um erro ao tentar fazer a pesquisa.",
                emotion='preocupado'
            )
            return True
    
    def get_weather(self, command_text: str) -> bool:
        """Informações do tempo (funcionalidade futura)"""
        self.speech_engine.speak(
            "A função de previsão do tempo ainda está sendo desenvolvida. "
            "Por enquanto, você pode pesquisar 'tempo hoje' no navegador.",
            emotion='pensativo'
        )
        return True
    
    def set_reminder(self, command_text: str) -> bool:
        """Define lembretes (funcionalidade futura)"""
        self.speech_engine.speak(
            "A função de lembretes ainda está sendo desenvolvida. "
            "Que tal usar o aplicativo de lembretes do seu sistema?",
            emotion='pensativo'
        )
        return True
    
    def play_music(self, command_text: str) -> bool:
        """Reproduz música (funcionalidade futura)"""
        self.speech_engine.speak(
            "A função de reprodução de música ainda está sendo desenvolvida. "
            "Por enquanto, você pode abrir seu player de música favorito.",
            emotion='pensativo'
        )
        return True
