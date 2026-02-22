import os
import sys
import ast
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.core.security.security_manager import SecurityManager

logger = logging.getLogger(__name__)


class SystemController:
    """
    Motor de EvoluÃ§Ã£o e Auto-ModificaÃ§Ã£o (Singularity Edition).
    Permite ao JARVIS estudar seu prÃ³prio cÃ³digo e aplicar correÃ§Ãµes/melhorias.
    """

    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.src_dir = self.project_root / "src"
        self.backup_dir = self.project_root / "data" / "backups"
        self.staging_dir = self.project_root / "data" / "staging"

        # Garantir diretÃ³rios
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def read_codebase_structure(self, max_depth: int = 4) -> List[str]:
        """Retorna a lista de todos os arquivos relevantes no src/"""
        paths = []
        for path in self.src_dir.rglob("*.py"):
            relative = path.relative_to(self.project_root)
            if "__pycache__" not in str(relative):
                paths.append(str(relative))
        return sorted(paths)

    def read_file_content(self, file_path: str) -> Optional[str]:
        """LÃª o conteÃºdo de um arquivo cÃ³digo do sistema"""
        try:
            if not SecurityManager.validate_path_access(file_path):
                logger.warning(
                    f"ðŸ›¡ï¸ Bloqueio Anti-Genesis: Tentativa de leitura em {file_path}"
                )
                return None

            full_path = self.project_root / file_path
            if not full_path.exists() or not str(full_path.absolute()).startswith(
                str(self.project_root.absolute())
            ):
                logger.error(
                    f"Tentativa de leitura fora do root ou arquivo inexistente: {file_path}"
                )
                return None

            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            return None

    def safe_code_update(self, file_path: str, new_code: str) -> Dict[str, Any]:
        """
        Ciclo de Cirurgia: Staging -> ValidaÃ§Ã£o -> Backup -> Merge -> Reload.
        Retorna status do processo.
        """
        logger.info(f"ðŸ§ Iniciando safe_code_update para: {file_path}")
        full_path = self.project_root / file_path

        # 0. SeguranÃ§a bÃ¡sica de path e Leis da RobÃ³tica
        if not SecurityManager.validate_path_access(file_path):
            return {
                "status": "error",
                "message": "Acesso negado: O SecurityManager bloqueou a modificaÃ§Ã£o deste recurso crÃ­tico.",
            }

        if not str(full_path.absolute()).startswith(str(self.src_dir.absolute())):
            return {
                "status": "error",
                "message": "Apenas arquivos em src/ podem ser modificados autonomamente.",
            }

        staging_path = self.staging_dir / f"{full_path.name}.staging.py"
        backup_path = (
            self.backup_dir
            / f"{full_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak.py"
        )

        try:
            # 1. STAGING: Salvar no ambiente de homologaÃ§Ã£o
            with open(staging_path, "w", encoding="utf-8") as f:
                f.write(new_code)

            # 2. VALIDAÃ‡ÃƒO SINTÃTICA: AST
            try:
                ast.parse(new_code)
            except SyntaxError as se:
                logger.error(f"âŒ Falha na validaÃ§Ã£o sintÃ¡tica (AST): {se}")
                return {
                    "status": "error",
                    "message": f"Erro de sintaxe no cÃ³digo gerado: {se}",
                }

            # 3. VALIDAÃ‡ÃƒO FUNCIONAL: Subprocesso isolado
            # Tenta rodar o arquivo para ver se nÃ£o quebra no import/runtime
            # bÃ¡sico
            val_script = f"""
import sys
import os
sys.path.append('{str(self.project_root)}')
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("validation_target", "{str(staging_path).replace(chr(92), '/')}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print("SUCCESS")
except Exception as e:
    print("FAILED: " + str(e))
    sys.exit(1)
"""
            val_cmd = [sys.executable, "-c", val_script]
            result = subprocess.run(val_cmd, capture_output=True, text=True, timeout=10)

            if "SUCCESS" not in result.stdout:
                logger.error(
                    f"âŒ Falha no teste de importaÃ§Ã£o: {result.stdout} {result.stderr}"
                )
                return {
                    "status": "error",
                    "message": f"O cÃ³digo falhou no teste de carregamento: {result.stdout}",
                }

            # 4. BACKUP
            if full_path.exists():
                shutil.copy2(full_path, backup_path)
                logger.info(f"ðŸ’¾ Backup criado em {backup_path}")

            # 5. MERGE: Sobrescrever original
            shutil.copy2(staging_path, full_path)
            logger.info("âœ… CÃ³digo aplicado com sucesso.")

            # 6. RELOAD (Opcional - pode ser perigoso se for core)
            # if file_path.endswith(".py"):
            #     # LÃ³gica de reload de mÃ³dulo aqui se necessÃ¡rio
            #     pass

            return {
                "status": "success",
                "message": f"Arquivo {file_path} atualizado com seguranÃ§a.",
                "backup": str(backup_path),
            }

        except Exception as e:
            logger.error(f"ðŸ’¥ Falha catastrÃ³fica no Evolution Engine: {e}")
            return {"status": "error", "message": f"Falha catastrÃ³fica: {str(e)}"}
        finally:
            # Limpar staging
            if staging_path.exists():
                os.remove(staging_path)


# InstÃ¢ncia global removida para evitar execuÃ§Ã£o durante import
# system_controller = SystemController()
