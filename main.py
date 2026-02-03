#!/usr/bin/env python3
"""
Jarvis 5.0 - Ponto de entrada principal
Assistente Virtual com Visão, Audição e Aprendizado Evolutivo
"""

import sys
import os
import logging
from pathlib import Path
import argparse
import signal
import atexit
import threading

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Imports dos módulos da aplicação
from utils.config import config
from utils.helpers import system_helper
from core.hardware_manager import hardware_manager
from core.local_brain import local_brain
from database.models import db_manager
from core.screen_capture import screen_capture
from core.ocr_processor import ocr_processor
from core.data_analyzer import data_analyzer
from core.data_organizer import data_organizer
# Jarvis Components
from core.voice_controller import voice_controller
from core.neural_memory import neural_memory
from core.ai_agent import ai_agent
from core.camera_controller import camera_controller
from core.proactive_monitor import proactive_monitor
from gui.main_window import main_window

# Configuração de logging global
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class JarvisApp:
    """Núcleo Principal do Jarvis 5.0"""

    def __init__(self):
        self.initialized = False
        self.running = False

    def initialize(self) -> bool:
        """
        Inicializa todos os componentes da aplicação

        Returns:
            True se inicialização foi bem-sucedida
        """
        try:
            logger.info("Iniciando Jarvis 5.0...")
            logger.info(f"Versão: {config.get_setting('app.version')}")
            logger.info(f"Sistema: {config.SYSTEM_INFO}")
            
            # Log de Hardware
            hw_status = hardware_manager.get_status()
            logger.info(f"Hardware Detectado: {hw_status['gpu_name']} ({hw_status['device']})")

            # Verificar requisitos do sistema
            if not self._check_system_requirements():
                return False

            # Inicializar banco de dados
            logger.info("Inicializando banco de dados...")
            # Banco já é inicializado automaticamente no import

            # Verificar engines OCR
            logger.info("Verificando engines OCR...")
            available_engines = ocr_processor.get_available_engines()
            if not available_engines:
                logger.warning("Nenhum engine OCR disponível. Alguns recursos estarão limitados.")
            else:
                logger.info(f"Engines OCR disponíveis: {', '.join(available_engines)}")

            # Inicializar Memória Neural
            logger.info("Inicializando Memória Neural Jarvis...")
            from core.memory_seed import seed_jarvis
            seed_jarvis()
            
            # Inicializar Agente de IA
            logger.info("Verificando Agente de IA...")
            if not ai_agent.api_key and ai_agent.provider == 'gemini':
                logger.warning("Google API Key não detectada. O modo online do Jarvis estará limitado.")
            
            # Carregar Cérebro Local (Background)
            logger.info("Preparando Cérebro Local (Transformers)...")
            threading.Thread(target=local_brain.load, daemon=True).start()

            # Verificar modelo NLP
            if not hasattr(data_analyzer, 'nlp') or data_analyzer.nlp is None:
                logger.warning("Modelo de linguagem natural não disponível. Análise de sentimento desabilitada.")
            else:
                logger.info("Modelo de linguagem natural carregado.")

            # Registrar função de limpeza
            atexit.register(self.cleanup)

            # Inicializar Câmera (FaceID)
            logger.info("Iniciando sistema de visão (FaceID)...")
            camera_controller.start_monitoring()

            # Inicializar Monitor Proativo (Stark Phase 1)
            logger.info("Iniciando Monitor Proativo (Iniciativa Stark)...")
            proactive_monitor.start()

            # Inicializar Wake Word
            logger.info("Iniciando escuta ativa (Wake Word)...")
            voice_controller.listen_for_wake_word(on_wake=self._on_wake_detected)

            self.initialized = True
            logger.info("Aplicação inicializada com sucesso!")

            return True

        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return False

    def _check_system_requirements(self) -> bool:
        """
        Verifica se os requisitos mínimos do sistema estão atendidos

        Returns:
            True se requisitos estão OK
        """
        try:
            # Verificar Python
            python_version = sys.version_info
            if python_version < (3, 9):
                logger.error(f"Python 3.9+ requerido. Versão atual: {python_version}")
                return False

            # Verificar espaço em disco
            system_info = system_helper.get_system_info()
            disk_free_gb = system_info.get('disk_free', 0)

            if disk_free_gb < 0.5:  # 500MB mínimo
                logger.warning(f"Espaço em disco baixo: {disk_free_gb:.2f}GB livre")

            # Verificar memória
            memory_total_gb = system_info.get('memory_total', 0)
            if memory_total_gb < 4:  # 4GB recomendado
                logger.warning(f"Memória RAM baixa: {memory_total_gb:.1f}GB total")

            # Verificar permissões de escrita
            test_file = config.DATA_DIR / "test_write.tmp"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                logger.error(f"Sem permissões de escrita no diretório de dados: {e}")
                return False

            logger.info("Requisitos do sistema verificados com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro na verificação de requisitos: {e}")
            return False

    def _on_wake_detected(self):
        """Callback acionado quando o Wake Word é detectado"""
        logger.info("Wake Word detectado! Ativando modo comando...")
        
        # Obter usuário da câmera para saudação personalizada (opcional)
        user_name = camera_controller.last_seen_user
        if user_name:
            logger.info(f"Interagindo com {user_name}")

        # Iniciar escuta de comando único
        # O VoiceController já fará o feedback de voz ("Pois não?")
        voice_controller.listen_once(on_command=self._process_voice_command)

    def _process_voice_command(self, text: str):
        """Processa o comando de voz recebido"""
        logger.info(f"Processando voz: {text}")
        ai_agent.process_command(text)

    def run_gui(self):
        """Executa a interface gráfica"""
        if not self.initialized:
            logger.error("Aplicação não inicializada. Execute initialize() primeiro.")
            return

        try:
            self.running = True
            logger.info("Iniciando interface gráfica...")

            # Executar interface
            main_window.run()

        except KeyboardInterrupt:
            logger.info("Aplicação interrompida pelo usuário")
        except Exception as e:
            logger.error(f"Erro na execução da interface: {e}")
        finally:
            self.running = False

    def run_cli(self, args):
        """Executa em modo linha de comando"""
        if not self.initialized:
            logger.error("Aplicação não inicializada. Execute initialize() primeiro.")
            return

        try:
            logger.info("Executando em modo CLI...")

            if args.command == 'capture':
                self._cli_capture(args)
            elif args.command == 'process':
                self._cli_process(args)
            elif args.command == 'analyze':
                self._cli_analyze(args)
            elif args.command == 'export':
                self._cli_export(args)
            elif args.command == 'batch':
                self._cli_batch(args)
            else:
                logger.error(f"Comando desconhecido: {args.command}")

        except Exception as e:
            logger.error(f"Erro no modo CLI: {e}")

    def _cli_capture(self, args):
        """Captura de tela via CLI"""
        logger.info("Iniciando captura via CLI...")

        try:
            if args.area:
                # Captura de área específica
                x, y, w, h = map(int, args.area.split(','))
                capture_path = screen_capture.capture_region((x, y, w, h))
            elif args.window:
                # Captura de janela específica
                capture_path = screen_capture.capture_window(args.window)
            else:
                # Captura de tela completa
                capture_path = screen_capture.capture_fullscreen()

            if capture_path:
                logger.info(f"Captura salva: {capture_path}")

                # Processar automaticamente se solicitado
                if args.process:
                    logger.info("Processando captura...")
                    ocr_result = ocr_processor.process_image(capture_path)
                    if ocr_result:
                        logger.info("OCR concluído")

                        if args.analyze:
                            logger.info("Analisando dados...")
                            analysis = data_analyzer.analyze_text(ocr_result.get('cleaned_text', ''))
                            logger.info(f"Análise concluída: {len(analysis.get('extracted_data', []))} dados extraídos")

                            if args.export:
                                logger.info("Exportando dados...")
                                # Obter ID da captura
                                capture_hash = ocr_processor.file_helper.get_file_hash(capture_path)
                                capture_record = db_manager.get_capture_by_hash(capture_hash)
                                if capture_record:
                                    organized_data = data_organizer.organize_capture_data(capture_record.id)
                                    export_path = data_organizer.export_data(organized_data, args.format or 'json')
                                    if export_path:
                                        logger.info(f"Dados exportados: {export_path}")
            else:
                logger.error("Falha na captura")

        except Exception as e:
            logger.error(f"Erro na captura CLI: {e}")

    def _cli_process(self, args):
        """Processamento de imagem via CLI"""
        if not args.input:
            logger.error("Arquivo de entrada não especificado")
            return

        try:
            logger.info(f"Processando arquivo: {args.input}")

            ocr_result = ocr_processor.process_image(args.input)
            if ocr_result:
                logger.info("Processamento OCR concluído")

                if args.analyze:
                    analysis = data_analyzer.analyze_text(ocr_result.get('cleaned_text', ''))
                    logger.info(f"Análise concluída: {len(analysis.get('extracted_data', []))} dados extraídos")

                    if args.export:
                        # Para arquivos externos, criar estrutura básica
                        organized_data = {
                            'file_path': args.input,
                            'ocr_result': ocr_result,
                            'analysis': analysis
                        }
                        export_path = data_organizer.export_data(organized_data, args.format or 'json')
                        if export_path:
                            logger.info(f"Dados exportados: {export_path}")
                else:
                    # Apenas mostrar resultado OCR
                    print("\n=== RESULTADO OCR ===")
                    print(ocr_result.get('cleaned_text', ''))
            else:
                logger.error("Falha no processamento")

        except Exception as e:
            logger.error(f"Erro no processamento CLI: {e}")

    def _cli_analyze(self, args):
        """Análise de texto via CLI"""
        if not args.text and not args.file:
            logger.error("Texto ou arquivo não especificado")
            return

        try:
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = args.text

            logger.info("Analisando texto...")
            analysis = data_analyzer.analyze_text(text)

            print("\n=== RESULTADO DA ANÁLISE ===")
            print(f"Dados extraídos: {len(analysis.get('extracted_data', []))}")
            print(f"Categorias identificadas: {analysis.get('categories', [])}")
            print(f"Confiança geral: {analysis.get('confidence', 0):.2f}")

            for data_item in analysis.get('extracted_data', []):
                print(f"- {data_item['field_name']}: {data_item['field_value']} "
                      f"(tipo: {data_item['data_type']}, confiança: {data_item['confidence']:.2f})")

            if args.export:
                export_path = data_organizer.export_data(analysis, args.format or 'json')
                if export_path:
                    logger.info(f"Análise exportada: {export_path}")

        except Exception as e:
            logger.error(f"Erro na análise CLI: {e}")

    def _cli_export(self, args):
        """Exportação de dados via CLI"""
        if not args.input:
            logger.error("Arquivo de entrada não especificado")
            return

        try:
            # Carregar dados do arquivo
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)

            export_path = data_organizer.export_data(data, args.format or 'json')
            if export_path:
                logger.info(f"Dados exportados: {export_path}")
            else:
                logger.error("Falha na exportação")

        except Exception as e:
            logger.error(f"Erro na exportação CLI: {e}")

    def _cli_batch(self, args):
        """Processamento em lote via CLI"""
        if not args.input_dir:
            logger.error("Diretório de entrada não especificado")
            return

        try:
            input_dir = Path(args.input_dir)
            if not input_dir.exists():
                logger.error(f"Diretório não existe: {input_dir}")
                return

            # Encontrar arquivos de imagem
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
            image_files = [
                f for f in input_dir.glob("*")
                if f.is_file() and f.suffix.lower() in image_extensions
            ]

            if not image_files:
                logger.warning(f"Nenhum arquivo de imagem encontrado em: {input_dir}")
                return

            logger.info(f"Processando {len(image_files)} imagens...")

            # Processar em lote
            results = ocr_processor.process_batch([str(f) for f in image_files])

            # Agregar resultados
            batch_summary = {
                'total_files': len(image_files),
                'processed_files': len(results),
                'successful_processes': sum(1 for r in results.values() if r is not None),
                'results': results
            }

            # Salvar resumo
            summary_file = input_dir / "batch_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(batch_summary, f, indent=2, ensure_ascii=False)

            logger.info(f"Processamento em lote concluído. Resumo salvo em: {summary_file}")

        except Exception as e:
            logger.error(f"Erro no processamento em lote: {e}")

    def cleanup(self):
        """Limpa recursos da aplicação"""
        try:
            logger.info("Executando limpeza...")

            # Parar gravações ativas
            if hasattr(screen_capture, 'recording_active') and screen_capture.recording_active:
                screen_capture.stop_screen_recording()

            # Fechar conexões de banco
            # SQLAlchemy gerencia automaticamente

            # Limpar arquivos temporários
            temp_dir = config.DATA_DIR / "temp"
            if temp_dir.exists():
                for temp_file in temp_dir.glob("*"):
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass

            logger.info("Limpeza concluída")

        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")

