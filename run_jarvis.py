"""Entry point for the minimal Jarvis MVP.

Usage examples:
  python run_jarvis.py                # voz somente
  python run_jarvis.py --text         # apenas texto (linha de comando)
  python run_jarvis.py --both         # voz e texto em paralelo

Na modalidade `both` você pode digitar comandos enquanto o Jarvis também
escuta o microfone.
"""
import argparse
import threading
import sys

from jarvis_minimal import JarvisAgent


def main():
    parser = argparse.ArgumentParser(description="Runner for Jarvis minimal")
    parser.add_argument("--mode", choices=["voice", "text", "both"], default="voice",
                        help="Modo de entrada: voz, texto ou ambos")
    # convenience flags matching README wording; they override --mode if provided
    parser.add_argument("--text", action="store_true",
                        help="mesmo que --mode text (modo só texto)")
    parser.add_argument("--both", action="store_true",
                        help="mesmo que --mode both (voz + texto)")
    parser.add_argument("--debug", action="store_true",
                        help="habilita logs detalhados e auto-treinamento periódico")
    args = parser.parse_args()
    # normalize backwards-compatible flags
    if args.text:
        args.mode = "text"
    elif args.both:
        args.mode = "both"

    agent = JarvisAgent()
    if args.debug:
        try:
            agent.debug = True
            print("[debug] modo debug ativado")
        except Exception:
            pass

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

    if args.mode in ("text", "both"):
        t = threading.Thread(target=text_loop, daemon=True)
        t.start()

    if args.mode in ("voice", "both"):
        agent.run()
    else:
        # text-only mode; just wait on text thread
        t.join()


if __name__ == "__main__":
    main()
