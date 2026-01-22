#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para o projeto JARVIS 5.0
Verifica todos os aspectos do sistema Docker e conectividade
"""

import subprocess
import requests
import os
import json
import sys
from datetime import datetime

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class Colors:
    """Cores para output no terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    try:
        print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")
    except:
        print(f"[OK] {text}")

def print_error(text):
    try:
        print(f"{Colors.RED}[ERRO] {text}{Colors.RESET}")
    except:
        print(f"[ERRO] {text}")

def print_warning(text):
    try:
        print(f"{Colors.YELLOW}[AVISO] {text}{Colors.RESET}")
    except:
        print(f"[AVISO] {text}")

def print_info(text):
    try:
        print(f"{Colors.BLUE}[INFO] {text}{Colors.RESET}")
    except:
        print(f"[INFO] {text}")

def run_command(cmd, shell=False):
    """Executa um comando e retorna o resultado"""
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=shell,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout ao executar comando"
    except Exception as e:
        return False, "", str(e)

def check_containers():
    """1. Verifica se os containers estão em execução"""
    print_header("1. VERIFICANDO CONTAINERS")
    
    # Obter diretório raiz do projeto (um nível acima de scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    success, output, error = run_command("docker compose -f docker/docker-compose.yml ps", shell=True)
    if not success:
        print_error(f"Erro ao verificar containers: {error}")
        return False
    
    print_info("Status dos containers:")
    print(output)
    
    if "jarvis_ai" in output and "jarvis_ollama" in output:
        if "Up" in output:
            print_success("Containers estão em execução!")
            return True
        else:
            print_warning("Alguns containers podem não estar rodando")
            return False
    else:
        print_error("Containers não encontrados!")
        return False

def check_ports():
    """2. Verifica as portas expostas"""
    print_header("2. VERIFICANDO PORTAS")
    
    ports_to_check = [
        ("http://localhost:8000", "JARVIS API"),
        ("http://localhost:11434", "Ollama API")
    ]
    
    all_ok = True
    for url, name in ports_to_check:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 404]:  # 404 ainda indica que o serviço está rodando
                print_success(f"{name} ({url}) está acessível")
            else:
                print_warning(f"{name} ({url}) retornou status {response.status_code}")
                all_ok = False
        except requests.exceptions.ConnectionError:
            print_error(f"{name} ({url}) não está acessível")
            all_ok = False
        except Exception as e:
            print_error(f"Erro ao verificar {name}: {e}")
            all_ok = False
    
    return all_ok

def check_network():
    """3. Verifica as configurações de rede"""
    print_header("3. VERIFICANDO REDE DOCKER")
    
    success, output, error = run_command(
        "docker network inspect project_jarvis_50_jarvis_network",
        shell=True
    )
    
    if success:
        try:
            network_info = json.loads(output)[0]
            print_success("Rede encontrada e funcionando!")
            print_info(f"Driver: {network_info.get('Driver', 'N/A')}")
            print_info(f"Containers conectados: {len(network_info.get('Containers', {}))}")
            return True
        except:
            print_warning("Rede encontrada mas não foi possível parsear informações")
            return True
    else:
        print_error(f"Erro ao verificar rede: {error}")
        return False

def validate_docker_compose():
    """4. Valida o arquivo docker-compose.yml"""
    print_header("4. VALIDANDO DOCKER-COMPOSE.YML")
    
    # Obter diretório raiz do projeto (um nível acima de scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    success, output, error = run_command("docker compose -f docker/docker-compose.yml config", shell=True)
    
    if success:
        print_success("Arquivo docker-compose.yml está válido!")
        return True
    else:
        print_error(f"Erro na validação: {error}")
        if output:
            print(output)
        return False

def check_logs():
    """5. Verifica os logs dos containers"""
    print_header("5. VERIFICANDO LOGS DOS CONTAINERS")
    
    containers = ["jarvis", "ollama"]
    all_ok = True
    
    # Obter diretório raiz do projeto (um nível acima de scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    for container in containers:
        print_info(f"\nÚltimas 10 linhas de log do container '{container}':")
        success, output, error = run_command(
            f"docker compose -f docker/docker-compose.yml logs --tail=10 {container}",
            shell=True
        )
        
        if success:
            if output.strip():
                print(output)
            else:
                print_warning(f"Container {container} não tem logs ainda")
        else:
            print_error(f"Erro ao obter logs de {container}: {error}")
            all_ok = False
    
    return all_ok

