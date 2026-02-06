# 🎯 JARVIS 5.0 - Enhanced Features

## 📋 Overview

This document describes the new enhanced features added to JARVIS 5.0, combining the best capabilities from multiple JARVIS repositories:

### Sources
- **llm-guy/jarvis**: Wake word detection, conversation timeout
- **Gladiator07/JARVIS**: Google Calendar, Weather, News, Wikipedia integrations
- **kishanrajput23/Jarvis-Desktop-Voice-Assistant**: Enhanced voice control
- **danilofalcao/jarvis**: Multi-model AI support concepts
- **Code-A2Z/jarvis**: Security and authentication patterns
- **projectswithdigambar/jarvis**: Desktop automation features

---

## 🆕 New Features

### 1. 🎤 Wake Word Detection

Voice-activated assistant with wake word support.

**Features:**
- Multiple wake words: "Jarvis", "Hey Jarvis", "Oi Jarvis"
- Automatic timeout and reset (30 seconds default)
- Conversation mode management
- Offline mode support (optional)

**Usage:**
```python
from modules.input.wake_word_detector import WakeWordDetector

detector = WakeWordDetector(
    wake_words=["jarvis", "hey jarvis"],
    timeout=30.0
)

def handle_command(command: str) -> bool:
    print(f"Processing: {command}")
    return True

detector.run_loop(handle_command)
```

**Commands:**
- Say "Jarvis" to activate
- After activation, speak your commands
- Say "sair" or "tchau" to exit
- Automatic deactivation after 30 seconds of inactivity

---

### 2. 📅 Google Calendar Integration

Full Google Calendar integration for event management.

**Features:**
- Get upcoming events
- Get today's events
- Create new events
- Delete events
- Event reminders

**Setup:**
1. Get Google Calendar API credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Download credentials JSON file
3. Set environment variable:
   ```bash
   export GOOGLE_CALENDAR_CREDENTIALS=path/to/credentials.json
   ```

**Voice Commands:**
- "agenda de hoje" - Today's events
- "próximos eventos" - Upcoming events
- "próximo evento" - Next event

**Example:**
```python
from modules.integrations.google_calendar import GoogleCalendarIntegration

calendar = GoogleCalendarIntegration()

# Get upcoming events
events = calendar.get_upcoming_events(5)
for event in events:
    print(f"{event['summary']} at {event['start']}")

# Create event
from datetime import datetime, timedelta
start = datetime.now() + timedelta(hours=1)
end = start + timedelta(hours=1)
calendar.create_event(
    summary="Meeting with team",
    start_time=start,
    end_time=end,
    description="Discuss project updates"
)
```

---

### 3. 🌤️ Weather Service

Real-time weather information using OpenWeatherMap API.

**Features:**
- Current weather
- Weather forecast (5 days)
- Multiple cities support
- Temperature, humidity, wind speed
- Portuguese descriptions

**Setup:**
1. Get free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Set environment variable:
   ```bash
   export OPENWEATHER_API_KEY=your_api_key_here
   ```

**Voice Commands:**
- "como está o tempo em São Paulo" - Current weather
- "previsão do tempo em Rio" - Weather forecast

**Example:**
```python
from modules.integrations.weather_service import WeatherService

weather = WeatherService()

# Current weather
current = weather.get_current_weather("São Paulo")
print(f"Temperature: {current['temperature']}°C")
print(f"Conditions: {current['description']}")

# Forecast
forecast = weather.get_forecast("São Paulo")
speech = weather.format_forecast_for_speech(forecast)
print(speech)
```

---

### 4. 📰 News Service

Latest news headlines from multiple sources.

**Features:**
- Top headlines by country
- Search news by topic
- Category filtering
- RSS fallback (no API key needed)

