# 📂 JARVIS 5.0 - Demos e Exemplos

**NOTA: Todos os arquivos funcionais foram movidos para seus módulos apropriados em `src/core/`**

Esta pasta agora contém apenas:
- Scripts de exemplo não funcionais
- Protótipos abandonados
- Documentação de conceitos

## 📋 Status dos Arquivos Anteriores

### ✅ **MOVIDOS E RENOMEADOS PARA `src/core/`** (Funcionalidades Reais)

| Arquivo Original | Novo Local | Status |
|------------------|------------|--------|
| `demo_auto_recovery.py` | `src/core/management/auto_recovery_demo.py` | ✅ Sistema funcional |
| `isolated_demo_auto_recovery.py` | `src/core/management/isolated_auto_recovery.py` | ✅ Demo isolado funcional |
| `quick_demo_auto_recovery.py` | `src/core/management/quick_auto_recovery.py` | ✅ Demo rápido funcional |
| `demo_distributed_recovery.py` | `src/core/network_mesh/distributed_recovery_system.py` | ✅ Sistema distribuído funcional |
| `demo_predictive_analytics.py` | `src/core/analytics/predictive_analytics_system.py` | ✅ Sistema de analytics funcional |
| `democratic_integration_example.py` | `src/core/democratic_integration.py` | ✅ **INTEGRAÇÃO COMPLETA FUNCIONAL** |

### 🎯 **Para Executar os Sistemas Agora:**

```bash
# Sistema de Auto-Recovery
python src/core/management/auto_recovery_demo.py
python src/core/management/quick_auto_recovery.py

# Sistema Distribuído de Recovery
python src/core/network_mesh/distributed_recovery_system.py

# Sistema de Analytics Preditivo
python src/core/analytics/predictive_analytics_system.py

# Integração Democrática (Sistema Completo)
python src/core/democratic_integration.py
```

### 🏛️ **Integração Democrática Completa**

O arquivo `democratic_integration_example.py` foi transformado em `src/core/democratic_integration.py` - **um sistema funcional completo** que inclui:

- ✅ **Integração democrática real** no JARVIS
- ✅ **Gerenciamento de perfis democráticos** (`conservative`, `balanced`, `aggressive`, `development`, `production`)
- ✅ **Controle de modo democrático** com ativação/desativação
- ✅ **Integração com sistemas distribuídos**
- ✅ **Validação e teste automático**
- ✅ **Compatibilidade com main.py**
- ✅ **Argumentos CLI completos** (`--activate-democratic`, `--deactivate-democratic`, `--democratic-status`)
- ✅ **Implementações mock** para funcionamento independente

**Para usar no main.py:**
```python
from src.core.democratic_integration import JarvisWithDemocraticCapabilities, handle_democratic_cli_args

# Substituir criação do JARVIS
jarvis = JarvisWithDemocraticCapabilities(JarvisSingularity(app, instances))
await jarvis.start_with_democratic_check()
```

**Para usar via linha de comando:**
```bash
# Verificar status democrático
python src/core/democratic_integration.py --democratic-status

# Ativar modo democrático
python src/core/democratic_integration.py --activate-democratic --profile development

# Desativar modo democrático
python src/core/democratic_integration.py --deactivate-democratic
```

## 📖 Sobre a Reorganização

Os "demos" eram na verdade **implementações funcionais completas** que foram integradas como módulos reais do sistema JARVIS 5.0. Não há mais "demos" - apenas **funcionalidades reais** organizadas corretamente na arquitetura do sistema.