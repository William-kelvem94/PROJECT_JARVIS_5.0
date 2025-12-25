"""
Engine de síntese de voz para JARVIS
"""

import pyttsx3
import tempfile
import time
import os
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from gtts import gTTS
    import playsound
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

from ..core.logger import default_logger
from .natural_speech import NaturalSpeechProcessor

# Importar engines locais aprimorados
try:
    from .enhanced_local_tts import EnhancedLocalTTSManager
    ENHANCED_LOCAL_AVAILABLE = True
except ImportError:
    ENHANCED_LOCAL_AVAILABLE = False

# Importar engines seguros em nuvem
try:
    from .secure_cloud_tts import SecureCloudTTSManager
    SECURE_CLOUD_AVAILABLE = True
except ImportError:
    SECURE_CLOUD_AVAILABLE = False

# Importar processador inteligente
try:
    from .smart_natural_speech import SmartNaturalSpeechProcessor
    SMART_PROCESSOR_AVAILABLE = True
except ImportError:
    SMART_PROCESSOR_AVAILABLE = False


class SpeechEngine:
    """Engine de síntese de voz com naturalidade extrema"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Usar processador inteligente se disponível
        if SMART_PROCESSOR_AVAILABLE:
            self.natural_processor = SmartNaturalSpeechProcessor(config)
            self.logger.info("Usando processador inteligente de fala natural")
        else:
            self.natural_processor = NaturalSpeechProcessor(config)
            self.logger.info("Usando processador padrão de fala natural")
        
        # Inicializar pyttsx3
        self._init_pyttsx3()
        
        # Configurar engines locais aprimorados se disponíveis
        self.enhanced_local_tts = None
        if ENHANCED_LOCAL_AVAILABLE and config.get('local_voice', {}).get('use_local_tts', True):
            self.enhanced_local_tts = EnhancedLocalTTSManager(config)
            if self.enhanced_local_tts.is_available():
                self.logger.info(f"Engines TTS locais aprimorados disponíveis: {self.enhanced_local_tts.get_available_engines()}")
            else:
                self.enhanced_local_tts = None
        
        # Configurar engines seguros em nuvem se disponíveis
        self.secure_cloud_tts = None
        if SECURE_CLOUD_AVAILABLE and config.get('cloud_voice', {}).get('use_cloud_tts', True):
            self.secure_cloud_tts = SecureCloudTTSManager(config)
            if self.secure_cloud_tts.is_available():
                self.logger.info(f"Engines TTS seguros em nuvem disponíveis: {self.secure_cloud_tts.get_available_engines()}")
            else:
                self.secure_cloud_tts = None
        
        # Configurar gTTS se disponível
        self.use_gtts = GTTS_AVAILABLE and config.get('voice', {}).get('use_gtts', True)
        
        if self.secure_cloud_tts and self.secure_cloud_tts.is_available():
            self.logger.info(f"Usando engines TTS seguros em nuvem: {self.secure_cloud_tts.preferred_engine}")
        elif self.enhanced_local_tts and self.enhanced_local_tts.is_available():
            self.logger.info(f"Usando engines TTS locais aprimorados: {self.enhanced_local_tts.preferred_engine}")
        elif self.use_gtts:
            self.logger.info("gTTS disponível - usando voz natural do Google")
        else:
            self.logger.info("Usando apenas pyttsx3 para síntese de voz")
    
    def _init_pyttsx3(self):
        """Inicializa e configura pyttsx3"""
        try:
            self.engine = pyttsx3.init()
            
            # Configurações básicas
            voice_config = self.config.get('voice', {})
            self.engine.setProperty('rate', voice_config.get('rate', 180))
            self.engine.setProperty('volume', voice_config.get('volume', 0.9))
            
            # Configurar voz em português
            self._configure_portuguese_voice()
            
            # Configurar pitch se suportado
            try:
                self.engine.setProperty('pitch', voice_config.get('pitch', 50))
            except:
                pass  # Nem todas as engines suportam pitch
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar pyttsx3: {e}")
            raise
    
    def _configure_portuguese_voice(self):
        """Configura voz em português se disponível"""
        try:
            voices = self.engine.getProperty('voices')
            portuguese_voice = None
            
            # Procurar voz em português
            for voice in voices:
                voice_name = voice.name.lower()
                if any(keyword in voice_name for keyword in ['portuguese', 'pt', 'brazil', 'br']):
                    if any(quality in voice_name for quality in ['female', 'natural']) or portuguese_voice is None:
                        portuguese_voice = voice.id
            
            if portuguese_voice:
                self.engine.setProperty('voice', portuguese_voice)
                self.logger.debug("Voz em português configurada")
            else:
                self.logger.warning("Voz em português não encontrada")
                
        except Exception as e:
            self.logger.warning(f"Erro ao configurar voz portuguesa: {e}")
    
    def speak(self, text: str, emotion: Optional[str] = None, speed: Optional[int] = None, 
              final_pause: float = 0.8) -> bool:
        """
        Fala o texto com naturalidade extrema
        
        Args:
            text: Texto para falar
            emotion: Emoção (entusiasta, preocupado, pensativo, aliviado)
            speed: Velocidade específica (sobrescreve config)
            final_pause: Pausa final em segundos
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"A,B,C","location":"speech_engine.py:speak:entry","message":"Iniciando síntese de voz","data":{"original_text":text,"emotion":emotion,"speed":speed,"use_gtts":self.use_gtts,"gtts_available":GTTS_AVAILABLE},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            
            self.logger.voice_event("speak_start", f"text_length={len(text)}, emotion={emotion}")
            
            # Processar texto com inteligência baseada no engine
            engine_type = "online" if (self.secure_cloud_tts and self.secure_cloud_tts.is_available()) else "offline"
            
            if hasattr(self.natural_processor, 'process_text') and len(self.natural_processor.process_text.__code__.co_varnames) > 3:
                # Processador inteligente
                processed_text = self.natural_processor.process_text(text, emotion, engine_type)
            else:
                # Processador padrão
                processed_text = self.natural_processor.process_text(text, emotion)
            
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"B","location":"speech_engine.py:speak:processed","message":"Texto processado pelo natural_processor","data":{"processed_text":processed_text,"original_length":len(text),"processed_length":len(processed_text)},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            
            # Pausa inicial conversacional
            self._initial_conversational_pause()
            
            # Escolher engine baseado na prioridade: Secure Cloud > Local TTS > gTTS > pyttsx3
            engine_used = "none"
            
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"A,D,F","location":"speech_engine.py:speak:engine_choice","message":"Escolha do engine de voz","data":{"has_secure_cloud":self.secure_cloud_tts is not None,"secure_cloud_available":self.secure_cloud_tts.is_available() if self.secure_cloud_tts else False,"has_enhanced_local":self.enhanced_local_tts is not None,"enhanced_local_available":self.enhanced_local_tts.is_available() if self.enhanced_local_tts else False,"use_gtts_config":self.use_gtts,"text_length":len(processed_text)},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            
            # Tentar engines seguros em nuvem primeiro (melhor qualidade)
            if self.secure_cloud_tts and self.secure_cloud_tts.is_available():
                success = self.secure_cloud_tts.speak(processed_text, emotion)
                engine_used = "secure_cloud"
                # #region agent log
                with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    import json, time
                    f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"F","location":"speech_engine.py:speak:secure_cloud_result","message":"Resultado Secure Cloud TTS","data":{"success":success,"engine":self.secure_cloud_tts.preferred_engine},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
            
            # Fallback para engines locais aprimorados se cloud falhou
            elif self.enhanced_local_tts and self.enhanced_local_tts.is_available():
                success = self.enhanced_local_tts.speak(processed_text, emotion)
                engine_used = "enhanced_local"
                # #region agent log
                with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    import json, time
                    f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"D","location":"speech_engine.py:speak:enhanced_local_result","message":"Resultado Enhanced Local TTS","data":{"success":success,"engine":self.enhanced_local_tts.preferred_engine},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
            
            # Fallback para gTTS se local TTS falhou
            elif self.use_gtts and self._should_use_gtts(processed_text):
                success = self._speak_with_gtts(processed_text, emotion)
                engine_used = "gtts"
                # #region agent log
                with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    import json, time
                    f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"A","location":"speech_engine.py:speak:gtts_result","message":"Resultado gTTS","data":{"success":success},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
            
            # Último fallback para pyttsx3
            else:
                success = self._speak_with_pyttsx3(processed_text, emotion, speed)
                engine_used = "pyttsx3"
                # #region agent log
                with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    import json, time
                    f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"E","location":"speech_engine.py:speak:pyttsx3_result","message":"Resultado pyttsx3","data":{"success":success,"engine_rate":self.engine.getProperty('rate') if hasattr(self, 'engine') else None},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
            
            # Pausa final conversacional
            time.sleep(final_pause)
            
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"A,D,E","location":"speech_engine.py:speak:exit","message":"Síntese finalizada","data":{"success":success,"engine_used":engine_used},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            
            self.logger.voice_event("speak_end", f"success={success}")
            return success
            
        except Exception as e:
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"A,B,C,D,E","location":"speech_engine.py:speak:error","message":"Erro na síntese de voz","data":{"error":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            self.logger.error(f"Erro na síntese de voz: {e}")
            return False
    
    def _should_use_gtts(self, text: str) -> bool:
        """Decide se deve usar gTTS baseado no conteúdo"""
        # Só usar gTTS se não tiver engines melhores disponíveis
        if self.secure_cloud_tts and self.secure_cloud_tts.is_available():
            return False  # Usar cloud TTS que é melhor
        
        if self.enhanced_local_tts and self.enhanced_local_tts.is_available():
            return False  # Usar local TTS aprimorado que é melhor
        
        # Usar gTTS para textos longos ou palavras-chave importantes
        return (len(text) > 50 or 
                any(keyword in text.lower() for keyword in ['olá', 'ajuda', 'erro', 'pronto']))
    
    def _initial_conversational_pause(self):
        """Pausa inicial simulando processamento humano"""
        import random
        pause = random.uniform(0.3, 0.8)
        time.sleep(pause)
    
    def _speak_with_gtts(self, text: str, emotion: Optional[str] = None) -> bool:
        """Fala usando gTTS (Google Text-to-Speech)"""
        try:
            phrases = self.natural_processor.break_into_phrases(text)
            
            for i, phrase in enumerate(phrases):
                # Pausas contextuais entre frases
                if i > 0:
                    pause = self.natural_processor.calculate_contextual_pause(
                        phrase, phrases[i-1], emotion
                    )
                    time.sleep(pause)
                
                # Processar marcadores especiais
                phrase, extra_pause = self.natural_processor.process_markers(phrase)
                
                if extra_pause > 0:
                    time.sleep(extra_pause)
                
                # Pular frases vazias
                if not phrase.strip():
                    continue
                
                # Criar arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_filename = temp_file.name
                
                # Configurar velocidade baseada na emoção
                slow = emotion in ['preocupado', 'pensativo']
                
                # Gerar áudio
                tts = gTTS(text=phrase, lang='pt-br', slow=slow)
                tts.save(temp_filename)
                
                # Reproduzir
                playsound.playsound(temp_filename)
                
                # Limpar arquivo temporário
                try:
                    os.unlink(temp_filename)
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no gTTS: {e}")
            # Fallback para pyttsx3
            return self._speak_with_pyttsx3(text, emotion)
    
    def _speak_with_pyttsx3(self, text: str, emotion: Optional[str] = None, 
                           speed: Optional[int] = None) -> bool:
        """Fala usando pyttsx3 com melhorias avançadas"""
        try:
            # Salvar configurações atuais
            current_rate = self.engine.getProperty('rate')
            current_volume = self.engine.getProperty('volume')
            
            if speed is not None:
                self.engine.setProperty('rate', speed)
            
            phrases = self.natural_processor.break_into_phrases(text)
            
            for i, phrase in enumerate(phrases):
                # Pausas contextuais
                if i > 0:
                    pause = self.natural_processor.calculate_contextual_pause(
                        phrase, phrases[i-1], emotion
                    )
                    time.sleep(pause)
                
                # Processar marcadores
                phrase, extra_pause = self.natural_processor.process_markers(phrase)
                
                if extra_pause > 0:
                    time.sleep(extra_pause)
                
                if not phrase.strip():
                    continue
                
                # Configurar parâmetros baseados no contexto
                self._configure_contextual_parameters(phrase, emotion)
                
                # Falar
                self.engine.say(phrase)
                self.engine.runAndWait()
            
            # Restaurar configurações
            self.engine.setProperty('rate', current_rate)
            self.engine.setProperty('volume', current_volume)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no pyttsx3: {e}")
            return False
    
    def _configure_contextual_parameters(self, phrase: str, emotion: Optional[str] = None):
        """Configura parâmetros contextuais para pyttsx3"""
        try:
            # Configurar velocidade contextual
            base_rate = self.config.get('voice', {}).get('rate', 180)
            contextual_rate = self.natural_processor.calculate_contextual_speed(
                phrase, base_rate, emotion
            )
            self.engine.setProperty('rate', contextual_rate)
            
            # Configurar pitch contextual
            base_pitch = self.config.get('voice', {}).get('pitch', 50)
            contextual_pitch = self.natural_processor.calculate_contextual_pitch(
                phrase, base_pitch, emotion
            )
            
            try:
                self.engine.setProperty('pitch', contextual_pitch)
            except:
                pass  # Nem todas as engines suportam pitch
            
            # Configurar volume contextual
            base_volume = self.config.get('voice', {}).get('volume', 0.9)
            contextual_volume = self.natural_processor.calculate_contextual_volume(
                phrase, base_volume, emotion
            )
            self.engine.setProperty('volume', max(0.1, min(1.0, contextual_volume)))
            
        except Exception as e:
            self.logger.debug(f"Erro ao configurar parâmetros contextuais: {e}")
    
    def test_voice(self) -> bool:
        """Testa o sistema de voz"""
        test_text = "Olá! Este é um teste do sistema de voz do JARVIS."
        return self.speak(test_text, emotion='entusiasta')
    
    def cleanup(self):
        """Limpa recursos do engine"""
        try:
            if hasattr(self, 'engine'):
                self.engine.stop()
        except:
            pass