def check_dependencies():
    """6. Verifica dependências entre serviços"""
    print_header("6. VERIFICANDO DEPENDÊNCIAS")
    
    # Verificar se Ollama está acessível internamente
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print_success(f"Ollama está acessível e tem {len(models)} modelo(s) disponível(is)")
            if models:
                print_info(f"Modelos: {', '.join([m.get('name', 'N/A') for m in models[:5]])}")
            return True
        else:
            print_warning(f"Ollama respondeu com status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ollama não está acessível: {e}")
        return False

def check_directories():
    """7. Verifica montagens de volumes e diretórios"""
    print_header("7. VERIFICANDO DIRETÓRIOS E VOLUMES")
    
    base_path = r"D:\PROGRAMAS PROG\JARVIS\PROJECT_JARVIS_5.0"
    directories = [
        ("plugins", os.path.join(base_path, "plugins")),
        ("web", os.path.join(base_path, "web")),
        ("config", os.path.join(base_path, "config")),
    ]
    
    all_ok = True
    for name, path in directories:
        if os.path.exists(path):
            if os.path.isdir(path):
                file_count = len(os.listdir(path)) if os.path.isdir(path) else 0
                print_success(f"Diretório '{name}' existe: {path} ({file_count} itens)")
            else:
                print_warning(f"'{name}' existe mas não é um diretório: {path}")
        else:
            print_warning(f"Diretório '{name}' não encontrado: {path}")
            all_ok = False
    
    # Verificar volumes Docker
    print_info("\nVerificando volumes Docker:")
    success, output, error = run_command("docker volume ls", shell=True)
    if success:
        if "jarvis" in output.lower() or "ollama" in output.lower():
            print_success("Volumes Docker encontrados")
        else:
            print_warning("Nenhum volume relacionado ao projeto encontrado")
    else:
        print_error(f"Erro ao listar volumes: {error}")
    
    return all_ok

def check_api_endpoints():
    """8. Verifica endpoints da API"""
    print_header("8. VERIFICANDO ENDPOINTS DA API")
    
    endpoints = [
        ("/api/status", "Status do sistema"),
    ]
    
    all_ok = True
    base_url = "http://localhost:8000"
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"{description} ({endpoint})")
                print_info(f"Resposta: {json.dumps(data, indent=2)}")
            else:
                print_warning(f"{description} retornou status {response.status_code}")
                all_ok = False
        except Exception as e:
            print_error(f"Erro ao acessar {endpoint}: {e}")
            all_ok = False
    
    return all_ok

def main():
    """Função principal"""
    try:
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("=" * 60)
        print("    DIAGNOSTICO JARVIS 5.0 - Sistema Docker")
        print("=" * 60)
        print(f"{Colors.RESET}")
    except:
        print("\n" + "=" * 60)
        print("    DIAGNOSTICO JARVIS 5.0 - Sistema Docker")
        print("=" * 60 + "\n")
    
    results = []
    
    # Executar todas as verificações
    results.append(("Containers", check_containers()))
    results.append(("Portas", check_ports()))
    results.append(("Rede", check_network()))
    results.append(("Docker Compose", validate_docker_compose()))
    results.append(("Logs", check_logs()))
    results.append(("Dependências", check_dependencies()))
    results.append(("Diretórios", check_directories()))
    results.append(("API Endpoints", check_api_endpoints()))
    
    # Resumo final
    print_header("RESUMO DO DIAGNÓSTICO")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print(f"\n{Colors.BOLD}Resultado Final: {passed}/{total} verificações passaram{Colors.RESET}\n")
    
    if passed == total:
        print_success("Todos os testes passaram! O sistema está funcionando corretamente.")
        return 0
    else:
        print_warning("Alguns problemas foram encontrados. Revise os detalhes acima.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDiagnóstico interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

