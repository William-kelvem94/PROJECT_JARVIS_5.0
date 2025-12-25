"""
Engines TTS locais aprimorados para máxima naturalidade offline
"""

import os
import tempfile
import time
import subprocess
import platform
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

# Coqui TTS otimizado
try:
    from TTS.api import TTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False

# Pygame para reprodução
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from ..core.logger import default_logger


class EnhancedCoquiTTS:
    """Coqui TTS aprimorado para máxima naturalidade"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        self.available = COQUI_TTS_AVAILABLE
        self.tts = None
        
        if self.available:
            try:
                # Usar modelo otimizado para português
                model_name = "tts_models/pt/cv/vits"  # Modelo específico para português
                self.tts = TTS(model_name)
                self.logger.info("Coqui TTS Enhanced inicializado com modelo português")
                
                # Configurações otimizadas
                self.voice_settings = {
                    'speed': 1.0,
                    'pitch': 1.0,
                    'energy': 1.0
                }
                
            except Exception as e:
                self.logger.error(f"Erro ao inicializar Coqui TTS Enhanced: {e}")
                # Fallback para modelo multilíngue
                try:
                    self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                    self.logger.info("Usando modelo multilíngue como fallback")
                except Exception as e2:
                    self.logger.error(f"Erro no fallback: {e2}")
                    self.available = False
    
    def speak(self, text: str, emotion: Optional[str] = None) -> bool:
        """Fala usando Coqui TTS otimizado"""
        if not self.available or not self.tts:
            return False
        
        try:
            # Ajustar configurações baseadas na emoção
            settings = self._get_emotion_settings(emotion)
            
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Gerar áudio com configurações otimizadas
            self.tts.tts_to_file(
                text=text,
                file_path=temp_filename,
                language="pt",
                **settings
            )
            
            # Reproduzir com qualidade otimizada
            success = self._play_optimized_audio(temp_filename)
            
            # Limpar
            try:
                os.unlink(temp_filename)
            except:
                pass
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro no Coqui TTS Enhanced: {e}")
            return False
    
    def _get_emotion_settings(self, emotion: Optional[str]) -> Dict[str, Any]:
        """Retorna configurações otimizadas por emoção"""
        emotion_settings = {
            'entusiasta': {'speed': 1.1, 'pitch': 1.05, 'energy': 1.2},
            'preocupado': {'speed': 0.9, 'pitch': 0.95, 'energy': 0.8},
            'pensativo': {'speed': 0.85, 'pitch': 0.9, 'energy': 0.9},
            'aliviado': {'speed': 1.0, 'pitch': 1.0, 'energy': 1.1}
        }
        
        return emotion_settings.get(emotion, {'speed': 1.0, 'pitch': 1.0, 'energy': 1.0})
    
    def _play_optimized_audio(self, filename: str) -> bool:
        """Reproduz áudio com qualidade otimizada"""
        try:
            if PYGAME_AVAILABLE:
                # Configurações otimizadas para pygame
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
                
                sound = pygame.mixer.Sound(filename)
                sound.play()
                
                # Aguardar conclusão
                while pygame.mixer.get_busy():
                    time.sleep(0.01)
                
                pygame.mixer.quit()
                return True
            else:
                # Fallback otimizado
                return self._play_with_system_optimized(filename)
                
        except Exception as e:
            self.logger.error(f"Erro na reprodução otimizada: {e}")
            return False
    
    def _play_with_system_optimized(self, filename: str) -> bool:
        """Reprodução otimizada usando sistema"""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                # Windows: usar PowerShell otimizado
                cmd = [
                    'powershell', '-Command',
                    f'Add-Type -AssemblyName presentationCore; '
                    f'$mediaPlayer = New-Object system.windows.media.mediaplayer; '
                    f'$mediaPlayer.open([uri]"{filename}"); '
                    f'$mediaPlayer.Play(); '
                    f'Start-Sleep -Seconds 1; '
                    f'while($mediaPlayer.NaturalDuration.HasTimeSpan -eq $false) {{ Start-Sleep -Milliseconds 50 }}; '
                    f'$duration = $mediaPlayer.NaturalDuration.TimeSpan.TotalSeconds; '
                    f'Start-Sleep -Seconds $duration'
                ]
                subprocess.run(cmd, check=True, capture_output=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na reprodução do sistema: {e}")
            return False


class OptimizedESpeakNG:
    """eSpeak-NG otimizado para máxima naturalidade"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        self.available = self._check_availability()
        
        # Configurações otimizadas
        self.base_settings = {
            'voice': 'pt-br+f3',  # Voz feminina brasileira
            'speed': 160,
            'pitch': 50,
            'amplitude': 100,
            'word_gap': 1,
            'capitals': 1
        }
    
    def _check_availability(self) -> bool:
        """Verifica disponibilidade do eSpeak-NG"""
        try:
            result = subprocess.run(['espeak-ng', '--version'], 
                                  capture_output=True, check=True, text=True)
            self.logger.info("eSpeak-NG disponível")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.info("eSpeak-NG não disponível")
            return False
    
    def speak(self, text: str, emotion: Optional[str] = None) -> bool:
        """Fala usando eSpeak-NG otimizado"""
        if not self.available:
            return False
        
        try:
            # Configurações baseadas na emoção
            settings = self._get_optimized_settings(emotion)
            
            # Pré-processar texto para melhor naturalidade
            processed_text = self._preprocess_text(text)
            
            # Comando otimizado
            cmd = [
                'espeak-ng',
                '-v', settings['voice'],
                '-s', str(settings['speed']),
                '-p', str(settings['pitch']),
                '-a', str(settings['amplitude']),
                '-g', str(settings['word_gap']),
                '-k', str(settings['capitals']),
                '--stdin'
            ]
            
            # Executar com entrada otimizada
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(input=processed_text.encode('utf-8'))
            
            return process.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Erro no eSpeak-NG otimizado: {e}")
            return False
    
    def _get_optimized_settings(self, emotion: Optional[str]) -> Dict[str, Any]:
        """Configurações otimizadas por emoção"""
        settings = self.base_settings.copy()
        
        emotion_mods = {
            'entusiasta': {'speed': 180, 'pitch': 60, 'amplitude': 110},
            'preocupado': {'speed': 140, 'pitch': 40, 'amplitude': 90},
            'pensativo': {'speed': 130, 'pitch': 35, 'amplitude': 85},
            'aliviado': {'speed': 170, 'pitch': 55, 'amplitude': 105}
        }
        
        if emotion in emotion_mods:
            settings.update(emotion_mods[emotion])
        
        return settings
    
    def _preprocess_text(self, text: str) -> str:
        """Pré-processa texto para melhor naturalidade"""
        # Adicionar pausas naturais
        text = text.replace(',', ', [[slnc 200]]')  # Pausa curta após vírgula
        text = text.replace('.', '. [[slnc 400]]')  # Pausa média após ponto
        text = text.replace('!', '! [[slnc 300]]')  # Pausa após exclamação
        text = text.replace('?', '? [[slnc 350]]')  # Pausa após interrogação
        
        # Melhorar pronúncia de palavras comuns
        replacements = {
            'você': 'vo-cê',
            'então': 'en-tão',
            'também': 'tam-bém',
            'através': 'a-tra-vés',
            'função': 'fun-ção'
        }
        
        for original, replacement in replacements.items():
            text = text.replace(original, replacement)
        
        return text


