"""
Integrations Module
Third-party service integrations for JARVIS
"""

from .google_calendar import GoogleCalendarIntegration
from .weather_service import WeatherService
from .email_service import EmailService
from .news_service import NewsService, RSSNewsService
from .wikipedia_service import WikipediaService
from .entertainment_service import JokeService, FunFactsService, QuoteService

__all__ = [
    'GoogleCalendarIntegration',
    'WeatherService',
    'EmailService',
    'NewsService',
    'RSSNewsService',
    'WikipediaService',
    'JokeService',
    'FunFactsService',
    'QuoteService',
]
