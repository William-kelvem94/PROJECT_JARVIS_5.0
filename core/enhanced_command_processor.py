"""
Enhanced Command Processor
Integrates all new features: wake word, calendar, weather, news, wikipedia, email, jokes
"""

import os
import re
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta

# Import all integrations
try:
    from modules.integrations.google_calendar import GoogleCalendarIntegration
    from modules.integrations.weather_service import WeatherService
    from modules.integrations.news_service import NewsService, RSSNewsService
    from modules.integrations.wikipedia_service import WikipediaService
    from modules.integrations.email_service import EmailService
    from modules.integrations.entertainment_service import JokeService, FunFactsService, QuoteService
    from modules.input.wake_word_detector import WakeWordDetector
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")


class EnhancedCommandProcessor:
    """
    Enhanced command processor with all new integrations.
    
    Features:
    - Wake word detection
    - Google Calendar
    - Weather information
    - News headlines
    - Wikipedia queries
    - Email sending
    - Jokes and entertainment
    - And all existing JARVIS features
    """
    
    def __init__(self, speak_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize enhanced command processor.
        
        Args:
            speak_callback: Function to call for text-to-speech output
        """
        self.speak_callback = speak_callback or self._default_speak
        
        # Initialize integrations
        print("\n[EnhancedProcessor] Initializing integrations...")
        
        self.calendar = GoogleCalendarIntegration()
        self.weather = WeatherService()
        self.news = NewsService()
        self.wikipedia = WikipediaService(language='pt')
        self.email = EmailService()
        self.jokes = JokeService()
        self.fun_facts = FunFactsService()
        self.quotes = QuoteService()
        self.wake_word = WakeWordDetector()
        
        # Fallback for news if API not available
        if not self.news.is_available:
            print("[EnhancedProcessor] Using RSS news service as fallback")
            self.news = RSSNewsService()
        
        # Command statistics
        self.stats = {
            'commands_processed': 0,
            'calendar_queries': 0,
            'weather_queries': 0,
            'news_queries': 0,
            'wiki_queries': 0,
            'emails_sent': 0,
            'jokes_told': 0
        }
        
        print("[EnhancedProcessor] ✓ Enhanced command processor ready!")
    
    def _default_speak(self, text: str):
        """Default speak function (just print)."""
        print(f"JARVIS: {text}")
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a command and return result.
        
        Args:
            command: User command text
            
        Returns:
            Dictionary with result information
        """
        command = command.lower().strip()
        self.stats['commands_processed'] += 1
        
        result = {
            'success': False,
            'response': '',
            'action': 'unknown'
        }
        
        try:
            # Calendar commands
            if self._is_calendar_command(command):
                result = self._handle_calendar(command)
            
            # Weather commands
            elif self._is_weather_command(command):
                result = self._handle_weather(command)
            
            # News commands
            elif self._is_news_command(command):
                result = self._handle_news(command)
            
            # Wikipedia commands
            elif self._is_wikipedia_command(command):
                result = self._handle_wikipedia(command)
            
            # Email commands
            elif self._is_email_command(command):
                result = self._handle_email(command)
            
            # Entertainment commands
            elif self._is_entertainment_command(command):
                result = self._handle_entertainment(command)
            
            # Time and date
            elif any(word in command for word in ['hora', 'horas', 'time']):
                result = self._handle_time()
            
            elif any(word in command for word in ['data', 'dia', 'date']):
                result = self._handle_date()
            
            # Help
            elif 'ajuda' in command or 'help' in command:
                result = self._handle_help()
            
            # Statistics
            elif 'estatística' in command or 'stats' in command or 'status' in command:
                result = self._handle_stats()
            
            # Default
            else:
                result = {
                    'success': False,
                    'response': 'Comando não reconhecido. Diga "ajuda" para ver comandos disponíveis.',
                    'action': 'unknown'
                }
            
            # Speak the response
            if result.get('response'):
                self.speak_callback(result['response'])
            
        except Exception as e:
            print(f"[EnhancedProcessor] Error processing command: {e}")
            result = {
                'success': False,
                'response': 'Desculpe, ocorreu um erro ao processar seu comando.',
                'action': 'error'
            }
        
        return result
    
    def _is_calendar_command(self, command: str) -> bool:
        """Check if command is calendar-related."""
        calendar_keywords = ['agenda', 'calendário', 'calendar', 'evento', 'compromisso', 'reunião']
        return any(word in command for word in calendar_keywords)
    
    def _handle_calendar(self, command: str) -> Dict[str, Any]:
        """Handle calendar commands."""
        self.stats['calendar_queries'] += 1
        
        if not self.calendar.is_available:
            return {
                'success': False,
                'response': 'Serviço de calendário não disponível. Configure as credenciais do Google.',
                'action': 'calendar'
            }
        
        # Get upcoming events
        if 'próximos' in command or 'upcoming' in command:
            events = self.calendar.get_upcoming_events(5)
            response = self.calendar.format_events_for_speech(events)
            return {
                'success': True,
                'response': response,
                'action': 'calendar_upcoming',
                'data': events
            }
        
        # Get today's events
        elif 'hoje' in command or 'today' in command:
            events = self.calendar.get_events_today()
            response = self.calendar.format_events_for_speech(events)
            return {
                'success': True,
                'response': response,
                'action': 'calendar_today',
                'data': events
            }
        
        # Next event
        elif 'próximo' in command or 'next' in command:
            event = self.calendar.get_next_event()
            if event:
                response = f"Seu próximo evento é: {event['summary']} às {event['start']}"
            else:
                response = "Você não tem eventos próximos."
            return {
                'success': True,
                'response': response,
                'action': 'calendar_next',
                'data': event
            }
        
        else:
            return {
                'success': False,
                'response': 'Comando de calendário não reconhecido. Tente "agenda de hoje" ou "próximos eventos".',
                'action': 'calendar'
            }
    
    def _is_weather_command(self, command: str) -> bool:
        """Check if command is weather-related."""
        weather_keywords = ['tempo', 'weather', 'clima', 'temperatura', 'previsão']
        return any(word in command for word in weather_keywords)
    
    def _handle_weather(self, command: str) -> Dict[str, Any]:
        """Handle weather commands."""
        self.stats['weather_queries'] += 1
        
        if not self.weather.is_available:
            return {
                'success': False,
                'response': 'Serviço de tempo não disponível. Configure a chave da API OpenWeatherMap.',
                'action': 'weather'
            }
        
        # Extract city name (default to São Paulo)
        city = self._extract_city(command) or "São Paulo"
        
        # Get forecast or current weather
        if 'previsão' in command or 'forecast' in command:
            forecast = self.weather.get_forecast(city)
            if forecast:
                response = self.weather.format_forecast_for_speech(forecast)
                return {
                    'success': True,
                    'response': response,
                    'action': 'weather_forecast',
                    'data': forecast
                }
        else:
            weather = self.weather.get_current_weather(city)
            if weather:
                response = self.weather.format_weather_for_speech(weather)
                return {
                    'success': True,
                    'response': response,
                    'action': 'weather_current',
                    'data': weather
                }
        
        return {
            'success': False,
            'response': f'Não foi possível obter informações do tempo para {city}.',
            'action': 'weather'
        }
    
    def _extract_city(self, command: str) -> Optional[str]:
        """Extract city name from command."""
        # Simple extraction - look for "em [city]" or "in [city]"
        patterns = [
            r'em ([A-Za-zÀ-ÿ\s]+)',
            r'in ([A-Za-z\s]+)',
            r'de ([A-Za-zÀ-ÿ\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                city = match.group(1).strip()
                # Clean up common words
                stop_words = ['hoje', 'agora', 'está', 'é', 'today', 'now', 'is']
                for word in stop_words:
                    city = city.replace(word, '').strip()
                if city:
                    return city
        
        return None
    
    def _is_news_command(self, command: str) -> bool:
        """Check if command is news-related."""
        news_keywords = ['notícia', 'notícias', 'news', 'manchete', 'headline']
        return any(word in command for word in news_keywords)
    
    def _handle_news(self, command: str) -> Dict[str, Any]:
        """Handle news commands."""
        self.stats['news_queries'] += 1
        
        if hasattr(self.news, 'get_top_headlines'):
            headlines = self.news.get_top_headlines(country='br', max_results=5)
        else:
            # RSS fallback
            headlines = self.news.get_top_headlines(country='br', max_results=5)
        
        if headlines:
            if hasattr(self.news, 'format_headlines_for_speech'):
                response = self.news.format_headlines_for_speech(headlines)
            else:
                # Format manually
                response = f"Aqui estão as principais notícias: "
                for i, article in enumerate(headlines[:5], 1):
                    response += f"{i}. {article['title']}. "
            
            return {
                'success': True,
                'response': response,
                'action': 'news',
                'data': headlines
            }
        
        return {
            'success': False,
            'response': 'Não foi possível obter as notícias no momento.',
            'action': 'news'
        }
    
    def _is_wikipedia_command(self, command: str) -> bool:
        """Check if command is Wikipedia-related."""
        wiki_keywords = ['quem é', 'o que é', 'who is', 'what is', 'wikipedia', 'pesquisar', 'search']
        return any(phrase in command for phrase in wiki_keywords)
    
    def _handle_wikipedia(self, command: str) -> Dict[str, Any]:
        """Handle Wikipedia commands."""
        self.stats['wiki_queries'] += 1
        
        if not self.wikipedia.is_available:
            return {
                'success': False,
                'response': 'Serviço da Wikipedia não disponível.',
                'action': 'wikipedia'
            }
        
        # Extract query
        query = self._extract_wiki_query(command)
        if not query:
            return {
                'success': False,
                'response': 'Não consegui entender o que você quer pesquisar.',
                'action': 'wikipedia'
            }
        
        # Search Wikipedia
        summary = self.wikipedia.search_and_summarize(query, sentences=3)
        if summary:
            response = self.wikipedia.format_summary_for_speech(summary, max_length=500)
            return {
                'success': True,
                'response': response,
                'action': 'wikipedia',
                'data': {'query': query, 'summary': summary}
            }
        
        return {
            'success': False,
            'response': f'Não encontrei informações sobre {query}.',
            'action': 'wikipedia'
        }
    
    def _extract_wiki_query(self, command: str) -> Optional[str]:
        """Extract query from Wikipedia command."""
        patterns = [
            r'quem é (.+)',
            r'o que é (.+)',
            r'who is (.+)',
            r'what is (.+)',
            r'sobre (.+)',
            r'about (.+)',
            r'pesquisar (.+)',
            r'search (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _is_email_command(self, command: str) -> bool:
        """Check if command is email-related."""
        email_keywords = ['email', 'e-mail', 'mensagem', 'enviar', 'send']
        return any(word in command for word in email_keywords)
    
    def _handle_email(self, command: str) -> Dict[str, Any]:
        """Handle email commands."""
        self.stats['emails_sent'] += 1
        
        if not self.email.is_available:
            return {
                'success': False,
                'response': 'Serviço de email não configurado.',
                'action': 'email'
            }
        
        # This is a simplified version - in production, you'd want more sophisticated parsing
        return {
            'success': False,
            'response': 'Funcionalidade de envio de email em desenvolvimento. Configure destinatário e mensagem.',
            'action': 'email'
        }
    
    def _is_entertainment_command(self, command: str) -> bool:
        """Check if command is entertainment-related."""
        entertainment_keywords = ['piada', 'joke', 'curiosidade', 'fact', 'frase', 'quote']
        return any(word in command for word in entertainment_keywords)
    
    def _handle_entertainment(self, command: str) -> Dict[str, Any]:
        """Handle entertainment commands."""
        self.stats['jokes_told'] += 1
        
        # Jokes
        if 'piada' in command or 'joke' in command:
            joke = self.jokes.get_random_joke('pt')
            return {
                'success': True,
                'response': joke,
                'action': 'entertainment_joke'
            }
        
        # Fun facts
        elif 'curiosidade' in command or 'fact' in command:
            fact = self.fun_facts.get_random_fact()
            return {
                'success': True,
                'response': fact,
                'action': 'entertainment_fact'
            }
        
        # Quotes
        elif 'frase' in command or 'quote' in command:
            quote = self.quotes.get_random_quote()
            return {
                'success': True,
                'response': quote,
                'action': 'entertainment_quote'
            }
        
        return {
            'success': False,
            'response': 'Comando de entretenimento não reconhecido.',
            'action': 'entertainment'
        }
    
    def _handle_time(self) -> Dict[str, Any]:
        """Handle time query."""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        return {
            'success': True,
            'response': f"São {time_str}.",
            'action': 'time'
        }
    
    def _handle_date(self) -> Dict[str, Any]:
        """Handle date query."""
        now = datetime.now()
        months = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        date_str = f"{now.day} de {months[now.month-1]} de {now.year}"
        return {
            'success': True,
            'response': f"Hoje é {date_str}.",
            'action': 'date'
        }
    
    def _handle_help(self) -> Dict[str, Any]:
        """Handle help command."""
        help_text = """
        Comandos disponíveis:
        
        CALENDÁRIO: "agenda de hoje", "próximos eventos"
        TEMPO: "como está o tempo em São Paulo", "previsão do tempo"
        NOTÍCIAS: "me conte as notícias"
        WIKIPEDIA: "quem é Albert Einstein", "o que é Python"
        ENTRETENIMENTO: "conte uma piada", "me dê uma curiosidade"
        INFORMAÇÕES: "que horas são", "que dia é hoje"
        """
        return {
            'success': True,
            'response': help_text.strip(),
            'action': 'help'
        }
    
    def _handle_stats(self) -> Dict[str, Any]:
        """Handle statistics command."""
        response = f"""
        Estatísticas do sistema:
        Comandos processados: {self.stats['commands_processed']}
        Consultas de calendário: {self.stats['calendar_queries']}
        Consultas de tempo: {self.stats['weather_queries']}
        Consultas de notícias: {self.stats['news_queries']}
        Consultas Wikipedia: {self.stats['wiki_queries']}
        Piadas contadas: {self.stats['jokes_told']}
        """
        return {
            'success': True,
            'response': response.strip(),
            'action': 'stats',
            'data': self.stats
        }


# Example usage
if __name__ == "__main__":
    processor = EnhancedCommandProcessor()
    
    # Test commands
    test_commands = [
        "que horas são",
        "como está o tempo em São Paulo",
        "me conte uma piada",
        "quem é Albert Einstein",
        "agenda de hoje",
        "notícias",
        "ajuda"
    ]
    
    print("\n=== Testing Enhanced Command Processor ===\n")
    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        result = processor.process_command(cmd)
        print(f"Result: {result['response']}")
