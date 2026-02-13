#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Democratic System Validator
===============================================
Validador completo do sistema democrático implementado
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import importlib.util
import json
from datetime import datetime

class DemocraticSystemValidator:
    """🔍 VALIDADOR DO SISTEMA DEMOCRÁTICO"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.validation_results: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def run_full_validation(self) -> bool:
        """🏁 EXECUTA VALIDAÇÃO COMPLETA"""
        
        print("🔍 VALIDANDO SISTEMA DEMOCRÁTICO JARVIS...")
        print(f"   📁 Base path: {self.base_path.absolute()}")
        print(f"   🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Verificar arquivos obrigatórios
        self._validate_required_files()
        
        # 2. Verificar importações Python
        self._validate_python_imports()
        
        # 3. Verificar estrutura de dados
        self._validate_data_structure()
        
        # 4. Verificar configurações
        self._validate_configurations()
        
        # 5. Verificar dependências
        self._validate_dependencies()
        
        # 6. Verificar integração
        self._validate_integration_points()
        
        # Resultados
        self._print_validation_report()
        
        return len(self.errors) == 0
    
    def _validate_required_files(self):
        """📁 VALIDA ARQUIVOS OBRIGATÓRIOS"""
        
        print("📁 Verificando arquivos obrigatórios...")
        
        required_files = {
            # Core democrático
            "src/core/democratic_core.py": "Integração principal do sistema democrático",
            
            # Rede democrática  
            "src/core/network_mesh/democratic_intelligence.py": "Sistema de rede democrática",
            
            # Auto-recovery
            "src/core/management/democratic_auto_recovery.py": "Sistema de auto-recovery democrático",
            
            # Analytics preditivo
            "src/core/analytics/predictive_analytics.py": "Sistema de análise preditiva",
            
            # Configuração
            "config/democratic_config.py": "Sistema de configuração democrática",
            
            # Scripts e exemplos
            "src/core/democratic_integration.py": "Sistema de integração democrática completa",
            
            # Documentação
            "docs/DEMOCRATIC_SYSTEM.md": "Documentação completa"
        }
        
        missing_files = []
        existing_files = []
        
        for file_path, description in required_files.items():
            full_path = self.base_path / file_path
            
            if full_path.exists():
                existing_files.append(file_path)
                print(f"   ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"   ❌ {file_path} - {description}")
        
        if missing_files:
            self.errors.extend([f"Arquivo obrigatório ausente: {f}" for f in missing_files])
        
        self.validation_results["files"] = {
            "total_required": len(required_files),
            "existing": len(existing_files),
            "missing": len(missing_files),
            "missing_files": missing_files
        }
        
        print(f"   📊 Arquivos: {len(existing_files)}/{len(required_files)} encontrados")
        print()
    
    def _validate_python_imports(self):
        """🐍 VALIDA IMPORTAÇÕES PYTHON"""
        
        print("🐍 Verificando importações Python...")
        
        import_tests = [
            ("src.core.democratic_core", "DemocraticIntelligenceCore"), 
            ("src.core.network_mesh.democratic_intelligence", "DemocraticNetworkIntelligence"),
            ("src.core.management.democratic_auto_recovery", "DemocraticAutoRecovery"),
            ("src.core.analytics.predictive_analytics", "DemocraticPredictiveAnalytics"),
            ("config.democratic_config", "DemocraticConfig")
        ]
        
        successful_imports = 0
        failed_imports = []
        
        # Adicionar path atual ao sys.path temporariamente
        original_path = sys.path.copy()
        sys.path.insert(0, str(self.base_path))
        
        try:
            for module_path, class_name in import_tests:
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, class_name):
                        print(f"   ✅ {module_path}.{class_name}")
                        successful_imports += 1
                    else:
                        print(f"   ⚠️ {module_path} existe mas não tem {class_name}")
                        self.warnings.append(f"Classe {class_name} não encontrada em {module_path}")
                except ImportError as e:
                    print(f"   ❌ {module_path} - {e}")
                    failed_imports.append(module_path)
                    self.errors.append(f"Erro importing {module_path}: {e}")
        finally:
            sys.path = original_path
        
        self.validation_results["imports"] = {
            "total_tested": len(import_tests),
            "successful": successful_imports,
            "failed": len(failed_imports),
            "failed_modules": failed_imports
        }
        
        print(f"   📊 Imports: {successful_imports}/{len(import_tests)} sucessful")
        print()
    
    def _validate_data_structure(self):
        """📂 VALIDA ESTRUTURA DE DADOS"""
        
        print("📂 Verificando estrutura de dados...")
        
        required_dirs = [
            "data/democratic_core",
            "data/democratic_recovery", 
            "data/predictive_analytics",
            "config"
        ]
        
        created_dirs = []
        missing_dirs = []
        
        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            
            if full_path.exists():
                created_dirs.append(dir_path)
                print(f"   ✅ {dir_path}/")
            else:
                missing_dirs.append(dir_path)
                print(f"   📁 {dir_path}/ (será criado automaticamente)")
        
        # Criar diretórios ausentes
        for dir_path in missing_dirs:
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   ➕ Criado: {dir_path}/")
        
        self.validation_results["data_structure"] = {
            "required_dirs": len(required_dirs),
            "existing_dirs": len(created_dirs),
            "created_dirs": len(missing_dirs)
        }
        
        print(f"   📊 Estrutura: {len(required_dirs)} diretórios verificados")
        print()
    
    def _validate_configurations(self):
        """⚙️ VALIDA CONFIGURAÇÕES"""
        
        print("⚙️ Verificando configurações...")
        
        # Tentar criar configuração de teste
        try:
            sys.path.insert(0, str(self.base_path))
            
            from config.democratic_config import DemocraticConfig, DemocraticConfigManager
            
            # Testar criação de config
            test_config = DemocraticConfig()
            print(f"   ✅ DemocraticConfig criado")
            
            # Testar manager
            config_manager = DemocraticConfigManager(str(self.base_path))
            config = config_manager.load_config()
            print(f"   ✅ DemocraticConfigManager funcional")
            
            # Verificar conta configurada
            if config.target_microsoft_account == "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "williamkelvem64@gmail.com")) + "")) + "":
                print(f"   ✅ Conta Microsoft configurada: {config.target_microsoft_account}")
            else:
                print(f"   ⚠️ Conta Microsoft: {config.target_microsoft_account} (esperado: " + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "williamkelvem64@gmail.com")) + "")) + ")")
                self.warnings.append("Conta Microsoft não é " + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "williamkelvem64@gmail.com")) + "")) + "")
            
            # Verificar features habilitadas
            print(f"   📊 Features habilitadas: {len(config.enabled_features)}")
            for feature in config.enabled_features:
                print(f"      🔹 {feature.value}")
            
            self.validation_results["configuration"] = {
                "config_loaded": True,
                "account": config.target_microsoft_account,
                "features_count": len(config.enabled_features),
                "automation_level": config.default_automation_level
            }
            
        except Exception as e:
            print(f"   ❌ Erro na configuração: {e}")
            self.errors.append(f"Erro validando configuração: {e}")
            
        print()
    
    def _validate_dependencies(self):
        """📦 VALIDA DEPENDÊNCIAS"""
        
        print("📦 Verificando dependências...")
        
        required_packages = {
            "asyncio": "Async programming (built-in)",
            "json": "JSON handling (built-in)", 
            "pathlib": "Path handling (built-in)",
            "dataclasses": "Data structures (built-in)",
            "enum": "Enumerations (built-in)",
            "datetime": "Date/time handling (built-in)",
            "typing": "Type hints (built-in)",
            "threading": "Threading (built-in)",
            "time": "Time utilities (built-in)",
            "psutil": "System info (external)",
            "numpy": "Numeric computing (external)",
            "pandas": "Data analysis (external)",
            # Biometria obrigatória
            "face_recognition": "Face recognition (biometric)",
            "dlib": "Facial processing (biometric)",
            # Áudio obrigatório
            "pyaudio": "Audio capture (speech)",
            "librosa": "Audio processing (speech)",
            "soundfile": "Audio I/O (speech)",
            # Interface obrigatória
            "tkinter": "GUI framework (built-in)",
            "tkinter_tooltip": "GUI tooltips (interface)",
            # Monitoramento obrigatório
            "wmi": "Windows Management Instrumentation (system monitoring)"
        }
        
        optional_packages = {
            "scikit-learn": "Machine learning (para predictive analytics)",
            "GPUtil": "GPU monitoring (para GPU analytics)"
        }
        
        available_packages = []
        missing_packages = []
        optional_available = []
        
        # Verificar packages obrigatórios
        for package, description in required_packages.items():
            try:
                importlib.import_module(package)
                available_packages.append(package)
                print(f"   ✅ {package} - {description}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} - {description}")
        
        # Verificar packages opcionais
        for package, description in optional_packages.items():
            try:
                importlib.import_module(package)
                optional_available.append(package)
                print(f"   ➕ {package} - {description}")
            except ImportError:
                print(f"   ⚪ {package} - {description} (opcional, não encontrado)")
        
        if missing_packages:
            self.errors.extend([f"Package obrigatório ausente: {p}" for p in missing_packages])
        
        if not optional_available:
            self.warnings.append("Nenhum package opcional encontrado. Algumas features podem ter funcionalidade limitada.")
        
        self.validation_results["dependencies"] = {
            "required_available": len(available_packages),
            "required_missing": len(missing_packages),
            "optional_available": len(optional_available),
            "missing_packages": missing_packages
        }
        
        print(f"   📊 Dependencies: {len(available_packages)}/{len(required_packages)} obrigatórias, {len(optional_available)}/{len(optional_packages)} opcionais")
        print()
    
    def _validate_integration_points(self):
        """🔗 VALIDA PONTOS DE INTEGRAÇÃO"""
        
        print("🔗 Verificando pontos de integração...")
        
        integration_tests = []
        
        # Verificar se main.py existe
        main_py = self.base_path / "main.py"
        if main_py.exists():
            integration_tests.append("main.py encontrado")
            print(f"   ✅ main.py encontrado para integração")
            
            # Verificar se já tem importações democráticas
            try:
                with open(main_py, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "democratic" in content.lower():
                    integration_tests.append("Possível integração democrática já presente")
                    print(f"   🔍 Possível integração democrática detectada em main.py")
                else:
                    print(f"   📝 main.py pronto para integração democrática")
            except:
                pass
        else:
            self.warnings.append("main.py não encontrado. Integração manual necessária.")
        
        # Verificar estrutura src/core
        core_path = self.base_path / "src" / "core"
        if core_path.exists():
            integration_tests.append("Estrutura src/core encontrada")
            print(f"   ✅ Estrutura src/core/ compatível")
        else:
            self.errors.append("Estrutura src/core não encontrada")
        
        self.validation_results["integration"] = {
            "tests_passed": len(integration_tests),
            "main_py_exists": main_py.exists(),
            "core_structure_exists": core_path.exists()
        }
        
        print()
    
    def _print_validation_report(self):
        """📊 IMPRIME RELATÓRIO DE VALIDAÇÃO"""
        
        print("="*60)
        print("📊 RELATÓRIO DE VALIDAÇÃO DO SISTEMA DEMOCRÁTICO")
        print("="*60)
        
        # Estatísticas gerais
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        
        # Status geral
        if total_errors == 0:
            status = "✅ SISTEMA VALIDADO COM SUCESSO"
            status_color = "🟢"
        else:
            status = "❌ SISTEMA COM PROBLEMAS"
            status_color = "🔴"
        
        print(f"{status_color} {status}")
        print()
        
        # Resumo por categoria
        print("📋 RESUMO POR CATEGORIA:")
        
        if "files" in self.validation_results:
            files = self.validation_results["files"]
            print(f"   📁 Arquivos: {files['existing']}/{files['total_required']} ({'✅' if files['missing'] == 0 else '❌'})")
        
        if "imports" in self.validation_results:
            imports = self.validation_results["imports"]
            print(f"   🐍 Imports: {imports['successful']}/{imports['total_tested']} ({'✅' if imports['failed'] == 0 else '❌'})")
        
        if "dependencies" in self.validation_results:
            deps = self.validation_results["dependencies"]
            print(f"   📦 Dependências: {deps['required_available']}/{deps['required_available'] + deps['required_missing']} ({'✅' if deps['required_missing'] == 0 else '❌'})")
        
        if "configuration" in self.validation_results:
            config = self.validation_results["configuration"]
            print(f"   ⚙️ Configuração: {'✅' if config.get('config_loaded', False) else '❌'}")
        
        print()
        
        # Detalhes dos erros
        if self.errors:
            print("❌ PROBLEMAS ENCONTRADOS:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
            print()
        
        # Avisos
        if self.warnings:
            print("⚠️ AVISOS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
            print()
        
        # Instruções de próximos passos
        if total_errors == 0:
            print("🎉 PRÓXIMOS PASSOS:")
            print("   1. ✅ Sistema democrático está pronto para uso")
            print("   2. 🔧 Integre usando: src/core/democratic_integration.py")
            print("   3. ⚙️ Configure perfil: python main.py --democratic-profile balanced")
            print("   4. 🚀 Execute: python main.py")
            print("   5. 📊 Monitore: python main.py --democratic-status")
        else:
            print("🔧 CORREÇÕES NECESSÁRIAS:")
            print("   1. ❌ Corrija os problemas listados acima")
            print("   2. 🔄 Execute o validador novamente")
            print("   3. 📖 Consulte a documentação: docs/DEMOCRATIC_SYSTEM.md")
        
        print()
        print("📖 DOCUMENTAÇÃO COMPLETA: docs/DEMOCRATIC_SYSTEM.md")
        print("🔧 EXEMPLO DE INTEGRAÇÃO: src/core/democratic_integration.py") 
        print("="*60)
    
    def save_validation_report(self, output_file: Optional[str] = None):
        """💾 SALVA RELATÓRIO DE VALIDAÇÃO"""
        
        if output_file is None:
            output_file = f"democratic_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": self.validation_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "status": "PASSED" if len(self.errors) == 0 else "FAILED"
        }
        
        output_path = self.base_path / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório salvo: {output_path}")

def main():
    """🏁 FUNCTION MAIN"""
    
    # Determinar base path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "."
    
    # Executar validação
    validator = DemocraticSystemValidator(base_path)
    success = validator.run_full_validation()
    
    # Salvar relatório
    validator.save_validation_report()
    
    # Retornar exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

# EXEMPLO DE USO:
# python scripts/validate_democratic_system.py
# python scripts/validate_democratic_system.py /path/to/jarvis/project