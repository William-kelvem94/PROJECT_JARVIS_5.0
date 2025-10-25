"""
Voice Plugin - Real implementation with Whisper STT and pyttsx3 TTS
"""
import asyncio
import tempfile
import os
from typing import Dict, Any, Optional
import pyttsx3
import whisper
import numpy as np
from pathlib import Path

from app.core.plugin_manager import PluginBase
from app.core.config import settings
from app.core.exceptions import VoiceException


class VoicePlugin(PluginBase):
    """
    Plugin for voice processing - Speech-to-Text and Text-to-Speech
    """
    
    name = "voice"
    version = "1.0.0"
    description = "Voice processing with Whisper STT and pyttsx3 TTS"
    author = "Jarvis Team"
    
    def __init__(self):
        super().__init__()
        self.whisper_model: Optional[whisper.Whisper] = None
        self.tts_engine: Optional[pyttsx3.Engine] = None
        self.model_name = settings.WHISPER_MODEL
    
    async def initialize(self) -> bool:
        """
        Initialize voice processing models
        """
        try:
            self.logger.info(f"Loading Whisper model: {self.model_name}")
            
            # Load Whisper model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.whisper_model = await loop.run_in_executor(
                None,
                whisper.load_model,
                self.model_name
            )
            
            # Initialize TTS engine
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS
            self.tts_engine.setProperty('rate', 150)  # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to use a more natural voice
                for voice in voices:
                    if 'english' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.logger.info("Voice plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize voice plugin: {str(e)}")
            return False
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process voice data
        
        Args:
            data: Input data with 'action' and relevant parameters
                - action: 'transcribe' or 'speak'
                - For transcribe: 'audio_path' or 'audio_data'
                - For speak: 'text' and optionally 'output_path'
        
        Returns:
            Processing result
        """
        action = data.get("action")
        
        if action == "transcribe":
            return await self._transcribe(data)
        elif action == "speak":
            return await self._speak(data)
        else:
            raise VoiceException(f"Unknown action: {action}")
    
    async def _transcribe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transcribe audio to text using Whisper
        
        Args:
            data: Audio data with 'audio_path' or 'audio_data'
        
        Returns:
            Transcription result
        """
        try:
            audio_path = data.get("audio_path")
            audio_data = data.get("audio_data")
            language = data.get("language", "en")
            
            if not audio_path and not audio_data:
                raise VoiceException("No audio input provided")
            
            # If audio data provided, save to temp file
            if audio_data:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    audio_path = tmp_file.name
            
            # Transcribe in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.whisper_model.transcribe,
                audio_path,
                {"language": language}
            )
            
            # Clean up temp file if created
            if audio_data and os.path.exists(audio_path):
                os.remove(audio_path)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": [
                    {
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"]
                    }
                    for seg in result.get("segments", [])
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            raise VoiceException(f"Transcription failed: {str(e)}")
    
    async def _speak(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert text to speech using pyttsx3
        
        Args:
            data: Text data with 'text' and optionally 'output_path'
        
        Returns:
            Speech generation result
        """
        try:
            text = data.get("text")
            output_path = data.get("output_path")
            
            if not text:
                raise VoiceException("No text provided")
            
            # Generate speech in thread pool
            loop = asyncio.get_event_loop()
            
            if output_path:
                # Save to file
                await loop.run_in_executor(
                    None,
                    self._save_speech,
                    text,
                    output_path
                )
                
                return {
                    "status": "success",
                    "output_path": output_path
                }
            else:
                # Play directly
                await loop.run_in_executor(
                    None,
                    self._play_speech,
                    text
                )
                
                return {
                    "status": "success",
                    "message": "Speech played"
                }
            
        except Exception as e:
            self.logger.error(f"Speech generation failed: {str(e)}")
            raise VoiceException(f"Speech generation failed: {str(e)}")
    
    def _save_speech(self, text: str, output_path: str):
        """
        Save speech to file (synchronous)
        """
        self.tts_engine.save_to_file(text, output_path)
        self.tts_engine.runAndWait()
    
    def _play_speech(self, text: str):
        """
        Play speech directly (synchronous)
        """
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    async def transcribe_audio(self, audio_path: str, language: str = "en") -> str:
        """
        Convenience method to transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Audio language
        
        Returns:
            Transcribed text
        """
        result = await self._transcribe({
            "audio_path": audio_path,
            "language": language
        })
        return result["text"]
    
    async def speak_text(self, text: str, output_path: Optional[str] = None):
        """
        Convenience method to speak text
        
        Args:
            text: Text to speak
            output_path: Optional path to save audio file
        """
        await self._speak({
            "text": text,
            "output_path": output_path
        })
    
    async def shutdown(self):
        """
        Cleanup resources
        """
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        
        self.whisper_model = None
        self.tts_engine = None
        
        self.logger.info("Voice plugin shut down")

