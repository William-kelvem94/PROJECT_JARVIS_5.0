# 🤝 Guia de Contribuição - Leitor de Tela Inteligente

Bem-vindo! Este documento explica como contribuir para o desenvolvimento do Leitor de Tela Inteligente.

## 📋 Como Contribuir

### Tipos de Contribuição

- 🐛 **Relatar bugs** - Encontrou um problema? [Abra uma issue](https://github.com/username/leitor-tela/issues)
- 💡 **Sugerir funcionalidades** - Tem uma ideia? [Crie uma discussão](https://github.com/username/leitor-tela/discussions)
- 🔧 **Correções e melhorias** - Envie um pull request
- 📚 **Documentação** - Melhore guias e tutoriais
- 🧪 **Testes** - Adicione ou melhore cobertura de testes

## 🚀 Desenvolvimento

### Configuração do Ambiente

```bash
# 1. Fork e clone o repositório
git clone https://github.com/SEU_USERNAME/leitor-tela.git
cd leitor-tela

# 2. Criar branch para desenvolvimento
git checkout -b feature/nome-da-feature

# 3. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 4. Instalar dependências de desenvolvimento
pip install -r requirements.txt
pip install -e .[dev]

# 5. Instalar pre-commit hooks
pre-commit install
```

### Estrutura do Código

```
src/
├── core/              # Lógica principal
│   ├── screen_capture.py   # Captura de tela
│   ├── ocr_processor.py    # Processamento OCR
│   ├── data_analyzer.py    # Análise inteligente
│   └── data_organizer.py   # Organização de dados
├── gui/               # Interface gráfica
│   └── main_window.py      # Janela principal
├── database/          # Persistência
│   └── models.py           # Modelos SQLAlchemy
├── utils/             # Utilitários
│   ├── config.py           # Configurações
│   └── helpers.py          # Funções auxiliares
└── api/               # API REST (futuro)
```

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Testes com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_config.py -v

# Testes de integração
pytest -m integration

# Testes unitários apenas
pytest -m unit
```

### Escrever Testes

```python
# Exemplo de teste unitário
import pytest
from src.utils.helpers import TextHelper

class TestTextHelper:
    def test_clean_ocr_text(self):
        """Testa limpeza de texto OCR"""
        dirty_text = "Texto    com\n\nmuitos   espaços"
        cleaned = TextHelper.clean_ocr_text(dirty_text)

        assert "    " not in cleaned
        assert "\n\n" not in cleaned
        assert cleaned == "Texto com muitos espaços"
```

### Cobertura de Testes

Mantenha cobertura acima de 80%:
```bash
pytest --cov=src --cov-fail-under=80
```

## 📝 Padrões de Código

### Python Style Guide

Seguimos [PEP 8](https://www.python.org/dev/peps/pep-008/) com [Black](https://black.readthedocs.io/):

```bash
# Formatar código
black src/ tests/

# Verificar estilo
flake8 src/ tests/

# Verificar tipos (opcional)
mypy src/
```

### Commits

Use commits convencionais:

```bash
# Formato: tipo(escopo): descrição

# Exemplos
feat: adicionar suporte a novos formatos de exportação
fix: corrigir erro de captura em alta resolução
docs: atualizar guia de instalação
test: adicionar testes para validação de CPF
refactor: otimizar processamento OCR
```

### Branches

```bash
# Branches principais
main          # Código estável
develop       # Desenvolvimento ativo

# Branches de feature
feature/nome-da-feature
bugfix/descricao-do-bug
hotfix/correcao-critica

# Branches de release
release/v1.1.0
```

## 🔧 Pull Requests

### Antes de Enviar

1. ✅ **Testes passando**: `pytest`
2. ✅ **Código formatado**: `black .`
3. ✅ **Sem erros de lint**: `flake8 .`
4. ✅ **Documentação atualizada**
5. ✅ **Commits limpos e descritivos**

### Template de PR

```markdown
## Descrição
Breve descrição das mudanças

## Tipo de Mudança
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 💥 Breaking change
- [ ] 📚 Documentation
- [ ] 🎨 Style
- [ ] ♻️ Refactor

## Testes
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes manuais

## Checklist
- [ ] Meu código segue os padrões do projeto
- [ ] Eu testei as mudanças
- [ ] Documentação foi atualizada
- [ ] Mudanças são compatíveis com versões anteriores
```

## 🐛 Relatar Bugs

### Template de Issue

```markdown
**Descrição do Bug**
Descrição clara do problema

**Para Reproduzir**
Passos para reproduzir:
1. Ir para '...'
2. Clicar em '....'
3. Ver erro

**Comportamento Esperado**
O que deveria acontecer

**Screenshots**
Se aplicável, adicione screenshots

**Ambiente:**
- OS: [Windows 10]
- Python: [3.9.7]
- Versão: [1.0.0]

**Logs**
```
Cole logs relevantes aqui
```
```

## 💡 Sugerir Funcionalidades

### Template de Feature Request

```markdown
**Resumo**
Breve descrição da funcionalidade

**Problema**
Qual problema isso resolve?

**Solução Proposta**
Descrição da solução

**Alternativas Consideradas**
Outras soluções avaliadas

**Contexto Adicional**
Informações extras
```

## 📚 Documentação

### Atualizar Documentação

```bash
# Construir documentação (se usar Sphinx)
cd docs
make html

# Verificar links
make linkcheck
```

### Guias a Manter

- `README.md` - Visão geral e instalação rápida
- `docs/installation.md` - Instalação detalhada
- `docs/getting_started.md` - Primeiros passos
- `docs/advanced_features.md` - Recursos avançados
- `docs/api.md` - Documentação da API
- `docs/contributing.md` - Este arquivo

## 🔒 Segurança

### Relatar Vulnerabilidades

Para vulnerabilidades de segurança, **não abra issues públicas**. Entre em contato diretamente:
- Email: security@exemplo.com
- PGP Key: [link para chave]

## 📊 Métricas de Qualidade

### Code Quality Gates

- ✅ **Cobertura de testes**: > 80%
- ✅ **Complexidade ciclomática**: < 10
- ✅ **Duplicação de código**: < 5%
- ✅ **Dívida técnica**: Baixa

### Performance

- ⚡ **Tempo de inicialização**: < 5s
- 📸 **Captura de tela**: < 2s
- 🔍 **OCR básico**: < 10s
- 🧠 **Análise inteligente**: < 30s

## 🎯 Roadmap de Desenvolvimento

### Próximas Versões

#### v1.1.0 (Q1 2024)
- [ ] Suporte a macOS
- [ ] Melhorias na interface
- [ ] Novos formatos de exportação

#### v1.2.0 (Q2 2024)
- [ ] API REST completa
- [ ] Sistema de plugins
- [ ] Integração com Google Cloud Vision

#### v2.0.0 (Q3 2024)
- [ ] Suporte a Linux
- [ ] Processamento em lote avançado
- [ ] Machine Learning personalizado

## 🙏 Reconhecimento

Contribuições são reconhecidas em:
- Lista de contribuidores no README
- Seção de agradecimentos
- Release notes

### Níveis de Contribuição

- **🥉 Contribuidor** - 1+ commits aceitos
- **🥈 Colaborador** - 5+ commits, melhorias significativas
- **🥇 Mantenedor** - Responsável por áreas específicas

## 📞 Suporte

- 💬 **Discussões gerais**: [GitHub Discussions](https://github.com/username/leitor-tela/discussions)
- 🐛 **Problemas técnicos**: [GitHub Issues](https://github.com/username/leitor-tela/issues)
- 💡 **Ideias**: [GitHub Discussions - Ideas](https://github.com/username/leitor-tela/discussions/categories/ideas)

---

**Obrigado por contribuir para o Leitor de Tela Inteligente! 🚀**

Sua contribuição ajuda a tornar a ferramenta melhor para todos os usuários.
