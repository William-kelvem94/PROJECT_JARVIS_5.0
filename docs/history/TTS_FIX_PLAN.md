# 🔧 PLANO DE CORREÇÃO - TTS XML/SSML Bug

## 📋 PROBLEMA IDENTIFICADO

**Sintoma relatado pelo usuário:**
- JARVIS falando XML literalmente: "Cruzolhe Voice Spik"
- Falando namespaces: "XMLNS igual HTTPWWW ponto W 3 ponto org 2001 10 sindesis XML Speak vergio"
- Sistema não entende comandos
- Processamento falha continuamente

**Causas raiz identificadas:**

### 1. **Pygame Mixer Desligando** (CRÍTICO)
```
pygame.error: mixer not initialized
```
- pygame.mixer não está inicializado ou se desliga durante execução
- Edge-TTS tenta usar mixer desligado
- Exception lança fallback para offline
- **MAS**: texto pode conter resíduos de SSML

### 2. **Limpeza de SSML Insuficiente**
- `strip_ssml()` só removia tags `<...>`
- Não removia atributos XML soltos: `xmlns=`, `xml:lang=`, `version=`
- Se edge-tts falhava, SSML ia para pyttsx3

### 3. **Falta de Logging Detalhado**
- Sem logs indicando qual TTS estava sendo usado
- Sem traceback completo de falhas
- Difícil diagnosticar qual parte falhava

---

## ✅ CORREÇÕES APLICADAS

### 1. **Proteção Tripla contra SSML** ✅
```python
# voice_controller.py (linha 185)
def speak(self, text: str, mode: str = 'auto', wait: bool = False):
    text = self.clean_text_for_speech(text)  # Limpa caminhos/URLs
    text = self.strip_ssml(text)  # 🆕 LIMPA SSML ANTES de tudo
    if not text or not text.strip(): return
    ...
```

```python
# voice_controller.py (linha 282)
def _speak_thread(self, text: str, mode: str):
    text = self.strip_ssml(text)  # 🆕 SEGUNDA limpeza
    if not text or not text.strip():
        logger.warning("⚠️ Texto vazio após limpeza SSML, abortando speak")
        return
    ...
```

```python
# voice_controller.py (linha 323)
# --- PROVEDOR OFFLINE (Fallback / Forced) ---
clean_text = self.strip_ssml(text)  # 🆕 TERCEIRA limpeza (fallback)
if not clean_text or not clean_text.strip():
    logger.warning("⚠️ Texto vazio após strip_ssml no offline")
    return
logger.debug(f"🔊 TTS Offline (pyttsx3): '{clean_text[:50]}...'")
...
```

### 2. **Limpeza Robusta de SSML** ✅
```python
# voice_controller.py (linha 267)
def strip_ssml(self, text: str) -> str:
    """Remove tags XML/SSML para que o TTS não as leia literalmente"""
    if not text:
        return ""
    # Remove tags XML/SSML completas
    text = re.sub(r'<[^>]+>', '', text)
    # 🆕 Remove namespaces e atributos XML que ficaram soltos
    text = re.sub(r'xmlns\s*=\s*["\'][^"\']+["\']', '', text)
    text = re.sub(r'xml:lang\s*=\s*["\'][^"\']+["\']', '', text)
    text = re.sub(r'version\s*=\s*["\'][^"\']+["\']', '', text)
    # Limpar espaços múltiplos
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

### 3. **Pygame Mixer Proteção** ✅
```python
# voice_controller.py (linha 118)
try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        logger.info("✅ Pygame mixer inicializado")
except Exception as e:
    logger.warning(f"⚠️ Falha ao inicializar pygame mixer: {e}")
    PYGAME_AVAILABLE = False
```

```python
# voice_controller.py (linha 410)
# 🆕 Verificar se mixer está initialized
if not pygame.mixer.get_init():
    logger.warning("⚠️ Pygame mixer não inicializado, tentando reinicializar...")
    try:
        pygame.mixer.init()
    except Exception as init_e:
        logger.error(f"❌ Falha ao reinicializar pygame: {init_e}")
        raise  # Cair no fallback offline
```

### 4. **Logging Detalhado** ✅
```python
# Logs adicionados:
logger.debug(f"🔊 TTS Edge: '{text[:50]}...'")
logger.debug(f"🔊 TTS Google: '{text[:50]}...'")
logger.debug(f"🔊 TTS Offline (pyttsx3): '{clean_text[:50]}...'")
logger.error(f"❌ Erro no TTS Online ({self.tts_provider}): {e}")
logger.error(f"❌ Falha no Edge-TTS SSML processing: {e}")
logger.error(traceback.format_exc())
```

### 5. **Exception Handling Robusto** ✅
```python
# voice_controller.py (linha 438)
try:
    communicate = edge_tts.Communicate(ssml, voice)
    ...