class EnhancedLocalTTSManager:
    """Gerenciador aprimorado de TTS locais"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Inicializar engines aprimorados
        self.coqui_engine = EnhancedCoquiTTS(config) if COQUI_TTS_AVAILABLE else None
        self.espeak_engine = OptimizedESpeakNG(config)
        
        # Determinar engine preferido
        self.preferred_engine = self._determine_best_engine()
        
        # Estatísticas
        self.usage_stats = {
            'coqui_requests': 0,
            'espeak_requests': 0,
            'total_requests': 0
        }
        
        self.logger.info(f"Enhanced Local TTS Manager inicializado. Engine preferido: {self.preferred_engine}")
    
    def _determine_best_engine(self) -> str:
        """Determina o melhor engine disponível"""
        # Prioridade: Coqui (melhor qualidade) > eSpeak otimizado
        if self.coqui_engine and self.coqui_engine.available:
            return 'coqui'
        
        if self.espeak_engine and self.espeak_engine.available:
            return 'espeak'
        
        return 'none'
    
    def is_available(self) -> bool:
        """Verifica se algum engine está disponível"""
        return self.preferred_engine != 'none'
    
    def speak(self, text: str, emotion: Optional[str] = None) -> bool:
        """Fala usando o melhor engine local disponível"""
        if not self.is_available():
            return False
        
        try:
            success = False
            
            if self.preferred_engine == 'coqui':
                success = self.coqui_engine.speak(text, emotion)
                if success:
                    self.usage_stats['coqui_requests'] += 1
            
            # Fallback para eSpeak se Coqui falhar
            if not success and self.espeak_engine.available:
                success = self.espeak_engine.speak(text, emotion)
                if success:
                    self.usage_stats['espeak_requests'] += 1
            
            if success:
                self.usage_stats['total_requests'] += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro no Enhanced Local TTS: {e}")
            return False
    
    def get_available_engines(self) -> List[str]:
        """Retorna engines disponíveis"""
        engines = []
        
        if self.coqui_engine and self.coqui_engine.available:
            engines.append('coqui')
        
        if self.espeak_engine and self.espeak_engine.available:
            engines.append('espeak')
        
        return engines
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso"""
        return self.usage_stats.copy()
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Retorna informações detalhadas dos engines"""
        return {
            'preferred': self.preferred_engine,
            'available': self.get_available_engines(),
            'coqui_available': self.coqui_engine.available if self.coqui_engine else False,
            'espeak_available': self.espeak_engine.available if self.espeak_engine else False,
            'total_engines': len(self.get_available_engines())
        }
