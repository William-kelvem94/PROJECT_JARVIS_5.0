"""
Integrations Module
Third-party service integrations for JARVIS
"""

from .google_calendar import GoogleCalendarIntegration
from .weather_service import WeatherService
from .email_service import EmailService
from .news_service import NewsService
from .wikipedia_service import WikipediaService

__all__ = [
    'GoogleCalendarIntegration',
    'WeatherService',
    'EmailService',
    'NewsService',
    'WikipediaService',
]
