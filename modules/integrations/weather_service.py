"""
Weather Service Integration
Provides weather information using OpenWeatherMap API
"""

import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime


class WeatherService:
    """
    Weather information service using OpenWeatherMap API.
    
    Features:
    - Current weather
    - Weather forecast
    - Temperature, humidity, conditions
    - Multiple cities support
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather service.
        
        Args:
            api_key: OpenWeatherMap API key (or use OPENWEATHER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.is_available = bool(self.api_key)
        
        if not self.is_available:
            print("[Weather] ⚠ No API key provided. Set OPENWEATHER_API_KEY environment variable.")
            print("[Weather] Get free API key from: https://openweathermap.org/api")
        else:
            print("[Weather] ✓ Weather service initialized")
    
    def get_current_weather(self, city: str, units: str = 'metric') -> Optional[Dict[str, Any]]:
        """
        Get current weather for a city.
        
        Args:
            city: City name (e.g., "São Paulo", "New York")
            units: Temperature units ('metric', 'imperial', 'standard')
            
        Returns:
            Weather data dictionary or None if error
        """
        if not self.is_available:
            return None
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units,
                'lang': 'pt_br'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_info = {
                'city': data.get('name', city),
                'country': data.get('sys', {}).get('country', ''),
                'temperature': data.get('main', {}).get('temp', 0),
                'feels_like': data.get('main', {}).get('feels_like', 0),
                'temp_min': data.get('main', {}).get('temp_min', 0),
                'temp_max': data.get('main', {}).get('temp_max', 0),
                'humidity': data.get('main', {}).get('humidity', 0),
                'pressure': data.get('main', {}).get('pressure', 0),
                'description': data.get('weather', [{}])[0].get('description', ''),
                'main': data.get('weather', [{}])[0].get('main', ''),
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'units': units
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            print(f"[Weather] Request error: {e}")
            return None
        except Exception as e:
            print(f"[Weather] Error getting weather: {e}")
            return None
    
    def get_forecast(self, city: str, units: str = 'metric', days: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for a city.
        
        Args:
            city: City name
            units: Temperature units
            days: Number of days (max 5 for free tier)
            
        Returns:
            Forecast data dictionary or None if error
        """
        if not self.is_available:
            return None
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units,
                'lang': 'pt_br',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract forecast information
            forecasts = []
            for item in data.get('list', []):
                forecast = {
                    'datetime': item.get('dt_txt', ''),
                    'temperature': item.get('main', {}).get('temp', 0),
                    'feels_like': item.get('main', {}).get('feels_like', 0),
                    'temp_min': item.get('main', {}).get('temp_min', 0),
                    'temp_max': item.get('main', {}).get('temp_max', 0),
                    'humidity': item.get('main', {}).get('humidity', 0),
                    'description': item.get('weather', [{}])[0].get('description', ''),
                    'main': item.get('weather', [{}])[0].get('main', ''),
                    'wind_speed': item.get('wind', {}).get('speed', 0),
                    'rain_prob': item.get('pop', 0) * 100  # Probability of precipitation
                }
                forecasts.append(forecast)
            
            return {
                'city': data.get('city', {}).get('name', city),
                'country': data.get('city', {}).get('country', ''),
                'forecasts': forecasts,
                'units': units
            }
            
        except requests.exceptions.RequestException as e:
            print(f"[Weather] Request error: {e}")
            return None
        except Exception as e:
            print(f"[Weather] Error getting forecast: {e}")
            return None
    
    def format_weather_for_speech(self, weather: Dict[str, Any]) -> str:
        """
        Format weather data for text-to-speech.
        
        Args:
            weather: Weather data dictionary
            
        Returns:
            Formatted string for TTS
        """
        if not weather:
            return "Não foi possível obter informações do tempo."
        
        city = weather.get('city', 'a cidade')
        temp = weather.get('temperature', 0)
        feels_like = weather.get('feels_like', 0)
        description = weather.get('description', 'sem informação')
        humidity = weather.get('humidity', 0)
        
        # Temperature unit
        unit = '°C' if weather.get('units') == 'metric' else '°F'
        
        response = f"O tempo em {city}: "
        response += f"{temp:.1f}{unit}, "
        response += f"sensação térmica de {feels_like:.1f}{unit}. "
        response += f"{description.capitalize()}. "
        response += f"Umidade de {humidity}%."
        
        return response
    
    def format_forecast_for_speech(self, forecast: Dict[str, Any], summary: bool = True) -> str:
        """
        Format forecast data for text-to-speech.
        
        Args:
            forecast: Forecast data dictionary
            summary: If True, provide summary; if False, detailed forecast
            
        Returns:
            Formatted string for TTS
        """
        if not forecast:
            return "Não foi possível obter a previsão do tempo."
        
        city = forecast.get('city', 'a cidade')
        forecasts = forecast.get('forecasts', [])
        
        if not forecasts:
            return f"Sem previsão disponível para {city}."
        
        if summary:
            # Summarize next 24 hours
            next_24h = forecasts[:8]  # First 24 hours (3-hour intervals)
            temps = [f['temperature'] for f in next_24h]
            avg_temp = sum(temps) / len(temps)
            min_temp = min(temps)
            max_temp = max(temps)
            
            # Most common condition
            conditions = [f['description'] for f in next_24h]
            most_common = max(set(conditions), key=conditions.count)
            
            unit = '°C' if forecast.get('units') == 'metric' else '°F'
            
            response = f"Previsão para {city} nas próximas 24 horas: "
            response += f"Temperatura média de {avg_temp:.1f}{unit}, "
            response += f"mínima de {min_temp:.1f}{unit}, "
            response += f"máxima de {max_temp:.1f}{unit}. "
            response += f"Condições: {most_common}."
            
            return response
        else:
            # Detailed forecast
            response = f"Previsão detalhada para {city}: "
            for i, f in enumerate(forecasts[:8]):  # Next 24 hours
                dt = f.get('datetime', '')
                temp = f.get('temperature', 0)
                desc = f.get('description', '')
                response += f"{dt}: {temp:.1f}°C, {desc}. "
            
            return response
    
    def is_raining(self, city: str) -> Optional[bool]:
        """Check if it's currently raining in a city."""
        weather = self.get_current_weather(city)
        if weather:
            main = weather.get('main', '').lower()
            return 'rain' in main
        return None


# Example usage
if __name__ == "__main__":
    # Initialize (requires API key)
    weather = WeatherService()
    
    if weather.is_available:
        # Get current weather
        print("\n=== Current Weather ===")
        current = weather.get_current_weather("São Paulo")
        if current:
            print(f"City: {current['city']}")
            print(f"Temperature: {current['temperature']}°C")
            print(f"Feels like: {current['feels_like']}°C")
            print(f"Conditions: {current['description']}")
            print(f"Humidity: {current['humidity']}%")
            
            # Format for speech
            print("\n=== Speech Format ===")
            print(weather.format_weather_for_speech(current))
        
        # Get forecast
        print("\n=== Forecast ===")
        forecast = weather.get_forecast("São Paulo")
        if forecast:
            print(weather.format_forecast_for_speech(forecast))
    else:
        print("\nWeather service not available. Set OPENWEATHER_API_KEY.")
