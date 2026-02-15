#!/usr/bin/env python3
"""
🔍 JARVIS 5.0 - Validador Completo de Projeto
Verifica integridade de todas as pastas e arquivos críticos
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# Configuração do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

class ProjectValidator:
    """Validador completo do projeto JARVIS 5.0"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def validate_structure(self) -> bool:
        """Valida estrutura de pastas"""
        print_header("📁 VALIDANDO ESTRUTURA DE PASTAS")
        
        required_dirs = [
            "src/core/intelligence",
            "src/core/audio",
            "src/core/vision",
            "src/core/actions",
            "src/core/management",
            "src/interface",
            "src/learning",
            "src/utils",
            "config",
            "data",
            "models/vision",
            "models/speech",
            "models/training",
            "tools",
            "tests",
            "scripts",
            "docs",
            "logs"
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            full_path = PROJECT_ROOT / dir_path
            if full_path.exists():
                print_success(f"{dir_path}")
            else:
                print_error(f"{dir_path} - NÃO ENCONTRADO")
                self.errors.append(f"Pasta ausente: {dir_path}")
                all_exist = False
        
        return all_exist
    
    def validate_critical_files(self) -> bool:
        """Valida arquivos críticos"""
        print_header("📄 VALIDANDO ARQUIVOS CRÍTICOS")
        
        critical_files = [
            "main.py",
            "SINGULARITY_LAUNCHER.py",
            "START_JARVIS.bat",
            "config/ai_config.yaml",
            "src/core/intelligence/ai_agent.py",
            "src/core/intelligence/brain_router.py",
            "src/core/audio/voice_controller.py",
            "src/core/vision/vision_system.py",
            "src/learning/dream_cycle.py",
            "src/learning/gap_analyzer.py",
            "src/interface/window_manager.py",
            "src/interface/modern_hud.py"
        ]
        
        all_exist = True
        for file_path in critical_files:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                size_kb = full_path.stat().st_size / 1024
                print_success(f"{file_path} ({size_kb:.1f} KB)")
            else:
                print_error(f"{file_path} - NÃO ENCONTRADO")
                self.errors.append(f"Arquivo ausente: {file_path}")
                all_exist = False
        
        return all_exist
    
    def validate_imports(self) -> bool:
        """Valida imports em arquivos Python"""
        print_header("🔍 VALIDANDO IMPORTS")
        
        # Procura por imports antigos (desatualizados)
        old_patterns = [
            ("core.brain.", "Deve ser: core.intelligence."),
            ("core.voice.", "Deve ser: core.audio."),
            ("database.memory_manager", "Deve ser: core.intelligence.memory_manager")
        ]
        
        found_issues = False
        for pattern, suggestion in old_patterns:
            # Busca em src/
            src_files = list((PROJECT_ROOT / "src").rglob("*.py"))
            for file in src_files:
                try:
                    content = file.read_text(encoding='utf-8')
                    if pattern in content:
                        print_warning(f"{file.relative_to(PROJECT_ROOT)}: Import antigo '{pattern}' - {suggestion}")
                        self.warnings.append(f"Import desatualizado em {file.name}")
                        found_issues = True
                except Exception as e:
                    pass
        
        if not found_issues:
            print_success("Todos os imports estão atualizados")
        
        return not found_issues
    
    def validate_models(self) -> bool:
        """Valida modelos de IA"""
        print_header("🧠 VALIDANDO MODELOS DE IA")
        
        models = [
            ("models/vision/yolov8n.pt", "YOLO v8 Nano", 6.5),
            ("models/vision/hand_landmarker.task", "MediaPipe Hand Tracker", 7.8),
            ("models/speech/vosk-model-small-pt-0.3", "Vosk PT-BR", None)
        ]
        
        all_exist = True
        for model_path, name, expected_mb in models:
            full_path = PROJECT_ROOT / model_path
            if full_path.exists():
                if expected_mb:
                    size_mb = full_path.stat().st_size / (1024 * 1024)
                    print_success(f"{name}: {size_mb:.1f} MB")
                else:
                    print_success(f"{name}: OK (diretório)")
            else:
                print_warning(f"{name}: NÃO ENCONTRADO (será baixado automaticamente)")
                self.warnings.append(f"Modelo ausente: {name}")
        
        return all_exist
    
    def validate_config(self) -> bool:
        """Valida arquivos de configuração"""
        print_header("⚙️  VALIDANDO CONFIGURAÇÕES")
        
        try:
            import yaml
            config_file = PROJECT_ROOT / "config" / "ai_config.yaml"
            
            if not config_file.exists():
                print_error("ai_config.yaml não encontrado")
                self.errors.append("Configuração principal ausente")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Verifica seções críticas
            required_sections = [
                "ollama_models",
                "cloud_models",
                "brain_router"
            ]
            
            for section in required_sections:
                if section in config:
                    print_success(f"Seção '{section}' presente")
                else:
                    print_warning(f"Seção '{section}' ausente")
                    self.warnings.append(f"Config: seção {section} não encontrada")
            
            return True
            
        except ImportError:
            print_warning("PyYAML não instalado - pulando validação de config")
            return True
        except Exception as e:
            print_error(f"Erro ao validar config: {e}")
            self.errors.append(f"Erro em config: {e}")
            return False
    
    def validate_documentation(self) -> bool:
        """Valida documentação"""
        print_header("📚 VALIDANDO DOCUMENTAÇÃO")
        
        docs = [
            "docs/README.md",
            "docs/technical/code-structure.md",
            "docs/ai-systems/brain-router.md",
            "docs/ai-systems/local-brain.md",
            "docs/getting-started/installation.md",
            "models/README.md",
            "logs/README.md",
            "tools/README.md"
        ]
        
        all_exist = True
        for doc_path in docs:
            full_path = PROJECT_ROOT / doc_path
            if full_path.exists():
                print_success(f"{doc_path}")
            else:
                print_warning(f"{doc_path} - Ausente")
                self.warnings.append(f"Doc ausente: {doc_path}")
        
        return all_exist
    
    def generate_report(self):
        """Gera relatório final"""
        print_header("📊 RELATÓRIO FINAL")
        
        total_checks = len(self.successes) + len(self.warnings) + len(self.errors)
        
        print(f"\n{Colors.BOLD}Resumo:{Colors.END}")
        print(f"  {Colors.GREEN}✅ Sucessos: {len(self.successes)}{Colors.END}")
        print(f"  {Colors.YELLOW}⚠️  Avisos: {len(self.warnings)}{Colors.END}")
        print(f"  {Colors.RED}❌ Erros: {len(self.errors)}{Colors.END}")
        
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}ERROS CRÍTICOS:{Colors.END}")
            for error in self.errors:
                print(f"  {Colors.RED}• {error}{Colors.END}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}AVISOS:{Colors.END}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}• {warning}{Colors.END}")
        
        # Status final
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        if not self.errors:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ PROJETO VALIDADO COM SUCESSO!{Colors.END}")
            print(f"{Colors.GREEN}O projeto está pronto para uso.{Colors.END}")
            return 0
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ PROJETO COM ERROS{Colors.END}")
            print(f"{Colors.RED}Corrija os erros acima antes de continuar.{Colors.END}")
            return 1
    
    def run_all_validations(self) -> int:
        """Executa todas as validações"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║         🔍 JARVIS 5.0 - VALIDADOR COMPLETO DE PROJETO           ║")
        print("║                    Verificação de Integridade                     ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        # Executa validações
        self.validate_structure()
        self.validate_critical_files()
        self.validate_imports()
        self.validate_models()
        self.validate_config()
        self.validate_documentation()
        
        # Gera relatório
        return self.generate_report()

def main():
    """Função principal"""
    validator = ProjectValidator()
    exit_code = validator.run_all_validations()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