except Exception as e:
    logger.error(f"❌ Falha no Edge-TTS SSML processing: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise  # Re-raise para cair no fallback offline
```

---

## 🧪 PLANO DE TESTE

### Teste 1: **Verificar limpeza de SSML**
```python
# Simular texto com SSML
test_ssml = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
    <voice name="pt-BR-AntonioNeural">
        <prosody pitch="+0Hz" rate="+0%" volume="+0%">
            Olá, como você está?
        </prosody>
    </voice>
</speak>
"""
# Após strip_ssml(): "Olá, como você está?"
```

### Teste 2: **Pygame Mixer Resilience**
1. Desligar pygame.mixer durante execução
2. Tentar falar
3. Verificar se re-inicializa ou cai no offline graciosamente

### Teste 3: **Comandos de voz**
- "Jarvis, que horas são?"
- "Jarvis, como você está?"
- "Jarvis, abra o navegador"

**Verificar:**
- ✅ Fala SEM XML/SSML literalmente
- ✅ Respostas coerentes
- ✅ Logs indicando qual TTS foi usado
- ✅ Fallback offline funciona se edge-tts falhar

---

## 📊 LOGS ESPERADOS

### ✅ Sucesso (Edge-TTS):
```
2026-02-09 XX:XX:XX - voice_controller - DEBUG - 🔊 TTS Edge: 'Olá, como posso ajudar?'
2026-02-09 XX:XX:XX - voice_controller - INFO - ✅ Pygame mixer inicializado
```

### ✅ Sucesso (Fallback Offline):
```
2026-02-09 XX:XX:XX - voice_controller - ERROR - ❌ Erro no TTS Online (edge): mixer not initialized
2026-02-09 XX:XX:XX - voice_controller - DEBUG - 🔊 TTS Offline (pyttsx3): 'Olá, como posso ajudar?'
```

### ❌ Falha (XML sendo falado - NÃO DEVE ACONTECER MAIS):
```
2026-02-09 XX:XX:XX - voice_controller - DEBUG - 🔊 TTS Offline (pyttsx3): '<speak version 1.0 xmlns http...'
```

---

## 🔄 PRÓXIMOS PASSOS

1. ✅ Correções aplicadas ao código
2. ⏱️ **TESTAR** sistema por 3-5 minutos
3. 🎤 **COMANDOS DE VOZ** - verificar se fala XML
4. 📊 **ANALISAR LOGS** - buscar por:
   - "🔊 TTS Edge" ou "🔊 TTS Offline"
   - Se aparecer XML nos logs de Offline
   - Erros de pygame mixer
5. 📝 **DOCUMENTAR** resultado final

---

## 🎯 CRITÉRIO DE SUCESSO

### Implementado e Validado:
- [x] Sistema roda por 5+ minutos sem crashes - ✅ **VALIDADO** (5.2min sem crashes - 09/02/2026 11:08)

### Implementado, Pendente de Teste de Voz:
- [ ] JARVIS fala texto limpo (SEM XML/SSML) - ⚙️ **CÓDIGO IMPLEMENTADO** → Testar com comando de voz
- [ ] Pygame mixer inicializa corretamente - ⚙️ **CÓDIGO IMPLEMENTADO** → Verificar logs na inicialização  
- [ ] Fallback offline funciona sem falar XML - ⚙️ **CÓDIGO IMPLEMENTADO** → Forçar offline e testar
- [ ] Logs detalhados mostram qual TTS foi usado - ⚙️ **CÓDIGO IMPLEMENTADO** → Verificar `🔊 TTS Edge/Offline` nos logs
- [ ] Comandos de voz são processados corretamente - ⚙️ **CÓDIGO IMPLEMENTADO** → Enviar comando e validar resposta

---

## 🧪 COMO VALIDAR OS 5 ITENS PENDENTES

1. **Falar comando para JARVIS** (ex: "Jarvis, que horas são?")
2. **Verificar nos logs:**
   ```
   grep -E "🔊 TTS|strip_ssml|pygame.mixer" logs/jarvis.log
   ```
3. **Confirmar que:**
   - Resposta NÃO contém XML/SSML (<speak>, xmlns, etc)
   - Log mostra `🔊 TTS Edge: 'texto limpo'` OU `🔊 TTS Offline: 'texto limpo'`
   - Pygame mixer inicializado: `✅ Pygame mixer inicializado`
   - Resposta é coerente e completa

---

**Data:** 09/02/2026 11:10
**Status:** ⏳ Aguardando validação de TTS com comando de voz
**Responsável:** AI Assistant (GitHub Copilot)
