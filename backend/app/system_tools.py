import asyncio
import os
import subprocess
import psutil
import json
from loguru import logger
from livekit import agents
from typing import Optional
import datetime

class SystemTools:
    """
    Ferramentas de Sistema para o JARVIS.
    Permite ao agente interagir com o computador, ler arquivos e executar comandos.
    """

    def __init__(self, room: Optional[agents.Room] = None):
        self._room = room
        from .utils.log_manager import log_manager
        from .utils.workflow_engine import workflow_engine
        self._log_manager = log_manager
        self._workflow_engine = workflow_engine

    async def _log_activity(self, title: str, detail: str, log_type: str = "info", status: str = "success"):
        """Envia o log para o frontend via LiveKit e salva no disco."""
        entry = {
            "type": "activity_log",
            "title": title,
            "detail": detail,
            "log_type": log_type,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 1. Salva no disco (Persistência)
        self._log_manager.save_log(entry)
        
        # 2. Envia para o frontend (Real-time)
        if self._room and self._room.connection_state == "connected":
            try:
                await self._room.local_participant.publish_data(
                    json.dumps(entry),
                    topic="activity"
                )
            except Exception as e:
                logger.error(f"Falha ao publicar log de atividade: {e}")

    @agents.llm.function_tool(description="Lista a estrutura de arquivos do projeto ou de um diretório específico.")
    def project_structure(self, path: str = "."):
        try:
            items = os.listdir(path)
            structure = []
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    structure.append(f"📁 {item}/")
                else:
                    structure.append(f"📄 {item}")
            structure_str = "\n".join(structure)
            asyncio.create_task(self._log_activity("Listar Projeto", f"Caminho: {path}", "info"))
            return structure_str
        except Exception as e:
            logger.error(f"Erro ao listar diretório: {e}")
            return f"Erro: {str(e)}"

    @agents.llm.function_tool(description="Lê o conteúdo de um arquivo específico.")
    def read_file(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                asyncio.create_task(self._log_activity("Ler Arquivo", f"Arquivo: {file_path}", "edit"))
                return content
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            return f"Erro ao ler arquivo: {str(e)}"

    @agents.llm.function_tool(description="Escreve ou modifica o conteúdo de um arquivo.")
    def write_file(self, file_path: str, content: str):
        try:
            # Garantir que o diretório pai existe
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.success(f"Arquivo {file_path} escrito com sucesso.")
            asyncio.create_task(self._log_activity("Escrever Arquivo", f"Arquivo: {file_path}", "edit"))
            return f"Arquivo {file_path} atualizado."
        except Exception as e:
            logger.error(f"Erro ao escrever no arquivo {file_path}: {e}")
            return f"Erro ao escrever: {str(e)}"

    @agents.llm.function_tool(description="Executa um comando no terminal do sistema OPERACIONAL WINDOWS.")
    def execute_command(self, command: str):
        try:
            logger.info(f"Executando comando: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout if result.stdout else result.stderr
            asyncio.create_task(self._log_activity("Terminal", f"Comando: {command}", "cmd", "success" if result.returncode == 0 else "error"))
            return f"Saída do comando:\n{output}"
        except subprocess.TimeoutExpired:
            return "Erro: O comando demorou muito para responder (Timeout)."
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return f"Erro: {str(e)}"

    @agents.llm.function_tool(description="Obtém estatísticas de hardware do sistema (CPU, RAM, Bateria).")
    def get_system_stats(self):
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            batt_pct = battery.percent if battery else "N/A"
            
            stats = {
                "cpu_usage_percent": cpu,
                "ram_usage_percent": ram,
                "battery_percent": batt_pct,
                "os": os.name
            }
            return json.dumps(stats, indent=2)
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return f"Erro: {str(e)}"

    @agents.llm.function_tool(description="Realiza operações básicas de Git (status, commit, push - use com cautela).")
    def git_operation(self, action: str, message: str = ""):
        if action == "status":
            return self.execute_command("git status")
        elif action == "commit":
            if not message: return "Erro: Mensagem de commit necessária."
            return self.execute_command(f'git add . && git commit -m "{message}"')
        elif action == "push":
            asyncio.create_task(self._log_activity("Git Push", "Enviando alterações...", "git"))
            return self.execute_command("git push")
        else:
            return "Ação Git não suportada."

    @agents.llm.function_tool(description="Registra uma nova macro (sequência de tarefas) para execução futura.")
    def register_macro(self, name: str, description: str, steps: str):
        """
        Steps deve ser uma string JSON contendo uma lista de comandos ou ferramentas.
        """
        try:
            steps_list = json.loads(steps)
            if self._workflow_engine.register_macro(name, steps_list):
                asyncio.create_task(self._log_activity("Macro Registrada", f"Nome: {name} - {description}", "info"))
                return f"Macro '{name}' salva e pronta para o combate."
            return "Erro ao salvar macro."
        except Exception as e:
            return f"Erro no formato das ferramentas: {str(e)}"

    @agents.llm.function_tool(description="Executa uma macro previamente registrada pelo nome.")
    async def run_macro(self, name: str):
        macro = self._workflow_engine.get_macro(name)
        if not macro:
            return f"Erro: Macro '{name}' não encontrada."

        asyncio.create_task(self._log_activity("Executando Macro", f"Iniciando sequência: {name}", "info"))

        results = []
        for step in macro:
            if isinstance(step, str):
                res = self.execute_command(step)
                results.append(f"✔ {step[:40]} → {res[:60]}")
            elif isinstance(step, dict) and "cmd" in step:
                res = self.execute_command(step["cmd"])
                results.append(f"✔ {step['cmd'][:40]} → {res[:60]}")

        summary = "\n".join(results) if results else "Nenhum passo executado."
        return f"Macro '{name}' concluída:\n{summary}"


    @agents.llm.function_tool(description="Configura um monitoramento (watchdog) para um arquivo ou condição específica.")
    def set_watchdog(self, name: str, type: str, target: str):
        """
        type: 'file' (monitora alteração de data de modificação)
        target: caminho do arquivo
        """
        if self._workflow_engine.add_watchdog(name, {"type": type, "target": target}):
            asyncio.create_task(self._log_activity("Watchdog Ativado", f"Monitorando {type}: {target}", "info"))
            return f"Watchdog '{name}' configurado. Vou te avisar se algo mudar."
        return "Erro ao configurar watchdog."

    # ─── OLHOS: Controle de Navegador ───────────────────────────────────────

    @agents.llm.function_tool(description="Navega para uma URL no navegador autônomo. Use para abrir sites, pesquisar, acessar sistemas web.")
    async def browser_navigate(self, url: str):
        from .browser_engine import browser_manager
        try:
            result = await browser_manager.navigate(url)
            asyncio.create_task(self._log_activity("Navegador", f"Acessando: {url}", "info"))
            return result
        except Exception as e:
            return f"Erro ao navegar: {e}"

    @agents.llm.function_tool(description="Tira um screenshot do navegador para VER o estado atual da página. Essencial para decisões visuais.")
    async def browser_screenshot(self):
        from .browser_engine import browser_manager
        try:
            path = await browser_manager.get_screenshot()
            url = await browser_manager.get_current_url()
            asyncio.create_task(self._log_activity("Screenshot", f"Captura salva: {path}", "info"))
            return f"Screenshot salvo em '{path}'. URL atual: {url}"
        except Exception as e:
            return f"Erro ao capturar screenshot: {e}"

    @agents.llm.function_tool(description="Clica em um elemento da página por seletor CSS ou por coordenadas X,Y.")
    async def browser_click(self, selector: str = None, x: int = None, y: int = None):
        from .browser_engine import browser_manager
        try:
            result = await browser_manager.click(selector=selector, x=x, y=y)
            asyncio.create_task(self._log_activity("Clique", f"Seletor: {selector or f'({x},{y})'}", "cmd"))
            return result
        except Exception as e:
            return f"Erro ao clicar: {e}"

    @agents.llm.function_tool(description="Digita texto em um campo de formulário no navegador usando seletor CSS.")
    async def browser_type(self, selector: str, text: str):
        from .browser_engine import browser_manager
        try:
            result = await browser_manager.type_text(selector=selector, text=text)
            asyncio.create_task(self._log_activity("Digitação", f"Em '{selector}': {text[:30]}", "edit"))
            return result
        except Exception as e:
            return f"Erro ao digitar: {e}"

    @agents.llm.function_tool(description="Rola a página do navegador. direction: 'up' ou 'down'. amount: número de rolagens (1-10).")
    async def browser_scroll(self, direction: str = "down", amount: int = 3):
        from .browser_engine import browser_manager
        try:
            return await browser_manager.scroll(direction=direction, amount=amount)
        except Exception as e:
            return f"Erro ao rolar: {e}"

    @agents.llm.function_tool(description="Extrai o texto visível da página atual do navegador. Use após navegar para entender o conteúdo.")
    async def browser_get_page_content(self):
        from .browser_engine import browser_manager
        try:
            content = await browser_manager.get_page_content()
            url = await browser_manager.get_current_url()
            asyncio.create_task(self._log_activity("Leitura de Página", f"URL: {url}", "info"))
            return f"URL: {url}\n\nConteúdo:\n{content}"
        except Exception as e:
            return f"Erro ao ler página: {e}"

    # ─── MÃOS AVANÇADAS: Controle de Desktop ────────────────────────────────

    @agents.llm.function_tool(description="Tira um screenshot da tela inteira do computador (desktop). Use para ver o que está acontecendo fora do navegador.")
    async def take_screen_capture(self):
        try:
            import mss
            import mss.tools
            screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"desktop_{timestamp}.png"
            path = os.path.join(screenshot_dir, filename)
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=path)
            asyncio.create_task(self._log_activity("Desktop Capture", f"Screenshot: {filename}", "info"))
            return f"Screenshot do desktop salvo em: {path}"
        except ImportError:
            # Fallback com PIL
            try:
                from PIL import ImageGrab
                screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(screenshot_dir, f"desktop_{timestamp}.png")
                img = ImageGrab.grab()
                img.save(path)
                return f"Screenshot do desktop salvo em: {path}"
            except Exception as e:
                return f"Erro ao capturar desktop (instale mss ou Pillow): {e}"
        except Exception as e:
            return f"Erro ao capturar desktop: {e}"

    @agents.llm.function_tool(description="Abre um aplicativo no Windows pelo nome (ex: 'notepad', 'chrome', 'spotify', 'code').")
    async def open_application(self, app_name: str):
        try:
            app_map = {
                "notepad": "notepad.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "spotify": "spotify.exe",
                "code": "code",
                "explorer": "explorer.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
            }
            executable = app_map.get(app_name.lower(), app_name)
            subprocess.Popen(executable, shell=True)
            asyncio.create_task(self._log_activity("Abrir App", f"Iniciando: {app_name}", "cmd"))
            return f"Aplicativo '{app_name}' iniciado."
        except Exception as e:
            return f"Erro ao abrir '{app_name}': {e}"

    @agents.llm.function_tool(description="Lê o texto atual da área de transferência (clipboard).")
    def get_clipboard(self):
        try:
            result = subprocess.run(
                ["powershell", "-command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=5
            )
            content = result.stdout.strip()
            return f"Clipboard: {content}" if content else "Clipboard vazio."
        except Exception as e:
            return f"Erro ao ler clipboard: {e}"

    @agents.llm.function_tool(description="Define o texto da área de transferência (clipboard). Útil para preparar conteúdo para colar.")
    def set_clipboard(self, text: str):
        try:
            subprocess.run(
                ["powershell", "-command", f"Set-Clipboard -Value '{text}'"],
                capture_output=True, text=True, timeout=5
            )
            return f"Clipboard definido com: {text[:50]}..."
        except Exception as e:
            return f"Erro ao definir clipboard: {e}"

    @agents.llm.function_tool(description="Aplica uma mudança cirúrgica em um arquivo de código: substitui um trecho específico por outro.")
    def apply_code_change(self, file_path: str, old_code: str, new_code: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if old_code not in content:
                return f"Erro: trecho '{old_code[:50]}...' não encontrado em {file_path}"
            new_content = content.replace(old_code, new_code, 1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            asyncio.create_task(self._log_activity("Code Change", f"Alterado: {file_path}", "edit"))
            return f"Alteração aplicada com sucesso em {file_path}."
        except Exception as e:
            return f"Erro ao aplicar mudança: {e}"

    @agents.llm.function_tool(description="Pesquisa um texto em todos os arquivos de um diretório. Útil para encontrar onde algo está definido.")
    def search_in_files(self, search_text: str, directory: str = ".", extension: str = ".py"):
        try:
            results = []
            for root, _, files in os.walk(directory):
                for fname in files:
                    if fname.endswith(extension):
                        fpath = os.path.join(root, fname)
                        try:
                            with open(fpath, "r", encoding="utf-8") as f:
                                for i, line in enumerate(f, 1):
                                    if search_text.lower() in line.lower():
                                        results.append(f"{fpath}:{i}: {line.strip()}")
                        except Exception:
                            pass
            if not results:
                return f"Nenhuma ocorrência de '{search_text}' encontrada."
            return "\n".join(results[:30])
        except Exception as e:
            return f"Erro na busca: {e}"

    # ─── CÉREBRO ENGENHEIRO: Raciocínio Avançado ────────────────────────────

    @agents.llm.function_tool(description="Salva um fato importante sobre o usuário na memória local permanente. Use quando o usuário revelar uma preferência, objetivo, contexto pessoal ou informação relevante que deve ser lembrada.")
    def save_memory(self, fact: str, user_id: str = "Chefe"):
        from .local_memory import local_memory
        saved = local_memory.save_fact(user_id, fact)
        if saved:
            asyncio.create_task(self._log_activity("Memória Salva", f"Fato registrado: {fact[:60]}", "info"))
            return f"Fato memorizado com sucesso: '{fact[:80]}'"
        return f"Fato similar já estava na memória (ignorado para evitar duplicata)."

    @agents.llm.function_tool(description="Consulta a memória local do usuário por palavra-chave. Use para recuperar informações de sessões anteriores.")
    def recall_memory(self, query: str, user_id: str = "Chefe"):
        from .local_memory import local_memory
        results = local_memory.search(user_id, query, limit=10)
        if not results:
            return f"Nenhuma memória encontrada para '{query}'."
        lines = [f"[{r.get('category','?')}] {r['memory']}" for r in results]
        return "Memórias encontradas:\n" + "\n".join(lines)

    @agents.llm.function_tool(description="Mostra estatísticas da memória local: total de fatos, categorias e tamanho em KB.")
    def memory_stats(self, user_id: str = "Chefe"):
        from .local_memory import local_memory
        stats = local_memory.get_stats(user_id)
        return (
            f"Memória local de '{user_id}':\n"
            f"  Total de fatos: {stats['total_memories']}\n"
            f"  Sessões salvas: {stats['sessions']}\n"
            f"  Por categoria: {stats['by_category']}\n"
            f"  Tamanho do banco: {stats['db_size_kb']} KB"
        )

    @agents.llm.function_tool(description="Consulta o Núcleo Engenheiro (OpenRouter) para problemas complexos de código, bugs difíceis ou arquitetura. Use quando precisar de uma segunda opinião técnica sênior.")
    async def think_with_engineer_brain(self, task: str, context: str = ""):
        from .engineer_brain import brain
        asyncio.create_task(self._log_activity("Cérebro Engenheiro", f"Consultando OpenRouter: {task[:60]}", "info"))
        try:
            result = await brain.reason(task, context)
            return result
        except Exception as e:
            return f"Falha ao consultar o cérebro engenheiro: {e}"

    # ─── SENSORES: Percepção (Face, Gesto, Voz) ──────────────────────────────

    @agents.llm.function_tool(description="Retorna o estado atual da percepção: emoção do usuário, gesto detectado, identidade facial, identidade de voz e direção do dedo apontando. Use para entender o contexto físico do usuário.")
    def get_perception_status(self):
        try:
            from .perception import perception_manager
            snap = perception_manager.get_snapshot()
            lines = [
                f"👁️  Face: {'presente' if snap['face_present'] else 'ausente'} ({snap['face_count']} pessoa(s))",
                f"😐  Emoção: {snap['face_emotion']} ({snap['face_emotion_score']:.0%})",
            ]
            if snap["face_identity"]:
                lines.append(f"🪪  Identidade facial: {snap['face_identity']} ({snap['face_identity_confidence']:.0%})")
            if snap["hand_gesture"]:
                lines.append(f"✋  Gesto: {snap['hand_gesture']} ({snap['hand_side']})")
            if snap["head_gesture"]:
                lines.append(f"🫡  Cabeça: {snap['head_gesture']}")
            if snap["pointing_direction"]:
                lines.append(f"👆  Apontando: {snap['pointing_direction']} {snap['pointing_xy'] or ''}")
            if snap["speaker_identity"]:
                lines.append(f"🎙️  Locutor: {snap['speaker_identity']}")
            if snap["offline_transcript"]:
                lines.append(f"📝  Transcrição offline: {snap['offline_transcript']}")
            lines.append(f"⚙️   Níveis ativos: {snap['active_levels']}")
            return "\n".join(lines)
        except Exception as e:
            return f"Percepção indisponível: {e}"

    @agents.llm.function_tool(description="Cadastra o rosto do usuário para reconhecimento de identidade. Tira uma foto agora via câmera e associa ao nome fornecido.")
    def enroll_face(self, name: str):
        try:
            from .perception import perception_manager
            from .perception.face_engine import enroll_face as _enroll
            frame = perception_manager.capture_frame()
            if frame is None:
                return "Câmera indisponível para cadastro de rosto."
            result = _enroll(name, frame)
            asyncio.create_task(self._log_activity("Rosto Cadastrado", f"Identidade: {name}", "info"))
            return result
        except Exception as e:
            return f"Erro ao cadastrar rosto: {e}"

    @agents.llm.function_tool(description="Cadastra a voz do usuário para reconhecimento de locutor. Grava 5 segundos de áudio agora e associa ao nome fornecido.")
    def enroll_voice(self, name: str):
        try:
            from .perception import perception_manager
            from .perception.voice_engine import enroll_voice as _enroll
            audio = perception_manager.get_audio_sample(seconds=5.0)
            if audio is None:
                return "Microfone indisponível para cadastro de voz."
            result = _enroll(name, audio)
            asyncio.create_task(self._log_activity("Voz Cadastrada", f"Locutor: {name}", "info"))
            return result
        except Exception as e:
            return f"Erro ao cadastrar voz: {e}"

    @agents.llm.function_tool(description="Pesquisa no banco de conhecimento de código local (RAG). Use para entender como funções, classes ou módulos específicos do projeto funcionam, mesmo que os arquivos não estejam abertos.")
    def search_codebase(self, query: str):
        from .utils.code_indexer import code_miner
        asyncio.create_task(self._log_activity("RAG de Código", f"Consultando: {query}", "info"))
        try:
            result = code_miner.query(query)
            return f"Resultado da análise do repositório:\n{result}"
        except Exception as e:
            return f"Erro ao consultar a base de conhecimento: {e}"

    @agents.llm.function_tool(description="Executa uma indexação completa do repositório de código para atualizar o banco de conhecimento (RAG).")
    def refresh_code_index(self):
        from .utils.code_indexer import code_miner
        asyncio.create_task(self._log_activity("Indexação", "Atualizando base vetorial...", "info"))
        try:
            # Indexa a partir do diretório pai (raiz do projeto)
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            code_miner.index_codebase(root_dir)
            return "Índice de código atualizado com sucesso."
        except Exception as e:
            return f"Erro na indexação: {e}"

    @agents.llm.function_tool(description="Executa um comando de teste/build e tenta AUTO-CORRIGIR o código se houver erro. O Jarvis entrará em um loop de pensamento->ação->verificação até o erro sumir (limite de 3 tentativas).")
    async def run_and_fix(self, command: str, target_file: str):
        """Modo de Auto-Cura: Executa um comando e tenta corrigir o arquivo se falhar."""
        attempt = 1
        max_attempts = 3
        last_error = ""

        while attempt <= max_attempts:
            asyncio.create_task(self._log_activity("God Mode", f"Tentativa {attempt}: {command}", "cmd"))
            # Executa com timeout longo para builds
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                asyncio.create_task(self._log_activity("Sucesso!", f"O código em {target_file} está funcionando.", "info", "success"))
                return f"Sucesso na tentativa {attempt}! Comando executado sem erros no arquivo {target_file}."
            
            # Se houver erro, captura e tenta corrigir
            last_error = (result.stdout or "") + "\n" + (result.stderr or "")
            logger.warning(f"[GodMode] Erro detectado na tentativa {attempt}: {last_error[:100]}...")
            
            # Consulta o cérebro engenheiro para uma correção
            from .engineer_brain import brain
            correction_task = (
                f"O comando '{command}' falhou com o seguinte erro:\n{last_error}\n"
                f"No arquivo: {target_file}.\n"
                f"Por favor, analise o erro e forneça APENAS o código corrigido completo para substituir este arquivo agora."
            )
            
            asyncio.create_task(self._log_activity("Auto-Correção", "Analisando erro e gerando reparo com IA...", "brain"))
            correction_code = await brain.reason(correction_task, "Você é um Engenheiro Sênior em modo de Auto-Reparo (God Mode).")
            
            # Extrai código do markdown se necessário
            if "```" in correction_code:
                parts = correction_code.split("```")
                # Pega a parte entre as crases (assume a maior se houver várias, ou a segunda parte do split)
                correction_code = parts[1].split("\n", 1)[1] if "\n" in parts[1] else parts[1]
                # Limpa rastro de fencas
                if correction_code.endswith("```"):
                    correction_code = correction_code[:-3]
            
            # Aplica a correção salvando o arquivo inteiro
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(correction_code.strip())
            
            logger.info(f"[GodMode] Correção aplicada para a tentativa {attempt}. Testando novamente...")
            attempt += 1
        
        return f"Falha após {max_attempts} tentativas de auto-correção. Último erro detectado:\n{last_error}"
