import sys
import os
from unittest.mock import MagicMock

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.intelligence.ai_agent import ai_agent

# Mock components to avoid real API/Network calls during this specific logic test
# Mock components for local verification
ai_agent._check_ollama_alive = MagicMock(return_value=True)
ai_agent._call_ollama = MagicMock(return_value="Olá senhor (Ollama)")
ai_agent.local_brain = MagicMock()
ai_agent.local_brain.generate_response.return_value = "Senhor (LocalBrain)"


def test_local_priority():
    print("\n[TEST] Verifying Local-First Priority...")

    # 1. Standard Command (Should use Ollama)
    print("  🧪 Test 1: Standard Command (Ollama)")
    response = ai_agent.process_command("Que dia é hoje?")

    if "Ollama" in response:
        print("  ✅ Accessing Ollama (Correct)")
    else:
        print(f"  ❌ Failed (Ollama not used?): {response}")

    # 2. Local Fallback (Should use LocalBrain)
    print("\n  🧪 Test 2: LocalBrain Fallback")
    # Simulate Ollama Failure
    ai_agent._call_ollama.return_value = "dificuldades no processamento offline"

    response = ai_agent.process_command("Comando para fallback")
    if "LocalBrain" in response:
        print("  ✅ Fell back to LocalBrain correctly")
    else:
        print(f"  ❌ Failed fallback: {response}")

    print("\n[TEST] 100% Local Logic Verification Complete.")


if __name__ == "__main__":
    test_local_priority()