def create_argument_parser():
    """Cria parser de argumentos para modo CLI"""
    parser = argparse.ArgumentParser(
        description="Jarvis 5.0 - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Captura de tela completa
  python main.py capture

  # Captura de área específica e processamento automático
  python main.py capture --area 100,100,800,600 --process --analyze --export --format json

  # Processamento de imagem existente
  python main.py process --input imagem.png --analyze --export --format pdf

  # Análise de texto
  python main.py analyze --text "CPF: 123.456.789-00" --export --format csv

  # Processamento em lote
  python main.py batch --input-dir ./imagens/
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando capture
    capture_parser = subparsers.add_parser('capture', help='Capturar tela')
    capture_parser.add_argument('--area', help='Área para capturar (x,y,width,height)')
    capture_parser.add_argument('--window', help='Título da janela para capturar')
    capture_parser.add_argument('--process', action='store_true', help='Processar após capturar')
    capture_parser.add_argument('--analyze', action='store_true', help='Analisar dados após processar')
    capture_parser.add_argument('--export', action='store_true', help='Exportar dados após analisar')
    capture_parser.add_argument('--format', choices=['json', 'csv', 'excel', 'pdf', 'txt'],
                               default='json', help='Formato de exportação')

    # Comando process
    process_parser = subparsers.add_parser('process', help='Processar imagem')
    process_parser.add_argument('--input', required=True, help='Arquivo de imagem para processar')
    process_parser.add_argument('--analyze', action='store_true', help='Analisar dados após processar')
    process_parser.add_argument('--export', action='store_true', help='Exportar dados após analisar')
    process_parser.add_argument('--format', choices=['json', 'csv', 'excel', 'pdf', 'txt'],
                               default='json', help='Formato de exportação')

    # Comando analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analisar texto')
    group = analyze_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', help='Texto para analisar')
    group.add_argument('--file', help='Arquivo de texto para analisar')
    analyze_parser.add_argument('--export', action='store_true', help='Exportar resultado')
    analyze_parser.add_argument('--format', choices=['json', 'csv', 'excel', 'pdf', 'txt'],
                               default='json', help='Formato de exportação')

    # Comando export
    export_parser = subparsers.add_parser('export', help='Exportar dados')
    export_parser.add_argument('--input', required=True, help='Arquivo JSON com dados para exportar')
    export_parser.add_argument('--format', choices=['json', 'csv', 'excel', 'pdf', 'txt'],
                              default='json', help='Formato de exportação')

    # Comando batch
    batch_parser = subparsers.add_parser('batch', help='Processamento em lote')
    batch_parser.add_argument('--input-dir', required=True, help='Diretório com imagens para processar')

    return parser

def main():
    """Função principal"""
    # Tratamento de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Parser de argumentos
    parser = create_argument_parser()
    args = parser.parse_args()

    # Inicializar aplicação
    app = JarvisApp()

    if not app.initialize():
        logger.error("Falha na inicialização da aplicação")
        sys.exit(1)

    # Executar modo apropriado
    if args.command:
        # Modo CLI
        app.run_cli(args)
    else:
        # Modo GUI
        app.run_gui()

def signal_handler(signum, frame):
    """Tratador de sinais do sistema"""
    logger.info(f"Sinal {signum} recebido. Encerrando...")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Aplicação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)
