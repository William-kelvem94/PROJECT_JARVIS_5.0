"""
Web Search Integration - Integração com Busca Web
Adiciona capacidade de pesquisa na web para JARVIS (online mode)
"""

from typing import Dict, Any, List, Optional
import os
import requests
from datetime import datetime
from core.logger import logger


class WebSearchProvider:
    """Provedor base para busca web."""
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza busca web.
        
        Args:
            query: Query de busca
            num_results: Número de resultados
            
        Returns:
            Lista de resultados
        """
        raise NotImplementedError


class DuckDuckGoSearch(WebSearchProvider):
    """Busca usando DuckDuckGo (sem necessidade de API key)."""
    
    def __init__(self):
        self.api_url = "https://api.duckduckgo.com/"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Busca usando DuckDuckGo Instant Answer API."""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"DuckDuckGo search failed: {response.status_code}")
                return []
            
            data = response.json()
            results = []
            
            # Abstract (resposta direta)
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Result'),
                    'snippet': data.get('Abstract'),
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo Instant Answer'
                })
            
            # Related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('Text', '')[:100],
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo'
                    })
            
            return results[:num_results]
            
        except Exception as e:
            logger.error(f"Error in DuckDuckGo search: {e}")
            return []


class WikipediaSearch(WebSearchProvider):
    """Busca usando Wikipedia API (sem necessidade de API key)."""
    
    def __init__(self, language: str = "pt"):
        self.language = language
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Busca artigos na Wikipedia."""
        try:
            # Primeiro, buscar artigos relacionados
            search_params = {
                'action': 'opensearch',
                'search': query,
                'limit': num_results,
                'format': 'json'
            }
            
            response = requests.get(
                self.api_url,
                params=search_params,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            titles = data[1] if len(data) > 1 else []
            descriptions = data[2] if len(data) > 2 else []
            urls = data[3] if len(data) > 3 else []
            
            results = []
            for i, title in enumerate(titles):
                results.append({
                    'title': title,
                    'snippet': descriptions[i] if i < len(descriptions) else '',
                    'url': urls[i] if i < len(urls) else '',
                    'source': 'Wikipedia'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Wikipedia search: {e}")
            return []


class WebSearchIntegration:
    """
    Integração completa de busca web para JARVIS.
    Combina múltiplos provedores para melhores resultados.
    """
    
    def __init__(
        self,
        enable_duckduckgo: bool = True,
        enable_wikipedia: bool = True
    ):
        """
        Inicializa integração de busca web.
        
        Args:
            enable_duckduckgo: Habilitar busca DuckDuckGo
            enable_wikipedia: Habilitar busca Wikipedia
        """
        self.providers = []
        
        if enable_duckduckgo:
            self.providers.append(DuckDuckGoSearch())
            logger.info("✅ DuckDuckGo search enabled")
        
        if enable_wikipedia:
            self.providers.append(WikipediaSearch())
            logger.info("✅ Wikipedia search enabled")
        
        logger.info(f"WebSearchIntegration inicializada com {len(self.providers)} provedores")
    
    def search(
        self,
        query: str,
        num_results: int = 5,
        providers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Realiza busca web agregando resultados de múltiplos provedores.
        
        Args:
            query: Query de busca
            num_results: Número de resultados por provedor
            providers: Lista de provedores específicos (None = todos)
            
        Returns:
            Resultados agregados da busca
        """
        try:
            logger.info(f"Buscando na web: {query}")
            
            all_results = []
            provider_results = {}
            
            for provider in self.providers:
                provider_name = provider.__class__.__name__
                
                # Filtrar por provedores específicos se fornecido
                if providers and provider_name not in providers:
                    continue
                
                results = provider.search(query, num_results)
                provider_results[provider_name] = results
                all_results.extend(results)
            
            # Remover duplicatas baseado em URL
            unique_results = []
            seen_urls = set()
            
            for result in all_results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
                elif not url:
                    unique_results.append(result)
            
            logger.info(f"Encontrados {len(unique_results)} resultados únicos")
            
            return {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'total_results': len(unique_results),
                'results': unique_results[:num_results * 2],  # Retornar até 2x o solicitado
                'provider_results': provider_results
            }
            
        except Exception as e:
            logger.error(f"Erro na busca web: {e}")
            return {
                'query': query,
                'error': str(e),
                'results': []
            }
    
    def search_and_summarize(
        self,
        query: str,
        num_results: int = 3
    ) -> str:
        """
        Busca e formata resultados para uso no LLM.
        
        Args:
            query: Query de busca
            num_results: Número de resultados
            
        Returns:
            String formatada com resultados
        """
        search_results = self.search(query, num_results)
        
        if not search_results.get('results'):
            return f"Nenhum resultado encontrado para: {query}"
        
        # Formatar para consumo pelo LLM
        formatted = f"Resultados da busca para '{query}':\n\n"
        
        for i, result in enumerate(search_results['results'][:num_results], 1):
            formatted += f"{i}. {result.get('title', 'Sem título')}\n"
            formatted += f"   {result.get('snippet', 'Sem descrição')}\n"
            if result.get('url'):
                formatted += f"   Fonte: {result.get('url')}\n"
            formatted += "\n"
        
        return formatted
    
    def is_available(self) -> bool:
        """Verifica se busca web está disponível."""
        return len(self.providers) > 0


