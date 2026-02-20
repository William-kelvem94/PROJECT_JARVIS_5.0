"""Entry point for the minimal Jarvis MVP.

Usage:
  python run_jarvis.py

This will run the always‑listening loop (hotword) using local STT + Ollama for responses.
"""
from jarvis_minimal import JarvisAgent


def main():
    agent = JarvisAgent()
    agent.run()


if __name__ == "__main__":
    main()
