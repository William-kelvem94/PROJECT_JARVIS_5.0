# 🚀 Primeiros Passos - Leitor de Tela Inteligente

Bem-vindo ao Leitor de Tela Inteligente! Este guia irá ajudá-lo a começar a usar a ferramenta rapidamente.

## 📋 O que é o Leitor de Tela?

O Leitor de Tela é uma ferramenta que **lê a tela do seu computador** e **extrai dados inteligentes** de qualquer conteúdo visual. Ideal para:

- 📄 **Digitalizar documentos** sem scanner
- 📊 **Extrair dados** de sistemas antigos
- 🧾 **Ler notas fiscais** e recibos
- 📝 **Capturar formulários** preenchidos
- 📈 **Analisar relatórios** automaticamente

**Funciona 100% local** - seus dados nunca saem do seu computador!

## 🎯 Seu Primeiro Uso

### 1. Iniciar a Aplicação

```bash
# Interface gráfica (recomendado)
python main.py

# Ou linha de comando
python main.py --help
```

### 2. Fazer Primeira Captura

1. **Abra a aplicação**
2. **Clique no botão** 📸 **"Capturar Tela"**
3. **Selecione a área** da tela que contém dados
4. **Aguarde** o processamento automático

### 3. Ver Resultados

Após a captura, você verá:
- **Imagem capturada** na aba "Visualização"
- **Texto extraído** na aba "OCR"
- **Dados organizados** na aba "Dados Extraídos"

## 📸 Como Capturar Dados

### Captura Básica

1. **Posicione** o conteúdo na tela
2. **Clique** 📸 **"Capturar Tela"**
3. **Aguarde** o processamento (alguns segundos)

### Captura de Área Específica

1. **Clique** 🎯 **"Selecionar Área"**
2. **Clique e arraste** para selecionar a região
3. **Solte** para confirmar

### Captura Automática

```bash
# Captura a cada 30 segundos por 5 minutos
python main.py capture --timer 30 --max-captures 10 --process
```

## 🔍 Entendendo os Resultados

### Aba "Visualização"
- Mostra a **imagem capturada**
- Permite **visualizar** o que foi lido

### Aba "OCR"
- Contém o **texto bruto** extraído
- Permite **copiar** ou **salvar** o texto
- Mostra **qualidade** da extração

### Aba "Dados Extraídos"
- **Dados inteligentes** encontrados
- **Campos estruturados** (CPF, valores, datas)
- **Categoria** do documento
- **Confiança** de cada extração

## 💾 Exportando Dados

### Formatos Disponíveis

1. **JSON** - Dados estruturados completos
2. **CSV** - Planilha simples
3. **Excel** - Planilha avançada
4. **PDF** - Relatório formatado
5. **TXT** - Texto puro

### Como Exportar

1. **Selecione** uma captura processada
2. **Clique** 💾 **"Exportar"**
3. **Escolha** o formato desejado
4. **Salve** no local preferido

## 🛠️ Exemplos Práticos

### Exemplo 1: Extrair dados de uma nota fiscal

```bash
# 1. Abra o PDF da NF na tela
# 2. Capture a área da NF
python main.py capture --process --analyze

# Resultado: Dados estruturados da nota fiscal
```

### Exemplo 2: Digitalizar formulários

```bash
# Processar múltiplos formulários
python main.py batch --input-dir ./formularios/ --analyze --export --format excel
```

### Exemplo 3: Monitorar dados em tempo real

```bash
# Captura automática para dashboards
python main.py capture --timer 60 --window "Dashboard" --process --export --format json
```

## ⚙️ Configurações Essenciais

### Tema da Interface
```json
{
  "interface": {
    "theme": "dark"
  }
}
```

### Qualidade de Captura
```json
{
  "capture": {
    "quality": 95,
    "format": "PNG"
  }
}
```

### Engine OCR
```json
{
  "ocr": {
    "engine": "tesseract",
    "languages": ["por", "eng"]
  }
}
```

## 🔧 Solução de Problemas Comuns

### "Texto não foi extraído corretamente"
- ✅ Verifique se a imagem está nítida
- ✅ Aumente o zoom da tela
- ✅ Use o engine EasyOCR: `"ocr": {"engine": "easyocr"}`

### "Captura não funcionou"
- ✅ Feche outras aplicações que usam captura de tela
- ✅ Execute como administrador
- ✅ Verifique se há antivírus bloqueando

### "Aplicação não abre"
- ✅ Verifique se Python está no PATH
- ✅ Instale dependências: `pip install -r requirements.txt`
- ✅ Execute: `python main.py`

### "Dados não foram organizados"
- ✅ Certifique-se de que o texto foi extraído
- ✅ Verifique configurações de análise
- ✅ Reinicie a aplicação

## 📚 Próximos Passos

### Aprenda Mais
- [Funcionalidades Avançadas](advanced_features.md)
- [Configurações Avançadas](configuration.md)
- [API de Integração](api.md)

### Exemplos Avançados
- **Automação:** Scripts para processamento contínuo
- **Integração:** Conectar com outros sistemas
- **Personalização:** Criar padrões customizados

### Dicas Profissionais
- Use **atalhos de teclado** para agilidade
- Configure **captura automática** para tarefas repetitivas
- **Categorize** seus documentos para melhor organização
- **Exporte regularmente** para backup

## 🎯 Casos de Uso Recomendados

### Para Empresas
- ✅ Extração de dados de ERPs antigos
- ✅ Digitalização de documentos físicos
- ✅ Automação de entrada de dados
- ✅ Validação de formulários

### Para Profissionais
- ✅ Organização de recibos e notas fiscais
- ✅ Extração de dados de contratos
- ✅ Análise de relatórios financeiros
- ✅ Captura de informações de sistemas web

### Para Pessoal
- ✅ Organização de documentos pessoais
- ✅ Backup de informações importantes
- ✅ Extração de dados de emails
- ✅ Digitalização rápida de recibos

## 💡 Dicas de Produtividade

1. **Configure atalhos:** `Ctrl+Shift+S` para captura rápida
2. **Use modo batch:** Processe múltiplas imagens de uma vez
3. **Categorize automaticamente:** Deixe a IA classificar seus documentos
4. **Exporte regularmente:** Mantenha backups organizados
5. **Monitore janelas específicas:** Automatize captura de aplicações importantes

## 🚀 Indo Além

Pronto para funcionalidades avançadas?

- [Análise Inteligente](advanced_features.md#análise-inteligente)
- [Integração com APIs](api.md)
- [Criação de Plugins](plugins.md)
- [Automação Avançada](automation.md)

---

**🎉 Parabéns! Você já sabe o básico do Leitor de Tela Inteligente.**

**Explore as funcionalidades avançadas e torne-se um especialista em extração de dados visuais!**
