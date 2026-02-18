import os
import sys
import subprocess
import time
import requests
import webbrowser


def print_colored(text, color_code):
    if sys.platform == "win32":
        os.system("color")
    print(f"\033[{color_code}m{text}\033[0m")


def check_ollama_installed():
    try:
        subprocess.run(
            ["ollama", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        return False


def check_ollama_running():
    try:
        requests.get("http://localhost:11434", timeout=1)
        return True
    except BaseException:
        return False


def install_model(model_name):
    print_colored(f"⬇️  Pulling Model: {model_name}...", "36")  # Cyan
    try:
        # Stream the output
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",  # Force utf-8 for emojis
        )

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        if process.returncode == 0:
            print_colored(f"✅ Model {model_name} installed!", "32")  # Green
            return True
        else:
            print_colored(f"❌ Failed to download {model_name}", "31")
            return False
    except Exception as e:
        print_colored(f"❌ Error pulling model: {e}", "31")
        return False


def main():
    print_colored("\n🧠 JARVIS BRAIN SETUP (OLLAMA)", "1m")

    # 1. Check Installation
    if not check_ollama_installed():
        print_colored("❌ Ollama not found in PATH.", "31")
        print("To give JARVIS a brain, you need to install Ollama.")
        print("Opening download page...")
        webbrowser.open("https://ollama.com/download")
        print("\n👉 Please install Ollama, then run this script again.")
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        print_colored("✅ Ollama binary found.", "32")

    # 2. Check Service
    if not check_ollama_running():
        print_colored("⚠️  Ollama is not running.", "33")
        print("Attempting to start Ollama serve...")
        try:
            subprocess.Popen(["ollama", "serve"], start_new_session=True)
            print("⏳ Waiting for brain to wake up...", end="", flush=True)
            for _ in range(10):
                time.sleep(1)
                if check_ollama_running():
                    print(" Done!")
                    break
                print(".", end="", flush=True)
            else:
                print("\n❌ Failed to start Ollama automatically.")
                print("Please open a new terminal and run 'ollama serve'")
                sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error starting Ollama: {e}")
            sys.exit(1)
    else:
        print_colored("✅ Ollama service is active.", "32")

    # 3. Install Models
    REQUIRED_MODELS = ["llama3", "mistral"]  # Compact and smart

    print("\n📦 Checking Neural Models...")
    try:
        response = requests.get("http://localhost:11434/api/tags").json()
        installed_models = [
            m["name"].split(":")[0] for m in response.get(
                "models", [])]
    except BaseException:
        installed_models = []

    model_installed = False
    for model in REQUIRED_MODELS:
        # Check fuzzy match
        if any(model in m for m in installed_models):
            print_colored(f"✅ {model} is already installed.", "32")
            model_installed = True
        else:
            print_colored(f"⚠️  {model} missing.", "33")
            if install_model(model):
                model_installed = True

    if model_installed:
        print_colored(
            "\n✨ BRAIN SETUP COMPLETE. JARVIS IS READY TO THINK.",
            "32")
    else:
        print_colored(
            "\n⚠️  No models installed. JARVIS will be brainless.",
            "31")


if __name__ == "__main__":
    main()
