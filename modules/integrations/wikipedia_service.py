"""
Wikipedia Service Integration
Provides Wikipedia search and information retrieval
"""

import re
from typing import Optional, List, Dict, Any


class WikipediaService:
    """
    Wikipedia integration for information retrieval.
    
    Features:
    - Search Wikipedia
    - Get article summaries
    - Get full article content
    - Multiple language support
    """
    
    def __init__(self, language: str = 'pt'):
        """
        Initialize Wikipedia service.
        
        Args:
            language: Wikipedia language code (e.g., 'pt', 'en')
        """
        self.language = language
        self.is_available = False
        
        try:
            import wikipedia
            self.wikipedia = wikipedia
            self.wikipedia.set_lang(language)
            self.is_available = True
            print(f"[Wikipedia] ✓ Wikipedia service initialized (language: {language})")
        except ImportError:
            print("[Wikipedia] ⚠ wikipedia library not installed")
            print("Install with: pip install wikipedia-api")
    
    def search(self, query: str, max_results: int = 5) -> List[str]:
        """
        Search Wikipedia.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of article titles
        """
        if not self.is_available:
            return []
        
        try:
            results = self.wikipedia.search(query, results=max_results)
            return results
        except Exception as e:
            print(f"[Wikipedia] Search error: {e}")
            return []
    
    def get_summary(
        self,
        title: str,
        sentences: int = 3,
        auto_suggest: bool = True
    ) -> Optional[str]:
        """
        Get Wikipedia article summary.
        
        Args:
            title: Article title
            sentences: Number of sentences to return
            auto_suggest: Enable auto-suggestion for similar titles
            
        Returns:
            Article summary or None if not found
        """
        if not self.is_available:
            return None
        
        try:
            summary = self.wikipedia.summary(
                title,
                sentences=sentences,
                auto_suggest=auto_suggest
            )
            return summary
        except self.wikipedia.exceptions.DisambiguationError as e:
            # Multiple options available
            print(f"[Wikipedia] Multiple options: {e.options[:5]}")
            # Try first option
            try:
                return self.wikipedia.summary(e.options[0], sentences=sentences)
            except:
                return None
        except self.wikipedia.exceptions.PageError:
            print(f"[Wikipedia] Page not found: {title}")
            return None
        except Exception as e:
            print(f"[Wikipedia] Error getting summary: {e}")
            return None
    
    def get_page(self, title: str, auto_suggest: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get full Wikipedia page.
        
        Args:
            title: Article title
            auto_suggest: Enable auto-suggestion
            
        Returns:
            Dictionary with page information or None if not found
        """
        if not self.is_available:
            return None
        
        try:
            page = self.wikipedia.page(title, auto_suggest=auto_suggest)
            return {
                'title': page.title,
                'content': page.content,
                'summary': page.summary,
                'url': page.url,
                'references': page.references,
                'links': page.links[:20],  # First 20 links
                'categories': page.categories
            }
        except self.wikipedia.exceptions.DisambiguationError as e:
            print(f"[Wikipedia] Multiple options: {e.options[:5]}")
            # Try first option
            try:
                return self.get_page(e.options[0], auto_suggest=False)
            except:
                return None
        except self.wikipedia.exceptions.PageError:
            print(f"[Wikipedia] Page not found: {title}")
            return None
        except Exception as e:
            print(f"[Wikipedia] Error getting page: {e}")
            return None
    
    def search_and_summarize(
        self,
        query: str,
        sentences: int = 3
    ) -> Optional[str]:
        """
        Search Wikipedia and return summary of first result.
        
        Args:
            query: Search query
            sentences: Number of sentences in summary
            
        Returns:
            Summary of first search result or None
        """
        results = self.search(query, max_results=1)
        if results:
            return self.get_summary(results[0], sentences=sentences)
        return None
    
    def format_summary_for_speech(
        self,
        summary: str,
        max_length: int = 500
    ) -> str:
        """
        Format summary for text-to-speech.
        
        Args:
            summary: Wikipedia summary
            max_length: Maximum character length
            
        Returns:
            Formatted string for TTS
        """
        if not summary:
            return "Não foi possível encontrar informações sobre este tópico."
        
        # Clean up summary
        clean_summary = summary.strip()
        
        # Truncate if too long
        if len(clean_summary) > max_length:
            # Try to cut at sentence boundary
            sentences = re.split(r'[.!?]\s+', clean_summary)
            result = ""
            for sentence in sentences:
                if len(result) + len(sentence) + 2 < max_length:
                    result += sentence + ". "
                else:
                    break
            clean_summary = result.strip()
        
        return clean_summary
    
    def get_info_about_person(self, person_name: str) -> Optional[str]:
        """
        Get information about a person.
        
        Args:
            person_name: Person's name
            
        Returns:
            Summary about the person
        """
        return self.search_and_summarize(person_name, sentences=4)
    
    def get_info_about_topic(self, topic: str) -> Optional[str]:
        """
        Get information about a topic.
        
        Args:
            topic: Topic to search
            
        Returns:
            Summary about the topic
        """
        return self.search_and_summarize(topic, sentences=3)


# Example usage
if __name__ == "__main__":
    # Initialize
    wiki = WikipediaService(language='pt')
    
    if wiki.is_available:
        # Search
        print("\n=== Search: Python ===")
        results = wiki.search("Python programação")
        print(f"Results: {results}")
        
        # Get summary
        print("\n=== Summary: Python ===")
        summary = wiki.get_summary("Python (linguagem de programação)", sentences=2)
        if summary:
            print(summary)
        
        # Format for speech
        print("\n=== Speech Format ===")
        if summary:
            speech_text = wiki.format_summary_for_speech(summary)
            print(speech_text)
        
        # Get info about person
        print("\n=== Info about Albert Einstein ===")
        person_info = wiki.get_info_about_person("Albert Einstein")
        if person_info:
            print(person_info)
        
        # Get full page
        print("\n=== Full Page: Artificial Intelligence ===")
        page = wiki.get_page("Inteligência artificial")
        if page:
            print(f"Title: {page['title']}")
            print(f"URL: {page['url']}")
            print(f"Links: {page['links'][:5]}")
    else:
        print("\nWikipedia service not available. Install wikipedia-api package.")
