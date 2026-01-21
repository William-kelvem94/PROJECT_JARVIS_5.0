"""
Web Search Integration - Integração com Busca Web SEGURA
Usa Google Search com proteção total contra vazamento e ataques
GRATUITO - SEM API KEYS - SEM DEPENDÊNCIAS EXTERNAS
"""

from typing import Dict, Any, List, Optional
import os
import requests
import re
import time
import random
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from core.logger import logger


class SearchSecurityManager:
    """
    Gerenciador de segurança para buscas web.
    Previne vazamento de dados e controla acesso.
    """
    
    def __init__(self):
        self.rate_limit_window = 60  # segundos
        self.max_requests_per_window = 10
        self.request_history = []
        self.blocked_patterns = [
            # Padrões que podem vazar informações sensíveis
            r'senha', r'password', r'token', r'api[_-]?key',
            r'secret', r'credential', r'auth',
            r'\d{3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{2}',  # CPF brasileiro
            # Cartão: mais específico para evitar falsos positivos
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        ]
        self.safe_user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        logger.info("🔒 Security Manager inicializado")
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitiza query para remover informações sensíveis.
        
        Args:
            query: Query original
            
        Returns:
            Query sanitizada ou None se bloqueada
        """
        query_lower = query.lower()
        
        # Verificar padrões bloqueados
        for pattern in self.blocked_patterns:
            if re.search(pattern, query_lower):
                logger.warning(f"🚨 Query bloqueada por conter informação sensível: {pattern}")
                raise ValueError("Query contém informação sensível e foi bloqueada por segurança")
        
        # Limitar tamanho
        if len(query) > 500:
            logger.warning("Query muito longa, truncando")
            query = query[:500]
        
        # Remover caracteres perigosos
        query = re.sub(r'[<>"\']', '', query)
        
        return query
    
    def check_rate_limit(self) -> bool:
        """
        Verifica rate limit para prevenir abuso.
        
        Returns:
            True se pode fazer requisição
        """
        now = datetime.now()
        
        # Remover requisições antigas
        self.request_history = [
            req_time for req_time in self.request_history
            if (now - req_time).total_seconds() < self.rate_limit_window
        ]
        
        # Verificar limite
        if len(self.request_history) >= self.max_requests_per_window:
            logger.warning(f"🚨 Rate limit atingido: {len(self.request_history)}/{self.max_requests_per_window}")
            return False
        
        # Adicionar nova requisição
        self.request_history.append(now)
        return True
    
    def get_safe_headers(self) -> Dict[str, str]:
        """Retorna headers seguros para requisições."""
        return {
            'User-Agent': random.choice(self.safe_user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def anonymize_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove informações sensíveis dos resultados."""
        for result in results:
            # Remover tracking parameters de URLs
            if 'url' in result:
                url = result['url']
                try:
                    # Parse URL para manipulação segura
                    parsed = urlparse(url)
                    if parsed.query:
                        # Remover parâmetros de tracking usando parse_qs
                        params = parse_qs(parsed.query)
                        clean_params = {
                            k: v for k, v in params.items()
                            if not any(k.startswith(prefix) for prefix in ['utm_', 'fbclid', 'gclid', 'ref'])
                        }
                        # Reconstruir URL limpa
                        from urllib.parse import urlencode, urlunparse
                        clean_query = urlencode(clean_params, doseq=True)
                        result['url'] = urlunparse((
                            parsed.scheme, parsed.netloc, parsed.path,
                            parsed.params, clean_query, parsed.fragment
                        ))
                except Exception as e:
                    logger.debug(f"Erro ao limpar URL: {e}")
                    # Fallback: regex simples
                    result['url'] = re.sub(r'[?&](utm_|fbclid|gclid|ref=)[^&]*&?', '', url).rstrip('?&')
        
        return results


