import sys
import os
import logging
from unittest.mock import MagicMock, patch

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.intelligence.ai_agent import ai_agent

# Mock components to avoid real API/Network calls during this specific logic test
ai_agent._check_ollama_alive = MagicMock(return_value=True) # Simulate Ollama is running
ai_agent._call_ollama = MagicMock(return_value="Olá senhor (Local)")
ai_agent._call_gemini = MagicMock(return_value="Hello Sir (Cloud)")
ai_agent.local_brain = MagicMock()
ai_agent.voice_controller = MagicMock()

def test_local_priority():
    print("\n[TEST] Verifying Local-First Priority...")
    
    # 1. Standard Command (Should stay local)
    print("  🧪 Test 1: Standard Command")
    response = ai_agent.process_command("Que dia é hoje?")
    
    if "Local" in response:
        print("  ✅ Accessing Local Brain (Correct)")
    else:
        print(f"  ❌ Failed (Went to cloud?): {response}")

    # 2. Complex/Uncertain Command (Should go to Cloud)
    print("\n  🧪 Test 2: Uncertainty Trigger")
    # Force the mock to return a trigger word exactly as checked in ai_agent
    ai_agent._call_ollama.return_value = "Desculpe, não sei a resposta." 
    
    # We also need to ensure check_internet returns True for this test to pass
    ai_agent.voice_controller.check_internet.return_value = True
    
    response = ai_agent.process_command("Quem é o presidente de Marte?")
    if "Cloud" in response: # Mocked gemini returns 'Cloud' string
        print("  ✅ Escalated to Cloud correctly")
    else:
        print(f"  ❌ Failed to escalate: {response}")

    print("\n[TEST] Logic Verification Complete.")

if __name__ == "__main__":
    test_local_priority()
