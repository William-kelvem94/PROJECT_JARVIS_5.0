# 🎤 JARVIS 5.0 - Comandos de Voz

**Guia Completo de Comandos por Voz**

---

## 🎯 Comandos Básicos

### Ativação e Saudações

| Comando | Resposta Esperada | Categoria |
|---------|-------------------|-----------|
| `Olá JARVIS` | "Sim, senhor. Como posso ajudar?" | Ativação |
| `Oi JARVIS` | "Às suas ordens, William." | Ativação |
| `Bom dia JARVIS` | "Bom dia, senhor. Sistemas operacionais ativos." | Saudação |
| `Obrigado JARVIS` | "Por nada, senhor." / "Disponha sempre." | Agradecimento |

---

## 💻 Controle de Programas

### Abrir Aplicações

```
"Abrir Chrome"
"Abrir Firefox"
"Abrir Notepad"
"Abrir Calculator"
"Abrir Spotify"
"Abrir VSCode"
"Abrir Discord"
```

### Fechar Aplicações

```
"Fechar Chrome"
"Fechar [nome do programa]"
```

---

## 🌐 Pesquisa e Informação

### Pesquisa Web

```
"Pesquise sobre Python"
"Busque notícias do Brasil"
"Procure receitas de bolo"
"Google: inteligência artificial"
```

### Informações Rápidas

```
"Que horas são?"
"Qual a data de hoje?"
"Como está o clima?"
```

---

## 🎛️ Controle de Sistema

### Volume

```
"Aumentar volume"
"Diminuir volume"
"Volume em 50%"
"Volume máximo"
"Silenciar"
```

### Brilho

```
"Aumentar brilho"
"Diminuir brilho"
"Brilho em 70%"
"Brilho máximo"
"Brilho mínimo"
```

### Energia

```
"Desligar o computador"
"Reiniciar o sistema"
"Suspender"
"Hibernar"
```

---

## 📁 Gerenciamento de Arquivos

### Navegação

```
"Abrir pasta Downloads"
"Abrir Documentos"
"Mostrar Desktop"
```

### Operações

```
"Criar pasta [nome]"
"Ler arquivo [caminho]"
"Listar arquivos em [pasta]"
```

---

## 🧠 Comandos de IA e Aprendizado

### Status

```
"Status do sistema"
"Como estão os sistemas?"
"Checkup do sistema"
```

### Aprendizado (Experimental)

```
"Estude sobre [tópico]"
"Treine por 30 minutos"
"Aprenda programação"
```

Esses comandos ativam o sistema de aprendizado autônomo.

---

## 📷 Visão e Reconhecimento

### FaceID

```
"Cadastrar meu rosto"
"Cadastrar rosto de [nome]"
"Quem sou eu?"
"Me reconheça"
```

### Análise Visual

```
"O que você está vendo?"
"Descreva a tela"
"Há algum erro na tela?"
```

---

## 🎵 Multimídia

### Música

```
"Tocar música"
"Ouvir [artista/música]"
"Pausar música"
"Próxima música"
```

### Vídeo

```
"Abrir YouTube"
"Buscar [vídeo] no YouTube"
```

---

## 🤖 Automação

### Scripts Personalizados

Você pode criar seus próprios comandos em:
`data/generated_scripts/`

Exemplo:
```python
# meu_comando.py
def executar():
    # Seu código aqui
    pass
```

Depois diga:
```
"Executar meu comando"
```

---

## ⚙️ Configuração de Voz

### Ajustar no Dashboard

1. Control Dashboard → **Voice** tab
2. Configurações disponíveis:
   - **STT Model:** faster-whisper (padrão)
   - **TTS Engine:** pyttsx3 ou elevenlabs
   - **VAD (Voice Activity Detection):** On/Off
   - **Speaker Verification:** On/Off

### Parâmetros Avançados

**Arquivo:** `config/ai_config.yaml`

```yaml
voice:
  stt:
    model: "faster-whisper"
    language: "pt"
    vad_threshold: 0.5
  tts:
    engine: "pyttsx3"
    voice: "pt-BR"
    rate: 150
```

---

## 🎯 Dicas de Uso

### Para Melhor Reconhecimento

1. **Fale claramente** e em ritmo normal
2. **Evite ruído de fundo** (use VAD)
3. **Diga "JARVIS"** antes do comando para ativar
4. **Espere resposta** antes do próximo comando

### Comandos Compostos

Você pode encadear comandos:
```
"JARVIS, abra o Chrome e pesquise sobre Python"
```

JARVIS executará:
1. Abrir Chrome
2. Fazer pesquisa no Google

---

## 📊 Feedback e Aprendizado

### Ensinar Novos Comandos

Se JARVIS não entender:

1. Dashboard → **Learning** tab
2. Dê feedback **👎 Bad Response**
3. Campo de correção: Explique o que deveria fazer
4. **Submit Correction**

Após ~100 interações, o sistema aprende automaticamente!

---

## 🔧 Solução de Problemas

### "JARVIS não responde"

**Verificar:**
- Microfone conectado?
- Dashboard → Voice → Microfone selecionado?
- VAD ativado? (pode estar bloqueando)

### "Reconhecimento ruim"

**Soluções:**
1. Trocar modelo STT para `whisper-large`
2. Aumentar VAD threshold (0.5 → 0.7)
3. Usar headset ao invés de microfone de mesa

### "Comando não executado"

**Motivos:**
- Comando não está na lista (ensine!)
- Permissões insuficientes (execute como Admin)
- Programa não instalado

---

## 📚 Comandos em Desenvolvimento

Futuros comandos planejados:

- [ ] Controle de IoT (lâmpadas, ar condicionado)
- [ ] Integração com agenda/calendário
- [ ] Envio de emails por voz
- [ ] Criação de lembretes
- [ ] Controle de streaming (Netflix, Prime)

---

## 🆘 Suporte

- **Problemas:** [troubleshooting.md](../maintenance/troubleshooting.md)
- **Configuração:** [installation.md](../getting-started/installation.md)
- **IA:** [learning-system.md](../ai-systems/learning-system.md)

---

<div align="center">

**Desenvolvido por JARVIS Development Team**

*Versão:* 5.0 Singularity

</div>