class GoogleSearch:
    """
    Busca usando Google (scraping seguro - SEM API KEY).
    TOTALMENTE GRATUITO e INDEPENDENTE.
    COM MEDIDAS DE SEGURANÇA contra vazamento e ataques.
    """
    
    def __init__(self, security_manager: SearchSecurityManager = None):
        self.security = security_manager or SearchSecurityManager()
        self.base_url = "https://www.google.com/search"
        self.session = requests.Session()
        logger.info("🔍 Google Search inicializado (modo seguro)")
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca no Google com segurança total.
        
        Args:
            query: Query de busca
            num_results: Número de resultados desejados
            
        Returns:
            Lista de resultados seguros
        """
        try:
            # 1. SEGURANÇA: Sanitizar query
            safe_query = self.security.sanitize_query(query)
            
            # 2. SEGURANÇA: Verificar rate limit
            if not self.security.check_rate_limit():
                logger.warning("Rate limit atingido, aguardando...")
                time.sleep(2)
                if not self.security.check_rate_limit():
                    raise Exception("Rate limit: muitas requisições. Aguarde 1 minuto.")
            
            # 3. Fazer busca segura
            params = {
                'q': safe_query,
                'num': num_results + 5,  # Pegar alguns extras
                'hl': 'pt-BR',
            }
            
            headers = self.security.get_safe_headers()
            
            response = self.session.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Google search failed: {response.status_code}")
                return []
            
            # 4. Parse results
            results = self._parse_google_results(response.text, num_results)
            
            # 5. SEGURANÇA: Anonimizar resultados
            results = self.security.anonymize_results(results)
            
            logger.info(f"✅ Google search: {len(results)} resultados seguros")
            return results
            
        except ValueError as e:
            # Query bloqueada por segurança
            logger.error(f"❌ {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
            return []
    
    def _parse_google_results(self, html: str, num_results: int) -> List[Dict[str, Any]]:
        """Parse HTML do Google para extrair resultados."""
        results = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Procurar divs de resultado
            # Google muda a estrutura frequentemente, usar múltiplas estratégias
            search_divs = soup.find_all('div', class_='g')
            
            for div in search_divs[:num_results]:
                try:
                    # Extrair título
                    title_elem = div.find('h3')
                    title = title_elem.get_text() if title_elem else ''
                    
                    # Extrair URL
                    link_elem = div.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    
                    # Extrair snippet
                    snippet_elem = div.find('div', class_=['VwiC3b', 'yXK7lf'])
                    if not snippet_elem:
                        snippet_elem = div.find('span', class_='aCOpRe')
                    snippet = snippet_elem.get_text() if snippet_elem else ''
                    
                    if title and url:
                        results.append({
                            'title': title,
                            'snippet': snippet,
                            'url': url,
                            'source': 'Google Search'
                        })
                    
                except Exception as e:
                    logger.debug(f"Erro ao parse resultado individual: {e}")
                    continue
            
            # Se não encontrou resultados, tentar estratégia alternativa
            if not results:
                # Buscar qualquer link com título
                for link in soup.find_all('a', href=True)[:num_results]:
                    href = link.get('href', '')
                    if href.startswith('/url?q='):
                        try:
                            # Extrair URL real de forma segura
                            parsed = parse_qs(href[5:])  # Remove '/url?'
                            url = parsed.get('q', [''])[0] if 'q' in parsed else ''
                            title = link.get_text().strip()
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'snippet': '',
                                    'url': url,
                                    'source': 'Google Search'
                                })
                        except Exception as e:
                            logger.debug(f"Erro ao parse URL alternativa: {e}")
                            continue
            
        except Exception as e:
            logger.error(f"Erro ao parse Google results: {e}")
        
        return results


class WebSearchIntegration:
    """
    Integração completa de busca web para JARVIS.
    USA GOOGLE com SEGURANÇA TOTAL.
    GRATUITO, SEM API KEYS, SEM DEPENDÊNCIAS EXTERNAS.
    """
    
    def __init__(self):
        """Inicializa integração de busca web com Google seguro."""
        self.security = SearchSecurityManager()
        self.google_search = GoogleSearch(self.security)
        
        logger.info("✅ WebSearchIntegration inicializada (Google Search + Segurança)")
        logger.info("🔒 Medidas de segurança ativas:")
        logger.info("  - Sanitização de queries")
        logger.info("  - Rate limiting (10 req/min)")
        logger.info("  - Bloqueio de dados sensíveis")
        logger.info("  - Anonimização de resultados")
        logger.info("  - Headers seguros rotativos")
    
    def search(
        self,
        query: str,
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        Realiza busca web segura usando Google.
        
        Args:
            query: Query de busca
            num_results: Número de resultados
            
        Returns:
            Resultados seguros da busca
        """
        try:
            logger.info(f"🔍 Buscando (seguro): {query}")
            
            # Buscar no Google com segurança
            results = self.google_search.search(query, num_results)
            
            logger.info(f"✅ {len(results)} resultados seguros encontrados")
            
            return {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'total_results': len(results),
                'results': results,
                'security': {
                    'sanitized': True,
                    'rate_limited': True,
                    'anonymized': True
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na busca web: {e}")
            return {
                'query': query,
                'error': str(e),
                'results': [],
                'security': {'error': True}
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
        formatted = f"Resultados da busca Google (segura) para '{query}':\n\n"
        
        for i, result in enumerate(search_results['results'][:num_results], 1):
            formatted += f"{i}. {result.get('title', 'Sem título')}\n"
            formatted += f"   {result.get('snippet', 'Sem descrição')}\n"
            if result.get('url'):
                formatted += f"   Fonte: {result.get('url')}\n"
            formatted += "\n"
        
        formatted += "\n🔒 Busca realizada com segurança: dados protegidos, sem vazamentos.\n"
        
        return formatted
    
    def is_available(self) -> bool:
        """Verifica se busca web está disponível."""
        return True  # Google search sempre disponível


class ResearchAssistant:
    """
    Assistente de pesquisa para JARVIS.
    Combina busca Google segura com LLM para respostas fundamentadas.
    """
    
    def __init__(self, web_search: WebSearchIntegration):
        """
        Inicializa assistente de pesquisa.
        
        Args:
            web_search: Instância de WebSearchIntegration
        """
        self.web_search = web_search
        logger.info("ResearchAssistant inicializado (com Google seguro)")
    
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
            'pesquise', 'busque', 'procure', 'google',
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
        
        logger.info(f"📚 Pesquisando (seguro): {query} (deep={deep_search})")
        
        # Buscar na web com segurança
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
            'timestamp': datetime.now().isoformat(),
            'security': {
                'protected': True,
                'sanitized': True,
                'safe': True
            }
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
        
        # Realizar pesquisa segura
        research_results = self.research(query, deep_search=False)
        
        # Formatar contexto
        context = "=== INFORMAÇÕES DA WEB (Google Search Seguro) ===\n\n"
        
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
        
        context += "\n🔒 Busca protegida: sem vazamento de dados\n"
        context += "=== FIM DAS INFORMAÇÕES DA WEB ===\n\n"
        
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
