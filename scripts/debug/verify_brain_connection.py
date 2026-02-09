
import sys
import requests
import yaml
from pathlib import Path

def load_config():
    try:
        with open("config/ai_config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Could not load config/ai_config.yaml: {e}")
        return None

def check_ollama():
    print("🧠 Testing Brain Connection (Ollama)...")
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url, timeout=2.0)
        if response.status_code == 200:
            print("✅ Ollama is ALIVE.")
            models = [m['name'] for m in response.json().get('models', [])]
            print(f"📚 Available Models: {models}")
            return models
        else:
            print(f"⚠️ Ollama reachable but returned status {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is OFFLINE (Connection Refused).")
        print("   -> Is Ollama installed and running?")
        return []
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return []

def main():
    config = load_config()
    if not config:
        return

    # Check Cloud Keys
    google_key = config.get('brain', {}).get('gemini_api_key', '') or "Not Set"
    if len(google_key) > 10:
        print("☁️  Gemini Key: FOUND")
    else:
        print("☁️  Gemini Key: MISSING (Cloud Brain Disabled)")

    # Check Local Brain
    available_models = check_ollama()
    
    # Check Match
    desired_models = config.get('brain_router', {}).get('ollama_models', {}).get('tier_pro', [])
    print(f"\n🎯 Desired Models (Tier Pro): {desired_models}")
    
    missing = [m for m in desired_models if m not in available_models]
    
    if available_models:
        if not missing:
            print("✨ INTELLIGENCE READY: Local Brain Fully Charged.")
        else:
            print(f"⚠️ INTELLIGENCE PARTIAL: Missing high-tier models: {missing}")
            print("   -> System will try to fallback to available models.")
    else:
        print("💀 INTELLIGENCE CRITICAL: No Brain Available (No Cloud, No Local).")

if __name__ == "__main__":
    main()
