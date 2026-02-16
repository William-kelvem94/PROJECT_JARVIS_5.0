"""
JARVIS 5.0 - File Indexer & MetaCache
=====================================
Responsabilidade: Escanear arquivos locais e extrair metadados (ID3, EXIF)
para permitir buscas evoluídas como 'Tocar música do gênero X'.

Mantém um cache local para buscas instantâneas.
Inspirado no MetacacheTask do PVA.
"""

import json
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Dependências opcionais para metadados
try:
    from mutagen.id3 import ID3

    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    from PIL import Image
    from PIL.ExifTags import TAGS

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class FileIndexer:
    """Indexador de arquivos com suporte a metadados"""

    def __init__(self, cache_file: str = "data/cache.metadata"):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.index = self._load_cache()
        self.is_indexing = False

        logger.info(f"✅ FileIndexer inicializado. Cache: {len(self.index)} itens")

    def _load_cache(self) -> Dict[str, Any]:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_cache(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache de indexação: {e}")

    def start_background_indexing(self, search_paths: List[str]):
        """Inicia indexação em thread separada"""
        if self.is_indexing:
            return
        self.is_indexing = True
        thread = threading.Thread(
            target=self._indexing_loop,
            args=(search_paths,),
            daemon=True,
            name="FileIndexer",
        )
        thread.start()

    def _indexing_loop(self, search_paths: List[str]):
        """Loop de indexação profunda com Adaptive Resource Management"""
        from src.core.management.hardware_manager import hardware_manager

        logger.info(f"🔍 Iniciando indexação adaptativa de {search_paths}...")

        processed_count = 0
        for path_str in search_paths:
            path = Path(path_str)
            if not path.exists():
                continue

            for file in path.rglob("*"):
                if not self.is_indexing:
                    break  # Permite parar o processamento
                if not file.is_file():
                    continue

                # --- RESOURCE ADAPTATION ---
                processed_count += 1
                if processed_count % 10 == 0:
                    if hardware_manager.is_throttled:
                        # Sistema pesado: Pausa longa entre arquivos
                        time.sleep(2.0)
                    else:
                        # Sistema ok: Pequena pausa para GUI/OS respirar
                        time.sleep(0.05)

                # Pula arquivos já indexados e não modificados
                try:
                    mtime = file.stat().st_mtime
                    if (
                        str(file) in self.index
                        and self.index[str(file)]["mtime"] == mtime
                    ):
                        continue

                    # Extrair metadados
                    meta = {
                        "filename": file.name,
                        "mtime": mtime,
                        "size": file.stat().st_size,
                        "ext": file.suffix.lower(),
                        "metadata": self._extract_metadata(file),
                    }

                    self.index[str(file)] = meta
                except Exception as e:
                    logger.debug(f"Pulo na indexação de {file.name}: {e}")
                    continue

                # Salva periodicamente
                if len(self.index) % 50 == 0:
                    self.save_cache()

        self.save_cache()
        self.is_indexing = False
        logger.info(
            f"✅ Indexação adaptativa concluída. Itens no cache: {len(self.index)}"
        )

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Universal File Deep Inspector (Singularity Edition)"""
        import mimetypes

        ext = file_path.suffix.lower()
        mime, _ = mimetypes.guess_type(file_path)
        meta = {"size_kb": round(file_path.stat().st_size / 1024, 2)}

        # 1. Proteção de Memória para Arquivos Gigantes
        file_size = file_path.stat().st_size
        is_large = file_size > (10 * 1024 * 1024)  # > 10MB

        try:
            # ESTRATÉGIA A: Documentos e Texto (Prioridade)
            if ext in [
                ".txt",
                ".py",
                ".md",
                ".json",
                ".yaml",
                ".log",
                ".csv",
                ".xml",
            ] or (mime and mime.startswith("text/")):
                meta["content_type"] = "text"
                meta["summary"] = self._read_smart_sample(file_path, is_large)

            # ESTRATÉGIA B: PDFs e Office
            elif ext == ".pdf":
                meta["content_type"] = "pdf"
                meta["summary"] = self._read_pdf_sample(file_path)

            elif ext in [".docx", ".xlsx", ".pptx"]:
                meta["content_type"] = "office"
                meta["summary"] = (
                    f"Documento Office ({ext}). Metadados serão extraídos em análise profunda."
                )

            # ESTRATÉGIA C: Mídia (Áudio e Vídeo)
            elif ext in [".mp3", ".ogg", ".flac", ".wav", ".m4a"]:
                meta["content_type"] = "audio"
                meta["summary"] = self._read_audio_metadata(file_path)

            elif ext in [".mp4", ".mkv", ".avi", ".mov", ".wmv"]:
                meta["content_type"] = "video"
                meta["summary"] = self._read_video_metadata(file_path)

            elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                meta["content_type"] = "image"
                if PIL_AVAILABLE:
                    from PIL import Image

                    try:
                        img = Image.open(file_path)
                        meta["resolution"] = f"{img.width}x{img.height}"
                    except:
                        pass

            # ESTRATÉGIA D: Arquivos Compactados
            elif ext in [".zip", ".rar", ".7z", ".tar", ".gz"]:
                meta["content_type"] = "archive"
                meta["summary"] = self._read_archive_contents(file_path)

            # ESTRATÉGIA E: Arquivos Binários Desconhecidos (Fallback Universal)
            else:
                meta["content_type"] = "binary"
                meta["summary"] = self._read_binary_signature(file_path)

        except Exception as e:
            logger.debug(f"Falha na inspeção profunda de {file_path.name}: {e}")
            meta["error"] = "deep_inspection_failed"

        return meta

    def _read_smart_sample(self, file_path: Path, is_large: bool) -> str:
        """Lê o início e, se for grande, o fim do arquivo para captar o contexto"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                head = f.read(2000)
                if not is_large:
                    return head

                # Para arquivos grandes, pega uma amostra do final também
                f.seek(0, 2)  # EOF
                file_size = f.tell()
                f.seek(max(0, file_size - 1000))
                tail = f.read(1000)
                return f"{head}\n\n[... AMOSTRAGEM DE ARQUIVO GRANDE ...]\n\n{tail}"
        except:
            return "[Erro ao ler texto]"

    def _read_binary_signature(self, file_path: Path) -> str:
        """Extrai strings legíveis de um arquivo binário (equivalente ao comando strings)"""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(4000)
                # Extrair sequências de 4 ou mais caracteres ASCII imprimíveis
                import re

                ascii_strings = re.findall(rb"[ -~]{4,}", chunk)
                summary = " ".join(
                    [s.decode("ascii", errors="ignore") for s in ascii_strings[:10]]
                )
                return (
                    f"Assinatura Binária: {chunk[:16].hex()} | Strings: {summary[:500]}"
                )
        except:
            return "Arquivo binário não interpretável."

    def _read_pdf_sample(self, file_path: Path) -> str:
        try:
            import pypdf

            reader = pypdf.PdfReader(file_path)
            text = ""
            # Pegar amostras de páginas distantes (Início, Meio, Fim)
            num_pages = len(reader.pages)
            indices = {0, num_pages // 2, num_pages - 1}
            for i in sorted(list(indices)):
                if 0 <= i < num_pages:
                    try:
                        extracted = reader.pages[i].extract_text()
                        if extracted:
                            text += extracted + "\n"
                    except:
                        pass
            return text[:2000]
        except:
            return "Falha ao extrair texto do PDF."

    def _read_audio_metadata(self, file_path: Path) -> str:
        """Extrai metadados de áudio (ID3, duração, etc)"""
        info = []
        if MUTAGEN_AVAILABLE:
            from mutagen.id3 import ID3
            from mutagen import File

            try:
                audio = File(file_path)
                if audio and audio.info:
                    info.append(f"Duração: {round(audio.info.length, 2)}s")
                    info.append(f"Samplerate: {audio.info.sample_rate}Hz")

                tags = ID3(file_path)
                artist = tags.get("TPE1", "Desconhecido")
                title = tags.get("TIT2", "Sem Título")
                info.append(f"Artista: {artist} | Título: {title}")
            except:
                pass
        return " | ".join(info) if info else "Áudio (Meta indisponível)"

    def _read_video_metadata(self, file_path: Path) -> str:
        """Extrai metadados de vídeo usando cv2"""
        try:
            import cv2

            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                return "Vídeo (Arquivo corrompido ou codec não suportado)"

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = (frame_count / fps) if fps > 0 else 0

            cap.release()
            return f"Resolução: {width}x{height} | FPS: {round(fps, 2)} | Duração: {round(duration, 2)}s"
        except:
            return "Vídeo (Erro na extração de metadados)"

    def _read_archive_contents(self, file_path: Path) -> str:
        """Lista conteúdos de arquivos Zip"""
        if file_path.suffix.lower() == ".zip":
            try:
                import zipfile

                with zipfile.ZipFile(file_path, "r") as z:
                    files = z.namelist()
                    summary = ", ".join(files[:20])  # Primeiros 20 arquivos
                    if len(files) > 20:
                        summary += f" ... e mais {len(files)-20} arquivos."
                    return f"Conteúdo do Zip: {summary}"
            except:
                return "Arquivo Zip corrompido ou protegido por senha."
        return f"Arquivo compactado ({file_path.suffix})"

    def search(self, query: str, filters: Dict[str, Any] = None) -> List[str]:
        """Busca no índice local"""
        results = []
        query = query.lower()

        for path, info in self.index.items():
            # Busca no nome do arquivo
            if query in info["filename"].lower():
                results.append(path)
                continue

            # Busca nos metadados
            found_in_meta = False
            for val in info["metadata"].values():
                if query in str(val).lower():
                    found_in_meta = True
                    break

            if found_in_meta:
                results.append(path)

        return results


# Singleton instance
file_indexer = FileIndexer()
