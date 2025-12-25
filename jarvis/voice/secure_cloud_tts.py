"""
Engines TTS em nuvem gratuitos e seguros para JARVIS
"""

import os
import tempfile
import time
import requests
import hashlib
import json
from typing import Optional, Dict, Any
from pathlib import Path
import urllib.parse
import ssl
import certifi

# Pygame para reprodução segura
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from ..core.logger import default_logger


class SecureHTTPClient:
    """Cliente HTTP seguro para APIs TTS"""
    
    def __init__(self):
        self.session = requests.Session()
        # Configurar SSL seguro
        self.session.verify = certifi.where()
        # Timeout para evitar travamentos
        self.timeout = 30
        # Headers seguros
        self.session.headers.update({
            'User-Agent': 'JARVIS-TTS/5.0',
            'Accept': 'audio/mpeg, audio/wav, application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
    
    def safe_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Faz requisição HTTP segura com validações"""
        try:
            # Validar URL
            if not self._is_safe_url(url):
                raise ValueError(f"URL não segura: {url}")
            
            # Configurar timeout
            kwargs['timeout'] = kwargs.get('timeout', self.timeout)
            
            # Fazer requisição
            response = self.session.request(method, url, **kwargs)
            
            # Validar resposta
            if response.status_code == 200:
                return response
            else:
                raise requests.HTTPError(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            default_logger.error(f"Erro na requisição segura: {e}")
            return None
    
    def _is_safe_url(self, url: str) -> bool:
        """Valida se a URL é segura"""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Deve usar HTTPS
            if parsed.scheme != 'https':
                return False
            
            # Domínios confiáveis
            safe_domains = [
                'translate.google.com',
                'texttospeech.googleapis.com',
                'speech.platform.bing.com',
                'polly.amazonaws.com',
                'api.elevenlabs.io'
            ]
            
            # Verificar se o domínio está na lista de confiáveis
            return any(parsed.netloc.endswith(domain) for domain in safe_domains)
            
        except Exception:
            return False


class GoogleTTSFree:
    """Google TTS gratuito com segurança aprimorada"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        self.http_client = SecureHTTPClient()
        self.base_url = "https://translate.google.com/translate_tts"
        
        # Limites de segurança
        self.max_text_length = 200  # Google TTS gratuito tem limite
        self.daily_requests = 0
        self.max_daily_requests = 1000  # Limite conservador
        
        self.logger.info("Google TTS Free inicializado com segurança")
    
    def speak(self, text: str, emotion: Optional[str] = None) -> bool:
        """Fala usando Google TTS gratuito de forma segura"""
        try:
            # Verificar limites
            if not self._check_limits(text):
                return False
            
            # Quebrar texto em chunks se necessário
            chunks = self._split_text(text)
            
            for chunk in chunks:
                if not self._speak_chunk(chunk, emotion):
                    return False
                time.sleep(0.5)  # Pausa entre chunks para não sobrecarregar
            
            self.daily_requests += len(chunks)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no Google TTS Free: {e}")
            return False
    
    def _check_limits(self, text: str) -> bool:
        """Verifica limites de uso"""
        if len(text) > self.max_text_length * 5:  # Máximo 5 chunks
            self.logger.warning("Texto muito longo para Google TTS gratuito")
            return False
        
        if self.daily_requests >= self.max_daily_requests:
            self.logger.warning("Limite diário do Google TTS atingido")
            return False
        
        return True
    
    def _split_text(self, text: str) -> list:
        """Quebra texto em chunks seguros"""
        if len(text) <= self.max_text_length:
            return [text]
        
        chunks = []
        words = text.split()
        current_chunk = ""
        
        for word in words:
            if len(current_chunk + " " + word) <= self.max_text_length:
                current_chunk += (" " + word) if current_chunk else word
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _speak_chunk(self, text: str, emotion: Optional[str] = None) -> bool:
        """Fala um chunk de texto"""
        try:
            # Parâmetros seguros
            params = {
                'ie': 'UTF-8',
                'q': text,
                'tl': 'pt-br',
                'client': 'tw-ob',
                'ttsspeed': '0.8' if emotion == 'pensativo' else '1.0'
            }
            
            # Fazer requisição segura
            response = self.http_client.safe_request('GET', self.base_url, params=params)
            
            if not response:
                return False
            
            # Salvar áudio temporariamente
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_filename = temp_file.name
            
            # Reproduzir
            success = self._play_audio(temp_filename)
            
            # Limpar arquivo
            try:
                os.unlink(temp_filename)
            except:
                pass
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao processar chunk: {e}")
            return False
    
    def _play_audio(self, filename: str) -> bool:
        """Reproduz áudio de forma segura"""
        try:
            if PYGAME_AVAILABLE:
                pygame.mixer.init()
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.quit()
                return True
            else:
                # Fallback para playsound
                import playsound
                playsound.playsound(filename)
                return True
                
        except Exception as e:
            self.logger.error(f"Erro na reprodução: {e}")
            return False


class MicrosoftTTSFree:
    """Microsoft Edge TTS gratuito"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        self.available = False
        
        # Tentar importar edge-tts
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.available = True
            self.logger.info("Microsoft Edge TTS disponível")
        except ImportError:
            self.logger.info("Microsoft Edge TTS não disponível (instale: pip install edge-tts)")
    
    def speak(self, text: str, emotion: Optional[str] = None) -> bool:
        """Fala usando Microsoft Edge TTS"""
        if not self.available:
            return False
        
        try:
            import asyncio
            
            # Executar síntese assíncrona
            return asyncio.run(self._async_speak(text, emotion))
            
        except Exception as e:
            self.logger.error(f"Erro no Microsoft TTS: {e}")
            return False
    
    async def _async_speak(self, text: str, emotion: Optional[str] = None) -> bool:
        """Síntese assíncrona"""
        try:
            # Voz em português brasileiro
            voice = "pt-BR-FranciscaNeural"
            
            # Criar comunicador
            communicate = self.edge_tts.Communicate(text, voice)
            
            # Salvar áudio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            await communicate.save(temp_filename)
            
            # Reproduzir
            success = self._play_audio(temp_filename)
            
            # Limpar
            try:
                os.unlink(temp_filename)
            except:
                pass
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro na síntese assíncrona: {e}")
            return False
    
    def _play_audio(self, filename: str) -> bool:
        """Reproduz áudio"""
        try:
            if PYGAME_AVAILABLE:
                pygame.mixer.init()
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.quit()
                return True
            else:
                import playsound
                playsound.playsound(filename)
                return True
                
        except Exception as e:
            self.logger.error(f"Erro na reprodução: {e}")
            return False


class SecureCloudTTSManager:
    """Gerenciador seguro de TTS em nuvem gratuitos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Inicializar engines seguros
        self.google_tts = GoogleTTSFree(config)
        self.microsoft_tts = MicrosoftTTSFree(config)
        
        # Determinar engine preferido
        self.preferred_engine = self._determine_preferred_engine()
        
        # Estatísticas de uso
        self.usage_stats = {
            'google_requests': 0,
            'microsoft_requests': 0,
            'total_requests': 0
        }
        
        self.logger.info(f"Secure Cloud TTS Manager inicializado. Engine preferido: {self.preferred_engine}")
    
    def _determine_preferred_engine(self) -> str:
        """Determina engine preferido baseado na disponibilidade"""
        cloud_config = self.config.get('cloud_voice', {})
        
        # Verificar preferência do usuário
        if cloud_config.get('prefer_microsoft', False) and self.microsoft_tts.available:
            return 'microsoft'
        
        if cloud_config.get('prefer_google', True):
            return 'google'
        
        # Fallback automático
        if self.microsoft_tts.available:
            return 'microsoft'
        
        return 'google'
    
    def is_available(self) -> bool:
        """Verifica se algum engine está disponível"""
        return True  # Google TTS sempre disponível via HTTP
    
    def speak(self, text: str, emotion: Optional[str] = None) -> bool:
        """Fala usando engine seguro preferido"""
        try:
            success = False
            
            if self.preferred_engine == 'microsoft' and self.microsoft_tts.available:
                success = self.microsoft_tts.speak(text, emotion)
                if success:
                    self.usage_stats['microsoft_requests'] += 1
            
            # Fallback para Google se Microsoft falhar
            if not success:
                success = self.google_tts.speak(text, emotion)
                if success:
                    self.usage_stats['google_requests'] += 1
            
            if success:
                self.usage_stats['total_requests'] += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro no Secure Cloud TTS: {e}")
            return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso"""
        return self.usage_stats.copy()
    
    def get_available_engines(self) -> list:
        """Retorna engines disponíveis"""
        engines = ['google']  # Sempre disponível
        
        if self.microsoft_tts.available:
            engines.append('microsoft')
        
        return engines
