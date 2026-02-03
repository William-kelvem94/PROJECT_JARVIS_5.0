"""
Janela principal da interface gráfica
Interface principal do Leitor de Tela Inteligente
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import customtkinter as ctk
from PIL import Image, ImageTk
from src.utils.config import config
from src.core.screen_capture import screen_capture
from src.core.ocr_processor import ocr_processor
from src.core.data_analyzer import data_analyzer
from src.core.data_organizer import data_organizer
from src.core.ai_agent import ai_agent
from src.core.voice_controller import voice_controller
from src.database.models import db_manager

logger = logging.getLogger(__name__)

class MainWindow:
    """Janela principal da aplicação"""

    def __init__(self):
        # Configurar aparência
        ctk.set_appearance_mode(config.get_setting('interface.theme', 'dark'))
        ctk.set_default_color_theme("blue")

        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title("Leitor de Tela Inteligente")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Variáveis de controle
        self.current_capture_path = None
        self.processing_active = False
        self.recording_active = False

        # Inicializar componentes da interface
        self._setup_ui()
        self._setup_menu()
        self._setup_bindings()

        # Configurar callbacks
        self._setup_callbacks()

        logger.info("Janela principal inicializada")

    def _setup_ui(self):
        """Configura a interface do usuário"""
        # Container principal
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Barra de ferramentas superior
        self._create_toolbar()

        # Área principal dividida
        self._create_main_area()

        # Barra de status inferior
        self._create_status_bar()

    def _create_toolbar(self):
        """Cria barra de ferramentas"""
        toolbar = ctk.CTkFrame(self.main_container, height=50)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Botões principais
        button_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        button_frame.pack(side=tk.LEFT, padx=10)

        # Botão Capturar Tela
        self.btn_capture = ctk.CTkButton(
            button_frame, text="📸 Capturar Tela",
            command=self._on_capture_screen,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_capture.pack(side=tk.LEFT, padx=5)

        # Botão Selecionar Área
        self.btn_select_area = ctk.CTkButton(
            button_frame, text="🎯 Selecionar Área",
            command=self._on_select_area,
            font=ctk.CTkFont(size=12)
        )
        self.btn_select_area.pack(side=tk.LEFT, padx=5)

        # Botão Gravar Tela
        self.btn_record = ctk.CTkButton(
            button_frame, text="🎬 Gravar Tela",
            command=self._on_toggle_recording,
            fg_color="red",
            font=ctk.CTkFont(size=12)
        )
        self.btn_record.pack(side=tk.LEFT, padx=5)

        # Separador
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Botões de processamento
        process_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        process_frame.pack(side=tk.LEFT, padx=10)

        self.btn_process = ctk.CTkButton(
            process_frame, text="⚙️ Processar",
            command=self._on_process_capture,
            state="disabled",
            font=ctk.CTkFont(size=12)
        )
        self.btn_process.pack(side=tk.LEFT, padx=5)

        # Botão Exportar
        self.btn_export = ctk.CTkButton(
            process_frame, text="💾 Exportar",
            command=self._on_export_data,
            state="disabled",
            font=ctk.CTkFont(size=12)
        )
        self.btn_export.pack(side=tk.LEFT, padx=5)

        # Configurações (lado direito)
        config_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        config_frame.pack(side=tk.RIGHT, padx=10)

        self.btn_settings = ctk.CTkButton(
            config_frame, text="⚙️ Configurações",
            command=self._on_open_settings,
            width=120,
            font=ctk.CTkFont(size=11)
        )
        self.btn_settings.pack(side=tk.LEFT, padx=5)

    def _create_main_area(self):
        """Cria área principal da interface"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.main_container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Painel esquerdo - Lista de capturas
        self._create_captures_panel(main_frame)

        # Painel direito - Visualização e resultados
        self._create_results_panel(main_frame)

    def _create_captures_panel(self, parent):
        """Cria painel de lista de capturas"""
        left_panel = ctk.CTkFrame(parent, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)

        # Título
        title_label = ctk.CTkLabel(
            left_panel, text="📁 Capturas Recentes",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10)

        # Lista de capturas
        self.captures_listbox = tk.Listbox(
            left_panel,
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1f538d",
            font=("Arial", 10)
        )
        self.captures_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbar para lista
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.captures_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.captures_listbox.config(yscrollcommand=scrollbar.set)

        # Botões de ação
        buttons_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)

        self.btn_refresh_captures = ctk.CTkButton(
            buttons_frame, text="🔄 Atualizar",
            command=self._refresh_captures_list,
            width=120
        )
        self.btn_refresh_captures.pack(side=tk.LEFT, padx=2)

        self.btn_delete_capture = ctk.CTkButton(
            buttons_frame, text="🗑️ Excluir",
            command=self._on_delete_capture,
            fg_color="red",
            width=80
        )
        self.btn_delete_capture.pack(side=tk.RIGHT, padx=2)

        # Vincular evento de seleção
        self.captures_listbox.bind('<<ListboxSelect>>', self._on_capture_selected)

    def _create_results_panel(self, parent):
        """Cria painel de visualização de resultados"""
        right_panel = ctk.CTkFrame(parent)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook para abas
        self.results_notebook = ttk.Notebook(right_panel)
        self.results_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba de Visualização
        self._create_preview_tab()

        # Aba de Dados Extraídos
        self._create_data_tab()

        # Aba de OCR
        self._create_ocr_tab()

        # Aba de IA Agent (NOVO)
        self._create_ai_agent_tab()

    def _create_preview_tab(self):
        """Cria aba de visualização da captura"""
        preview_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(preview_frame, text="📸 Visualização")

        # Área de imagem
        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg="#1a1a1a",
            highlightthickness=1,
            highlightbackground="#404040"
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Label para quando não há imagem
        self.preview_label = ctk.CTkLabel(
            self.preview_canvas,
            text="Nenhuma captura selecionada\n\nClique em 'Capturar Tela' para começar",
            font=ctk.CTkFont(size=14)
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Barra de progresso para processamento
        self.progress_bar = ctk.CTkProgressBar(preview_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Label de status
        self.status_label = ctk.CTkLabel(
            preview_frame,
            text="Pronto para capturar",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)

    def _create_data_tab(self):
        """Cria aba de dados extraídos"""
        data_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(data_frame, text="📊 Dados Extraídos")

        # Treeview para dados
        columns = ("Campo", "Valor", "Tipo", "Confiança")
        self.data_tree = ttk.Treeview(data_frame, columns=columns, show="headings", height=20)

        # Configurar colunas
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Botões de ação
        buttons_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        self.btn_edit_data = ctk.CTkButton(
            buttons_frame, text="✏️ Editar",
            command=self._on_edit_data,
            width=100
        )
        self.btn_edit_data.pack(side=tk.LEFT, padx=5)

        self.btn_validate_data = ctk.CTkButton(
            buttons_frame, text="✅ Validar",
            command=self._on_validate_data,
            width=100
        )
        self.btn_validate_data.pack(side=tk.LEFT, padx=5)

    def _create_ocr_tab(self):
        """Cria aba de resultados OCR"""
        ocr_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(ocr_frame, text="📝 OCR")

        # Área de texto para OCR
        self.ocr_text = ctk.CTkTextbox(ocr_frame, wrap="word")
        self.ocr_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Botões de controle
        controls_frame = ctk.CTkFrame(ocr_frame, fg_color="transparent")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        self.btn_copy_ocr = ctk.CTkButton(
            controls_frame, text="📋 Copiar Texto",
            command=self._on_copy_ocr_text,
            width=120
        )
        self.btn_copy_ocr.pack(side=tk.LEFT, padx=5)

        self.btn_save_ocr = ctk.CTkButton(
            controls_frame, text="💾 Salvar TXT",
            command=self._on_save_ocr_text,
            width=120
        )
        self.btn_save_ocr.pack(side=tk.LEFT, padx=5)

    def _create_ai_agent_tab(self):
        """Cria aba de interação com o Agente de IA"""
        ai_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(ai_frame, text="🤖 IA Agent")

        # Histórico de Chat
        self.chat_history = ctk.CTkTextbox(ai_frame, wrap="word", state="disabled")
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Container de Entrada
        input_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.chat_input = ctk.CTkEntry(input_frame, placeholder_text="Digite um comando ou clique no microfone...")
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind("<Return>", lambda e: self._on_send_command())

        # Botão de Microfone (Jarvis)
        self.btn_mic = ctk.CTkButton(input_frame, text="🎤", width=40, command=self._on_toggle_voice)
        self.btn_mic.pack(side=tk.LEFT, padx=5)

        self.btn_send = ctk.CTkButton(input_frame, text="Enviar", width=80, command=self._on_send_command)
        self.btn_send.pack(side=tk.RIGHT)
        
        # Registrar callback de voz
        voice_controller.on_speech_recognized = self._on_voice_recognized

    def _on_toggle_voice(self):
        """Alterna o reconhecimento de voz"""
        if voice_controller.is_listening:
            voice_controller.stop_listening()
            self.btn_mic.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            self._set_processing_status("Voz desativada")
        else:
            voice_controller.start_listening()
            self.btn_mic.configure(fg_color="red")
            self._set_processing_status("Ouvindo comandos...")
            voice_controller.speak("Sim senhor? Estou ouvindo.")

    def _on_voice_recognized(self, text: str):
        """Callback chamado quando a voz é reconhecida"""
        self.root.after(0, lambda: self.chat_input.insert(0, text))
        self.root.after(100, self._on_send_command)

    def _on_send_command(self):
        """Envia comando para o Agente de IA"""
        command = self.chat_input.get()
        if not command:
            return

        self.chat_input.delete(0, tk.END)
        self._add_to_chat(f"Você: {command}")
        
        # Processar em thread para não travar a GUI
        threading.Thread(target=self._process_ai_command, args=(command,), daemon=True).start()

    def _process_ai_command(self, command: str):
        """Processa o comando usando o AIAgent"""
        self._add_to_chat("IA: Pensando...")
        response = ai_agent.process_command(command)
        self.root.after(0, lambda: self._add_to_chat(f"IA: {response}"))

    def _add_to_chat(self, text: str):
        """Adiciona mensagem ao histórico do chat"""
        self.chat_history.configure(state="normal")
        self.chat_history.insert(tk.END, text + "\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.configure(state="disabled")

    def _create_status_bar(self):
        """Cria barra de status"""
        status_frame = ctk.CTkFrame(self.main_container, height=30)
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        # Labels de status
        self.status_engine = ctk.CTkLabel(
            status_frame,
            text="Engine: Verificando...",
            font=ctk.CTkFont(size=10)
        )
        self.status_engine.pack(side=tk.LEFT, padx=10)

        self.status_captures = ctk.CTkLabel(
            status_frame,
            text="Capturas: 0",
            font=ctk.CTkFont(size=10)
        )
        self.status_captures.pack(side=tk.LEFT, padx=10)

        self.status_memory = ctk.CTkLabel(
            status_frame,
            text="Memória: OK",
            font=ctk.CTkFont(size=10)
        )
        self.status_memory.pack(side=tk.RIGHT, padx=10)

    def _setup_menu(self):
        """Configura menu da aplicação"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Nova Captura", command=self._on_capture_screen, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir Captura", command=self._on_open_capture, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exportar Dados", command=self._on_export_data, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self._on_exit, accelerator="Ctrl+Q")

        # Menu Editar
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Configurações", command=self._on_open_settings, accelerator="Ctrl+,")

        # Menu Visualizar
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_command(label="Atualizar Lista", command=self._refresh_captures_list, accelerator="F5")

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self._on_show_about)
        help_menu.add_command(label="Documentação", command=self._on_show_docs)

    def _setup_bindings(self):
        """Configura atalhos de teclado"""
        self.root.bind('<Control-n>', lambda e: self._on_capture_screen())
        self.root.bind('<Control-o>', lambda e: self._on_open_capture())
        self.root.bind('<Control-e>', lambda e: self._on_export_data())
        self.root.bind('<Control-q>', lambda e: self._on_exit())
        self.root.bind('<Control-comma>', lambda e: self._on_open_settings())
        self.root.bind('<F5>', lambda e: self._refresh_captures_list())
        self.root.bind('<Escape>', lambda e: self._on_escape_pressed())

        # Configurar hotkey global para captura (se disponível)
        try:
            import keyboard
            hotkey = config.get_setting('capture.hotkey', 'ctrl+shift+s')
            keyboard.add_hotkey(hotkey, self._on_global_capture_hotkey)
            logger.info(f"Hotkey global configurado: {hotkey}")
        except ImportError:
            logger.warning("Biblioteca keyboard não disponível - hotkey global desabilitado")

    def _setup_callbacks(self):
        """Configura callbacks dos módulos core"""
        screen_capture.on_capture_complete = self._on_capture_completed
        screen_capture.on_recording_complete = self._on_recording_completed

    def _on_capture_screen(self):
        """Callback para captura de tela completa"""
        try:
            self._set_processing_status("Capturando tela...")
            self.btn_capture.configure(state="disabled")

            # Executar em thread separada
            threading.Thread(target=self._capture_screen_thread, daemon=True).start()

        except Exception as e:
            logger.error(f"Erro ao iniciar captura: {e}")
            self._reset_capture_button()

    def _capture_screen_thread(self):
        """Thread para captura de tela"""
        try:
            capture_path = screen_capture.capture_fullscreen()
            if capture_path:
                self.current_capture_path = capture_path
                self.root.after(0, lambda: self._on_capture_success(capture_path))
            else:
                self.root.after(0, self._on_capture_error)

        except Exception as e:
            logger.error(f"Erro na captura: {e}")
            self.root.after(0, self._on_capture_error)

    def _on_select_area(self):
        """Callback para seleção de área"""
        try:
            # Por enquanto, implementar captura de área simples
            messagebox.showinfo("Seleção de Área",
                              "Funcionalidade de seleção de área será implementada em breve.\n\n"
                              "Por enquanto, use a captura completa da tela.")
        except Exception as e:
            logger.error(f"Erro na seleção de área: {e}")

    def _on_toggle_recording(self):
        """Callback para alternar gravação de tela"""
        if self.recording_active:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        """Inicia gravação de tela"""
        try:
            success = screen_capture.start_screen_recording(duration=30)  # 30 segundos por padrão
            if success:
                self.recording_active = True
                self.btn_record.configure(text="⏹️ Parar Gravação", fg_color="red")
                self._set_processing_status("Gravando tela...")
            else:
                messagebox.showerror("Erro", "Não foi possível iniciar a gravação")

        except Exception as e:
            logger.error(f"Erro ao iniciar gravação: {e}")
            messagebox.showerror("Erro", f"Erro ao iniciar gravação: {e}")

    def _stop_recording(self):
        """Para gravação de tela"""
        try:
            success = screen_capture.stop_screen_recording()
            if success:
                self.recording_active = False
                self.btn_record.configure(text="🎬 Gravar Tela", fg_color=["#3B8ED0", "#1F6AA5"])
                self._set_processing_status("Gravação parada")
            else:
                messagebox.showwarning("Aviso", "Nenhuma gravação ativa para parar")

        except Exception as e:
            logger.error(f"Erro ao parar gravação: {e}")

    def _on_process_capture(self):
        """Callback para processar captura atual"""
        if not self.current_capture_path:
            messagebox.showwarning("Aviso", "Nenhuma captura selecionada para processar")
            return

        try:
            self._set_processing_status("Processando captura...")
            self.btn_process.configure(state="disabled")
            self.progress_bar.set(0)

            # Executar processamento em thread
            threading.Thread(
                target=self._process_capture_thread,
                args=(self.current_capture_path,),
                daemon=True
            ).start()

        except Exception as e:
            logger.error(f"Erro ao iniciar processamento: {e}")
            self._reset_process_button()

    def _process_capture_thread(self, image_path: str):
        """Thread para processamento da captura"""
        try:
            # Passo 1: OCR
            self.root.after(0, lambda: self._update_progress(0.2, "Executando OCR..."))
            ocr_result = ocr_processor.process_image(image_path)

            if not ocr_result:
                self.root.after(0, lambda: self._on_processing_error("Falha no OCR"))
                return

            # Passo 2: Análise de dados
            self.root.after(0, lambda: self._update_progress(0.6, "Analisando dados..."))
            text = ocr_result.get('cleaned_text', '')
            analysis_result = data_analyzer.analyze_text(text)

            # Passo 3: Organização
            self.root.after(0, lambda: self._update_progress(0.9, "Organizando dados..."))
            # (Organização será feita quando necessário)

            # Sucesso
            self.root.after(0, lambda: self._on_processing_success(ocr_result, analysis_result))

        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            self.root.after(0, lambda: self._on_processing_error(str(e)))

    def _on_export_data(self):
        """Callback para exportar dados"""
        if not self.current_capture_path:
            messagebox.showwarning("Aviso", "Nenhuma captura selecionada para exportar")
            return

        try:
            # Obter dados organizados
            capture_id = self._get_current_capture_id()
            if not capture_id:
                messagebox.showwarning("Aviso", "ID da captura não encontrado")
                return

            organized_data = data_organizer.organize_capture_data(capture_id)

            # Diálogo para escolher formato
            format_choice = self._show_export_format_dialog()
            if not format_choice:
                return

            # Exportar
            export_path = data_organizer.export_data(organized_data, format_choice)

            if export_path:
                messagebox.showinfo("Sucesso", f"Dados exportados com sucesso!\n\nArquivo: {export_path}")
            else:
                messagebox.showerror("Erro", "Falha na exportação dos dados")

        except Exception as e:
            logger.error(f"Erro na exportação: {e}")
            messagebox.showerror("Erro", f"Erro na exportação: {e}")

    def _show_export_format_dialog(self) -> Optional[str]:
        """Mostra diálogo para escolher formato de exportação"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Escolher Formato de Exportação")
        dialog.geometry("300x200")
        dialog.resizable(False, False)

        # Centralizar diálogo
        dialog.transient(self.root)
        dialog.grab_set()

        label = ctk.CTkLabel(dialog, text="Escolha o formato de exportação:")
        label.pack(pady=20)

        format_var = tk.StringVar(value="json")

        formats = [
            ("JSON", "json"),
            ("CSV", "csv"),
            ("Excel", "excel"),
            ("PDF", "pdf"),
            ("Texto", "txt")
        ]

        for text, value in formats:
            rb = ctk.CTkRadioButton(dialog, text=text, variable=format_var, value=value)
            rb.pack(pady=5)

        result = [None]

        def on_ok():
            result[0] = format_var.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, pady=20, padx=20)

        ok_btn = ctk.CTkButton(buttons_frame, text="OK", command=on_ok, width=80)
        ok_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancelar", command=on_cancel, width=80)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        self.root.wait_window(dialog)
        return result[0]

    def _on_open_settings(self):
        """Abre janela de configurações"""
        # TODO: Implementar janela de configurações
        messagebox.showinfo("Configurações", "Janela de configurações será implementada em breve")

    def _refresh_captures_list(self):
        """Atualiza lista de capturas"""
        try:
            self.captures_listbox.delete(0, tk.END)

            # Buscar capturas recentes
            captures = db_manager.get_recent_captures(50)

            for capture in captures:
                # Formatar texto para lista
                timestamp = capture.created_at.strftime("%d/%m/%Y %H:%M") if capture.created_at else "N/A"
                status = capture.processing_status
                filename = capture.filename

                display_text = f"{timestamp} - {filename} ({status})"
                self.captures_listbox.insert(tk.END, display_text)

                # Armazenar ID da captura como metadata
                self.captures_listbox.itemconfig(tk.END, {'tags': (str(capture.id),)})

            # Atualizar contador de status
            self._update_status_bar()

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de capturas: {e}")

    def _on_capture_selected(self, event):
        """Callback quando uma captura é selecionada"""
        try:
            selection = self.captures_listbox.curselection()
            if not selection:
                return

            # Obter ID da captura da tag
            item_tags = self.captures_listbox.itemcget(selection[0], 'tags')
            if item_tags:
                capture_id = int(item_tags.split()[0])

                # Buscar captura no banco
                session = db_manager.get_session()
                capture = session.query(db_manager.Capture).filter(db_manager.Capture.id == capture_id).first()
                db_manager.close_session(session)

                if capture:
                    self.current_capture_path = capture.file_path
                    self._display_capture(capture)
                    self._load_capture_data(capture_id)

                    # Habilitar botões
                    self.btn_process.configure(state="normal")
                    self.btn_export.configure(state="normal")

        except Exception as e:
            logger.error(f"Erro ao selecionar captura: {e}")

    def _display_capture(self, capture):
        """Exibe captura no preview"""
        try:
            # Limpar canvas
            self.preview_canvas.delete("all")
            self.preview_label.place_forget()

            # Carregar e exibir imagem
            image = Image.open(capture.file_path)

            # Redimensionar para caber no canvas
            canvas_width = self.preview_canvas.winfo_width() or 400
            canvas_height = self.preview_canvas.winfo_height() or 300

            image_ratio = image.width / image.height
            canvas_ratio = canvas_width / canvas_height

            if image_ratio > canvas_ratio:
                new_width = canvas_width
                new_height = int(canvas_width / image_ratio)
            else:
                new_height = canvas_height
                new_width = int(canvas_height * image_ratio)

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Converter para PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Centralizar imagem
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2

            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.preview_canvas.image = photo  # Manter referência

        except Exception as e:
            logger.error(f"Erro ao exibir captura: {e}")
            self.preview_label.configure(text="Erro ao carregar imagem")
            self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def _load_capture_data(self, capture_id: int):
        """Carrega dados da captura selecionada"""
        try:
            # Limpar dados anteriores
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            self.ocr_text.delete("0.0", tk.END)

            # Buscar dados extraídos
            session = db_manager.get_session()
            extracted_data = session.query(db_manager.ExtractedData)\
                                  .filter(db_manager.ExtractedData.capture_id == capture_id)\
                                  .all()

            # Buscar resultado OCR
            ocr_result = session.query(db_manager.OCRResult)\
                              .filter(db_manager.OCRResult.capture_id == capture_id)\
                              .first()

            db_manager.close_session(session)

            # Preencher treeview de dados
            for item in extracted_data:
                self.data_tree.insert("", tk.END, values=(
                    item.field_name,
                    item.field_value,
                    item.data_type,
                    ".2f"
                ))

            # Preencher texto OCR
            if ocr_result:
                self.ocr_text.insert("0.0", ocr_result.cleaned_text or ocr_result.raw_text or "")

        except Exception as e:
            logger.error(f"Erro ao carregar dados da captura: {e}")

    def _on_delete_capture(self):
        """Exclui captura selecionada"""
        try:
            selection = self.captures_listbox.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Nenhuma captura selecionada")
                return

            if not messagebox.askyesno("Confirmar", "Deseja realmente excluir esta captura?"):
                return

            # Obter ID da captura
            item_tags = self.captures_listbox.itemcget(selection[0], 'tags')
            capture_id = int(item_tags.split()[0])

            # Excluir do banco (cascade delete)
            session = db_manager.get_session()
            capture = session.query(db_manager.Capture).filter(db_manager.Capture.id == capture_id).first()
            if capture:
                # Remover arquivo físico
                Path(capture.file_path).unlink(missing_ok=True)
                session.delete(capture)
                session.commit()

            db_manager.close_session(session)

            # Atualizar lista
            self._refresh_captures_list()

            # Limpar seleção atual se foi a excluída
            if self.current_capture_path and str(capture_id) in item_tags:
                self.current_capture_path = None
                self.btn_process.configure(state="disabled")
                self.btn_export.configure(state="disabled")

        except Exception as e:
            logger.error(f"Erro ao excluir captura: {e}")
            messagebox.showerror("Erro", f"Erro ao excluir captura: {e}")

    def _get_current_capture_id(self) -> Optional[int]:
        """Obtém ID da captura atualmente selecionada"""
        try:
            selection = self.captures_listbox.curselection()
            if selection:
                item_tags = self.captures_listbox.itemcget(selection[0], 'tags')
                return int(item_tags.split()[0])
        except Exception:
            pass
        return None

    def _on_capture_completed(self, capture_path: str):
        """Callback chamado quando captura é completada"""
        self.current_capture_path = capture_path
        self.root.after(0, lambda: self._on_capture_success(capture_path))

    def _on_recording_completed(self, recording_path: str):
        """Callback chamado quando gravação é completada"""
        self.recording_active = False
        self.root.after(0, lambda: self._on_recording_success(recording_path))

    def _on_capture_success(self, capture_path: str):
        """Tratamento de sucesso na captura"""
        self._set_processing_status(f"Captura salva: {Path(capture_path).name}")
        self._reset_capture_button()
        self._refresh_captures_list()

        # Selecionar a captura recém-criada
        # (Implementação simplificada - em produção seria mais robusta)

    def _on_capture_error(self):
        """Tratamento de erro na captura"""
        self._set_processing_status("Erro na captura")
        self._reset_capture_button()
        messagebox.showerror("Erro", "Falha na captura de tela")

    def _on_recording_success(self, recording_path: str):
        """Tratamento de sucesso na gravação"""
        self._set_processing_status(f"Gravação salva: {Path(recording_path).name}")
        self.btn_record.configure(text="🎬 Gravar Tela", fg_color=["#3B8ED0", "#1F6AA5"])
        self._refresh_captures_list()

    def _on_processing_success(self, ocr_result: Dict, analysis_result: Dict):
        """Tratamento de sucesso no processamento"""
        self._set_processing_status("Processamento concluído")
        self._reset_process_button()
        self.progress_bar.set(1.0)

        # Atualizar interface com resultados
        self._load_capture_data(self._get_current_capture_id())

    def _on_processing_error(self, error_msg: str):
        """Tratamento de erro no processamento"""
        self._set_processing_status(f"Erro no processamento: {error_msg}")
        self._reset_process_button()
        self.progress_bar.set(0)
        messagebox.showerror("Erro", f"Erro no processamento: {error_msg}")

    def _update_progress(self, value: float, message: str):
        """Atualiza barra de progresso"""
        self.progress_bar.set(value)
        self._set_processing_status(message)

    def _set_processing_status(self, message: str):
        """Define mensagem de status"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()

    def _reset_capture_button(self):
        """Reseta botão de captura"""
        self.btn_capture.configure(state="normal", text="📸 Capturar Tela")

    def _reset_process_button(self):
        """Reseta botão de processamento"""
        self.btn_process.configure(state="normal", text="⚙️ Processar")

    def _update_status_bar(self):
        """Atualiza informações da barra de status"""
        try:
            # Contar capturas
            session = db_manager.get_session()
            total_captures = session.query(db_manager.Capture).count()
            db_manager.close_session(session)

            self.status_captures.configure(text=f"Capturas: {total_captures}")

            # Status do engine OCR
            engine_status = "OK" if ocr_processor.get_available_engines() else "Indisponível"
            self.status_engine.configure(text=f"OCR: {engine_status}")

        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")

    def _on_open_capture(self):
        """Abre arquivo de captura"""
        file_path = filedialog.askopenfilename(
            title="Abrir Captura",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if file_path:
            self.current_capture_path = file_path
            # TODO: Implementar carregamento de arquivo externo

    def _on_edit_data(self):
        """Edita dados extraídos"""
        # TODO: Implementar edição de dados
        messagebox.showinfo("Editar", "Funcionalidade de edição será implementada em breve")

    def _on_validate_data(self):
        """Valida dados extraídos"""
        # TODO: Implementar validação de dados
        messagebox.showinfo("Validar", "Funcionalidade de validação será implementada em breve")

    def _on_copy_ocr_text(self):
        """Copia texto OCR para clipboard"""
        try:
            text = self.ocr_text.get("0.0", tk.END).strip()
            if text:
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                messagebox.showinfo("Sucesso", "Texto copiado para a área de transferência")
            else:
                messagebox.showwarning("Aviso", "Nenhum texto para copiar")
        except Exception as e:
            logger.error(f"Erro ao copiar texto: {e}")

    def _on_save_ocr_text(self):
        """Salva texto OCR em arquivo"""
        try:
            text = self.ocr_text.get("0.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Aviso", "Nenhum texto para salvar")
                return

            file_path = filedialog.asksaveasfilename(
                title="Salvar Texto OCR",
                defaultextension=".txt",
                filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("Sucesso", f"Texto salvo em: {file_path}")

        except Exception as e:
            logger.error(f"Erro ao salvar texto: {e}")

    def _on_global_capture_hotkey(self):
        """Callback para hotkey global de captura"""
        self.root.after(0, self._on_capture_screen)

    def _on_escape_pressed(self):
        """Callback para tecla Escape"""
        # Cancelar operações em andamento se necessário
        pass

    def _on_exit(self):
        """Callback para sair da aplicação"""
        if messagebox.askyesno("Sair", "Deseja realmente sair da aplicação?"):
            self.root.quit()

    def _on_show_about(self):
        """Mostra janela Sobre"""
        about_text = """
        Leitor de Tela Inteligente v1.0.0

        Uma ferramenta avançada para captura, processamento
        e análise de dados da tela do computador.

        Desenvolvido para extrair informações estruturadas
        de qualquer conteúdo visual, funcionando mesmo quando
        APIs/sites bloqueiam extração tradicional.

        Funcionalidades:
        • Captura de tela inteligente
        • OCR multilíngue
        • Análise de dados automática
        • Exportação em múltiplos formatos
        • Interface moderna e intuitiva

        Tecnologia: Python + IA + Visão Computacional
        """

        messagebox.showinfo("Sobre", about_text)

    def _on_show_docs(self):
        """Abre documentação"""
        # TODO: Implementar abertura de documentação
        messagebox.showinfo("Documentação", "Documentação será implementada em breve")

    def run(self):
        """Executa a aplicação"""
        try:
            # Carregar dados iniciais
            self._refresh_captures_list()
            self._update_status_bar()

            # Iniciar loop principal
            self.root.mainloop()

        except Exception as e:
            logger.error(f"Erro na execução da aplicação: {e}")
            messagebox.showerror("Erro Fatal", f"Erro na execução: {e}")

# Instância global da janela principal
main_window = MainWindow()
