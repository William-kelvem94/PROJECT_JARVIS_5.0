#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - DOWNLOAD DE MODELOS LOCAIS
Script para baixar todos os modelos necessários para funcionamento offline
"""

import os
import sys
import requests
import hashlib
import tarfile
import zipfile
from pathlib import Path
from tqdm import tqdm
import argparse

class ModelDownloader:
    """Downloader de modelos para funcionamento 100% local"""

    def __init__(self, base_dir="./"):
        self.base_dir = Path(base_dir)
        self.models_dir = self.base_dir / "models"
        self.data_dir = self.base_dir / "data"

        # Configurações de download
        self.chunk_size = 8192
        self.timeout = 300  # 5 minutos timeout

        # Lista de modelos necessários
        self.models = {
            # Modelos de Visão Computacional
            "facenet_pytorch": {
                "url": "https://github.com/timesler/facenet-pytorch/releases/download/v2.5.2/20180402-114759-vggface2.pt",
                "path": "facenet/vggface2.pt",
                "size": "~100MB",
                "description": "FaceNet PyTorch - Reconhecimento Facial"
            },

            # Modelos de Áudio (Whisper)
            "whisper_base": {
                "url": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c551/base.pt",
                "path": "whisper_base.pt",
                "size": "~74MB",
                "description": "Whisper Base - Reconhecimento de Voz"
            },
            "whisper_medium": {
                "url": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c614f32c102/medium.pt",
                "path": "whisper_medium.pt",
                "size": "~764MB",
                "description": "Whisper Medium - Melhor qualidade"
            },

            # Modelos de TTS (Piper)
            "piper_tts_en": {
                "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
                "path": "piper_voices/en_US-lessac-medium.onnx",
                "size": "~30MB",
                "description": "Piper TTS - Voz Inglesa"
            },
            "piper_tts_config": {
                "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
                "path": "piper_voices/en_US-lessac-medium.onnx.json",
                "size": "~1KB",
                "description": "Configuração Piper TTS"
            },

            # Modelos de NLP (GPT4All)
            "gpt4all_orca": {
                "url": "https://gpt4all.io/models/gguf/orca-2-13b.Q4_0.gguf",
                "path": "orca-2-13b.Q4_0.gguf",
                "size": "~7GB",
                "description": "GPT4All Orca - LLM Local"
            },

            # Modelos de NLP (Llama.cpp)
            "llama_2_7b": {
                "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_0.gguf",
                "path": "llama-2-7b-chat.Q4_0.gguf",
                "size": "~3.5GB",
                "description": "Llama 2 7B Chat - LLM Local"
            }
        }

    def download_file(self, url, local_path, description=""):
        """Download de arquivo com barra de progresso"""
        try:
            print(f"\n📥 Baixando: {description}")
            print(f"URL: {url}")
            print(f"Destino: {local_path}")

            # Criar diretório se não existir
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Headers para simular navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            # Download com requests
            with requests.get(url, headers=headers, stream=True, timeout=self.timeout) as response:
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(local_path, 'wb') as file, tqdm(
                    desc=f"📥 {description}",
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            bar.update(len(chunk))

            print(f"✅ Download concluído: {local_path}")
            return True

        except Exception as e:
            print(f"❌ Erro no download de {url}: {e}")
            return False

    def verify_file(self, file_path, expected_hash=None):
        """Verificar integridade do arquivo (opcional)"""
        if not file_path.exists():
            return False

        if expected_hash:
            # Calcular hash do arquivo
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)

            if sha256.hexdigest() != expected_hash:
                print(f"⚠️ Hash incorreto para {file_path}")
                return False

        return True

    def download_model(self, model_key):
        """Baixar modelo específico"""
        if model_key not in self.models:
            print(f"❌ Modelo {model_key} não encontrado")
            return False

        model_info = self.models[model_key]
        local_path = self.models_dir / model_info["path"]

        # Verificar se já existe
        if local_path.exists():
            print(f"⏭️ Modelo {model_key} já existe: {local_path}")
            return True

        # Download
        success = self.download_file(
            model_info["url"],
            local_path,
            f"{model_info['description']} ({model_info['size']})"
        )

        if success:
            # Verificar arquivo
            if self.verify_file(local_path):
                print(f"✅ Modelo {model_key} validado com sucesso")
                return True
            else:
                print(f"❌ Validação falhou para {model_key}")
                return False

        return False

    def download_all_models(self, skip_large=False):
        """Baixar todos os modelos"""
        print("🚀 JARVIS 5.0 - DOWNLOAD DE MODELOS LOCAIS")
        print("=" * 60)
        print("⚠️ IMPORTANTE: Este processo pode demorar horas/dias")
        print("e requer ~15GB de espaço em disco e conexão estável")
        print("=" * 60)

        success_count = 0
        total_count = len(self.models)

        for model_key, model_info in self.models.items():
            # Pular modelos grandes se solicitado
            if skip_large and "GB" in model_info["size"]:
                print(f"⏭️ Pulando modelo grande: {model_key} ({model_info['size']})")
                continue

            if self.download_model(model_key):
                success_count += 1
            else:
                print(f"❌ Falha no download: {model_key}")

        print("\n" + "=" * 60)
        print("📊 RESUMO DO DOWNLOAD")
        print("=" * 60)
        print(f"✅ Sucesso: {success_count}/{total_count} modelos")
        print(f"❌ Falhas: {total_count - success_count} modelos")

        if success_count == total_count:
            print("🎉 Todos os modelos foram baixados com sucesso!")
            print("💡 O JARVIS 5.0 agora pode funcionar 100% offline")
        else:
            print("⚠️ Alguns modelos falharam. Você pode tentar novamente")

        return success_count == total_count

    def create_model_info(self):
        """Criar arquivo de informações dos modelos"""
        info_path = self.models_dir / "models_info.json"

        info = {
            "download_date": str(Path(__file__).parent.stat().st_mtime),
            "models": {}
        }

        for model_key, model_info in self.models.items():
            local_path = self.models_dir / model_info["path"]
            info["models"][model_key] = {
                **model_info,
                "local_path": str(local_path),
                "exists": local_path.exists(),
                "size_bytes": local_path.stat().st_size if local_path.exists() else 0
            }

        import json
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

        print(f"📝 Informações dos modelos salvas em: {info_path}")

    def cleanup_temp_files(self):
        """Limpar arquivos temporários"""
        import glob
        temp_files = glob.glob(str(self.base_dir / "*.tmp")) + \
                    glob.glob(str(self.base_dir / "*.part"))

        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                print(f"🗑️ Removido arquivo temporário: {temp_file}")
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description="Download de modelos para JARVIS Local")
    parser.add_argument("--skip-large", action="store_true",
                       help="Pular modelos grandes (>1GB)")
    parser.add_argument("--model", type=str,
                       help="Baixar apenas um modelo específico")
    parser.add_argument("--dir", type=str, default="./",
                       help="Diretório base (padrão: ./)")

    args = parser.parse_args()

    # Inicializar downloader
    downloader = ModelDownloader(args.dir)

    try:
        if args.model:
            # Baixar modelo específico
            success = downloader.download_model(args.model)
            if success:
                print(f"✅ Modelo {args.model} baixado com sucesso!")
            else:
                print(f"❌ Falha no download do modelo {args.model}")
                sys.exit(1)
        else:
            # Baixar todos os modelos
            success = downloader.download_all_models(skip_large=args.skip_large)

        # Criar arquivo de informações
        downloader.create_model_info()

        # Limpar temporários
        downloader.cleanup_temp_files()

        if success:
            print("\n🎉 JARVIS 5.0 está pronto para funcionar 100% offline!")
            sys.exit(0)
        else:
            print("\n⚠️ Alguns downloads falharam. Verifique a conexão e tente novamente.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Download interrompido pelo usuário")
        downloader.cleanup_temp_files()
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        downloader.cleanup_temp_files()
        sys.exit(1)


if __name__ == "__main__":
    main()