**Setup (Optional):**
1. Get free API key from [NewsAPI](https://newsapi.org/)
2. Set environment variable:
   ```bash
   export NEWS_API_KEY=your_api_key_here
   ```
3. If no API key, RSS feeds are used automatically

**Voice Commands:**
- "me conte as notícias" - Top headlines
- "notícias de tecnologia" - Technology news

**Example:**
```python
from modules.integrations.news_service import NewsService

news = NewsService()

# Top headlines
headlines = news.get_top_headlines(country='br', max_results=5)
for article in headlines:
    print(f"{article['title']} - {article['source']}")

# Search news
tech_news = news.search_news('tecnologia', max_results=5)
```

---

### 5. 📚 Wikipedia Integration

Wikipedia search and information retrieval.

**Features:**
- Search Wikipedia
- Get article summaries
- Full article content
- Multiple language support
- Auto-suggestion for similar titles

**Setup:**
```bash
pip install wikipedia-api
```

**Voice Commands:**
- "quem é Albert Einstein" - Person information
- "o que é Python" - Topic information

**Example:**
```python
from modules.integrations.wikipedia_service import WikipediaService

wiki = WikipediaService(language='pt')

# Search
results = wiki.search("Python programação")

# Get summary
summary = wiki.get_summary("Python (linguagem de programação)", sentences=3)
print(summary)

# Quick info
info = wiki.search_and_summarize("Albert Einstein")
```

---

### 6. 📧 Email Service

Send emails through JARVIS.

**Features:**
- Send plain text emails
- Send HTML emails
- Multiple recipients
- Gmail, Outlook, Yahoo support

**Setup:**
1. For Gmail: Enable 2FA and generate App Password
2. Set environment variables:
   ```bash
   export EMAIL_ADDRESS=your_email@gmail.com
   export EMAIL_PASSWORD=your_app_password
   ```

**Example:**
```python
from modules.integrations.email_service import EmailService

email = EmailService()

# Send email
email.send_email(
    to_address="recipient@example.com",
    subject="Hello from JARVIS",
    body="This is a test email!"
)
```

**Supported Providers:**
- Gmail (smtp.gmail.com:587)
- Outlook (smtp-mail.outlook.com:587)
- Yahoo (smtp.mail.yahoo.com:587)
- Office 365 (smtp.office365.com:587)

---

### 7. 🎭 Entertainment Features

Fun features for user engagement.

**Features:**
- Random jokes (Portuguese and English)
- Dad jokes
- Programming jokes
- Fun facts
- Inspirational quotes

**Voice Commands:**
- "conte uma piada" - Tell a joke
- "me dê uma curiosidade" - Fun fact
- "me dê uma frase inspiradora" - Quote

**Example:**
```python
from modules.integrations.entertainment_service import (
    JokeService, FunFactsService, QuoteService
)

jokes = JokeService()
print(jokes.get_random_joke('pt'))
print(jokes.get_programming_joke())

facts = FunFactsService()
print(facts.get_random_fact())

quotes = QuoteService()
print(quotes.get_random_quote())
```

---

## 🎯 Enhanced Command Processor

The new `EnhancedCommandProcessor` integrates all features into a unified interface.

**Features:**
- Natural language understanding
- Context-aware responses
- Multi-feature integration
- Command statistics
- Error handling

**Example:**
```python
from core.enhanced_command_processor import EnhancedCommandProcessor

processor = EnhancedCommandProcessor()

# Process commands
commands = [
    "que horas são",
    "como está o tempo em São Paulo",
    "me conte as notícias",
    "quem é Albert Einstein",
    "conte uma piada",
    "agenda de hoje"
]

for cmd in commands:
    result = processor.process_command(cmd)
    print(result['response'])
```

---

## 📊 Available Commands

### Time & Date
- "que horas são" - Current time
- "que dia é hoje" - Current date

### Calendar
- "agenda de hoje" - Today's events
- "próximos eventos" - Upcoming events
- "próximo evento" - Next event

### Weather
- "como está o tempo" - Current weather
- "previsão do tempo" - Weather forecast
- "como está o tempo em [cidade]" - Weather for specific city

### News
- "me conte as notícias" - Top headlines
- "notícias de [categoria]" - Category news

### Wikipedia
- "quem é [pessoa]" - Person information
- "o que é [tópico]" - Topic information

### Entertainment
- "conte uma piada" - Tell a joke
- "me dê uma curiosidade" - Fun fact
- "me dê uma frase" - Inspirational quote

### System
- "ajuda" - Show help
- "status" - Show statistics
- "sair" - Exit

---

## 🔧 Installation

### Required Dependencies

```bash
pip install -r requirements.txt
```

### Optional Dependencies

For Google Calendar:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

For Wikipedia:
```bash
pip install wikipedia-api
```

For News (RSS fallback):
```bash
pip install feedparser
```

---

## 🚀 Quick Start

### Basic Usage

```python
from core.enhanced_command_processor import EnhancedCommandProcessor
from modules.input.voice_module import VoiceModule

# Initialize
voice = VoiceModule()
processor = EnhancedCommandProcessor(speak_callback=voice.speak)

# Listen and process
while True:
    command = voice.listen()
    if command:
        result = processor.process_command(command)
        if not result['success'] and 'sair' in command:
            break
```

### With Wake Word Detection

```python
from modules.input.wake_word_detector import WakeWordDetector
from core.enhanced_command_processor import EnhancedCommandProcessor

processor = EnhancedCommandProcessor()
detector = WakeWordDetector()

def handle_command(command: str) -> bool:
    result = processor.process_command(command)
    return True  # Continue listening

detector.run_loop(handle_command)
```

---

## 🔐 Security & Privacy

### API Keys
- Store API keys in environment variables
- Never commit credentials to git
- Use `.env` file for local development

### Google Calendar
- Credentials stored in `config/` directory
- Token refresh handled automatically
- Use OAuth2 for secure authentication

### Email
- Use App Passwords, not regular passwords
- Enable 2FA for Gmail
- SMTP connection uses TLS encryption

---

## 📝 Configuration

Create a `.env` file in the project root:

```bash
# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS=config/google_credentials.json

# Weather
OPENWEATHER_API_KEY=your_api_key

# News (optional)
NEWS_API_KEY=your_api_key

# Email
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

---

## 🧪 Testing

Test individual services:

```bash
# Test wake word detection
python modules/input/wake_word_detector.py

# Test calendar
python modules/integrations/google_calendar.py

# Test weather
python modules/integrations/weather_service.py

# Test news
python modules/integrations/news_service.py

# Test Wikipedia
python modules/integrations/wikipedia_service.py

# Test entertainment
python modules/integrations/entertainment_service.py

# Test enhanced processor
python core/enhanced_command_processor.py
```

---

## 🤝 Contributing

These features were inspired by and combined from multiple open-source JARVIS projects. We thank all the original contributors for their excellent work!

---

## 📄 License

This project is open-source and follows the same license as the main JARVIS 5.0 project.

---

## 🙏 Acknowledgments

Special thanks to:
- **llm-guy/jarvis** - Wake word detection concept
- **Gladiator07/JARVIS** - Comprehensive integrations
- **kishanrajput23/Jarvis-Desktop-Voice-Assistant** - Voice control patterns
- **danilofalcao/jarvis** - Multi-model AI concepts
- **Code-A2Z/jarvis** - Security patterns
- **projectswithdigambar/jarvis** - Desktop automation ideas

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section in main README
2. Review the configuration guide above
3. Test individual services independently
4. Verify API keys and credentials

---

**Made with ❤️ by combining the best features from the JARVIS community!**
