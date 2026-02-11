    def greet_user_on_startup(self, system_health: dict = None):
        """
        🌟 SPARK OF LIFE: Gera saudação espontânea e humana ao iniciar.
        
        Não usa frases prontas. Usa o cérebro (LLM) para 'sentir' o momento
        e criar uma apresentação única a cada boot.
        
        Args:
            system_health: Dict com status de componentes (opcional)
                          Ex: {"ai_agent": True, "vision": True, "audio": True, ...}
        """
        if not voice_controller:
            logger.warning("⚠️ Voice controller indisponível para saudação.")
            return
        
        try:
            import datetime
            now = datetime.datetime.now()
            hora = now.hour
            
            # 1. CONTEXTO TEMPORAL
            periodo = (
                "madrugada" if 0 <= hora < 6 else
                "manhã" if 6 <= hora < 12 else
                "tarde" if 12 <= hora < 18 else
                "noite"
            )
            hora_formatada = now.strftime("%H:%M")
            
            # 2. CONTEXTO DO SISTEMA
            status_info = ""
            if system_health:
                ativos = sum(1 for v in system_health.values() if v)
                total = len(system_health)
                tier = getattr(hardware_manager, 'tier', 'BALANCED')
                gpu_name = getattr(hardware_manager, 'gpu_name', 'CPU')
                
                status_info = (
                    f"- {ativos}/{total} módulos principais carregados com sucesso\\n"
                    f"- Hardware: {tier} tier ({gpu_name})\\n"
                )
            
            # 3. CONTEXTO EMOCIONAL (se câmera disponível)
            emocao_detectada = ""
            try:
                from src.core.vision.camera_controller import camera_controller
                if camera_controller and hasattr(camera_controller, 'current_emotion'):
                    emocao = camera_controller.current_emotion
                    if emocao and emocao != "neutral":
                        emocao_detectada = f"- Sua expressão atual parece: {emocao}\\n"
            except:
                pass
            
            # 4. PROMPT ENGINEERING (Criatividade Total)
            prompt_saudacao = f"""Você é JARVIS, o assistente pessoal do William. Você acabou de iniciar seus sistemas agora de {periodo} (são {hora_formatada}).

**Status atual:**
{status_info}{emocao_detectada}

**Tarefa:** Gere UMA ÚNICA frase de saudação curta, elegante e natural para dizer ao William que você está pronto.

**Regras imperativas:**
1. Use "William", "senhor" ou "chefe" (NUNCA "usuário")
2. NÃO liste logs técnicos (ex: "módulo X carregado com sucesso")
3. Seja humano e imprevisível - cada boot deve soar diferente
4. Varie entre: sarcástico (Tony Stark), formal britânico (JARVIS clássico), ou motivador
5. Se for madrugada/noite tarde, pode comentar sobre a hora
6. Máximo 2 frases curtas

**Exemplos de vibe (NÃO COPIE, apenas inspire-se):**
- "Sistemas online, William. {periodo} tranquil{'a' if periodo in ['manhã', 'tarde', 'madrugada'] else 'a'}. O que vamos criar hoje?"
- "E aí, chefe. Acabei de sincronizar. Pronto para bagunçar o código ou concertar o mundo?"
- "Boa {periodo}, senhor. Cérebro 100%, visão calibrada. Como posso ajudar?"

**IMPORTANTE:** Responda APENAS a frase falada. Sem explicações ou formatação extra."""

            # 5. GERAR SAUDAÇÃO VIA LLM
            resposta_viva = ""
            
            # Tentar Gemini primeiro (mais criativo e rápido)
            if self.api_key and not self.safe_mode:
                try:
                    logger.info("🧠 Gerando saudação via Gemini...")
                    resposta_viva = self._call_gemini(prompt_saudacao, image_path=None, system_prompt="Você é JARVIS. Seja criativo e humano.")
                except Exception as e:
                    logger.warning(f"Gemini falhou na saudação: {e}")
            
            # Fallback para Ollama
            if not resposta_viva and self._check_ollama_alive():
                try:
                    logger.info("🧠 Gerando saudação via Ollama...")
                    resposta_viva = self._call_ollama(
                        prompt_saudacao, 
                        image_path=None,
                        model="qwen2.5:7b",
                        system_prompt="Você é JARVIS. Seja criativo, humano e conciso."
                    )
                except Exception as e:
                    logger.warning(f"Ollama falhou na saudação: {e}")
            
            # 6. FALAR A SAUDAÇÃO
            if resposta_viva and len(resposta_viva.strip()) > 5:
                # Limpar possível lixo (às vezes o LLM adiciona aspas ou prefixos)
                resposta_viva = resposta_viva.strip().strip('"').strip("'")
                
                logger.info(f"⚡ JARVIS Startup Greeting: {resposta_viva}")
                voice_controller.speak(resposta_viva)
            else:
                # Fallback ultra-simples se tudo falhar
                fallback = f"Sistemas online, William. Estou pronto."
                logger.warning(f"⚠️ LLM falhou, usando fallback: {fallback}")
                voice_controller.speak(fallback)
        
        except Exception as e:
            logger.error(f"❌ Erro crítico na saudação inicial: {e}")
            # Último recurso
            try:
                voice_controller.speak("Sistemas prontos.")
            except:
                pass