class ResearchAssistant:
    """
    Assistente de pesquisa para JARVIS.
    Combina busca web com LLM para respostas fundamentadas.
    """
    
    def __init__(self, web_search: WebSearchIntegration):
        """
        Inicializa assistente de pesquisa.
        
        Args:
            web_search: Instância de WebSearchIntegration
        """
        self.web_search = web_search
        logger.info("ResearchAssistant inicializado")
    
    def should_use_web_search(self, query: str) -> bool:
        """
        Decide se deve usar busca web baseado na query.
        
        Args:
            query: Query do usuário
            
        Returns:
            True se deve buscar na web
        """
        # Indicadores de necessidade de busca web
        web_indicators = [
            'pesquise', 'busque', 'procure',
            'pesquisar', 'buscar', 'procurar',
            'o que é', 'quem é', 'quando foi',
            'qual', 'como funciona',
            'notícias', 'atual', 'recente',
            'últimas', 'novidades',
            'search', 'find', 'look up'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in web_indicators)
    
    def research(
        self,
        query: str,
        deep_search: bool = False
    ) -> Dict[str, Any]:
        """
        Realiza pesquisa completa sobre um tópico.
        
        Args:
            query: Tópico de pesquisa
            deep_search: Se True, busca mais resultados
            
        Returns:
            Resultados da pesquisa
        """
        num_results = 10 if deep_search else 5
        
        logger.info(f"Pesquisando: {query} (deep={deep_search})")
        
        # Buscar na web
        web_results = self.web_search.search(query, num_results)
        
        # Extrair informações chave
        key_findings = []
        sources = []
        
        for result in web_results.get('results', []):
            if result.get('snippet'):
                key_findings.append(result['snippet'])
            if result.get('url'):
                sources.append(result['url'])
        
        return {
            'query': query,
            'findings': key_findings,
            'sources': sources,
            'full_results': web_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_research_context(
        self,
        query: str,
        include_sources: bool = True
    ) -> str:
        """
        Gera contexto de pesquisa para adicionar ao prompt do LLM.
        
        Args:
            query: Query de pesquisa
            include_sources: Incluir URLs das fontes
            
        Returns:
            Contexto formatado
        """
        if not self.web_search.is_available():
            return ""
        
        # Realizar pesquisa
        research_results = self.research(query, deep_search=False)
        
        # Formatar contexto
        context = "=== INFORMAÇÕES DA WEB ===\n\n"
        
        findings = research_results.get('findings', [])
        if findings:
            for i, finding in enumerate(findings[:3], 1):  # Top 3
                context += f"{i}. {finding}\n\n"
        else:
            context += "Nenhuma informação relevante encontrada na web.\n\n"
        
        if include_sources and research_results.get('sources'):
            context += "Fontes:\n"
            for source in research_results['sources'][:3]:
                context += f"- {source}\n"
        
        context += "\n=== FIM DAS INFORMAÇÕES DA WEB ===\n\n"
        
        return context


# Instância global (será inicializada se necessário)
_web_search_instance = None
_research_assistant_instance = None


def get_web_search() -> Optional[WebSearchIntegration]:
    """Retorna instância global de WebSearchIntegration."""
    global _web_search_instance
    if _web_search_instance is None:
        try:
            _web_search_instance = WebSearchIntegration()
        except Exception as e:
            logger.error(f"Erro ao inicializar web search: {e}")
            return None
    return _web_search_instance


def get_research_assistant() -> Optional[ResearchAssistant]:
    """Retorna instância global de ResearchAssistant."""
    global _research_assistant_instance
    if _research_assistant_instance is None:
        web_search = get_web_search()
        if web_search:
            _research_assistant_instance = ResearchAssistant(web_search)
    return _research_assistant_instance
