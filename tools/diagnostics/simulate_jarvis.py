#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Stark Integration Stress Test
===========================================
Simula comandos e entradas sensoriais para verificar as Fases 2, 3 e 4.
"""

import sys
import time
import logging
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("STRESS-TEST")


def run_test_suite():
    errors = []

    print("\n🚀 INICIANDO SIMULAÇÃO DE ESTRESSE - STARK OS v10.0\n")

    # --- TESTE 1: ANALISADOR DE CONTEXTO ---
    print("🧪 Teste 1: Analisador de Contexto (NLP)")
    try:
        from src.core.intelligence.analisador_contexto import analisador_contexto

        commands = [
            ("Aumentar brilho da tela", "HARDWARE"),
            ("Quero estudar sobre buracos negros", "AUTONOMIA"),
            ("Tocar música clássica", "MULTIMIDIA"),
            ("O que é o sol?", "GERAL"),
        ]
        for cmd, expected in commands:
            res = analisador_contexto.analisar(cmd)
            if res["contexto"] == expected:
                print(f"  ✅ '{cmd}' -> {res['contexto']}")
            else:
                print(f"  ❌ '{cmd}' -> {res['contexto']} (Esperado: {expected})")
                errors.append(f"Contexto errado para: {cmd}")
    except Exception as e:
        print(f"  🔥 Erro Fatal Teste 1: {e}")
        errors.append(str(e))

    # --- TESTE 2: DEVICE MANAGER (HARDWARE) ---
    print("\n🧪 Teste 2: Device Manager (Hardware Control)")
    try:
        from src.core.management.device_manager import device_manager

        # Simulação de brilho
        device_manager.set_brightness(50)
        print("  ✅ Ajuste de Brilho (PowerShell/Lib) invocado.")
        # Simulação de volume
        device_manager.set_volume(30)
        print("  ✅ Ajuste de Volume invocado.")
    except Exception as e:
        print(f"  🔥 Erro Fatal Teste 2: {e}")
        errors.append(str(e))

    # --- TESTE 3: NEURAL DREAMING (AUTONOMIA) ---
    print("\n🧪 Teste 3: Protocolo Neural Dreaming")
    try:
        from src.core.intelligence.neural_dreaming import neural_dreaming

        res = neural_dreaming.start_dream(
            "Programação Quântica", duration_min=1, focus_mode=False
        )
        if res:
            print("  ✅ Protocolo Dreaming iniciado em background.")
            time.sleep(1)
            if neural_dreaming.is_dreaming:
                print(
                    f"  ✅ Estado Dreaming: {neural_dreaming.is_dreaming} (Tópico: {neural_dreaming.current_topic})"
                )
            neural_dreaming.stop_dream()
            print("  ✅ Protocolo Dreaming interrompido manualmente.")
        else:
            print("  ❌ Falha ao iniciar Dreaming.")
            errors.append("Dreaming startup failed.")
    except Exception as e:
        print(f"  🔥 Erro Fatal Teste 3: {e}")
        errors.append(str(e))

    # --- TESTE 4: QUICK RESPONSE ROUTER (AI AGENT) ---
    print("\n🧪 Teste 4: AIAgent QuickResponse Integration")
    try:
        # Mocking voice_controller to avoid speech synthesis in terminal
        import src.core.audio.voice_controller as vc_mod

        original_vc = vc_mod.voice_controller

        class MockVC:
            def speak(self, text, mode="online"):
                print(f"  🗣️ Jarvis: {text}")

        vc_mod.voice_controller = MockVC()

        from src.core.intelligence.ai_agent import ai_agent

        test_prompts = ["brilho em 80%", "estude sobre psicologia", "volume no máximo"]

        for p in test_prompts:
            print(f"  👤 Usuário: {p}")
            response = ai_agent.process_command(p)
            print(f"  🤖 Resposta do Agente: {response[:100]}...")
            if not response:
                errors.append(f"Resposta vazia para: {p}")

        vc_mod.voice_controller = original_vc  # Restore
    except Exception as e:
        print(f"  🔥 Erro Fatal Teste 4: {e}")
        errors.append(str(e))

    # --- RESULTADO FINAL ---
    print("\n" + "=" * 50)
    if not errors:
        print("🏆 RESULTADO: SISTEMA 100% OPERACIONAL")
    else:
        print(f"⚠️ RESULTADO: {len(errors)} ERROS ENCONTRADOS")
        for err in errors:
            print(f"  - {err}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_test_suite()
