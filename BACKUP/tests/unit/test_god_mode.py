"""
Test script for SystemController (God Mode)
Tests deep Windows integration capabilities
"""

from src.core.system_controller import system_controller

print("=" * 70)
print("🔥 JARVIS GOD MODE - System Controller Test")
print("=" * 70)

# Test 1: Capabilities
print("\n1️⃣ CAPACIDADES DISPONÍVEIS:")
for cap, available in system_controller.capabilities.items():
    status = "✅" if available else "❌"
    print(f"   {status} {cap.upper()}")

# Test 2: Hardware Info
print("\n2️⃣ INFORMAÇÕES DE HARDWARE:")
hw_info = system_controller.get_hardware_info()
print(f"   CPU: {hw_info['cpu']['percent']}% ({hw_info['cpu']['count']} cores)")
print(
    f"   RAM: {hw_info['memory']['used_gb']}GB / {hw_info['memory']['total_gb']}GB ({hw_info['memory']['percent']}%)"
)
print(
    f"   Disco: {hw_info['disk']['used_gb']}GB / {hw_info['disk']['total_gb']}GB ({hw_info['disk']['percent']}%)"
)
if hw_info["bios"]:
    print(
        f"   BIOS: {hw_info['bios'].get('manufacturer', 'N/A')} - {hw_info['bios'].get('version', 'N/A')}"
    )

# Test 3: Process List (top 5)
print("\n3️⃣ TOP 5 PROCESSOS (CPU):")
processes = system_controller.list_processes()
sorted_procs = sorted(processes, key=lambda x: x.get("cpu_percent", 0), reverse=True)[
    :5
]
for proc in sorted_procs:
    print(
        f"   {proc['name']}: {proc['cpu_percent']}% CPU, {proc.get('memory_percent', 0):.1f}% RAM"
    )

# Test 4: Shell Command
print("\n4️⃣ TESTE DE COMANDO SHELL:")
result = system_controller.execute_shell_command("echo Hello from JARVIS God Mode!")
if result["success"]:
    print(f"   ✅ Output: {result['stdout'].strip()}")
else:
    print(f"   ❌ Erro: {result['stderr']}")

# Test 5: Volume Control (safe test - just read current)
print("\n5️⃣ CONTROLE DE ÁUDIO:")
if system_controller.capabilities["pycaw"]:
    print("   ✅ PyCAW disponível - controle de volume ativo")
    print("   💡 Teste: system_controller.set_master_volume(0.5)  # 50%")
else:
    print("   ⚠️ PyCAW não disponível - instale: pip install pycaw")

# Test 6: Window Management
print("\n6️⃣ GERENCIAMENTO DE JANELAS:")
if system_controller.capabilities["win32"]:
    print("   ✅ Win32 API disponível")
    # Buscar janela do próprio terminal
    hwnd = system_controller.find_window_by_title("python", partial=True)
    if hwnd:
        print(f"   ✅ Janela Python encontrada (Handle: {hwnd})")
    else:
        print("   ⚠️ Nenhuma janela Python encontrada")
else:
    print("   ⚠️ pywin32 não disponível - instale: pip install pywin32")

print("\n" + "=" * 70)
print("✅ TESTE COMPLETO!")
print("=" * 70)
