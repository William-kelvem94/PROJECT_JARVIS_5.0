"""
JARVIS SINGULARITY - Script de Migração Seguro
Reorganiza estrutura existente para arquitetura modular sem perder código
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

class StructureMigrator:
    """Migrador seguro de estrutura de arquivos"""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root).resolve()
        self.backup_dir = self.root / "_backup_legacy"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Nova estrutura
        self.jarvis_core = self.root / "jarvis_core"
        self.tools_dir = self.root / "tools"
        
        # Mapeamento de migração
        self.migration_map = {
            # Código legado
            "src": "jarvis_core/legacy_src",
            
            # Scripts redundantes para backup
            "launcher.py": "_backup_legacy/launcher.py",
            "start_jarvis.py": "_backup_legacy/start_jarvis.py",
            "diagnostico.py": "tools/diagnostico.py",
            "verify_install.py": "tools/verify_install.py",
            "simulate_startup.py": "tools/simulate_startup.py",
            
            # Manter na raiz
            "main_singularity.py": "main_singularity.py",
            "config.yaml": "config.yaml",
            "README.md": "README.md"
        }
        
        # Estrutura de módulos Singularity
        self.singularity_modules = [
            "jarvis_core/brain",
            "jarvis_core/senses",
            "jarvis_core/mouth",
            "jarvis_core/hive_mind",
            "jarvis_core/interface",
            "jarvis_core/world",
            "jarvis_core/guardian",
            "jarvis_core/legacy_src",  # Código antigo preservado
            "tools"
        ]
    
    def create_backup(self):
        """Cria backup completo antes de qualquer mudança"""
        print(f"\n📦 Criando backup em: {self.backup_dir}")
        
        if self.backup_dir.exists():
            print(f"⚠️ Backup já existe. Renomeando...")
            old_backup = self.backup_dir.parent / f"_backup_legacy_{self.timestamp}"
            self.backup_dir.rename(old_backup)
        
        self.backup_dir.mkdir(exist_ok=True)
        
        # Copiar arquivos importantes
        important_dirs = ["src", "config", "data", "models"]
        important_files = ["main.py", "launcher.py", "start_jarvis.py", 
                          "requirements.txt", "config.yaml"]
        
        for dir_name in important_dirs:
            src_dir = self.root / dir_name
            if src_dir.exists():
                dst_dir = self.backup_dir / dir_name
                print(f"  Copiando: {dir_name}/")
                shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
        
        for file_name in important_files:
            src_file = self.root / file_name
            if src_file.exists():
                dst_file = self.backup_dir / file_name
                print(f"  Copiando: {file_name}")
                shutil.copy2(src_file, dst_file)
        
        print("✅ Backup completo criado!")
    
    def create_singularity_structure(self):
        """Cria estrutura de pastas Singularity"""
        print(f"\n🏗️ Criando estrutura Singularity...")
        
        for module_path in self.singularity_modules:
            full_path = self.root / module_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Criar __init__.py em cada módulo Python
            if "jarvis_core" in module_path and module_path != "jarvis_core/legacy_src":
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text(f'"""\n{module_path.split("/")[-1].title()} Module\n"""\n')
            
            print(f"  ✅ {module_path}/")
        
        # Criar __init__.py raiz do jarvis_core
        core_init = self.jarvis_core / "__init__.py"
        if not core_init.exists():
            core_init.write_text('"""\nJARVIS Singularity Core\n"""\n')
        
        print("✅ Estrutura criada!")
    
    def migrate_src_to_legacy(self):
        """Move src/ para jarvis_core/legacy_src/"""
        print(f"\n📦 Migrando src/ para legacy_src/...")
        
        src_dir = self.root / "src"
        legacy_dir = self.jarvis_core / "legacy_src"
        
        if src_dir.exists():
            if legacy_dir.exists():
                print("  ⚠️ legacy_src já existe. Mesclando...")
                # Copiar arquivos que não existem
                for item in src_dir.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(src_dir)
                        dst = legacy_dir / rel_path
                        if not dst.exists():
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dst)
            else:
                print(f"  Movendo src/ → legacy_src/")
                shutil.move(str(src_dir), str(legacy_dir))
            
            print("✅ Código legado preservado em jarvis_core/legacy_src/")
        else:
            print("  ℹ️ Pasta src/ não encontrada")
    
    def organize_scripts(self):
        """Organiza scripts soltos"""
        print(f"\n🧹 Organizando scripts...")
        
        scripts_to_move = [
            ("launcher.py", "_backup_legacy"),
            ("start_jarvis.py", "_backup_legacy"),
            ("diagnostico.py", "tools"),
            ("verify_install.py", "tools"),
        ]
        
        for script, destination in scripts_to_move:
            src = self.root / script
            if src.exists():
                dst_dir = self.root / destination
                dst_dir.mkdir(exist_ok=True)
                dst = dst_dir / script
                
                print(f"  Movendo: {script} → {destination}/")
                shutil.move(str(src), str(dst))
        
        print("✅ Scripts organizados!")
    
    def create_migration_report(self):
        """Cria relatório de migração"""
        print(f"\n📊 Criando relatório de migração...")
        
        report = {
            "timestamp": self.timestamp,
            "backup_location": str(self.backup_dir),
            "new_structure": self.singularity_modules,
            "migrated_files": [],
            "preserved_files": []
        }
        
        # Listar arquivos migrados
        legacy_src = self.jarvis_core / "legacy_src"
        if legacy_src.exists():
            for item in legacy_src.rglob("*.py"):
                report["migrated_files"].append(str(item.relative_to(self.root)))
        
        # Salvar relatório
        report_file = self.root / "migration_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Relatório salvo em: migration_report.json")
        return report
    
    def run_migration(self):
        """Executa migração completa"""
        print("="*60)
        print("  JARVIS SINGULARITY - MIGRAÇÃO DE ESTRUTURA")
        print("="*60)
        
        try:
            # 1. Backup
            self.create_backup()
            
            # 2. Criar nova estrutura
            self.create_singularity_structure()
            
            # 3. Migrar código legado
            self.migrate_src_to_legacy()
            
            # 4. Organizar scripts
            self.organize_scripts()
            
            # 5. Relatório
            report = self.create_migration_report()
            
            print("\n" + "="*60)
            print("  ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print(f"\n📋 Resumo:")
            print(f"  • Backup criado em: {self.backup_dir}")
            print(f"  • Código legado em: jarvis_core/legacy_src/")
            print(f"  • Scripts em: tools/")
            print(f"  • Módulos Singularity criados: {len(self.singularity_modules)}")
            print(f"\n📁 Nova estrutura:")
            for module in self.singularity_modules:
                print(f"  ✅ {module}/")
            
            print(f"\n🚀 Próximos passos:")
            print(f"  1. Revisar jarvis_core/legacy_src/ para entender código existente")
            print(f"  2. Começar a implementar módulos em jarvis_core/brain/, senses/, etc")
            print(f"  3. Atualizar main_singularity.py para usar novos módulos")
            print(f"  4. Executar testes de integração")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO na migração: {e}")
            print(f"⚠️ Restaure o backup de: {self.backup_dir}")
            return False


if __name__ == "__main__":
    import sys
    
    # Confirmar com usuário
    print("\n⚠️ ATENÇÃO: Este script vai reorganizar a estrutura do projeto.")
    print("Um backup completo será criado em _backup_legacy/")
    print("\nDeseja continuar? (s/n): ", end="")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        choice = "s"
    else:
        choice = input().lower()
    
    if choice == 's':
        migrator = StructureMigrator()
        success = migrator.run_migration()
        sys.exit(0 if success else 1)
    else:
        print("Migração cancelada.")
        sys.exit(0)
