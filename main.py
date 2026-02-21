"""Entry point for the Jarvis 5.0 Production System.

Usage examples:
  python main.py                # voz somente
  python main.py --text         # apenas texto (linha de comando)
  python main.py --both         # voz e texto em paralelo
"""
import argparse
import threading
import sys
import os
import json
import logging

from jarvis import JarvisAgent



# --- startup helpers --------------------------------------------------------

def configure_logging(debug: bool = False):
    """Configure root logger with console and file handlers."""
    root = logging.getLogger()
    # avoid configuring twice
    if root.handlers:
        return
    level = logging.DEBUG if debug else logging.INFO
    root.setLevel(level)
    fmt = logging.Formatter("[%(levelname)s] %(name)s:%(lineno)d: %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    logfile = os.path.join(os.getcwd(), "startup.log")
    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)
    logging.info("logs sendo enviados para %s", logfile)


def load_config(path: str):
    """Load custom configuration file if provided."""
    if not path:
        return
    if not os.path.exists(path):
        logging.warning("arquivo de configuração %s não existe", path)
        return
    try:
        if path.lower().endswith(".json"):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            import yaml

            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        logging.info("configuração carregada de %s", path)
        # merge into os.environ or config module as needed
        for k, v in data.items():
            os.environ[k] = str(v)
    except Exception as e:
        logging.error("falha ao carregar config %s: %s", path, e)


def check_prerequisites():
    """Simple dependency check before starting the agent."""
    missing = []
    try:
        import torch  # noqa: F401
    except ImportError:
        missing.append("torch")
    if missing:
        logging.warning("módulos faltando: %s, a inicialização pode falhar", missing)
    else:
        logging.debug("verificação de dependências concluída")


def main():
    parser = argparse.ArgumentParser(description="Runner for Jarvis minimal")
    parser.add_argument("--mode", choices=["voice", "text", "both"], default="voice",
                        help="Modo de entrada: voz, texto ou ambos")
    parser.add_argument("--text", action="store_true",
                        help="mesmo que --mode text (modo só texto)")
    parser.add_argument("--both", action="store_true",
                        help="mesmo que --mode both (voz + texto)")
    parser.add_argument("--no-text", action="store_true",
                        help="desativa interface de texto (útil se quiser apenas voz)")
    parser.add_argument("--debug", action="store_true",
                        help="habilita logs detalhados e auto-treinamento periódico")
    parser.add_argument("--config", help="arquivo JSON/YAML com variáveis de configuração")

    args = parser.parse_args()
    if args.text:
        args.mode = "text"
    elif args.both:
        args.mode = "both"
    # if user asked to suppress text, override modes
    if args.no_text:
        # even in "both" we'll pretend it's pure voice
        args.mode = "voice"

    configure_logging(args.debug)
    check_prerequisites()
    load_config(args.config)

    logging.info("iniciando Jarvis (modo=%s, debug=%s)", args.mode, args.debug)
    try:
        agent = JarvisAgent()
    except Exception as e:
        logging.error("falha ao criar agente: %s", e, exc_info=True)
        sys.exit(1)

    if args.debug:
        agent.debug = True
        logging.info("modo debug ativado no agente")

    logging.debug("startup report: %s", getattr(agent, "startup_report", {}))

    def text_loop():
        print("[text] digite suas mensagens abaixo (CTRL+C para sair)")
        try:
            while True:
                line = input("> ").strip()
                if not line:
                    continue
                agent.handle_command(line)
        except (EOFError, KeyboardInterrupt):
            print("\n[text] encerrando interface de texto")
            sys.exit(0)

    # always offer text interface unless explicitly disabled
    t = None
    if not args.no_text:
        t = threading.Thread(target=text_loop, daemon=True)
        t.start()

    if args.mode in ("voice", "both"):
        agent.run()
    else:
        # if voice-only mode but text thread exists, keep program running
        if t:
            t.join()


if __name__ == "__main__":
    main()
