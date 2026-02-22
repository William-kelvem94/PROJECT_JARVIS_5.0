# Scripts de Treinamento JARVIS 5.0

Esta pasta contém todos os scripts organizados para treinamento e verificação do JARVIS 5.0.

## 📁 Estrutura dos Scripts

### Treinamento Interativo
- `train_jarvis_fixed.py` - **RECOMENDADO** - Script completo com dashboard e logs em tempo real
- `train_jarvis.py` - Versão básica do treinamento interativo
- `start_training_interactive.py` - Versão alternativa interativa
- `start_training_with_dashboard.py` - Treinamento com dashboard básico

### Diagnóstico e Verificação
- `diagnostico_jarvis.py` - Diagnóstico completo do sistema
- `verificar_conhecimento.py` - **IMPORTANTE** - Demonstra que o treinamento é REAL
- `test_import.py` - Teste básico de imports

## 🚀 Como Usar

### 1. Treinar o JARVIS (Recomendado)
```bash
python scripts/training/train_jarvis_fixed.py
```

Este script:
- ✅ Pergunta qual tópico treinar
- ✅ Inicia dashboard web automaticamente
- ✅ Mostra logs em tempo real
- ✅ Salva dados de treinamento
- ✅ Funciona com qualquer assunto

### 2. Verificar Conhecimento Adquirido
```bash
python scripts/training/verificar_conhecimento.py
```

Este script demonstra que o treinamento é REAL:
- 📚 Mostra todos os tópicos aprendidos
- 🧠 Permite testar conhecimento
- 🤖 Prova que há rede neural funcionando
- 📊 Exibe dados salvos em disco

### 3. Diagnosticar Sistema
```bash
python scripts/training/diagnostico_jarvis.py
```

Verifica:
- 🌐 Status do web server
- 📊 Dados de treinamento
- 🔌 Conectividade WebSocket
- 📁 Arquivos gerados

## 🎯 Funcionalidades

### Treinamento Real (Não Simulação)
- ✅ Dados JSON estruturados salvos
- ✅ Sistema de destilação de conhecimento
- ✅ Logs detalhados de processamento
- ✅ Integração com modelos de IA
- ✅ Persistência de aprendizado

### Dashboard Web em Tempo Real
- 🌐 Interface cyberpunk
- 📈 Gráficos de telemetria
- 📝 Logs em tempo real via WebSocket
- 📚 Visualização de conhecimento adquirido
- ⏰ Relógio atualizado

### Flexibilidade Total
- 🎯 Qualquer tópico pode ser treinado
- 🔧 Múltiplos componentes (study, llm, vision, distributed)
- 📁 Dados salvos automaticamente
- 🔄 Sistema expansível

## 📊 O que o JARVIS Aprende

Quando você treina um tópico como "Python":

1. **Geração Automática**: Sistema cria exemplos de treinamento
2. **Destilação**: Conhecimento é processado e estruturado
3. **Persistência**: Dados salvos em `data/learning/training_data/`
4. **Integração**: Conhecimento fica disponível para o JARVIS usar

## 🌟 Exemplo de Uso

```bash
# 1. Treinar
python scripts/training/train_jarvis_fixed.py
# Digite: "Python programming"

# 2. Verificar aprendizado
python scripts/training/verificar_conhecimento.py
# Veja todos os tópicos aprendidos

# 3. Acessar dashboard
# Abra: http://localhost:5000 (ou 5001, 5002, 8000, 8001)
```

## 🔧 Resolução de Problemas

### Dashboard não carrega
- ✅ Script usa portas alternativas automaticamente
- ✅ Tente diferentes portas: 5000, 5001, 5002, 8000, 8001

### Logs não aparecem
- ✅ WebSocket configurado para transmitir logs
- ✅ Verifique se o navegador permite WebSocket
- ✅ Recarregue a página (F5)

### Treinamento falha
- ✅ Verifique se há espaço em disco
- ✅ Use `study` para começar (mais simples)
- ✅ Verifique logs de erro

## 🎉 Resultado Final

O JARVIS 5.0 agora tem:
- 🤖 Treinamento interativo real
- 📊 Dashboard cyberpunk funcional
- 🧠 Sistema de aprendizado comprovado
- 📚 Base de conhecimento expansível
- 🔄 Logs em tempo real
- 💾 Persistência de dados

**O treinamento é REAL, não simulação!** 🎯