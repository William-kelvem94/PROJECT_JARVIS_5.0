"""
News Service Integration
Provides news headlines from multiple sources
"""

import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime


class NewsService:
    """
    News service integration using NewsAPI.
    
    Features:
    - Top headlines
    - Search news by topic
    - Multiple sources
    - Category filtering
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize news service.
        
        Args:
            api_key: NewsAPI key (or use NEWS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('NEWS_API_KEY', '')
        self.base_url = "https://newsapi.org/v2"
        self.is_available = bool(self.api_key)
        
        if not self.is_available:
            print("[News] ⚠ No API key provided. Set NEWS_API_KEY environment variable.")
            print("[News] Get free API key from: https://newsapi.org/")
        else:
            print("[News] ✓ News service initialized")
    
    def get_top_headlines(
        self,
        country: str = 'br',
        category: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top news headlines.
        
        Args:
            country: Country code (e.g., 'br', 'us')
            category: Category (business, entertainment, general, health, science, sports, technology)
            max_results: Maximum number of articles to return
            
        Returns:
            List of news article dictionaries
        """
        if not self.is_available:
            return []
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'country': country,
                'pageSize': max_results
            }
            
            if category:
                params['category'] = category
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Format articles
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    'title': article.get('title', 'No title'),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'author': article.get('author', 'Unknown')
                })
            
            return formatted_articles
            
        except requests.exceptions.RequestException as e:
            print(f"[News] Request error: {e}")
            return []
        except Exception as e:
            print(f"[News] Error getting headlines: {e}")
            return []
    
    def search_news(
        self,
        query: str,
        language: str = 'pt',
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for news by topic.
        
        Args:
            query: Search query
            language: Language code (e.g., 'pt', 'en')
            max_results: Maximum number of articles
            
        Returns:
            List of news article dictionaries
        """
        if not self.is_available:
            return []
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                'apiKey': self.api_key,
                'q': query,
                'language': language,
                'pageSize': max_results,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Format articles
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    'title': article.get('title', 'No title'),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'author': article.get('author', 'Unknown')
                })
            
            return formatted_articles
            
        except requests.exceptions.RequestException as e:
            print(f"[News] Request error: {e}")
            return []
        except Exception as e:
            print(f"[News] Error searching news: {e}")
            return []
    
    def format_headlines_for_speech(
        self,
        articles: List[Dict[str, Any]],
        max_headlines: int = 5
    ) -> str:
        """
        Format headlines for text-to-speech.
        
        Args:
            articles: List of article dictionaries
            max_headlines: Maximum number of headlines to include
            
        Returns:
            Formatted string for TTS
        """
        if not articles:
            return "Não há notícias disponíveis no momento."
        
        count = min(len(articles), max_headlines)
        response = f"Aqui estão as {count} principais notícias: "
        
        for i, article in enumerate(articles[:max_headlines], 1):
            title = article.get('title', 'Sem título')
            source = article.get('source', 'Fonte desconhecida')
            response += f"{i}. {title}, da {source}. "
        
        return response
    
    def get_category_news(
        self,
        category: str,
        country: str = 'br',
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get news by category.
        
        Args:
            category: News category
            country: Country code
            max_results: Maximum number of articles
            
        Returns:
            List of news articles
        """
        return self.get_top_headlines(
            country=country,
            category=category,
            max_results=max_results
        )


# Fallback news service using RSS feeds (no API key required)
class RSSNewsService:
    """
    Simple RSS-based news service (no API key required).
    Falls back when NewsAPI is not available.
    """
    
    def __init__(self):
        """Initialize RSS news service."""
        self.feeds = {
            'br': [
                'https://g1.globo.com/rss/g1/',
                'https://www.bbc.com/portuguese/topics/c404v027de8t/rss',
            ],
            'us': [
                'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
                'https://feeds.bbci.co.uk/news/rss.xml',
            ]
        }
        print("[News] ✓ RSS News service initialized")
    
    def get_top_headlines(
        self,
        country: str = 'br',
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top headlines from RSS feeds.
        
        Args:
            country: Country code
            max_results: Maximum number of articles
            
        Returns:
            List of news articles
        """
        try:
            import feedparser
            
            feeds = self.feeds.get(country, self.feeds['br'])
            all_articles = []
            
            for feed_url in feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:max_results]:
                        all_articles.append({
                            'title': entry.get('title', 'No title'),
                            'description': entry.get('summary', ''),
                            'source': feed.feed.get('title', 'Unknown'),
                            'url': entry.get('link', ''),
                            'published_at': entry.get('published', ''),
                            'author': entry.get('author', 'Unknown')
                        })
                except Exception as e:
                    print(f"[News] Error parsing feed {feed_url}: {e}")
            
            return all_articles[:max_results]
            
        except ImportError:
            print("[News] feedparser not installed. Install with: pip install feedparser")
            return []
        except Exception as e:
            print(f"[News] Error getting RSS headlines: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Try NewsAPI first
    news = NewsService()
    
    if news.is_available:
        print("\n=== Top Headlines (Brazil) ===")
        headlines = news.get_top_headlines(country='br', max_results=5)
        for i, article in enumerate(headlines, 1):
            print(f"{i}. {article['title']}")
            print(f"   Source: {article['source']}")
        
        # Format for speech
        print("\n=== Speech Format ===")
        print(news.format_headlines_for_speech(headlines))
        
        # Search news
        print("\n=== Search: Technology ===")
        tech_news = news.search_news('tecnologia', max_results=3)
        for article in tech_news:
            print(f"- {article['title']}")
    else:
        print("\nNewsAPI not available. Trying RSS...")
        rss_news = RSSNewsService()
        headlines = rss_news.get_top_headlines(country='br', max_results=5)
        for i, article in enumerate(headlines, 1):
            print(f"{i}. {article['title']}")
