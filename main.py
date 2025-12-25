#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Assistente de Voz Modular
Ponto de entrada principal do assistente
"""

import sys
import argparse
from pathlib import Path

# Adicionar diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jarvis import JarvisAssistant, ConfigManager


def parse_arguments():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="JARVIS 5.0 - Assistente de Voz Inteligente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main_new.py                    # Executar com configuração padrão
  python main_new.py --config custom.json  # Usar configuração personalizada
  python main_new.py --test            # Testar sistemas
  python main_new.py --calibrate       # Calibrar microfone
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.json',
        help='Caminho para arquivo de configuração (padrão: config.json)'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Testar sistemas e sair'
    )
    
    parser.add_argument(
        '--calibrate',
        action='store_true',
        help='Calibrar microfone e sair'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Ativar modo debug'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='JARVIS 5.0.0'
    )
    
    return parser.parse_args()


def setup_debug_mode(config_manager: ConfigManager):
    """Configura modo debug"""
    config_manager.set('system.debug_mode', True)
    config_manager.set('system.log_level', 'DEBUG')
    config_manager.save()
    print("Modo debug ativado")


def test_systems(assistant: JarvisAssistant) -> bool:
    """
    Testa todos os sistemas do JARVIS
    
    Returns:
        True se todos os testes passaram
    """
    print("=== Testando Sistemas do JARVIS ===")
    
    results = assistant.test_systems()
    
    print(f"Microfone: {'OK' if results.get('microphone') else 'ERRO'}")
    print(f"Sistema de Voz: {'OK' if results.get('speech') else 'ERRO'}")
    print(f"Configuracao: {'OK' if results.get('config') else 'ERRO'}")
    
    if 'error' in results:
        print(f"Erro: {results['error']}")
    
    overall = results.get('overall', False)
    print(f"\nStatus Geral: {'TODOS OS SISTEMAS OK' if overall else 'PROBLEMAS DETECTADOS'}")
    
    return overall


def main():
    """Função principal"""
    try:
        # Parse argumentos
        args = parse_arguments()
        
        print("JARVIS 5.0 - Assistente de Voz Inteligente")
        print("=" * 50)
        
        # Verificar se arquivo de configuração existe
        config_path = Path(args.config)
        if not config_path.exists() and args.config != 'config.json':
            print(f"Erro: Arquivo de configuração '{args.config}' não encontrado")
            return 1
        
        # Inicializar gerenciador de configuração
        config_manager = ConfigManager(args.config)
        
        # Configurar modo debug se solicitado
        if args.debug:
            setup_debug_mode(config_manager)
        
        # Inicializar assistente
        print("Inicializando JARVIS...")
        assistant = JarvisAssistant(args.config)
        
        # Executar ação solicitada
        if args.test:
            # Testar sistemas
            success = test_systems(assistant)
            return 0 if success else 1
        
        elif args.calibrate:
            # Calibrar microfone
            print("Calibrando microfone...")
            success = assistant.calibrate()
            return 0 if success else 1
        
        else:
            # Executar assistente normalmente
            print("Iniciando assistente...")
            print("Pressione Ctrl+C para encerrar")
            print("-" * 50)
            
            assistant.start()
            return 0
    
    except KeyboardInterrupt:
        print("\nEncerrando JARVIS...")
        return 0
    
    except Exception as e:
        print(f"Erro crítico: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
