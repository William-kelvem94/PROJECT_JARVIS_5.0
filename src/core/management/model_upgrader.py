"""
Model Upgrader - Sistema de Upgrade de Modelos de IA
Gerencia download e upgrade de modelos avanÃ§ados
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
                    "installed": True  # JÃ¡ instalado
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
        """Verifica se Ollama estÃ¡ instalado"""
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
        logger.info("ðŸ”„ Iniciando upgrade Qwen 0.5B â†’ 3B...")
        
        if not self.check_ollama_installed():
            logger.error("âŒ Ollama nÃ£o estÃ¡ instalado")
            logger.info("ðŸ“¥ Instale Ollama: https://ollama.ai/download")
            return False
        
        try:
            # Pull do modelo Qwen 2.5 3B
            logger.info("ðŸ“¥ Baixando Qwen 2.5 3B (pode levar alguns minutos)...")
            
            result = subprocess.run(
                ["ollama", "pull", "qwen2.5:3b"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
            
            if result.returncode == 0:
                logger.info("âœ… Qwen 2.5 3B instalado com sucesso!")
                self.available_models["qwen"]["3B"]["installed"] = True
                return True
            else:
                logger.error(f"âŒ Erro ao instalar: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("âŒ Timeout ao baixar modelo (>10min)")
            return False
        except Exception as e:
            logger.error(f"âŒ Erro ao fazer upgrade: {e}")
            return False
    
    def install_llava_1_6(self) -> bool:
        """Instala LLaVA 1.6 via Ollama"""
        logger.info("ðŸ”„ Instalando LLaVA 1.6...")
        
        if not self.check_ollama_installed():
            logger.error("âŒ Ollama nÃ£o estÃ¡ instalado")
            return False
        
        try:
            logger.info("ðŸ“¥ Baixando LLaVA 1.6 (pode levar alguns minutos)...")
            
            result = subprocess.run(
                ["ollama", "pull", "llava:7b"],
                capture_output=True,
                text=True,
                timeout=900  # 15 minutos
            )
            
            if result.returncode == 0:
                logger.info("âœ… LLaVA 1.6 instalado com sucesso!")
                self.available_models["llava"]["1.6-7B"]["installed"] = True
                return True
            else:
                logger.error(f"âŒ Erro ao instalar: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"âŒ Erro ao instalar LLaVA: {e}")
            return False
    
    def install_xtts_v2(self) -> bool:
        """Instala XTTS-v2 para TTS neural"""
        logger.info("ðŸ”„ Instalando XTTS-v2...")
        
        try:
            # Instalar via pip
            logger.info("ðŸ“¥ Instalando TTS (Coqui)...")
            
            result = subprocess.run(
                ["pip", "install", "TTS"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("âœ… XTTS-v2 instalado com sucesso!")
                self.available_models["xtts"]["v2"]["installed"] = True
                
                # Baixar modelo
                logger.info("ðŸ“¥ Baixando modelo XTTS-v2...")
                try:
                    from TTS.api import TTS
                    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                    logger.info("âœ… Modelo XTTS-v2 baixado!")
                except Exception as e:
                    logger.warning(f"âš ï¸ Modelo serÃ¡ baixado no primeiro uso: {e}")
                
                return True
            else:
                logger.error(f"âŒ Erro ao instalar: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"âŒ Erro ao instalar XTTS-v2: {e}")
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
        logger.info("ðŸš€ Iniciando upgrade completo de modelos...")
        
        results = {
            "qwen_3b": self.upgrade_qwen_to_3b(),
            "llava_1_6": self.install_llava_1_6(),
            "xtts_v2": self.install_xtts_v2()
        }
        
        success_count = sum(results.values())
        total = len(results)
        
        logger.info(f"âœ… Upgrade completo: {success_count}/{total} modelos instalados")
        
        return results
    
    def get_recommendations(self) -> List[str]:
        """Retorna recomendaÃ§Ãµes de upgrade"""
        recommendations = []
        
        # Verificar Ollama
        if not self.check_ollama_installed():
            recommendations.append(
                "ðŸ“¥ Instale Ollama para modelos locais: https://ollama.ai/download"
            )
        
        # Verificar modelos nÃ£o instalados
        if not self.available_models["qwen"]["3B"]["installed"]:
            recommendations.append(
                "ðŸ§  Upgrade Qwen para 3B para melhor performance"
            )
        
        if not self.available_models["llava"]["1.6-7B"]["installed"]:
            recommendations.append(
                "ðŸ‘ï¸ Instale LLaVA 1.6 para visÃ£o multimodal avanÃ§ada"
            )
        
        if not self.available_models["xtts"]["v2"]["installed"]:
            recommendations.append(
                "ðŸ—£ï¸ Instale XTTS-v2 para TTS de alta qualidade"
            )
        
        return recommendations



# InstÃ¢ncia global removida para evitar execuÃ§Ã£o durante import
# model_upgrader = ModelUpgrader()


# Exemplo de uso
if __name__ == "__main__":
    print("ðŸ” Verificando status dos modelos...\n")
    
    status = model_upgrader.get_model_status()
    
    for model_type, versions in status.items():
        print(f"\n{model_type.upper()}:")
        for version, info in versions.items():
            status_icon = "âœ…" if info["installed"] else "âŒ"
            print(f"  {status_icon} {info['name']} ({info['size']})")
    
    print("\nðŸ“‹ RecomendaÃ§Ãµes:")
    for rec in model_upgrader.get_recommendations():
        print(f"  {rec}")
    
    # Perguntar se quer fazer upgrade
    print("\nðŸš€ Deseja fazer upgrade de todos os modelos? (s/n)")
    choice = input().lower()
    
    if choice == 's':
        results = model_upgrader.upgrade_all()
        print("\nðŸ“Š Resultados:")
        for model, success in results.items():
            icon = "âœ…" if success else "âŒ"
            print(f"  {icon} {model}")
