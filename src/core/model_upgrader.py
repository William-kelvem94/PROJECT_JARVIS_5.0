"""
Model Upgrader - Sistema de Upgrade de Modelos de IA
Gerencia download e upgrade de modelos avançados
"""

import logging
import os
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import shutil

logger = logging.getLogger(__name__)

class ModelUpgrader:
    """Gerenciador de upgrades de modelos"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.available_models = {
            "qwen": {
                "0.5B": {
                    "name": "Qwen 2.5 0.5B",
                    "size": "500MB",
                    "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF",
                    "installed": True  # Já instalado
                },
                "3B": {
                    "name": "Qwen 2.5 3B",
                    "size": "2GB",
                    "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF",
                    "installed": False
                }
            },
            "llava": {
                "1.5-7B": {
                    "name": "LLaVA 1.5 7B",
                    "size": "4GB",
                    "url": "https://huggingface.co/liuhaotian/llava-v1.5-7b",
                    "installed": False
                },
                "1.6-7B": {
                    "name": "LLaVA 1.6 7B",
                    "size": "4.5GB",
                    "url": "https://huggingface.co/liuhaotian/llava-v1.6-vicuna-7b",
                    "installed": False
                }
            },
            "xtts": {
                "v2": {
                    "name": "XTTS-v2",
                    "size": "1.8GB",
                    "url": "https://huggingface.co/coqui/XTTS-v2",
                    "installed": False
                }
            }
        }
    
    def check_ollama_installed(self) -> bool:
        """Verifica se Ollama está instalado"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def upgrade_qwen_to_3b(self) -> bool:
        """Upgrade do Qwen 0.5B para 3B via Ollama"""
        logger.info("🔄 Iniciando upgrade Qwen 0.5B → 3B...")
        
        if not self.check_ollama_installed():
            logger.error("❌ Ollama não está instalado")
            logger.info("📥 Instale Ollama: https://ollama.ai/download")
            return False
        
        try:
            # Pull do modelo Qwen 2.5 3B
            logger.info("📥 Baixando Qwen 2.5 3B (pode levar alguns minutos)...")
            
            result = subprocess.run(
                ["ollama", "pull", "qwen2.5:3b"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
            
            if result.returncode == 0:
                logger.info("✅ Qwen 2.5 3B instalado com sucesso!")
                self.available_models["qwen"]["3B"]["installed"] = True
                return True
            else:
                logger.error(f"❌ Erro ao instalar: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout ao baixar modelo (>10min)")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao fazer upgrade: {e}")
            return False
    
    def install_llava_1_6(self) -> bool:
        """Instala LLaVA 1.6 via Ollama"""
        logger.info("🔄 Instalando LLaVA 1.6...")
        
        if not self.check_ollama_installed():
            logger.error("❌ Ollama não está instalado")
            return False
        
        try:
            logger.info("📥 Baixando LLaVA 1.6 (pode levar alguns minutos)...")
            
            result = subprocess.run(
                ["ollama", "pull", "llava:7b"],
                capture_output=True,
                text=True,
                timeout=900  # 15 minutos
            )
            
            if result.returncode == 0:
                logger.info("✅ LLaVA 1.6 instalado com sucesso!")
                self.available_models["llava"]["1.6-7B"]["installed"] = True
                return True
            else:
                logger.error(f"❌ Erro ao instalar: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao instalar LLaVA: {e}")
            return False
    
    def install_xtts_v2(self) -> bool:
        """Instala XTTS-v2 para TTS neural"""
        logger.info("🔄 Instalando XTTS-v2...")
        
        try:
            # Instalar via pip
            logger.info("📥 Instalando TTS (Coqui)...")
            
            result = subprocess.run(
                ["pip", "install", "TTS"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ XTTS-v2 instalado com sucesso!")
                self.available_models["xtts"]["v2"]["installed"] = True
                
                # Baixar modelo
                logger.info("📥 Baixando modelo XTTS-v2...")
                try:
                    from TTS.api import TTS
                    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                    logger.info("✅ Modelo XTTS-v2 baixado!")
                except Exception as e:
                    logger.warning(f"⚠️ Modelo será baixado no primeiro uso: {e}")
                
                return True
            else:
                logger.error(f"❌ Erro ao instalar: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao instalar XTTS-v2: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """Retorna status de todos os modelos"""
        status = {}
        
        for model_type, versions in self.available_models.items():
            status[model_type] = {}
            for version, info in versions.items():
                status[model_type][version] = {
                    "name": info["name"],
                    "size": info["size"],
                    "installed": info["installed"]
                }
        
        return status
    
    def upgrade_all(self) -> Dict[str, bool]:
        """Tenta fazer upgrade de todos os modelos"""
        logger.info("🚀 Iniciando upgrade completo de modelos...")
        
        results = {
            "qwen_3b": self.upgrade_qwen_to_3b(),
            "llava_1_6": self.install_llava_1_6(),
            "xtts_v2": self.install_xtts_v2()
        }
        
        success_count = sum(results.values())
        total = len(results)
        
        logger.info(f"✅ Upgrade completo: {success_count}/{total} modelos instalados")
        
        return results
    
    def get_recommendations(self) -> List[str]:
        """Retorna recomendações de upgrade"""
        recommendations = []
        
        # Verificar Ollama
        if not self.check_ollama_installed():
            recommendations.append(
                "📥 Instale Ollama para modelos locais: https://ollama.ai/download"
            )
        
        # Verificar modelos não instalados
        if not self.available_models["qwen"]["3B"]["installed"]:
            recommendations.append(
                "🧠 Upgrade Qwen para 3B para melhor performance"
            )
        
        if not self.available_models["llava"]["1.6-7B"]["installed"]:
            recommendations.append(
                "👁️ Instale LLaVA 1.6 para visão multimodal avançada"
            )
        
        if not self.available_models["xtts"]["v2"]["installed"]:
            recommendations.append(
                "🗣️ Instale XTTS-v2 para TTS de alta qualidade"
            )
        
        return recommendations


# Instância global
model_upgrader = ModelUpgrader()


# Exemplo de uso
if __name__ == "__main__":
    print("🔍 Verificando status dos modelos...\n")
    
    status = model_upgrader.get_model_status()
    
    for model_type, versions in status.items():
        print(f"\n{model_type.upper()}:")
        for version, info in versions.items():
            status_icon = "✅" if info["installed"] else "❌"
            print(f"  {status_icon} {info['name']} ({info['size']})")
    
    print("\n📋 Recomendações:")
    for rec in model_upgrader.get_recommendations():
        print(f"  {rec}")
    
    # Perguntar se quer fazer upgrade
    print("\n🚀 Deseja fazer upgrade de todos os modelos? (s/n)")
    choice = input().lower()
    
    if choice == 's':
        results = model_upgrader.upgrade_all()
        print("\n📊 Resultados:")
        for model, success in results.items():
            icon = "✅" if success else "❌"
            print(f"  {icon} {model}")
