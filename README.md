# JARVIS 5.0 - Assistente de Voz

Um assistente inteligente que responde a comandos de voz, similar a uma Alexa, mas rodando no seu computador.

## 🚀 Funcionalidades

- **Reconhecimento de voz** em português brasileiro
- **Síntese de voz** para respostas naturais
- **Execução de comandos do sistema**
- **Abertura de programas** comuns
- **Consultas de hora e data**
- **Calculadora integrada**
- **Pesquisa no Google**
- **Interface conversacional**

## 📋 Requisitos

- Python 3.8 ou superior
- Microfone funcional
- Conexão com internet (para reconhecimento de voz)
- Windows/Linux/MacOS

## 🛠️ Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o assistente:
   ```bash
   python main.py
   ```

## 🎯 Comandos Disponíveis

### Básicos
- **"Ajuda"** - Mostra todos os comandos disponíveis
- **"Sair"** - Encerra o assistente

### Sistema
- **"Abrir navegador"** - Abre o navegador padrão
- **"Abrir calculadora"** - Abre a calculadora
- **"Abrir bloco de notas"** - Abre o editor de texto
- **"Abrir explorer"** - Abre o explorador de arquivos

### Utilitários
- **"Que horas são?"** ou **"Hora"** - Diz a hora atual
- **"Que dia é hoje?"** ou **"Data"** - Diz a data atual
- **"Calcular 2 + 2"** - Faz cálculos matemáticos
- **"Pesquisar Python"** - Pesquisa no Google

### Avançado
- **"Executar dir"** - Executa comandos do sistema (use com cuidado!)

## 🔧 Como Funciona

1. **Reconhecimento**: O assistente usa Google Speech Recognition para converter sua fala em texto
2. **Processamento**: O texto é analisado para identificar comandos
3. **Execução**: Comandos são executados usando subprocess ou APIs do sistema
4. **Resposta**: O assistente responde verbalmente usando pyttsx3

## ⚙️ Configuração

O assistente é configurado automaticamente, mas você pode ajustar:

- **Velocidade da voz**: Modificar `rate` no código
- **Volume**: Ajustar `volume` no código
- **Idioma**: Alterar `language` para outros idiomas

## 🐛 Solução de Problemas

### Erro de microfone
- Verifique se o microfone está conectado e funcionando
- Teste o microfone em outras aplicações

### Erro de reconhecimento
- Verifique sua conexão com internet
- Fale claramente e próximo ao microfone
- Evite ruído de fundo

### Voz não funciona
- Instale codecs de áudio se necessário
- Verifique drivers de áudio

## 🔒 Segurança

- Use comandos de sistema com cuidado
- O assistente pode executar qualquer comando que você disser
- Não use em ambientes críticos sem supervisão

## 📈 Melhorias Futuras

- Integração com APIs de IA (ChatGPT, etc.)
- Reconhecimento offline
- Mais comandos personalizáveis
- Interface gráfica
- Suporte a múltiplos idiomas
- Controle de dispositivos IoT

## 🤝 Contribuição

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades!

## 📄 Licença

Este projeto é open source. Use por sua conta e risco.
