#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Full System Diagnostics
====================================
Script completo de diagnóstico que verifica:
- Versões de dependências críticas
- Carregamento de módulos ML
- Disponibilidade de DLLs (Windows)
- Configurações e encoding
- Health status de todos os subsistemas
- Gera relatório HTML detalhado
"""

import sys
import os
from pathlib import Path

# Adicionar root ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import platform
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# Configurar logging mínimo
logging.basicConfig(level=logging.WARNING)

class DiagnosticRunner:
    """Executor de diagnósticos do sistema JARVIS"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "python_environment": {},
            "dependencies": {},
            "ml_stack": {},
            "config_status": {},
            "file_system": {},
            "health_checks": {},
            "recommendations": []
        }
        self.warnings = []
        self.errors = []
    
    def run_all_diagnostics(self):
        """Executa todos os diagnósticos"""
        print("🔬 JARVIS 5.0 - Diagnóstico Completo do Sistema")
        print("=" * 60)
        print()
        
        tests = [
            ("Informações do Sistema", self.check_system_info),
            ("Ambiente Python", self.check_python_environment),
            ("Dependências Críticas", self.check_critical_dependencies),
            ("Stack de Machine Learning", self.check_ml_stack),
            ("Configurações e Encoding", self.check_config_files),
            ("Sistema de Arquivos", self.check_file_system),
            ("Health Checks dos Módulos", self.check_module_health)
        ]
        
        for i, (name, test_func) in enumerate(tests, 1):
            print(f"[{i}/{len(tests)}] {name}...", end=' ', flush=True)
            try:
                test_func()
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
                self.errors.append(f"{name}: {e}")
        
        print()
        self.generate_recommendations()
        self.print_summary()
        self.save_html_report()
    
    def check_system_info(self):
        """Verifica informações básicas do sistema"""
        self.results["system_info"] = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation()
        }
    
    def check_python_environment(self):
        """Verifica ambiente Python e virtual environment"""
        import site
        
        self.results["python_environment"] = {
            "executable": sys.executable,
            "prefix": sys.prefix,
            "site_packages": site.getsitepackages(),
            "is_venv": hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
            )
        }
        
        # Verificar se está em venv
        if not self.results["python_environment"]["is_venv"]:
            self.warnings.append("⚠️ Não detectado ambiente virtual (venv)")
    
    def check_critical_dependencies(self):
        """Verifica versões de dependências críticas"""
        dependencies = [
            "numpy", "torch", "cv2", "PyQt6", "yaml", "chromadb",
            "transformers", "whisper", "face_recognition", "ultralytics",
            "easyocr", "mediapipe", "onnxruntime"
        ]
        
        for dep in dependencies:
            try:
                if dep == "cv2":
                    import cv2
                    version = cv2.__version__
                elif dep == "PyQt6":
                    from PyQt6 import QtCore
                    version = QtCore.QT_VERSION_STR
                elif dep == "yaml":
                    import yaml
                    version = yaml.__version__ if hasattr(yaml, '__version__') else "unknown"
                else:
                    module = __import__(dep)
                    version = module.__version__ if hasattr(module, '__version__') else "unknown"
                
                self.results["dependencies"][dep] = {"status": "installed", "version": version}
            except ImportError as e:
                self.results["dependencies"][dep] = {"status": "missing", "error": str(e)}
                if dep in ["numpy", "torch", "cv2", "PyQt6"]:
                    self.errors.append(f"❌ Dependência crítica faltando: {dep}")
                else:
                    self.warnings.append(f"⚠️ Dependência opcional faltando: {dep}")
            except Exception as e:
                self.results["dependencies"][dep] = {"status": "error", "error": str(e)}
    
    def check_ml_stack(self):
        """Verifica stack de ML e carregamento de DLLs"""
        # Teste PyTorch
        try:
            import torch
            self.results["ml_stack"]["torch"] = {
                "version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
                "device": "cuda" if torch.cuda.is_available() else "cpu"
            }
            
            # Testar carregamento c10.dll (crítico no Windows)
            try:
                test_tensor = torch.tensor([1.0, 2.0, 3.0])
                self.results["ml_stack"]["torch"]["c10_dll_status"] = "OK"
            except Exception as e:
                self.results["ml_stack"]["torch"]["c10_dll_status"] = f"ERROR: {e}"
                self.errors.append(f"❌ Erro ao carregar c10.dll: {e}")
        except Exception as e:
            self.results["ml_stack"]["torch"] = {"error": str(e)}
            self.errors.append(f"❌ PyTorch falhou: {e}")
        
        # Teste EasyOCR
        try:
            import easyocr
            self.results["ml_stack"]["easyocr"] = {
                "version": easyocr.__version__,
                "status": "available"
            }
        except Exception as e:
            self.results["ml_stack"]["easyocr"] = {"status": "unavailable", "error": str(e)}
            self.warnings.append(f"⚠️ EasyOCR não disponível (OCR desabilitado)")
        
        # Teste Ultralytics
        try:
            import ultralytics
            self.results["ml_stack"]["ultralytics"] = {
                "version": ultralytics.__version__,
                "status": "available"
            }
        except Exception as e:
            self.results["ml_stack"]["ultralytics"] = {"status": "unavailable", "error": str(e)}
            self.warnings.append(f"⚠️ Ultralytics não disponível (YOLO desabilitado)")
        
        # Teste Whisper
        try:
            import whisper
            self.results["ml_stack"]["whisper"] = {
                "status": "available"
            }
        except Exception as e:
            self.results["ml_stack"]["whisper"] = {"status": "unavailable", "error": str(e)}
            self.warnings.append(f"⚠️ Whisper não disponível (STT limitado)")
    
    def check_config_files(self):
        """Verifica arquivos de configuração e encoding"""
        config_files = [
            PROJECT_ROOT / "config" / "config.yaml",
            PROJECT_ROOT / "config" / "settings.json",
            PROJECT_ROOT / "config" / "auto_healing.yaml",
            PROJECT_ROOT / "data" / "system_health.json"
        ]
        
        for config_file in config_files:
            if not config_file.exists():
                self.results["config_status"][str(config_file.name)] = {"status": "missing"}
                self.warnings.append(f"⚠️ Arquivo de config faltando: {config_file.name}")
                continue
            
            # Verificar encoding
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Tentar parsear
                if config_file.suffix == '.json':
                    json.loads(content)
                elif config_file.suffix == '.yaml':
                    import yaml
                    yaml.safe_load(content)
                
                self.results["config_status"][str(config_file.name)] = {
                    "status": "ok",
                    "size": len(content),
                    "encoding": "utf-8"
                }
            except UnicodeDecodeError as e:
                self.results["config_status"][str(config_file.name)] = {
                    "status": "encoding_error",
                    "error": str(e)
                }
                self.errors.append(f"❌ Erro de encoding em {config_file.name}: {e}")
            except Exception as e:
                self.results["config_status"][str(config_file.name)] = {
                    "status": "parse_error",
                    "error": str(e)
                }
                self.errors.append(f"❌ Erro ao parsear {config_file.name}: {e}")
    
    def check_file_system(self):
        """Verifica estrutura de diretórios"""
        required_dirs = [
            "src", "data", "config", "models", "logs", "tests",
            "data/logs", "data/captures", "data/faces", "data/knowledge"
        ]
        
        for dir_path in required_dirs:
            full_path = PROJECT_ROOT / dir_path
            exists = full_path.exists()
            self.results["file_system"][dir_path] = {"exists": exists}
            
            if not exists and dir_path in ["src", "config"]:
                self.errors.append(f"❌ Diretório crítico faltando: {dir_path}")
            elif not exists:
                self.warnings.append(f"⚠️ Diretório faltando: {dir_path}")
    
    def check_module_health(self):
        """Verifica health status dos módulos principais"""
        try:
            # Tentar importar orchestrator
            from src.core.orchestrator import StarkOrchestrator
            
            # Criar instância mock para testar health checks
            class MockJarvis:
                pass
            
            orchestrator = StarkOrchestrator(MockJarvis())
            
            # Verificar cada módulo
            modules = ["vision", "audio", "intelligence", "actions", "infrastructure"]
            for module in modules:
                try:
                    status = orchestrator.get_module_status(module)
                    self.results["health_checks"][module] = {"status": status}
                    
                    if status == "OFFLINE":
                        self.errors.append(f"❌ Módulo {module} está OFFLINE")
                    elif status == "DEGRADED":
                        self.warnings.append(f"⚠️ Módulo {module} está DEGRADED")
                except Exception as e:
                    self.results["health_checks"][module] = {"status": "ERROR", "error": str(e)}
        except Exception as e:
            self.results["health_checks"]["error"] = str(e)
            self.warnings.append(f"⚠️ Não foi possível verificar health dos módulos: {e}")
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos diagnósticos"""
        # Verificar NumPy version
        if "numpy" in self.results["dependencies"]:
            numpy_info = self.results["dependencies"]["numpy"]
            if numpy_info["status"] == "installed":
                version = numpy_info["version"]
                if version.startswith("2."):
                    self.recommendations.append({
                        "priority": "CRITICAL",
                        "issue": "NumPy 2.x detectado",
                        "solution": "Downgrade para NumPy 1.26.4: pip uninstall numpy -y && pip install 'numpy==1.26.4'",
                        "reason": "PyTorch 2.2.2 requer NumPy < 2.0"
                    })
        
        # Verificar c10.dll
        if "torch" in self.results["ml_stack"]:
            torch_info = self.results["ml_stack"]["torch"]
            if isinstance(torch_info, dict) and torch_info.get("c10_dll_status", "").startswith("ERROR"):
                self.recommendations.append({
                    "priority": "CRITICAL",
                    "issue": "c10.dll falha ao carregar",
                    "solution": "Instalar Visual C++ Redistributables: https://aka.ms/vs/17/release/vc_redist.x64.exe",
                    "reason": "PyTorch requer MSVC runtime libraries"
                })
        
        # Verificar encoding de configs
        encoding_errors = [k for k, v in self.results["config_status"].items() 
                          if v.get("status") == "encoding_error"]
        if encoding_errors:
            self.recommendations.append({
                "priority": "HIGH",
                "issue": f"Erro de encoding: {', '.join(encoding_errors)}",
                "solution": "Resalvar arquivos com encoding UTF-8 (sem BOM)",
                "reason": "Caracteres especiais causam falha no carregamento"
            })
        
        # Verificar dependências opcionais
        optional_missing = [k for k, v in self.results["dependencies"].items()
                           if v.get("status") == "missing" and k not in ["numpy", "torch", "cv2", "PyQt6"]]
        if optional_missing:
            self.recommendations.append({
                "priority": "MEDIUM",
                "issue": f"Dependências opcionais faltando: {', '.join(optional_missing)}",
                "solution": "pip install " + " ".join(optional_missing),
                "reason": "Features avançadas desabilitadas"
            })
    
    def print_summary(self):
        """Imprime resumo no console"""
        print()
        print("=" * 60)
        print("📊 RESUMO DO DIAGNÓSTICO")
        print("=" * 60)
        
        print(f"\n✅ Testes executados: {len(self.results)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Erros: {len(self.errors)}")
        
        if self.errors:
            print("\n🔴 ERROS CRÍTICOS:")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print("\n🟡 AVISOS:")
            for warning in self.warnings[:5]:  # Mostrar apenas 5 primeiros
                print(f"  {warning}")
            if len(self.warnings) > 5:
                print(f"  ... e mais {len(self.warnings) - 5} avisos")
        
        if self.recommendations:
            print("\n💡 RECOMENDAÇÕES:")
            for rec in self.recommendations:
                print(f"\n  [{rec['priority']}] {rec['issue']}")
                print(f"  → {rec['solution']}")
                print(f"  Razão: {rec['reason']}")
        
        if not self.errors and not self.warnings:
            print("\n🎉 Sistema totalmente funcional! Nenhum problema detectado.")
    
    def save_html_report(self):
        """Salva relatório HTML detalhado"""
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS 5.0 - Relatório de Diagnóstico</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #e0e0e0; }}
        h1 {{ color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px; }}
        h2 {{ color: #00a8cc; margin-top: 30px; }}
        .section {{ background: #2a2a2a; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #00d9ff; }}
        .status-ok {{ color: #4caf50; }}
        .status-warning {{ color: #ff9800; }}
        .status-error {{ color: #f44336; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #444; }}
        th {{ background: #333; color: #00d9ff; }}
        .recommendation {{ background: #003d5c; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ff9800; }}
        .priority-critical {{ border-left-color: #f44336; }}
        .priority-high {{ border-left-color: #ff9800; }}
        .priority-medium {{ border-left-color: #ffeb3b; }}
        pre {{ background: #1a1a1a; padding: 10px; border-radius: 3px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>🔬 JARVIS 5.0 - Relatório de Diagnóstico Completo</h1>
    <p><strong>Gerado em:</strong> {self.results['timestamp']}</p>
    
    <div class="section">
        <h2>📊 Resumo</h2>
        <ul>
            <li><span class="status-ok">✅ Testes executados: {len(self.results)}</span></li>
            <li><span class="status-warning">⚠️  Warnings: {len(self.warnings)}</span></li>
            <li><span class="status-error">❌ Erros: {len(self.errors)}</span></li>
        </ul>
    </div>
    
    <div class="section">
        <h2>🖥️ Informações do Sistema</h2>
        <table>
            <tr><th>Propriedade</th><th>Valor</th></tr>
            {''.join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in self.results['system_info'].items())}
        </table>
    </div>
    
    <div class="section">
        <h2>📦 Dependências Críticas</h2>
        <table>
            <tr><th>Pacote</th><th>Status</th><th>Versão</th></tr>
            {''.join(f"<tr><td>{k}</td><td class='status-{v['status']}'>{v['status']}</td><td>{v.get('version', v.get('error', 'N/A'))}</td></tr>" 
                     for k, v in self.results['dependencies'].items())}
        </table>
    </div>
    
    <div class="section">
        <h2>🧠 Stack de Machine Learning</h2>
        <pre>{json.dumps(self.results['ml_stack'], indent=2)}</pre>
    </div>
    """
        
        # Adicionar recomendações se existirem
        if self.recommendations:
            html_content += """
    <div class="section">
        <h2>💡 Recomendações</h2>
    """
            for rec in self.recommendations:
                priority_class = rec['priority'].lower()
                html_content += f"""
        <div class="recommendation priority-{priority_class}">
            <h3>[{rec['priority']}] {rec['issue']}</h3>
            <p><strong>Solução:</strong> {rec['solution']}</p>
            <p><em>Razão: {rec['reason']}</em></p>
        </div>
    """
            html_content += """
    </div>
    """
        
        html_content += f"""
    <div class="section">
        <h2>📄 Dados Completos (JSON)</h2>
        <pre>{json.dumps(self.results, indent=2, ensure_ascii=False)}</pre>
    </div>
</body>
</html>
"""
        
        # Salvar relatório
        report_path = PROJECT_ROOT / "data" / "diagnostics.html"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n📁 Relatório HTML salvo em: {report_path}")
        print(f"   Abra no navegador para visualização completa.")

def main():
    """Função principal"""
    runner = DiagnosticRunner()
    runner.run_all_diagnostics()
    
    # Retornar código de erro se houver problemas críticos
    sys.exit(1 if runner.errors else 0)

if __name__ == "__main__":
    main()
