# 🎛️ JARVIS Advanced Device Manager - Documentação Completa

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Instalação](#instalação)
3. [Arquitetura](#arquitetura)
4. [API Completa](#api-completa)
5. [Exemplos de Uso](#exemplos-de-uso)
6. [Segurança](#segurança)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **Advanced Device Manager** é o módulo de controle total do sistema operacional do JARVIS 5.0. Ele fornece acesso programático a TODAS as funcionalidades do Windows, permitindo que o JARVIS controle completamente a máquina.

### 🌟 Capabilities

✅ **Hardware Monitoring**
- CPU (cores, frequência, temperatura, uso por core)
- RAM e SWAP (total, usado, disponível)
- GPU (modelo, VRAM, driver, status)
- Disco (partições, uso, S.M.A.R.T.)
- Bateria (percentual, carregando, tempo restante)

✅ **Network Control**
- Listar interfaces de rede
- Habilitar/desabilitar interfaces
- Bloquear processos no firewall
- Monitorar tráfego de rede
- Listar conexões ativas

✅ **Power Management**
- Shutdown/Restart (com timeout)
- Sleep/Hibernate
- Planos de energia (Balanced, High Performance, Power Saver)
- Cancelar shutdown agendado

✅ **Windows Registry**
- Ler valores do registro
- Escrever valores (com backup automático)
- Deletar valores (com backup)
- Suporte a HKLM, HKCU, etc.

✅ **Windows Services**
- Listar todos os serviços
- Start/Stop/Restart serviços
- Verificar dependências
- Status detalhado

✅ **Display Control**
- Controle de brilho (0-100%)
- Informações de monitores
- Alterar resolução
- Refresh rate
- Suporte multi-monitor

✅ **Audio Control**
- Volume do sistema (0.0-1.0)
- Mute/Unmute
- Listar dispositivos de áudio
- Estado atual do áudio

✅ **Process Management**
- Listar processos (com ordenação)
- Encerrar processos (graceful/force)
- Alterar prioridade
- Informações detalhadas
- CPU/RAM por processo

✅ **Disk Health**
- Dados S.M.A.R.T.
- Análise de espaço
- Arquivos grandes
- Desfragmentação

✅ **Security & Privileges**
- Verificar privilégios admin
- Listar privilégios do usuário
- Verificar status do UAC
- Solicitar elevação (UAC)

---

## 📦 Instalação

### Dependências

```bash
# Dependências principais (já no requirements.txt)
pip install psutil
pip install pywin32
pip install pycaw
pip install comtypes
pip install WMI
pip install screen-brightness-control
pip install watchdog
```

### Verificação de Instalação

```python
from src.core.management.device_manager import device_manager

# Verifica se está funcionando
info = device_manager.get_system_info()
print(f"CPU Cores: {info['cpu']['cores_physical']}")
print(f"RAM: {info['memory']['ram']['total_gb']} GB")
print(f"Admin: {device_manager.is_admin}")
```

---

## 🏗️ Arquitetura

### Estrutura de Classes

```
AdvancedDeviceManager
├── Hardware Monitoring
│   ├── get_system_info()
│   ├── _get_cpu_info()
│   ├── _get_memory_info()
│   ├── _get_disk_info()
│   ├── _get_gpu_info()
│   └── _get_battery_info()
│
├── Network Control
│   ├── get_network_info()
│   ├── list_network_interfaces()
│   ├── list_network_connections()
│   ├── enable_network_interface()
│   └── block_process_network()
│
├── Power Management
│   ├── shutdown()
│   ├── restart()
│   ├── sleep()
│   ├── hibernate()
│   ├── set_power_plan()
│   └── get_active_power_plan()
│
├── Windows Registry
│   ├── read_registry()
│   ├── write_registry()
│   └── delete_registry_value()
│
├── Windows Services
│   ├── list_services()
│   ├── control_service()
│   └── get_service_dependencies()
│
├── Display Control
│   ├── set_brightness()
│   ├── get_brightness()
│   ├── get_display_info()
│   └── set_display_resolution()
│
├── Audio Control
│   ├── set_volume()
│   ├── get_volume()
│   ├── mute()
│   └── list_audio_devices()
│
├── Process Management
│   ├── list_processes()
│   ├── kill_process()
│   ├── set_process_priority()
│   └── get_process_info()
│
├── Disk Health
│   ├── get_disk_smart_data()
│   ├── analyze_disk_space()
│   └── defragment_disk()
│
└── Security
    ├── _check_admin_rights()
    ├── request_admin_elevation()
    ├── get_user_privileges()
    └── check_uac_enabled()
```

### Padrões de Design

1. **Singleton Pattern**: Uma única instância global (`device_manager`)
2. **Graceful Degradation**: Funciona mesmo sem dependências opcionais
3. **Error Handling**: Tratamento robusto de exceções
4. **Backup System**: Backup automático antes de modificar registro
5. **Logging**: Log detalhado de todas as operações

---

## 📚 API Completa

### Hardware Monitoring

#### `get_system_info() -> Dict[str, Any]`

Coleta informações completas do sistema.

**Returns:**
```python
{
    'cpu': {
        'cores_physical': 8,
        'cores_logical': 16,
        'usage_percent': 45.2,
        'usage_per_core': [40, 50, 45, ...],
        'frequency_mhz': 3600,
        'temperature_celsius': 65.5
    },
    'memory': {
        'ram': {
            'total_gb': 16.0,
            'available_gb': 8.5,
            'used_gb': 7.5,
            'percent': 46.9
        },
        'swap': {
            'total_gb': 4.0,
            'used_gb': 1.2,
            'free_gb': 2.8,
            'percent': 30.0
        }
    },
    'disk': [...],
    'network': {...},
    'gpu': [...],
    'battery': {...},
    'timestamp': '2026-02-08T10:30:00'
}
```

**Exemplo:**
```python
info = device_manager.get_system_info()
cpu_usage = info['cpu']['usage_percent']
if cpu_usage > 80:
    print("⚠️ CPU está sobrecarregada!")
```

---

### Network Control

#### `list_network_interfaces() -> List[Dict[str, Any]]`

Lista todas as interfaces de rede do sistema.

**Returns:**
```python
[
    {
        'name': 'Ethernet',
        'is_up': True,
        'speed_mbps': 1000,
        'addresses': [
            {
                'family': 'AddressFamily.AF_INET',
                'address': '192.168.1.100',
                'netmask': '255.255.255.0',
                'broadcast': '192.168.1.255'
            }
        ]
    }
]
```

**Exemplo:**
```python
interfaces = device_manager.list_network_interfaces()
for iface in interfaces:
    if iface['is_up']:
        print(f"✅ {iface['name']}: {iface['speed_mbps']} Mbps")
```

#### `block_process_network(pid: int) -> bool`

Bloqueia conexões de rede de um processo via Firewall do Windows.

**Requer: Privilégios Administrativos**

**Exemplo:**
```python
# Bloqueia Chrome de acessar a internet
chrome_pid = 12345  # Obter PID via list_processes()
if device_manager.block_process_network(chrome_pid):
    print("🔥 Processo bloqueado no firewall")
```

---

### Power Management

#### `shutdown(force: bool = False, timeout: int = 30) -> bool`

Desliga o sistema.

**Args:**
- `force`: Força desligamento sem salvar
- `timeout`: Segundos até o desligamento

**Exemplo:**
```python
# Desligamento suave em 60 segundos
device_manager.shutdown(force=False, timeout=60)

# Cancelar se necessário
device_manager.cancel_shutdown()
```

#### `set_power_plan(plan: PowerPlan) -> bool`

Define o plano de energia ativo.

**Args:**
- `plan`: PowerPlan.BALANCED | HIGH_PERFORMANCE | POWER_SAVER

**Exemplo:**
```python
from src.core.management.device_manager import PowerPlan

# Alta performance para jogos/processamento
device_manager.set_power_plan(PowerPlan.HIGH_PERFORMANCE)

# Economia de bateria
device_manager.set_power_plan(PowerPlan.POWER_SAVER)
```

---

### Windows Registry

#### `read_registry(hive: int, key_path: str, value_name: str) -> Any`

Lê valor do registro do Windows.

**Args:**
- `hive`: winreg.HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc.
- `key_path`: Caminho da chave
- `value_name`: Nome do valor

**Exemplo:**
```python
import winreg

# Lê versão do Windows
version = device_manager.read_registry(
    winreg.HKEY_LOCAL_MACHINE,
    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
    "ProductName"
)
print(f"Windows: {version}")
```

#### `write_registry(hive, key_path, value_name, value, value_type, backup=True) -> bool`

Escreve valor no registro (com backup automático).

**⚠️ ATENÇÃO: Modificações no registro podem afetar o sistema!**

**Exemplo:**
```python
import winreg

# Escreve valor de teste (HKCU é seguro)
success = device_manager.write_registry(
    winreg.HKEY_CURRENT_USER,
    r"Software\JARVIS",
    "TestValue",
    "Hello World",
    winreg.REG_SZ,
    backup=True  # Backup automático
)
```

---

### Windows Services

#### `list_services() -> List[Dict[str, Any]]`

Lista todos os serviços do Windows.

**Returns:**
```python
[
    {
        'name': 'wuauserv',
        'display_name': 'Windows Update',
        'state': 'Running',
        'start_mode': 'Manual',
        'status': 'OK',
        'process_id': 1234
    }
]
```

**Exemplo:**
```python
services = device_manager.list_services()
running = [s for s in services if s['state'] == 'Running']
print(f"Serviços em execução: {len(running)}")
```

#### `control_service(service_name: str, action: ServiceAction) -> bool`

Controla um serviço Windows.

**Requer: Privilégios Administrativos**

**Args:**
- `service_name`: Nome do serviço
- `action`: ServiceAction.START | STOP | RESTART | PAUSE | RESUME

**Exemplo:**
```python
from src.core.management.device_manager import ServiceAction

# Para Windows Update
if device_manager.control_service('wuauserv', ServiceAction.STOP):
    print("✅ Windows Update parado")
```

---

### Display Control

#### `set_brightness(level: int) -> bool`

Ajusta o brilho do monitor.

**Args:**
- `level`: 0-100

**Exemplo:**
```python
# Reduz brilho à noite
device_manager.set_brightness(30)

# Máximo brilho durante o dia
device_manager.set_brightness(100)
```

#### `set_display_resolution(width: int, height: int, refresh_rate: int) -> bool`

Altera resolução e taxa de atualização do display.

**Requer: pywin32**

**Exemplo:**
```python
# Full HD @ 60Hz
device_manager.set_display_resolution(1920, 1080, 60)

# 4K @ 144Hz
device_manager.set_display_resolution(3840, 2160, 144)
```

---

### Audio Control

#### `set_volume(level: float) -> bool`

Define volume do sistema.

**Args:**
- `level`: 0.0 (mudo) a 1.0 (máximo)

**Exemplo:**
```python
# Volume médio
device_manager.set_volume(0.5)

# Volume máximo
device_manager.set_volume(1.0)
```

#### `mute(muted: bool = True) -> bool`

Silencia/ativa áudio do sistema.

**Exemplo:**
```python
# Muta durante reunião
device_manager.mute(True)

# Desmuta depois
device_manager.mute(False)
```

---

### Process Management

#### `list_processes(sort_by: str = 'cpu') -> List[Dict[str, Any]]`

Lista todos os processos do sistema.

**Args:**
- `sort_by`: 'cpu', 'memory', 'name'

**Returns:**
```python
[
    {
        'pid': 1234,
        'name': 'chrome.exe',
        'username': 'DESKTOP\\User',
        'cpu_percent': 15.3,
        'memory_percent': 8.2,
        'status': 'running',
        'create_time': '2026-02-08T08:00:00'
    }
]
```

**Exemplo:**
```python
# Top 10 processos por CPU
processes = device_manager.list_processes(sort_by='cpu')
for proc in processes[:10]:
    print(f"{proc['name']}: CPU={proc['cpu_percent']:.1f}%")
```

#### `kill_process(pid: int, force: bool = False, timeout: int = 5) -> bool`

Encerra um processo.

**Args:**
- `pid`: ID do processo
- `force`: True para kill forçado
- `timeout`: Tempo de espera para término gracioso

**Exemplo:**
```python
# Encerra processo travado
device_manager.kill_process(pid=5678, force=True)
```

#### `set_process_priority(pid: int, priority: ProcessPriority) -> bool`

Define prioridade de um processo.

**Args:**
- `pid`: ID do processo
- `priority`: ProcessPriority enum

**Exemplo:**
```python
from src.core.management.device_manager import ProcessPriority

# Alta prioridade para renderização
device_manager.set_process_priority(pid=1234, priority=ProcessPriority.HIGH)

# Baixa prioridade para tarefas de background
device_manager.set_process_priority(pid=5678, priority=ProcessPriority.IDLE)
```

---

### Disk Health

#### `get_disk_smart_data(disk_path: str = "C:") -> Dict[str, Any]`

Obtém dados S.M.A.R.T. do disco.

**Requer: WMI**

**Returns:**
```python
{
    'model': 'Samsung SSD 970 EVO Plus',
    'serial_number': 'S4P2NJ0M123456',
    'size_gb': 500.0,
    'interface_type': 'NVMe',
    'media_type': 'Fixed hard disk media',
    'status': 'OK',
    'partitions': 3
}
```

#### `analyze_disk_space(path: str = "C:\\") -> Dict[str, Any]`

Analisa uso de espaço em disco.

**Returns:**
```python
{
    'path': 'C:\\',
    'total_gb': 500.0,
    'used_gb': 350.5,
    'free_gb': 149.5,
    'percent': 70.1,
    'large_files': [
        {'path': 'C:\\pagefile.sys', 'size_mb': 16384},
        {'path': 'C:\\Videos\\movie.mp4', 'size_mb': 8500}
    ],
    'timestamp': '2026-02-08T10:30:00'
}
```

---

### Security & Privileges

#### `is_admin` (property)

Verifica se o processo tem privilégios administrativos.

**Exemplo:**
```python
if not device_manager.is_admin:
    print("⚠️ Algumas operações requerem privilégios admin")
    device_manager.request_admin_elevation()
```

#### `get_user_privileges() -> List[str]`

Lista privilégios do usuário/processo atual.

**Requer: pywin32**

**Returns:**
```python
[
    'SeChangeNotifyPrivilege',
    'SeImpersonatePrivilege',
    'SeCreateGlobalPrivilege',
    ...
]
```

---

### Utility Methods

#### `get_system_health_report() -> Dict[str, Any]`

Gera relatório completo de saúde do sistema.

**Returns:**
```python
{
    'timestamp': '2026-02-08T10:30:00',
    'is_admin': True,
    'system_info': {...},  # Full system info
    'processes_count': 245,
    'boot_time': '2026-02-07T08:00:00',
    'uptime_seconds': 93600,
    'alerts': [
        '⚠️ Uso de RAM crítico (>90%)',
        '⚠️ Disco C: quase cheio (>90%)'
    ]
}
```

#### `export_system_report(filepath: Optional[str] = None) -> bool`

Exporta relatório de sistema para arquivo JSON.

**Exemplo:**
```python
# Salva relatório no diretório padrão
device_manager.export_system_report()

# Salva em local específico
device_manager.export_system_report("C:\\reports\\system_health.json")
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Monitoramento de Sistema

```python
from src.core.management.device_manager import device_manager

def monitor_system():
    """Monitora recursos críticos do sistema"""
    info = device_manager.get_system_info()
    
    # CPU
    cpu_usage = info['cpu']['usage_percent']
    if cpu_usage > 90:
        print(f"⚠️ CPU CRÍTICO: {cpu_usage}%")
    
    # RAM
    ram_usage = info['memory']['ram']['percent']
    if ram_usage > 90:
        print(f"⚠️ RAM CRÍTICO: {ram_usage}%")
        # Libera memória matando processo pesado
        processes = device_manager.list_processes(sort_by='memory')
        heaviest = processes[0]
        print(f"Matando processo pesado: {heaviest['name']}")
        device_manager.kill_process(heaviest['pid'], force=True)
    
    # Disco
    for disk in info['disk']:
        if disk['percent'] > 95:
            print(f"⚠️ Disco {disk['mountpoint']} CRÍTICO: {disk['percent']}%")
            # Analisa arquivos grandes
            analysis = device_manager.analyze_disk_space(disk['mountpoint'])
            print("Arquivos grandes encontrados:")
            for file in analysis.get('large_files', [])[:5]:
                print(f"  - {file['path']}: {file['size_mb']} MB")

# Executar monitoramento
monitor_system()
```

### Exemplo 2: Modo Gaming (Performance Máxima)

```python
from src.core.management.device_manager import (
    device_manager, 
    PowerPlan, 
    ProcessPriority
)

def enable_gaming_mode(game_pid: int):
    """Otimiza sistema para jogos"""
    
    # 1. Plano de energia de alta performance
    device_manager.set_power_plan(PowerPlan.HIGH_PERFORMANCE)
    print("⚡ Plano de energia: HIGH PERFORMANCE")
    
    # 2. Prioridade alta para o jogo
    device_manager.set_process_priority(game_pid, ProcessPriority.HIGH)
    print(f"🎮 Prioridade alta para PID {game_pid}")
    
    # 3. Fecha processos pesados desnecessários
    processes = device_manager.list_processes(sort_by='cpu')
    heavy_processes = [
        'chrome.exe', 'spotify.exe', 'discord.exe', 
        'OneDrive.exe', 'dropbox.exe'
    ]
    
    for proc in processes:
        if proc['name'].lower() in [p.lower() for p in heavy_processes]:
            print(f"💀 Fechando {proc['name']}")
            device_manager.kill_process(proc['pid'])
    
    # 4. Para serviços não essenciais
    # device_manager.control_service('wuauserv', ServiceAction.STOP)
    
    # 5. Aumenta brilho e volume
    device_manager.set_brightness(100)
    device_manager.set_volume(0.8)
    
    print("✅ Modo Gaming ativado!")

# Uso
game_pid = 12345  # PID do jogo
enable_gaming_mode(game_pid)
```

### Exemplo 3: Modo Economia de Bateria

```python
def enable_battery_saver():
    """Otimiza para economia de bateria"""
    
    # 1. Verifica se tem bateria
    battery = device_manager._get_battery_info()
    if not battery:
        print("⚠️ Sistema não possui bateria")
        return
    
    # 2. Plano de energia econômico
    device_manager.set_power_plan(PowerPlan.POWER_SAVER)
    
    # 3. Reduz brilho
    device_manager.set_brightness(30)
    
    # 4. Fecha processos pesados
    processes = device_manager.list_processes(sort_by='cpu')
    for proc in processes[:10]:  # Top 10 CPU
        if proc['cpu_percent'] > 20:
            print(f"Fechando processo pesado: {proc['name']}")
            device_manager.kill_process(proc['pid'])
    
    # 5. Desabilita Wi-Fi (se solicitado)
    # interfaces = device_manager.list_network_interfaces()
    # for iface in interfaces:
    #     if 'wi-fi' in iface['name'].lower():
    #         device_manager.enable_network_interface(iface['name'], enable=False)
    
    print(f"🔋 Bateria: {battery['percent']}%")
    print(f"⚡ Tempo restante: {battery['time_left_seconds'] // 60} minutos")
    print("✅ Modo Economia de Bateria ativado!")

enable_battery_saver()
```

### Exemplo 4: Segurança - Bloquear Aplicativo da Internet

```python
def block_app_from_internet(app_name: str):
    """Bloqueia um aplicativo de acessar a internet"""
    
    if not device_manager.is_admin:
        print("❌ Requer privilégios de administrador!")
        return
    
    # 1. Encontra processo do aplicativo
    processes = device_manager.list_processes()
    target_processes = [p for p in processes if app_name.lower() in p['name'].lower()]
    
    if not target_processes:
        print(f"⚠️ Aplicativo '{app_name}' não está rodando")
        return
    
    # 2. Bloqueia cada instância no firewall
    for proc in target_processes:
        success = device_manager.block_process_network(proc['pid'])
        if success:
            print(f"🔥 {proc['name']} (PID: {proc['pid']}) bloqueado no firewall")
        else:
            print(f"❌ Falha ao bloquear {proc['name']}")
    
    print("✅ Aplicativo bloqueado da internet!")

# Bloqueia Chrome de acessar internet
block_app_from_internet("chrome")
```

### Exemplo 5: Auto-diagnóstico do Sistema

```python
def system_diagnostic():
    """Executa diagnóstico completo do sistema"""
    
    print("="*60)
    print(" DIAGNÓSTICO COMPLETO DO SISTEMA ".center(60, "="))
    print("="*60 + "\n")
    
    # 1. Relatório de saúde
    report = device_manager.get_system_health_report()
    
    print(f"⏱️ Uptime: {report['uptime_seconds'] // 3600} horas")
    print(f"📊 Processos: {report['processes_count']}\n")
    
    # 2. Alertas
    if report['alerts']:
        print("⚠️ ALERTAS:")
        for alert in report['alerts']:
            print(f"  {alert}")
        print()
    
    # 3. Disco
    print("💾 DISCOS:")
    for disk in report['system_info']['disk']:
        status = "⚠️" if disk['percent'] > 90 else "✅"
        print(f"  {status} {disk['mountpoint']}: {disk['percent']}% usado ({disk['free_gb']:.1f} GB livre)")
    print()
    
    # 4. Rede
    network = report['system_info']['network']
    print(f"🌐 REDE:")
    print(f"  Interfaces: {len(network['interfaces'])}")
    print(f"  Conexões ativas: {len(network['connections'])}")
    stats = network['stats']
    print(f"  Tráfego enviado: {stats['bytes_sent'] / (1024**2):.2f} MB")
    print(f"  Tráfego recebido: {stats['bytes_recv'] / (1024**2):.2f} MB\n")
    
    # 5. GPU
    gpus = report['system_info']['gpu']
    if gpus:
        print("🎮 GPU:")
        for gpu in gpus:
            print(f"  - {gpu['name']}: {gpu['status']}")
    print()
    
    # 6. Bateria
    battery = report['system_info']['battery']
    if battery:
        print(f"🔋 BATERIA:")
        print(f"  Carga: {battery['percent']}%")
        print(f"  Carregando: {'Sim' if battery['plugged'] else 'Não'}")
        if battery['time_left_seconds']:
            print(f"  Tempo restante: {battery['time_left_seconds'] // 60} min")
    
    # 7. Exporta relatório
    device_manager.export_system_report()
    print("\n✅ Relatório completo exportado para data/system_reports/")
    
    print("\n" + "="*60)

system_diagnostic()
```

---

## 🔒 Segurança

### Privilégios Administrativos

Muitas operações requerem privilégios administrativos:

**Requer Admin:**
- ❌ Modificar serviços Windows
- ❌ Modificar firewall
- ❌ Desabilitar interfaces de rede
- ❌ Desfragmentação de disco
- ❌ Alguns registros em HKLM

**Não Requer Admin:**
- ✅ Monitoramento de hardware
- ✅ Listar processos
- ✅ Controle de volume/brilho
- ✅ Abrir navegador
- ✅ Ler registro (maioria)

### Verificando Privilégios

```python
if device_manager.is_admin:
    print("✅ Executando como administrador")
else:
    print("⚠️ Executando sem privilégios administrativos")
    print("Solicitando elevação...")
    device_manager.request_admin_elevation()  # Reinicia com UAC
```

### Backup Automático

O Device Manager faz backup automático antes de modificar o registro:

```python
# Backup é feito automaticamente
device_manager.write_registry(
    hive=winreg.HKEY_CURRENT_USER,
    key_path=r"Software\MyApp",
    value_name="config",
    value="new_value",
    backup=True  # Salva em data/registry_backups/
)
```

### Auditoria

Todas as operações críticas são logadas:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Logs automáticos:
# INFO: 💡 Brilho ajustado para 50%
# WARNING: ⚠️ Sem permissão para modificar registro
# ERROR: ❌ Falha ao encerrar processo 1234
```

---

## 🔧 Troubleshooting

### Problema: "screen_brightness_control não instalado"

```bash
pip install screen-brightness-control
```

Se ainda falhar, o controle de brilho pode não ser suportado pelo hardware.

### Problema: "WMI não disponível"

```bash
pip install WMI
```

WMI é específico para Windows. Em Linux, muitas funções usarão fallbacks.

### Problema: "pywin32 não disponível"

```bash
pip install pywin32
# Depois execute:
python -m pywin32_postinstall -install
```

### Problema: "pycaw não disponível"

```bash
pip install pycaw
pip install comtypes
```

### Problema: "Acesso negado ao listar processos"

Execute como administrador ou alguns processos do sistema não serão visíveis.

### Problema: "UAC bloqueia operações"

```python
# Solicita elevação
device_manager.request_admin_elevation()
# Nota: Reiniciará o script com privilégios elevados
```

### Problema: "Timeout ao modificar serviços"

Alguns serviços podem demorar muito para parar/iniciar. Aumente o timeout:

```python
# Modificar timeout interno (avançado)
import subprocess
result = subprocess.run(
    ['net', 'stop', 'SomeService'],
    capture_output=True,
    timeout=60  # 60 segundos
)
```

---

## 📊 Performance

### Benchmarks

```python
import time

# Benchmark: get_system_info()
start = time.time()
info = device_manager.get_system_info()
print(f"get_system_info(): {(time.time() - start) * 1000:.2f} ms")
# Típico: ~50-200ms

# Benchmark: list_processes()
start = time.time()
processes = device_manager.list_processes()
print(f"list_processes(): {(time.time() - start) * 1000:.2f} ms")
# Típico: ~100-500ms (depende do número de processos)

# Benchmark: network info
start = time.time()
network = device_manager.get_network_info()
print(f"get_network_info(): {(time.time() - start) * 1000:.2f} ms")
# Típico: ~50-150ms
```

### Otimização

```python
# Evite chamar get_system_info() em loop apertado
# Use cache ou intervalo de atualização:

import time
last_update = 0
cached_info = None

def get_cached_system_info(cache_duration=5):
    """Cache de 5 segundos"""
    global last_update, cached_info
    now = time.time()
    
    if now - last_update > cache_duration:
        cached_info = device_manager.get_system_info()
        last_update = now
    
    return cached_info
```

---

## 🎓 Best Practices

1. **Sempre verifique privilégios antes de operações críticas**
   ```python
   if device_manager.is_admin:
       device_manager.control_service(...)
   else:
       print("Requer admin!")
   ```

2. **Use try-except para operações que podem falhar**
   ```python
   try:
       device_manager.kill_process(pid)
   except Exception as e:
       logger.error(f"Falha ao matar processo: {e}")
   ```

3. **Faça backup antes de modificar registro**
   ```python
   device_manager.write_registry(..., backup=True)
   ```

4. **Use timeouts para operações de bloqueio**
   ```python
   device_manager.restart(timeout=60)  # 1 minuto de aviso
   ```

5. **Documente operações críticas**
   ```python
   logger.info("Modificando plano de energia para jogos")
   device_manager.set_power_plan(PowerPlan.HIGH_PERFORMANCE)
   ```

6. **Teste em ambiente seguro primeiro**
   - Nunca teste em produção
   - Use VMs para testar operações de sistema
   - Sempre tenha backup do registro

---

## 📝 Changelog

### v2.0.0 (2026-02-08) - Current

✨ **New Features:**
- Controle completo de rede (interfaces, firewall, bandwidth)
- Power management (shutdown, sleep, hibernate, power plans)
- Windows Registry (read/write/delete com backup)
- Windows Services (list/control/dependencies)
- Display avançado (resolução, multi-monitor)
- Disk health (S.M.A.R.T., space analysis, defrag)
- Security (privileges, UAC, admin checks)
- Process management (priority, kill, detailed info)
- System health reports com exportação JSON

🔧 **Improvements:**
- Graceful degradation para dependências opcionais
- Logging robusto de todas as operações
- Backup automático antes de modificar registro
- Error handling aprimorado

### v1.0.0 (2026-02-05) - Legacy

- Controle básico de brilho
- Controle básico de volume
- Abertura de navegador

---

## 🤝 Contribuindo

Para adicionar novas funcionalidades ao Device Manager:

1. Mantenha padrão de nomenclatura consistente
2. Adicione docstrings detalhadas
3. Implemente error handling robusto
4. Adicione logs informativos
5. Teste em Windows 10 e 11
6. Documente em `DEVICE_MANAGER.md`

---

## 📄 Licença

Parte do projeto JARVIS 5.0 - Todos os direitos reservados.

---

**JARVIS Advanced Device Manager** - God Mode para Windows 🚀
