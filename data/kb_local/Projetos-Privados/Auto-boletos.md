---
title: "Auto-boletos (Clonado)"
source: "d:/Documents/GitHub/Auto-boletos"
language: Python
private: true
description: "Automação de boletos Equatorial com IA local, Flask, Docker e OCR."
updated: 2026-04-12
tags: [privados, python, flask, docker, ia, automacao]
---

# Auto-boletos [[../Projetos.md|Projetos]] [[GitHub-Completo]]

**Status**: 🏗️ Em Desenvolvimento
**Foco**: Automação crítica e processamento de documentos com IA.

## 🌐 Visão Geral (Pública)
Sistema moderno e completo que associa imóveis cadastrados aos dados oficiais da plataforma Equatorial Energy, com **Sistema de IA Local integrado** para análise de débitos e predição de consumo.

## 🛠️ Detalhes de Engenharia (Privado)
- **Backend**: Flask + SQLAlchemy (migrando para Neon DB).
- **Automação**: Playwright (Equatorial Facade) com CAPTCHA handling.
- **IA**: OCR Tesseract + Memória local (Ollama).
- **Frontend**: React/Vite com design responsivo (Tailwind).

## 🏗️ Estrutura
- `src/`: Lógica de automação e modelos de dados.
- `frontend/`: Dashboard de controle dos boletos.
- `docs/`: Documentação de infraestrutura e deployment.

**Links:** [[GitHub-Completo]] | [[skills/Skill-Project-Matrix|📊 Matriz Skills]] #flask #playwright #ocr #python
