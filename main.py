#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Assistente de Voz
Um assistente inteligente que responde a comandos de voz
"""

import speech_recognition as sr
import pyttsx3
import os
import subprocess
import sys
import platform
import json
import re
import tempfile
import time
from datetime import datetime

# Tentar importar gTTS e playsound para voz mais natural
try:
    from gtts import gTTS
    import playsound
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("gTTS não disponível, usando apenas pyttsx3")

class JarvisAssistant:
    def __init__(self):
        # Carregar configurações
        self.config = self.carregar_config()

        # Inicializar reconhecimento de fala
        self.recognizer = sr.Recognizer()

        # Inicializar síntese de voz
        self.engine = pyttsx3.init()
        self.use_gtts = GTTS_AVAILABLE  # Preferir gTTS quando disponível

        # Configurações aprimoradas para voz mais natural
        self.engine.setProperty('rate', self.config['voice']['rate'])
        self.engine.setProperty('volume', self.config['voice']['volume'])

        # Configurar voz em português se disponível (tentar vozes mais naturais)
        voices = self.engine.getProperty('voices')
        voz_portuguesa = None

        # Priorizar vozes femininas ou naturais em português
        for voice in voices:
            voice_name = voice.name.lower()
            if ('portuguese' in voice_name or 'pt' in voice_name or
                'brazil' in voice_name or 'br' in voice_name):
                if 'female' in voice_name or 'natural' in voice_name or voz_portuguesa is None:
                    voz_portuguesa = voice.id

        if voz_portuguesa:
            self.engine.setProperty('voice', voz_portuguesa)

        # Configurações adicionais para voz mais natural
        try:
            self.engine.setProperty('pitch', 50)  # Tom de voz mais natural
        except:
            pass  # Nem todas as engines suportam pitch

        # Debug: Inicialização voz - gTTS disponível: {GTTS_AVAILABLE}, use_gtts: {self.use_gtts}

        # Comandos disponíveis
        self.commands = {
            'abrir': self.abrir_programa,
            'executar': self.executar_comando,
            'fechar': self.fechar_programa,
            'hora': self.dizer_hora,
            'data': self.dizer_data,
            'sair': self.sair,
            'ajuda': self.mostrar_ajuda,
            'calcular': self.calcular,
            'pesquisar': self.pesquisar
        }

        print("JARVIS 5.0 inicializado. Diga 'ajuda' para ver os comandos disponíveis.")

    def carregar_config(self):
        """Carrega configurações do arquivo config.json"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuração padrão se arquivo não existir
            return {
                "voice": {
                    "rate": 180,
                    "volume": 0.9,
                    "language": "pt-BR"
                },
                "recognition": {
                    "timeout": 5,
                    "phrase_limit": 10
                },
                "system": {
                    "os": "auto"
                }
            }

    def falar(self, texto, velocidade=None, usar_expressoes=True, emocao=None, pausa_final=0.8):
        """Fala o texto fornecido de forma EXTREMAMENTE natural com controle de fluxo"""
        print(f"JARVIS: {texto}")

        # Debug: Fala ultra-natural - gTTS: {self.use_gtts}, texto: {len(texto)} chars, emocao: {emocao}

        # Pré-processar texto para naturalidade extrema
        texto_processado = self._preprocessar_para_naturalidade_extrema(texto, emocao)

        # Controle de fluxo conversacional - pausa antes de começar a falar
        self._pausa_conversacional_inicial()

        try:
            # Usar gTTS se disponível (voz muito mais natural)
            if self.use_gtts and self._deve_usar_gtts(texto_processado):
                self._falar_com_gtts_ultra_natural(texto_processado, usar_expressoes, emocao)
            else:
                # Fallback para pyttsx3 com melhorias ultra-naturais
                self._falar_com_pyttsx3_ultra_natural(texto_processado, velocidade, usar_expressoes, emocao)

            # Pausa final conversacional (muito importante!)
            time.sleep(pausa_final)

        except Exception as e:
            print(f"Erro na fala: {e}")
            # Mesmo com erro, manter pausa para não falar sem parar
            time.sleep(1.0)

    def _deve_usar_gtts(self, texto):
        """Decide se deve usar gTTS baseado no conteúdo"""
        # Usar gTTS para textos mais longos ou respostas principais
        return len(texto) > 50 or any(palavra in texto.lower() for palavra in ['olá', 'ajuda', 'erro', 'pronto'])

    def _falar_com_gtts_ultra_natural(self, texto, usar_expressoes=True, emocao=None):
        """Fala usando gTTS com naturalidade EXTREMA"""
        try:
            # Quebrar em frases ultra-inteligentes considerando respiração
            frases = self._quebrar_em_frases_ultra_inteligente(texto)

            for i, frase in enumerate(frases):
                # Pausas ultra-contextuais (simulando respiração humana)
                if i > 0:
                    pausa = self._calcular_pausa_ultra_natural(frase, frases[i-1] if i > 0 else "", emocao)
                    time.sleep(pausa)

                # Processar marcadores conversacionais
                frase, pausa_extra = self._processar_marcadores_conversacionais(frase)

                # Aplicar pausa extra se houver
                if pausa_extra > 0:
                    time.sleep(pausa_extra)

                # Detectar marcadores especiais
                if '[resp]' in frase:
                    # Pausa de respiração simulada
                    time.sleep(0.4)
                    frase = frase.replace('[resp]', '')

                # Criar arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_filename = temp_file.name

                # Configurar gTTS baseado na emoção
                slow = emocao in ['preocupado', 'pensativo']  # Mais devagar para emoções reflexivas
                tts = gTTS(text=frase, lang='pt-br', slow=slow)
                tts.save(temp_filename)

                # Reproduzir
                playsound.playsound(temp_filename)

                # Limpar arquivo temporário
                try:
                    os.unlink(temp_filename)
                except:
                    pass

        except Exception as e:
            # Debug: Erro gTTS ultra-natural, fallback para pyttsx3 - erro: {str(e)}
            # Fallback para pyttsx3
            self.use_gtts = False
            self._falar_com_pyttsx3_ultra_natural(texto, None, usar_expressoes, emocao)

    def _falar_com_pyttsx3_ultra_natural(self, texto, velocidade=None, usar_expressoes=True, emocao=None):
        """Fala usando pyttsx3 com naturalidade EXTREMA"""
        # Salvar configurações atuais
        velocidade_atual = self.engine.getProperty('rate')
        if velocidade is not None:
            self.engine.setProperty('rate', velocidade)

        # Quebrar texto em frases ultra-inteligentes
        frases = self._quebrar_em_frases_ultra_inteligente(texto)

        for i, frase in enumerate(frases):
            # Pausas ultra-naturais simulando respiração e pensamento
            if i > 0:
                pausa = self._calcular_pausa_ultra_natural(frase, frases[i-1] if i > 0 else "", emocao)
                time.sleep(pausa)

            # Processar marcadores conversacionais
            frase, pausa_extra = self._processar_marcadores_conversacionais(frase)

            # Aplicar pausa extra se houver
            if pausa_extra > 0:
                time.sleep(pausa_extra)

            # Detectar marcadores especiais
            pitch_modifier = 0
            volume_modifier = 0

            if '[resp]' in frase:
                # Pausa de respiração simulada
                time.sleep(0.4)
                frase = frase.replace('[resp]', '')
                pitch_modifier = 2  # Respiração = tom mais relaxado

            # Variação ultra-contextual de velocidade
            velocidade_frase = self._calcular_velocidade_ultra_contextual(frase, velocidade_atual, emocao)
            self.engine.setProperty('rate', velocidade_frase)

            # Variação ultra-sofisticada de pitch baseada em emoção e contexto
            try:
                pitch_base = 50 + pitch_modifier
                frase_lower = frase.lower()

                # Variação baseada em emoção
                if emocao == 'entusiasta':
                    pitch_base += 8
                    volume_modifier = 0.1
                elif emocao == 'preocupado':
                    pitch_base -= 5
                    volume_modifier = -0.05
                elif emocao == 'aliviado':
                    pitch_base += 3

                # Variação baseada em conteúdo
                if any(palavra in frase_lower for palavra in ['erro', 'ops', 'desculpe', 'problema']):
                    pitch_base -= 12  # Muito mais grave para erros
                    volume_modifier = -0.1
                elif any(palavra in frase_lower for palavra in ['pronto', 'feito', 'sucesso', 'ótimo']):
                    pitch_base += 6  # Mais animado para sucesso
                    volume_modifier = 0.05
                elif any(palavra in frase_lower for palavra in ['hmm', 'eh', 'tipo', 'ah']):
                    pitch_base -= 3  # Hesitação = tom mais baixo

                # Variação silábica para naturalidade
                pitch_variation = self._calcular_variacao_pitch_silabica(frase)
                pitch_base += pitch_variation

                self.engine.setProperty('pitch', pitch_base)

                # Ajustar volume se suportado
                try:
                    volume_atual = self.engine.getProperty('volume')
                    self.engine.setProperty('volume', max(0.1, min(1.0, volume_atual + volume_modifier)))
                except:
                    pass

            except:
                pass  # Nem todas as engines suportam pitch/volume

            self.engine.say(frase)
            self.engine.runAndWait()

        # Restaurar configurações
        self.engine.setProperty('rate', velocidade_atual)
        try:
            self.engine.setProperty('volume', self.config['voice']['volume'])
        except:
            pass

    def _preprocessar_para_naturalidade_extrema(self, texto, emocao=None):
        """Pré-processa texto para naturalidade EXTREMA com controle de fluxo"""
        texto = texto.lower()

        # Adicionar emoção se especificada
        if emocao:
            texto = self._adicionar_emocao_ao_texto(texto, emocao)

        # Adicionar fillers conversacionais ultra-naturais
        texto = self._adicionar_fillers_ultra_naturais(texto)

        # Adicionar hesitações simuladas
        texto = self._adicionar_hesitacoes_humanas(texto)

        # Adicionar respiração simulada
        texto = self._adicionar_respiracao_simulada(texto)

        # Adicionar marcadores conversacionais para controle de fluxo
        texto = self._adicionar_marcadores_conversacionais(texto)

        return texto

    def _adicionar_emocao_ao_texto(self, texto, emocao):
        """Adiciona elementos emocionais ao texto"""
        if emocao == 'entusiasta':
            return "Uau! " + texto + " Que legal, né?"
        elif emocao == 'preocupado':
            return "Ah... " + texto + " Será que está tudo bem?"
        elif emocao == 'aliviado':
            return "Ufa! " + texto + " Ainda bem!"
        elif emocao == 'pensativo':
            return "Hmm... " + texto
        return texto

    def _adicionar_fillers_ultra_naturais(self, texto):
        """Adiciona fillers conversacionais extremamente naturais"""
        import random

        fillers = {
            'inicio': ["Então, ", "Olha, ", "Tipo, ", "Sabe, ", "Ah, ", "Bom, "],
            'meio': ["né?", "tá?", "então", "tipo", "sabe", "né mesmo"],
            'longo': ["então quer dizer", "tipo assim", "sabe como é"]
        }

        # Adicionar filler no início (40% de chance)
        if random.random() < 0.4 and not texto.startswith(tuple(fillers['inicio'])):
            texto = random.choice(fillers['inicio']) + texto

        # Adicionar filler no meio para frases longas (25% de chance)
        if len(texto.split()) > 10 and random.random() < 0.25:
            palavras = texto.split()
            posicao = len(palavras) // 2
            filler_meio = random.choice(fillers['meio'])
            palavras.insert(posicao, filler_meio)
            texto = ' '.join(palavras)

        # Adicionar filler no final para perguntas (60% de chance)
        if '?' in texto and random.random() < 0.6:
            texto = texto.rstrip('?') + " " + random.choice(fillers['meio']) + "?"

        return texto

    def _adicionar_hesitacoes_humanas(self, texto):
        """Adiciona hesitações que simulam pensamento humano"""
        import random

        hesitacoes = ["eh...", "hmm...", "tipo...", "ah...", "então..."]

        # Adicionar hesitação antes de informações importantes (20% de chance)
        palavras_chave = ['erro', 'problema', 'importante', 'atenção', 'cuidado']
        for palavra in palavras_chave:
            if palavra in texto and random.random() < 0.2:
                pos = texto.find(palavra)
                if pos > 0:
                    hesitacao = random.choice(hesitacoes)
                    texto = texto[:pos] + hesitacao + " " + texto[pos:]
                    break

        return texto

    def _adicionar_respiracao_simulada(self, texto):
        """Adiciona marcadores de respiração simulada"""
        # Adicionar pequenas pausas que simulam respiração
        # Isso será usado pelo sistema de fala para pausas mais naturais
        if len(texto.split()) > 15:
            # Para frases muito longas, adicionar marcador de respiração
            palavras = texto.split()
            resp_pos = len(palavras) // 2
            palavras.insert(resp_pos, "[resp]")
            texto = ' '.join(palavras)

        return texto

    def _calcular_pausa_contextual(self, frase_atual, frase_anterior):
        """Calcula pausa baseada no contexto entre frases"""
        # Pausas maiores após perguntas ou exclamações
        if any(punct in frase_anterior for punct in ['?', '!', '...']):
            return 0.8
        # Pausas médias após pontos
        elif frase_anterior.endswith('.'):
            return 0.5
        # Pausas menores para continuidade
        else:
            return 0.3

    def _quebrar_em_frases_ultra_inteligente(self, texto):
        """Quebra texto em frases de forma ULTRA inteligente considerando contexto conversacional"""
        if not texto or len(texto.strip()) == 0:
            return [texto]

        # Primeiro, quebra básica por pontuação
        frases_basicas = self._quebrar_em_frases_inteligente(texto)

        resultado_final = []
        for frase in frases_basicas:
            # Análise ultra-detalhada para quebra conversacional
            if len(frase.split()) > 25:  # Frases muito longas precisam de análise profunda
                subfrases = self._quebrar_por_contexto_conversacional(frase)
                resultado_final.extend(subfrases)
            else:
                resultado_final.append(frase)

        return resultado_final

    def _quebrar_por_contexto_conversacional(self, frase):
        """Quebra frases baseada em contexto conversacional humano"""
        # Priorizar quebra por marcadores conversacionais
        marcadores_conversacionais = [
            ' e então ', ' mas sabe ', ' tipo assim ', ' quer dizer ', ' na verdade ',
            ' por exemplo ', ' ou seja ', ' em outras palavras ', ' acontece que ',
            ' o problema é ', ' a questão é ', ' o fato é ', ' então né ',
            ' sabe como é ', ' entende ', ' percebe ', ' vê só '
        ]

        for marcador in marcadores_conversacionais:
            if marcador in frase.lower():
                partes = frase.split(marcador)
                if len(partes) == 2:
                    # Verificar se ambas as partes têm tamanho razoável
                    if len(partes[0].split()) >= 5 and len(partes[1].split()) >= 3:
                        return [
                            partes[0] + marcador.rstrip(),
                            marcador.lstrip() + partes[1]
                        ]

        # Fallback: quebra por conectivos lógicos
        conectivos_logicos = [' e ', ' mas ', ' porém ', ' pois ', ' porque ', ' então ']
        for conectivo in conectivos_logicos:
            if conectivo in frase.lower():
                partes = frase.split(conectivo)
                if len(partes) == 2 and len(partes[0].split()) > 8 and len(partes[1].split()) > 4:
                    return [
                        partes[0] + conectivo.rstrip(),
                        conectivo.lstrip() + partes[1]
                    ]

        # Último recurso: quebra no meio para frases muito longas
        palavras = frase.split()
        if len(palavras) > 30:
            meio = len(palavras) // 2
            # Tentar encontrar quebra natural próxima ao meio
            for i in range(meio - 3, meio + 3):
                if i > 0 and i < len(palavras):
                    palavra = palavras[i].lower()
                    if palavra in ['que', 'e', 'mas', 'porém', 'pois', 'porque', 'então']:
                        return [' '.join(palavras[:i+1]), ' '.join(palavras[i+1:])]

            # Quebra simples no meio
            return [' '.join(palavras[:meio]), ' '.join(palavras[meio:])]

        return [frase]

    def _calcular_pausa_ultra_natural(self, frase_atual, frase_anterior, emocao=None):
        """Calcula pausa ultra-natural simulando respiração e pensamento humanos"""
        base_pausa = 0.3

        # Pausas emocionais
        if emocao == 'preocupado':
            base_pausa += 0.2  # Pausa mais longa quando preocupado
        elif emocao == 'entusiasta':
            base_pausa -= 0.1  # Pausa mais curta quando entusiasmado

        # Pausas contextuais baseadas no conteúdo
        frase_atual_lower = frase_atual.lower()
        frase_anterior_lower = frase_anterior.lower() if frase_anterior else ""

        # Pausas após hesitações
        if any(hesit in frase_anterior_lower for hesit in ['hmm', 'eh', 'tipo', 'ah']):
            base_pausa += 0.3

        # Pausas antes de informações importantes
        if any(palavra in frase_atual_lower for palavra in ['erro', 'problema', 'atenção', 'importante']):
            base_pausa += 0.4

        # Pausas após pontuação forte
        if frase_anterior.endswith(('!', '?', '...')):
            base_pausa += 0.5
        elif frase_anterior.endswith('.'):
            base_pausa += 0.3

        # Pausas conversacionais (simulando pensamento)
        if any(filler in frase_atual_lower for filler in ['né', 'tá', 'então', 'sabe']):
            base_pausa += 0.2

        # Garantir limites razoáveis
        return max(0.1, min(1.2, base_pausa))

    def _calcular_velocidade_ultra_contextual(self, frase, velocidade_base, emocao=None):
        """Calcula velocidade ultra-contextual baseada em emoção e conteúdo"""
        palavras = len(frase.split())
        frase_lower = frase.lower()

        # Base velocidade
        velocidade = float(velocidade_base)

        # Ajustes emocionais
        if emocao == 'entusiasta':
            velocidade *= 1.1  # Mais rápido quando entusiasmado
        elif emocao == 'preocupado':
            velocidade *= 0.85  # Mais devagar quando preocupado
        elif emocao == 'pensativo':
            velocidade *= 0.9  # Mais devagar quando pensativo

        # Ajustes contextuais ultra-detalhados
        if palavras > 20:
            velocidade *= 0.8  # Muito mais devagar para frases longas
        elif palavras < 4:
            velocidade *= 1.25  # Muito mais rápido para frases curtas

        # Ajustes por tipo de conteúdo
        if any(palavra in frase_lower for palavra in ['erro', 'problema', 'desculpe', 'ops']):
            velocidade *= 0.75  # Muito mais devagar para erros
        elif any(palavra in frase_lower for palavra in ['pronto', 'feito', 'sucesso', 'ótimo']):
            velocidade *= 1.15  # Mais animado para sucesso
        elif any(palavra in frase_lower for palavra in ['hmm', 'eh', 'tipo', 'ah', 'então']):
            velocidade *= 0.9  # Mais devagar para hesitações

        # Ajustes por pontuação
        if '?' in frase:
            velocidade *= 0.95  # Ligeiramente mais devagar para perguntas
        elif '!' in frase:
            velocidade *= 1.05  # Ligeiramente mais animado para exclamações

        return int(max(80, min(300, velocidade)))

    def _calcular_variacao_pitch_silabica(self, frase):
        """Calcula variação de pitch baseada na estrutura silábica (simula entonação natural)"""
        palavras = frase.split()
        if len(palavras) < 2:
            return 0

        # Análise básica de sílabas (aproximada)
        silabas_totais = sum(self._contar_silabas_aproximadas(palavra) for palavra in palavras)

        # Padrões de entonação natural
        variacao = 0

        # Última palavra tende a ter pitch mais baixo (declinação natural)
        if len(palavras) > 1:
            variacao -= 2

        # Frases com muitas sílabas tendem a ter variação maior
        if silabas_totais > 15:
            variacao += 1

        # Perguntas tendem a ter pitch mais alto no final
        if '?' in frase:
            variacao += 3

        # Hesitações tendem a ter pitch mais baixo
        if any(hesit in frase.lower() for hesit in ['hmm', 'eh', 'tipo']):
            variacao -= 3

        return variacao

    def _contar_silabas_aproximadas(self, palavra):
        """Conta sílabas de forma aproximada para português"""
        palavra = palavra.lower()
        silabas = 0
        vogais = 'aeiouáéíóúâêôãõ'

        for i, letra in enumerate(palavra):
            if letra in vogais:
                silabas += 1
                # Pular vogais consecutivas (ditongos)
                while i + 1 < len(palavra) and palavra[i + 1] in vogais:
                    i += 1

        return max(1, silabas)  # Mínimo 1 sílaba

    def _pausa_conversacional_inicial(self):
        """Pausa inicial simulando processamento humano antes de falar"""
        import random
        # Pausa variável simulando pensamento humano (0.3-0.8 segundos)
        pausa = random.uniform(0.3, 0.8)
        time.sleep(pausa)

    def _adicionar_marcadores_conversacionais(self, texto):
        """Adiciona marcadores que controlam o fluxo conversacional"""
        # Adicionar marcadores de pausa em pontos estratégicos
        texto = texto.replace('. ', '. [pausa_curta] ')
        texto = texto.replace('! ', '! [pausa_media] ')
        texto = texto.replace('? ', '? [pausa_longa] ')

        # Adicionar pausa antes de mudanças de assunto
        marcadores_mudanca = ['mas', 'porém', 'entretanto', 'no entanto']
        for marcador in marcadores_mudanca:
            if f' {marcador} ' in texto.lower():
                texto = texto.replace(f' {marcador} ', f' {marcador} [pausa_mudanca] ')

        return texto

    def _quebrar_em_frases_inteligente(self, texto):
        """Quebra texto em frases de forma inteligente e contextual"""
        if not texto or len(texto.strip()) == 0:
            return [texto]

        # Normalizar espaços e pontuação
        texto = re.sub(r'\s+', ' ', texto.strip())

        # Quebrar por marcadores de frases principais
        marcadores_principais = [
            r'(?<=[.!?])\s+(?=[A-ZÀ-Ú])',  # Após pontuação + espaço + maiúscula
            r'(?<=!)\s+',  # Após exclamação
            r'(?<=\?)\s+',  # Após interrogação
            r'(?<=\.)\s+(?=\d)',  # Após ponto + espaço + número
        ]

        frases = [texto]
        for marcador in marcadores_principais:
            novas_frases = []
            for frase in frases:
                partes = re.split(marcador, frase)
                # Manter pontuação com a frase anterior
                for i, parte in enumerate(partes):
                    if i > 0 and partes[i-1]:
                        # Se a parte anterior terminava com pontuação, manter junto
                        continue
                    if parte.strip():
                        novas_frases.append(parte.strip())
            frases = novas_frases

        # Quebrar frases muito longas por conectivos ou tamanho
        resultado_final = []
        for frase in frases:
            if len(frase.split()) > 20:  # Frases muito longas
                # Quebrar por conectivos
                conectivos = [' e ', ' mas ', ' porém ', ' pois ', ' porque ', ' então ', ' depois ', ' antes ']
                subfrases = [frase]

                for conectivo in conectivos:
                    if conectivo in frase.lower():
                        partes = frase.split(conectivo)
                        if len(partes) == 2 and len(partes[0].split()) > 8 and len(partes[1].split()) > 3:
                            subfrases = [partes[0] + conectivo.rstrip(), conectivo.lstrip() + partes[1]]
                            break

                # Se não conseguiu quebrar por conectivos, quebrar por tamanho
                if len(subfrases) == 1 and len(frase.split()) > 25:
                    palavras = frase.split()
                    meio = len(palavras) // 2
                    subfrases = [' '.join(palavras[:meio]), ' '.join(palavras[meio:])]

                resultado_final.extend(subfrases)
            else:
                resultado_final.append(frase)

        # Filtrar frases vazias e muito curtas (exceto se for a única)
        if len(resultado_final) > 1:
            resultado_final = [f for f in resultado_final if len(f.strip()) > 3]

        # Garantir que há pelo menos uma frase
        return resultado_final if resultado_final else [texto]

    def _quebrar_em_frases(self, texto):
        """Método legado - redireciona para o método inteligente"""
        return self._quebrar_em_frases_inteligente(texto)

    def _processar_marcadores_conversacionais(self, frase):
        """Processa marcadores conversacionais e retorna frase limpa + pausa extra"""
        pausa_extra = 0

        # Processar marcadores de pausa
        if '[pausa_curta]' in frase:
            pausa_extra = 0.3
            frase = frase.replace('[pausa_curta]', '')
        elif '[pausa_media]' in frase:
            pausa_extra = 0.6
            frase = frase.replace('[pausa_media]', '')
        elif '[pausa_longa]' in frase:
            pausa_extra = 1.0
            frase = frase.replace('[pausa_longa]', '')
        elif '[pausa_mudanca]' in frase:
            pausa_extra = 0.8
            frase = frase.replace('[pausa_mudanca]', '')

        # Limpar espaços extras
        frase = ' '.join(frase.split())

        return frase, pausa_extra

    def ouvir(self):
        """Escuta e reconhece fala do microfone"""
        with sr.Microphone() as source:
            print("Ouvindo...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source,
                                             timeout=self.config['recognition']['timeout'],
                                             phrase_time_limit=self.config['recognition']['phrase_limit'])
                comando = self.recognizer.recognize_google(audio, language=self.config['voice']['language'])
                print(f"Você disse: {comando}")
                return comando.lower()
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                self.falar("Desculpe, mas não consegui entender o que você disse. Pode repetir, por favor?", velocidade=160, emocao='preocupado')
                return None
            except sr.RequestError:
                self.falar("Ops! Parece que há um problema com a conexão. Verifique sua internet e tente novamente.", velocidade=160)
                return None

    def processar_comando(self, comando):
        """Processa o comando de voz e executa a ação correspondente"""
        if not comando:
            return

        # Procurar por comandos conhecidos
        for chave, funcao in self.commands.items():
            if chave in comando:
                try:
                    funcao(comando)
                    return
                except Exception as e:
                    self.falar(f"Ops! Ocorreu um erro ao executar o comando. Detalhes: {str(e)}", velocidade=160, emocao='preocupado')
                    return

        # Comando não reconhecido
        self.falar("Hmm... não entendi muito bem o que você quis dizer. Que tal tentar dizer 'ajuda' para ver todas as opções que eu tenho disponíveis?", velocidade=160)

    def abrir_programa(self, comando):
        """Abre programas no sistema"""
        programas = {
            'navegador': ('chrome.exe' if platform.system() == 'Windows' else 'google-chrome', 'navegador'),
            'calculadora': ('calc.exe' if platform.system() == 'Windows' else 'gnome-calculator', 'calculadora'),
            'bloco de notas': ('notepad.exe' if platform.system() == 'Windows' else 'gedit', 'bloco de notas'),
            'explorer': ('explorer.exe' if platform.system() == 'Windows' else 'nautilus', 'explorador de arquivos'),
            'cmd': ('cmd.exe' if platform.system() == 'Windows' else 'gnome-terminal', 'terminal')
        }

        for nome, (exe, nome_amigavel) in programas.items():
            if nome in comando:
                try:
                    subprocess.Popen(exe)
                    self.falar(f"Pronto! Abrindo o {nome_amigavel} para você.", velocidade=190, emocao='entusiasta', pausa_final=1.2)
                    return
                except FileNotFoundError:
                    self.falar(f"Ops! Não encontrei o {nome_amigavel} no seu sistema.", emocao='preocupado')

        self.falar("Desculpe, mas não reconheci qual programa você quer abrir. Tente dizer 'abrir navegador' ou 'abrir calculadora'.")

    def executar_comando(self, comando):
        """Executa comandos do sistema"""
        # Extrair o comando após "executar"
        cmd_match = re.search(r'executar (.+)', comando)
        if cmd_match:
            cmd = cmd_match.group(1)
            try:
                if platform.system() == 'Windows':
                    subprocess.run(['cmd', '/c', cmd], shell=True)
                else:
                    subprocess.run(cmd, shell=True)
                self.falar("Pronto! Comando executado com sucesso.", velocidade=170)
            except Exception as e:
                self.falar(f"Ops! Não consegui executar o comando. Erro: {str(e)}", velocidade=160)
        else:
            self.falar("Qual comando do sistema você gostaria que eu executasse?", velocidade=170)

    def fechar_programa(self, comando):
        """Fecha programas (básico)"""
        self.falar("A função de fechar programas ainda está sendo desenvolvida. Por enquanto, use o gerenciador de tarefas do sistema.", velocidade=160)

    def dizer_hora(self, comando):
        """Diz a hora atual"""
        hora = datetime.now().strftime("%H:%M")
        periodo = "da manhã" if int(hora.split(':')[0]) < 12 else "da tarde" if int(hora.split(':')[0]) < 18 else "da noite"
        self.falar(f"Agora são exatamente {hora} {periodo}.", velocidade=170)

    def dizer_data(self, comando):
        """Diz a data atual"""
        data = datetime.now().strftime("%d de %B de %Y")
        dia_semana = datetime.now().strftime("%A")
        dias_semana = {
            'Monday': 'segunda-feira',
            'Tuesday': 'terça-feira',
            'Wednesday': 'quarta-feira',
            'Thursday': 'quinta-feira',
            'Friday': 'sexta-feira',
            'Saturday': 'sábado',
            'Sunday': 'domingo'
        }
        dia_pt = dias_semana.get(dia_semana, dia_semana)
        self.falar(f"Hoje é {dia_pt}, {data}.", velocidade=170)

    def calcular(self, comando):
        """Faz cálculos simples"""
        # Extrair expressão matemática
        calc_match = re.search(r'calcular (.+)', comando)
        if calc_match:
            expressao = calc_match.group(1)
            try:
                # Avaliar expressão matemática de forma segura
                resultado = eval(expressao, {"__builtins__": {}})
                self.falar(f"O resultado de {expressao} é {resultado}.", velocidade=160)
            except:
                self.falar("Hmm, não consegui calcular essa expressão. Tente usar apenas números e operadores básicos como +, -, * e /.")
        else:
            self.falar("Claro! Qual cálculo você gostaria que eu fizesse? Por exemplo, diga 'calcular 25 vezes 4'.", velocidade=170)

    def pesquisar(self, comando):
        """Abre navegador para pesquisa"""
        search_match = re.search(r'pesquisar (.+)', comando)
        if search_match:
            termo = search_match.group(1)
            url = f"https://www.google.com/search?q={termo.replace(' ', '+')}"
            try:
                if platform.system() == 'Windows':
                    os.startfile(url)
                else:
                    subprocess.run(['xdg-open', url])
                self.falar(f"Pronto! Abrindo o navegador para pesquisar sobre '{termo}'.", velocidade=170)
            except:
                self.falar("Ops! Não consegui abrir o navegador para fazer a pesquisa.")
        else:
            self.falar("O que você gostaria que eu pesquisasse? Basta dizer 'pesquisar' seguido do que procura.", velocidade=170)

    def mostrar_ajuda(self, comando):
        """Mostra comandos disponíveis"""
        ajuda = """Ah, claro! Deixa eu te mostrar o que eu sei fazer. Então, olha só:

        Para abrir programas, você pode dizer: abrir navegador, abrir calculadora, abrir bloco de notas ou abrir explorer.

        Para saber informações, pergunte: que horas são, ou qual é a data de hoje.

        Para fazer cálculos, diga: calcular 25 mais 15, ou qualquer conta que quiser.

        Para pesquisar algo, fale: pesquisar Python, ou qualquer assunto que te interessar.

        Para executar comandos do sistema, diga: executar dir, por exemplo.

        E quando quiser encerrar nossa conversa, é só dizer: sair.

        O que você gostaria de tentar primeiro?"""
        self.falar(ajuda, velocidade=160, pausa_final=2.0)

    def sair(self, comando):
        """Encerra o assistente"""
        self.falar("Até logo! Foi um prazer ajudar você. Volte sempre que precisar!", velocidade=170)
        sys.exit(0)

    def run(self):
        """Loop principal do assistente"""
        self.falar("Ah, olá! Eu sou o JARVIS 5.0, seu assistente de voz pessoal. Estou aqui para te ajudar no que precisar. O que você gostaria de fazer hoje?", velocidade=170, emocao='entusiasta', pausa_final=1.5)

        while True:
            try:
                comando = self.ouvir()
                if comando:
                    self.processar_comando(comando)
            except KeyboardInterrupt:
                self.falar("Assistente interrompido. Até a próxima!", velocidade=170)
                break
            except Exception as e:
                print(f"Erro: {e}")
                self.falar("Ocorreu um erro inesperado. Vamos tentar novamente?", velocidade=160)

if __name__ == "__main__":
    assistant = JarvisAssistant()
    assistant.run()
