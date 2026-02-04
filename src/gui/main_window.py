"""
Janela principal da interface gráfica
Interface principal do Jarvis 5.0
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
from src.core.camera_controller import camera_controller
from src.core.gesture_controller import gesture_controller
from src.core.neural_memory import neural_memory
from src.database.models import db_manager, Capture
from src.gui.theme import COLORS, FONTS, DIMENSIONS 

logger = logging.getLogger(__name__)

class MainWindow:
    """Janela principal da aplicação"""

    def __init__(self):
        # Configurar aparência - Midnight Jarvis Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title("JARVIS 5.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # --- FRAMELESS CONFIGURATION (STARK STYLE) ---
        self.root.overrideredirect(True) # Remove borda padrão do Windows
        self.root.configure(fg_color=COLORS.BG_MAIN)
        
        # Variáveis de controle de movimento da janela
        self._offsetx = 0
        self._offsety = 0

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
        # 1. Custom Title Bar (Essential for Frameless)
        self._create_title_bar()
        
        # Container para o resto da interface (abaixo da title bar)
        self.body_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar Navigation Panel
        self._create_sidebar(self.body_frame)

        # Container principal de conteúdo (lado direito)
        self.main_container = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.main_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        # Barra de ferramentas superior (compacta)
        self._create_toolbar()

        # Área principal de exibição
        self._create_main_area()

        # Barra de status inferior
        self._create_status_bar()
        
    def _create_title_bar(self):
        """Cria barra de título personalizada estilo Stark"""
        self.title_bar = ctk.CTkFrame(self.root, height=DIMENSIONS.TITLE_BAR_HEIGHT, corner_radius=0, fg_color=COLORS.BG_SIDEBAR)
        self.title_bar.pack(side=tk.TOP, fill=tk.X)
        self.title_bar.pack_propagate(False)
        
        # Eventos de arrastar janela
        self.title_bar.bind("<Button-1>", self._start_move)
        self.title_bar.bind("<B1-Motion>", self._do_move)

        # Título da Janela
        title_lbl = ctk.CTkLabel(
            self.title_bar, text="JARVIS 5.0 | MARK V PROTOCOL",
            font=ctk.CTkFont(family=FONTS.FAMILY_DISPLAY, size=12, weight="bold"),
            text_color=COLORS.TEXT_SUB
        )
        title_lbl.pack(side=tk.LEFT, padx=15)
        title_lbl.bind("<Button-1>", self._start_move)
        title_lbl.bind("<B1-Motion>", self._do_move)

        # Botões da Janela (Fechar, Minimizar)
        close_btn = ctk.CTkButton(
            self.title_bar, text="✕", width=40, height=DIMENSIONS.TITLE_BAR_HEIGHT,
            fg_color="transparent", hover_color=COLORS.ERROR,
            command=self._on_exit, corner_radius=0
        )
        close_btn.pack(side=tk.RIGHT)
        
        min_btn = ctk.CTkButton(
            self.title_bar, text="─", width=40, height=DIMENSIONS.TITLE_BAR_HEIGHT,
            fg_color="transparent", hover_color=COLORS.BG_CARD_HOVER,
            command=self.root.iconify, corner_radius=0
        )
        min_btn.pack(side=tk.RIGHT)

    def _start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def _do_move(self, event):
        x = self.root.winfo_x() + (event.x - self._offsetx)
        y = self.root.winfo_y() + (event.y - self._offsety)
        self.root.geometry(f"+{x}+{y}")

    def _create_sidebar(self, parent):
        """Cria barra lateral de navegação premium"""
        self.sidebar = ctk.CTkFrame(parent, width=DIMENSIONS.SIDEBAR_WIDTH, corner_radius=0, fg_color=COLORS.BG_SIDEBAR)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Logo / Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="J.A.R.V.I.S.", 
            font=ctk.CTkFont(size=28, weight="bold", family=FONTS.FAMILY_DISPLAY),
            text_color=COLORS.PRIMARY
        )
        self.logo_label.pack(pady=(30, 10))
        
        ctk.CTkLabel(self.sidebar, text="STARK INDUSTRIES", 
                     font=ctk.CTkFont(size=10), text_color=COLORS.TEXT_SUB).pack(pady=(0, 30))

        # Botões da Sidebar
        self.nav_buttons = {}
        nav_items = [
            ("📸 CAPTURAS", "preview"),
            ("🤖 IA AGENT", "ai"),
            ("🖖 GESTOS", "gestures"),
            ("🧠 MEMÓRIA", "memories"),
            ("⚙️ SISTEMA", "settings")
        ]

        for text, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=text,
                fg_color="transparent",
                text_color=COLORS.TEXT_MAIN,
                hover_color=COLORS.BG_CARD_HOVER,
                anchor="w",
                font=ctk.CTkFont(family=FONTS.FAMILY, size=FONTS.BODY),
                height=DIMENSIONS.BUTTON_HEIGHT,
                command=lambda k=key: self._on_nav_click(k)
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
            self.nav_buttons[key] = btn

        # Versão no rodapé
        self.version_label = ctk.CTkLabel(
            self.sidebar, text="MARK V | v5.0.0",
            font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=10),
            text_color=COLORS.TEXT_SUB
        )
        self.version_label.pack(side=tk.BOTTOM, pady=(0, 20))

        # System Health Monitor (Novo)
        self._create_sidebar_health_monitor()

    def _create_sidebar_health_monitor(self):
        """Cria monitor de saúde do sistema na sidebar"""
        self.health_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.health_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        
        ctk.CTkLabel(self.health_frame, text="SYSTEM DIAGNOSTICS", 
                     font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=9, weight="bold"), 
                     text_color=COLORS.TEXT_SUB).pack(anchor="w", padx=5)
        
        self.lbl_cpu = ctk.CTkLabel(self.health_frame, text="CPU: --%", 
                                  font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=10), 
                                  text_color=COLORS.TEXT_MAIN)
        self.lbl_cpu.pack(anchor="w", padx=5)
        
        self.lbl_gpu = ctk.CTkLabel(self.health_frame, text="GPU: --", 
                                  font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=10), 
                                  text_color=COLORS.TEXT_MAIN)
        self.lbl_gpu.pack(anchor="w", padx=5)
        
        self.lbl_brain = ctk.CTkLabel(self.health_frame, text="BRAIN: ONLINE", 
                                    font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=10), 
                                    text_color=COLORS.SUCCESS)
        self.lbl_brain.pack(anchor="w", padx=5)
        
        # Iniciar atualização periódica
        self._update_health_stats()

    def _update_health_stats(self):
        """Atualiza estatísticas de hardware em tempo real"""
        try:
            import psutil
            cpu_usage = psutil.cpu_percent()
            self.lbl_cpu.configure(text=f"CPU: {cpu_usage}%")
            
            # RAM Usage
            ram = psutil.virtual_memory()
            ram_usage = ram.percent
            
            hw_status = hardware_manager.get_status()
            self.lbl_gpu.configure(text=f"GPU: {hw_status['device'].upper()} | RAM: {ram_usage}%")
            
            # Provider Status
            provider = "Local" if not ai_agent.gemini_handler else "Gemini"
            self.lbl_brain.configure(text=f"BRAIN: {provider}")
            
            # Agendar próxima atualização
            self.root.after(5000, self._update_health_stats)
        except Exception:
            pass

    def _on_nav_click(self, key):
        """Gerencia clique na navegação lateral com feedback do Orb"""
        # Resetar estilos
        for k, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent", text_color=COLORS.TEXT_MAIN)
        
        # Destacar selecionado
        self.nav_buttons[key].configure(fg_color=COLORS.BG_CARD_HOVER, text_color=COLORS.PRIMARY)
        
        # Mudar estado do orb se for IA
        if key == "ai":
            self._set_orb_state("idle")
        
        # Mudar aba (Map keys to Tab Names defined in _create_results_panel)
        tab_map = {
            "preview": "PREVIEW",
            "ai": "AI AGENT",
            "gestures": "GESTURES",
            "memories": "MEMORY"
        }
        
        if key == "settings":
            self._on_open_settings()
        elif key in tab_map:
            self.results_notebook.set(tab_map[key])

    def _create_toolbar(self):
        """Cria barra de ferramentas futurista"""
        toolbar = ctk.CTkFrame(self.main_container, height=60, fg_color=COLORS.BG_CARD, corner_radius=DIMENSIONS.CORNER_RADIUS)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Dashboard Label
        dash_label = ctk.CTkLabel(toolbar, text="COMMAND CENTER", 
                                font=ctk.CTkFont(family=FONTS.FAMILY_DISPLAY, size=FONTS.H3, weight="bold"), 
                                text_color=COLORS.TEXT_MAIN)
        dash_label.pack(side=tk.LEFT, padx=20)

        # Botões principais
        button_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        button_frame.pack(side=tk.LEFT, padx=10)

        # Botão Capturar Tela - Estilo Premium
        self.btn_capture = ctk.CTkButton(
            button_frame, text="⚡ INITIALIZE CAPTURE",
            command=self._on_capture_screen,
            font=ctk.CTkFont(family=FONTS.FAMILY, size=FONTS.BODY, weight="bold"),
            fg_color=COLORS.PRIMARY,
            text_color=COLORS.BG_MAIN,
            hover_color=COLORS.PRIMARY_HOVER,
            width=180, height=DIMENSIONS.BUTTON_HEIGHT,
            corner_radius=DIMENSIONS.CORNER_RADIUS
        )
        self.btn_capture.pack(side=tk.LEFT, padx=5)

        self.btn_record = ctk.CTkButton(
            button_frame, text="🔴 REC BUFFER",
            command=self._on_toggle_recording,
            font=ctk.CTkFont(family=FONTS.FAMILY, size=FONTS.BODY, weight="bold"),
            fg_color=COLORS.BG_MAIN,
            text_color=COLORS.ERROR,
            hover_color=COLORS.BG_CARD_HOVER,
            border_width=1,
            border_color=COLORS.ERROR,
            width=120, height=DIMENSIONS.BUTTON_HEIGHT,
            corner_radius=DIMENSIONS.CORNER_RADIUS
        )
        self.btn_record.pack(side=tk.LEFT, padx=5)

        # Botões de processamento (Lado Direito)
        self.btn_export = ctk.CTkButton(
            toolbar, text="EXPORT DATA",
            command=self._on_export_data,
            state="disabled",
            font=ctk.CTkFont(family=FONTS.FAMILY, size=FONTS.BODY),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS.BORDER_SUBTLE,
            text_color=COLORS.TEXT_SUB,
            width=120, height=DIMENSIONS.BUTTON_HEIGHT,
            corner_radius=DIMENSIONS.CORNER_RADIUS
        )
        self.btn_export.pack(side=tk.RIGHT, padx=5)

        self.btn_process = ctk.CTkButton(
            toolbar, text="RUN NEURAL NET",
            command=self._on_process_capture,
            state="disabled",
            font=ctk.CTkFont(family=FONTS.FAMILY, size=FONTS.BODY, weight="bold"),
            fg_color=COLORS.BG_MAIN,
            hover_color=COLORS.BG_CARD_HOVER,
            text_color=COLORS.PRIMARY,
            border_width=1,
            border_color=COLORS.PRIMARY,
            width=140, height=DIMENSIONS.BUTTON_HEIGHT,
            corner_radius=DIMENSIONS.CORNER_RADIUS
        )
        self.btn_process.pack(side=tk.RIGHT, padx=5)

    def _create_main_area(self):
        """Cria área principal da interface"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Painel esquerdo - Lista de capturas
        self._create_captures_panel(main_frame)

        # Painel direito - Visualização e resultados
        self._create_results_panel(main_frame)

    def _create_captures_panel(self, parent):
        """Cria painel de lista de capturas"""
        left_panel = ctk.CTkFrame(parent, width=320, fg_color=COLORS.BG_CARD, corner_radius=DIMENSIONS.CORNER_RADIUS)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)

        # Título
        title_label = ctk.CTkLabel(
            left_panel, text="DATA FEED",
            font=ctk.CTkFont(family=FONTS.FAMILY_DISPLAY, size=14, weight="bold"),
            text_color=COLORS.TEXT_SUB
        )
        title_label.pack(pady=(15, 10), padx=15, anchor="w")

        # Container de Capturas (Scrollable)
        self.captures_scroll = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent",
            label_text=None
        )
        self.captures_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mapeamento para guardar referências aos widgets de card
        self.capture_cards = {}

        # Botões de ação (Compactos)
        buttons_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        self.btn_refresh_captures = ctk.CTkButton(
            buttons_frame, text="🔄",
            command=self._refresh_captures_list,
            width=40, height=30,
            fg_color=COLORS.BG_MAIN,
            text_color=COLORS.TEXT_MAIN,
            hover_color=COLORS.BG_CARD_HOVER,
            corner_radius=DIMENSIONS.CORNER_RADIUS
        )
        self.btn_refresh_captures.pack(side=tk.LEFT, padx=2)

        self.btn_delete_capture = ctk.CTkButton(
            buttons_frame, text="DELETE",
            command=self._on_delete_capture,
            fg_color=COLORS.ERROR,
            text_color=COLORS.TEXT_MAIN,
            hover_color="#B00020",
            height=30,
            font=ctk.CTkFont(family=FONTS.FAMILY, size=FONTS.SMALL, weight="bold"),
            state="disabled",
            corner_radius=DIMENSIONS.CORNER_RADIUS
        )
        self.btn_delete_capture.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

    def _create_results_panel(self, parent):
        """Cria painel de visualização de resultados"""
        right_panel = ctk.CTkFrame(parent, fg_color="transparent")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook para abas (TODO: Custom Tabview for complete Stark Look)
        # Using basic ttk Notebook for now but styled dark via theme
        self.results_notebook = ctk.CTkTabview(right_panel, corner_radius=DIMENSIONS.CORNER_RADIUS, fg_color=COLORS.BG_CARD)
        self.results_notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Tabs
        self.results_notebook.add("PREVIEW")
        self.results_notebook.add("DATA")
        self.results_notebook.add("OCR")
        self.results_notebook.add("AI AGENT")
        self.results_notebook.add("GESTURES")
        self.results_notebook.add("MEMORY")

        # Aba de Visualização
        self._create_preview_tab(self.results_notebook.tab("PREVIEW"))

        # Aba de Dados Extraídos
        self._create_data_tab(self.results_notebook.tab("DATA"))

        # Aba de OCR
        self._create_ocr_tab(self.results_notebook.tab("OCR"))

        # Aba de IA Agent (NOVO)
        self._create_ai_agent_tab(self.results_notebook.tab("AI AGENT")) # Ajustado para passar parent

        # Aba de Gestos (NOVO)
        self._create_gesture_tab(self.results_notebook.tab("GESTURES"))

        # Aba de Memórias (EVOLUÇÃO)
        self._create_memories_tab(self.results_notebook.tab("MEMORY"))
    
    def _create_preview_tab(self, parent):
        """Cria aba de visualização da captura"""
        # Área de imagem
        self.preview_canvas = tk.Canvas(
            parent,
            bg=COLORS.BG_MAIN,
            highlightthickness=0,
            bd=0
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Label para quando não há imagem
        self.preview_label = ctk.CTkLabel(
            self.preview_canvas,
            text="NO SIGNAL INPUT\n\nINITIALIZE CAPTURE PROTOCOL",
            font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=12),
            text_color=COLORS.TEXT_SUB
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Barra de progresso para processamento
        self.progress_bar = ctk.CTkProgressBar(parent, width=400, progress_color=COLORS.PRIMARY)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Label de status
        self.status_label = ctk.CTkLabel(
            parent,
            text="SYSTEM READY",
            font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=10),
            text_color=COLORS.SUCCESS
        )
        self.status_label.pack(pady=5)

    def _create_data_tab(self, parent):
        """Cria aba de dados extraídos"""
        # Treeview para dados
        columns = ("Campo", "Valor", "Tipo", "Confiança")
        self.data_tree = ttk.Treeview(parent, columns=columns, show="headings", height=20)

        # Configurar colunas
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Botões de ação
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        self.btn_edit_data = ctk.CTkButton(
            buttons_frame, text="✏️ EDIT ENTRY",
            command=self._on_edit_data,
            width=100,
            fg_color=COLORS.BG_MAIN,
            hover_color=COLORS.BG_CARD_HOVER,
            corner_radius=DIMENSIONS.CORNER_RADIUS,
            border_width=1,
            border_color=COLORS.BORDER_SUBTLE
        )
        self.btn_edit_data.pack(side=tk.LEFT, padx=5)

        self.btn_validate_data = ctk.CTkButton(
            buttons_frame, text="✅ VALIDATE",
            command=self._on_validate_data,
            width=100,
            fg_color=COLORS.SUCCESS,
            text_color="#000000",
            hover_color="#00C853",
            corner_radius=DIMENSIONS.CORNER_RADIUS
        )
        self.btn_validate_data.pack(side=tk.LEFT, padx=5)

    def _create_ocr_tab(self, parent=None):
        """Cria aba de resultados OCR"""
        if parent is None:
             parent = ctk.CTkFrame(self.results_notebook)
             self.results_notebook.add(parent, text="📝 OCR")

        # Área de texto para OCR
        self.ocr_text = ctk.CTkTextbox(parent, wrap="word", fg_color=COLORS.BG_MAIN, text_color=COLORS.TEXT_MAIN, font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=12))
        self.ocr_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Botões de controle
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        self.btn_copy_ocr = ctk.CTkButton(
            controls_frame, text="📋 COPY",
            command=self._on_copy_ocr_text,
            width=120,
            fg_color=COLORS.BG_MAIN,
            hover_color=COLORS.BG_CARD_HOVER,
            corner_radius=DIMENSIONS.CORNER_RADIUS,
            border_width=1,
            border_color=COLORS.BORDER_SUBTLE
        )
        self.btn_copy_ocr.pack(side=tk.LEFT, padx=5)

        self.btn_save_ocr = ctk.CTkButton(
            controls_frame, text="💾 SAVE LOG",
            command=self._on_save_ocr_text,
            width=120,
            fg_color=COLORS.BG_MAIN,
            hover_color=COLORS.BG_CARD_HOVER,
            corner_radius=DIMENSIONS.CORNER_RADIUS,
            border_width=1,
            border_color=COLORS.BORDER_SUBTLE
        )
        self.btn_save_ocr.pack(side=tk.LEFT, padx=5)

    def _create_ai_agent_tab(self, parent):
        """Cria aba de interação com o Agente de IA com o Orb Pulsante"""
        # Top Section: Jarvis Orb
        orb_container = ctk.CTkFrame(parent, fg_color="transparent", height=200)
        orb_container.pack(fill=tk.X, pady=20)
        
        self.orb_canvas = tk.Canvas(orb_container, width=150, height=150, bg=COLORS.BG_CARD, highlightthickness=0)
        self.orb_canvas.pack(pady=10)
        
        # Desenhar Orb Inicial
        self.orb_color = COLORS.PRIMARY
        self.orb_radius = 50
        self.orb_growth = 1
        self.orb_id = self.orb_canvas.create_oval(25, 25, 125, 125, fill="", outline=COLORS.PRIMARY, width=2)
        self.glow_id = self.orb_canvas.create_oval(10, 10, 140, 140, fill="", outline=COLORS.PRIMARY, width=1, dash=(4, 4))
        
        self._animate_orb()

        # Histórico de Chat (Estilo futurista)
        self.chat_history = ctk.CTkTextbox(
            parent, wrap="word", state="disabled", 
            fg_color=COLORS.BG_MAIN, 
            border_width=1, border_color=COLORS.BORDER_SUBTLE, 
            font=ctk.CTkFont(family=FONTS.FAMILY, size=13)
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=30, pady=(10, 20))

        # Container de Entrada
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.chat_input = ctk.CTkEntry(
            input_frame, placeholder_text="Awaiting command...",
            fg_color=COLORS.BG_MAIN, border_color=COLORS.BORDER_SUBTLE,
            text_color=COLORS.TEXT_MAIN
        )
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind("<Return>", lambda e: self._on_send_command())

        # Botão de Microfone (Jarvis)
        self.btn_mic = ctk.CTkButton(
            input_frame, text="🎤", width=40, command=self._on_toggle_voice,
            fg_color=COLORS.BG_MAIN, hover_color=COLORS.BG_CARD_HOVER,
            corner_radius=DIMENSIONS.CORNER_RADIUS, border_width=1, border_color=COLORS.BORDER_SUBTLE
        )
        self.btn_mic.pack(side=tk.LEFT, padx=5)

        self.btn_send = ctk.CTkButton(
            input_frame, text="SEND", width=80, command=self._on_send_command,
            fg_color=COLORS.PRIMARY, text_color=COLORS.BG_MAIN, hover_color=COLORS.PRIMARY_HOVER,
            corner_radius=DIMENSIONS.CORNER_RADIUS
        )
        self.btn_send.pack(side=tk.RIGHT)
        
        # Registrar callback de voz
        voice_controller.on_speech_recognized = self._on_voice_recognized

    def _animate_orb(self):
        """Animação pulsante do Orb do Jarvis"""
        if not hasattr(self, 'orb_canvas'): return
        
        # Pulsação do Radius
        self.orb_radius += self.orb_growth
        if self.orb_radius > 55 or self.orb_radius < 45:
            self.orb_growth *= -1
            
        r = self.orb_radius
        self.orb_canvas.coords(self.orb_id, 75-r, 75-r, 75+r, 75+r)
        
        # Rotação do Glow Circle
        self.orb_canvas.itemconfig(self.orb_id, outline=self.orb_color)
        self.orb_canvas.itemconfig(self.glow_id, outline=self.orb_color)
        
        # Agendar próximo frame
        self.root.after(50, self._animate_orb)

    def _set_orb_state(self, state):
        """Muda a cor do orb baseado no estado (idle, thinking, alert)"""
        if state == "thinking":
            self.orb_color = "#00ffff" # Cyan
        elif state == "alert":
            self.orb_color = "#ff4b4b" # Red
        else:
            self.orb_color = COLORS.PRIMARY # Blue

    def _create_gesture_tab(self, parent):
        """Cria aba de treinamento e visualização de gestos"""
        # Container principal
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Lado Esquerdo: Vídeo
        video_frame = ctk.CTkFrame(container, fg_color=COLORS.BG_MAIN, corner_radius=DIMENSIONS.CORNER_RADIUS)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.gesture_video_label = ctk.CTkLabel(video_frame, text="VISUAL SENSORS OFFLINE", font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=14), text_color=COLORS.TEXT_SUB)
        self.gesture_video_label.pack(fill=tk.BOTH, expand=True)

        # Lado Direito: Controles e Info
        controls_frame = ctk.CTkFrame(container, width=250, fg_color="transparent")
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        ctk.CTkLabel(controls_frame, text="SENSOR STATUS", font=ctk.CTkFont(family=FONTS.FAMILY_MONO, weight="bold"), text_color=COLORS.TEXT_MAIN).pack(pady=10)
        
        self.lbl_gesture_status = ctk.CTkLabel(controls_frame, text="LAST INPUT: NONE", font=ctk.CTkFont(family=FONTS.FAMILY, size=14, weight="bold"), text_color=COLORS.PRIMARY)
        self.lbl_gesture_status.pack(pady=5)

        ctk.CTkLabel(controls_frame, text="ACTIVE GESTURES:", font=ctk.CTkFont(family=FONTS.FAMILY_MONO, size=12), text_color=COLORS.TEXT_SUB).pack(pady=(20, 5))
        gestures_info = [
            "👍 THUMB_UP: CONFIRM",
            "✋ OPEN_PALM: HALT",
            "✊ FIST: SCROLL (WIP)"
        ]
        text_info = "\n".join(gestures_info)
        ctk.CTkTextbox(controls_frame, height=100, fg_color=COLORS.BG_MAIN, text_color=COLORS.TEXT_SUB).insert("0.0", text_info) # Apenas visual
        
        # Switch para ativar visualização
        self.switch_camera_view = ctk.CTkSwitch(
            controls_frame, 
            text="Visual Debug",
            command=self._toggle_camera_view,
            progress_color=COLORS.PRIMARY,
            button_color=COLORS.PRIMARY_HOVER,
            button_hover_color=COLORS.PRIMARY_HOVER
        )
        self.switch_camera_view.pack(pady=20)
        self.switch_camera_view.select() # Já inicia ativado se possível
        self._toggle_camera_view()

    def _toggle_camera_view(self):
        """Ativa/Desativa feed de vídeo na GUI"""
        if self.switch_camera_view.get():
            camera_controller.on_frame_ready = self._update_video_feed
            if not camera_controller.is_monitoring:
                 camera_controller.start_monitoring()
        else:
            camera_controller.on_frame_ready = None
            self.gesture_video_label.configure(image=None, text="Visualização Pausada")

    def _update_video_feed(self, frame_rgb):
        """Atualiza label de vídeo com frame processado (vem da thread da câmera)"""
        try:
            # Redimensionar para caber na label (fixo por enquanto para performance)
            # Ideal seria redimensionar dinamicamente
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 480)) 
            photo = ImageTk.PhotoImage(image=img)
            
            # Atualizar GUI na thread principal
            self.root.after(0, lambda: self._update_gui_image(photo))
            
            # Atualizar label de gesto
            current_gesture = gesture_controller.last_gesture
            self.root.after(0, lambda: self.lbl_gesture_status.configure(text=f"Gesto: {current_gesture}"))
            
        except Exception as e:
            logger.error(f"Erro ao atualizar feed de vídeo: {e}")

    def _update_gui_image(self, photo):
        self.gesture_video_label.configure(image=photo, text="")
        self.gesture_video_label.image = photo 
    
    def _create_memories_tab(self, parent):
        """Cria aba de memórias neurais"""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(container, text="NEURAL SEMANTIC MEMORY", font=ctk.CTkFont(family=FONTS.FAMILY_DISPLAY, size=16, weight="bold"), text_color=COLORS.TEXT_MAIN).pack(pady=10)

        # Treeview para lições
        columns = ("TRIGGER", "ACTION", "TIMESTAMP")
        self.memories_tree = ttk.Treeview(container, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.memories_tree.heading(col, text=col)
            self.memories_tree.column(col, width=200)

        self.memories_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Botão atualizar
        ctk.CTkButton(
            container, text="REFRESH KNOWLEDGE BASE", command=self._refresh_memories,
            fg_color=COLORS.BG_MAIN, hover_color=COLORS.BG_CARD_HOVER,
            corner_radius=DIMENSIONS.CORNER_RADIUS, border_width=1, border_color=COLORS.BORDER_SUBTLE
        ).pack(pady=10)
        
    def _refresh_memories(self):
        """Atualiza lista de memórias"""
        try:
            for item in self.memories_tree.get_children():
                self.memories_tree.delete(item)
                
            lessons = neural_memory.get_all_lessons()
            for lesson in lessons:
                self.memories_tree.insert("", tk.END, values=(lesson.get('trigger'), lesson.get('action'), lesson.get('timestamp')))
        except Exception as e:
            logger.error(f"Erro ao atualizar memórias: {e}")

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
        
        # Verificar comandos de UI (Navegação por Voz)
        if self._process_ui_voice_command(command):
            self._add_to_chat("Sistema: Comando de interface executado.")
            return

        # Processar em thread para não travar a GUI
        threading.Thread(target=self._process_ai_command, args=(command,), daemon=True).start()

    def _process_ui_voice_command(self, command: str) -> bool:
        """Processa comandos de voz para controle da UI"""
        cmd = command.lower()
        
        if "configura" in cmd: # configurações
            self.root.after(0, self._on_open_settings)
            return True
        elif "capturar" in cmd or "tira foto" in cmd or "screenshot" in cmd:
            self.root.after(0, self._on_capture_screen)
            return True
        elif "gravar" in cmd and "tela" in cmd:
            self.root.after(0, self._on_toggle_recording)
            return True
        elif "exportar" in cmd:
            self.root.after(0, self._on_export_data)
            return True
        elif "atualizar" in cmd:
            self.root.after(0, self._refresh_captures_list)
            return True
        elif "sair" in cmd or "fechar" in cmd:
            self.root.after(0, self._on_exit)
            return True
            
        return False

    def _process_ai_command(self, command: str):
        """Processa o comando usando o AIAgent"""
        self.root.after(0, lambda: self._set_orb_state("thinking"))
        self._add_to_chat("IA: Pensando...")
        
        response = ai_agent.process_command(command)
        
        self.root.after(0, lambda: self._set_orb_state("idle"))
        self.root.after(0, lambda: self._add_to_chat(f"IA: {response}"))

    def _add_to_chat(self, text: str):
        """Adiciona mensagem ao histórico do chat com estilo futurista"""
        self.chat_history.configure(state="normal")
        
        # Separar quem está falando
        if text.startswith("Você:"):
            msg = text.replace("Você:", "👤 VOCÊ >")
            tag_color = self.PRIMARY_COLOR
        elif text.startswith("IA:"):
            msg = text.replace("IA:", "🤖 JARVIS >")
            tag_color = "#00ffff"
        else:
            msg = f"⚙️ {text}"
            tag_color = "#606060"

        self.chat_history.insert(tk.END, msg + "\n\n")
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
        """Abre janela de configurações real"""
        if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
            
        self.settings_window = SettingsWindow(self.root)
        self.settings_window.grab_set()

    def _refresh_captures_list(self):
        """Atualiza lista de capturas com Cards Premium"""
        try:
            # Limpar cards antigos
            for widget in self.captures_scroll.winfo_children():
                widget.destroy()
            self.capture_cards = {}

            # Buscar capturas recentes
            captures = db_manager.get_recent_captures(50)

            if not captures:
                lbl = ctk.CTkLabel(self.captures_scroll, text="Nenhuma captura", font=ctk.CTkFont(slant="italic"))
                lbl.pack(pady=20)
                return

            for capture in captures:
                card = ctk.CTkFrame(self.captures_scroll, fg_color=self.CARD_BG, height=60, corner_radius=8)
                card.pack(fill=tk.X, pady=5, padx=5)
                
                # Timestamp formatado
                ts = capture.created_at.strftime("%H:%M - %d/%m") if capture.created_at else "N/A"
                
                # Info Principal
                lbl_title = ctk.CTkLabel(card, text=capture.filename, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
                lbl_title.pack(fill=tk.X, padx=10, pady=(8, 0))
                
                lbl_info = ctk.CTkLabel(card, text=f"{ts} • {capture.processing_status}", font=ctk.CTkFont(size=10), text_color="#606060", anchor="w")
                lbl_info.pack(fill=tk.X, padx=10, pady=(0, 8))

                # Bind de clique no card e nos filhos
                card.bind("<Button-1>", lambda e, c=capture, f=card: self._on_card_click(c, f))
                lbl_title.bind("<Button-1>", lambda e, c=capture, f=card: self._on_card_click(c, f))
                lbl_info.bind("<Button-1>", lambda e, c=capture, f=card: self._on_card_click(c, f))
                
                # Hover effect
                card.bind("<Enter>", lambda e, f=card: f.configure(fg_color="#222224"))
                card.bind("<Leave>", lambda e, f=card: f.configure(fg_color=self.CARD_BG if self.current_capture_path != f.capture_path else "#2a2a2b"))
                
                # Guardar referência do path no frame para facilidade
                card.capture_path = capture.file_path
                card.capture_id = capture.id
                self.capture_cards[capture.id] = card

            self._update_status_bar()

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de capturas: {e}")

    def _on_card_click(self, capture, frame):
        """Gerencia seleção de um Card de captura"""
        # Limpar seleção visual anterior
        for f in self.capture_cards.values():
            f.configure(fg_color=self.CARD_BG, border_width=0)
        
        # Destacar selecionado
        frame.configure(fg_color="#2a2a2b", border_width=1, border_color=self.PRIMARY_COLOR)
        
        # Atualizar estado
        self.current_capture_path = capture.file_path
        self._on_capture_selected_by_id(capture.id)
        
        # Habilitar botões
        self.btn_process.configure(state="normal")
        self.btn_export.configure(state="normal")
        self.btn_delete_capture.configure(state="normal")

    def _on_capture_selected_by_id(self, capture_id):
        """Lógica de carregamento quando uma captura é escolhida"""
        try:
            # Buscar detalhes no banco
            session = db_manager.get_session()
            capture = session.query(Capture).filter(Capture.id == capture_id).first()
            
            if capture:
                # 1. Carregar Pré-visualização
                self._display_image_from_path(capture.file_path)
                
                # 2. Carregar OCR e Dados se existirem
                self._load_capture_results(capture)
            
            session.close()
        except Exception as e:
            logger.error(f"Erro ao carregar detalhes da captura {capture_id}: {e}")

    def _display_image_from_path(self, file_path):
        """Exibe imagem no preview"""
        try:
            # Limpar canvas
            self.preview_canvas.delete("all")
            self.preview_label.place_forget()

            if not Path(file_path).exists():
                self.preview_label.configure(text="Arquivo não encontrado")
                self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                return

            # Carregar e exibir imagem
            image = Image.open(file_path)

            # Redimensionar para caber no canvas
            canvas_width = self.preview_canvas.winfo_width() or 400
            canvas_height = self.preview_canvas.winfo_height() or 300
            
            # Evitar divisão por zero
            if canvas_width == 0 or canvas_height == 0:
                return

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

    def _load_capture_results(self, capture):
        """Carrega resultados de OCR e dados (Wrapper)"""
        self._load_capture_data(capture.id)

    # ... skipping logic ...

    def _on_open_capture(self):
        """Abre arquivo de captura e importa para o sistema"""
        file_path = filedialog.askopenfilename(
            title="Abrir Captura",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if file_path:
            try:
                # Copiar para pasta de capturas
                import shutil
                dest_path = config.CAPTURES_DIR / Path(file_path).name
                
                # Evitar sobrescrever
                if dest_path.exists():
                    idx = 1
                    while dest_path.exists():
                        dest_path = config.CAPTURES_DIR / f"{Path(file_path).stem}_{idx}{Path(file_path).suffix}"
                        idx += 1
                
                shutil.copy2(file_path, dest_path)
                
                # Criar entrada no banco
                session = db_manager.get_session()
                img = Image.open(dest_path)
                new_capture = Capture(
                    filename=dest_path.name,
                    file_path=str(dest_path),
                    file_hash=FileHelper.calculate_hash(str(dest_path)),
                    file_size_mb=dest_path.stat().st_size / (1024 * 1024),
                    width=img.width,
                    height=img.height,
                    capture_type="imported",
                    capture_method="manual"
                )
                session.add(new_capture)
                session.commit()
                capture_id = new_capture.id
                db_manager.close_session(session)
                
                # Atualizar GUI
                self._refresh_captures_list()
                
                # Selecionar o novo item (precisa achar o card)
                if capture_id in self.capture_cards:
                    card = self.capture_cards[capture_id]
                    self._on_card_click(new_capture, card)
                    
                messagebox.showinfo("Sucesso", "Imagem importada com sucesso!")
                
            except Exception as e:
                logger.error(f"Erro ao importar imagem: {e}")
                messagebox.showerror("Erro", f"Falha ao importar imagem: {e}")

    def _on_edit_data(self):
        """Edita dados extraídos"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um item para editar")
            return
            
        item = self.data_tree.item(selection[0])
        # Values: Field, Value, Type, Confidence
        field_name = item['values'][0]
        current_value = item['values'][1]
        
        dialog = ctk.CTkInputDialog(text=f"Novo valor para '{field_name}':", title="Editar Dados")
        new_value = dialog.get_input()
        
        if new_value is not None:
             try:
                 capture_id = self._get_current_capture_id()
                 if not capture_id: return
                 
                 # Atualizar no banco
                 session = db_manager.get_session()
                 # Buscar dado pelo field_name e capture_id (assumindo unicidade por campo nesta versão simples)
                 data_entry = session.query(db_manager.ExtractedData)\
                     .filter(db_manager.ExtractedData.capture_id == capture_id)\
                     .filter(db_manager.ExtractedData.field_name == field_name)\
                     .first()
                     
                 if data_entry:
                     data_entry.field_value = new_value
                     data_entry.confidence = 1.0 # 100% de confiança pois foi editado manualmente
                     session.commit()
                     
                     # Atualizar UI
                     self._load_capture_data(capture_id)
                 
                 db_manager.close_session(session)
             except Exception as e:
                 logger.error(f"Erro ao atualizar dado: {e}")
                 messagebox.showerror("Erro", str(e))

    def _on_validate_data(self):
        """Valida todos os dados da captura atual"""
        capture_id = self._get_current_capture_id()
        if not capture_id:
            messagebox.showwarning("Aviso", "Nenhuma captura selecionada")
            return
            
        try:
            session = db_manager.get_session()
            capture = session.query(Capture).filter(Capture.id == capture_id).first()
            if capture:
                capture.processing_status = "validated"
                session.commit()
                messagebox.showinfo("Sucesso", "Dados marcados como validados!")
                self._update_status_bar()
                
                # Visualmente marcar na lista (opcional - requer refresh)
                self._refresh_captures_list()
                
            db_manager.close_session(session)
        except Exception as e:
            logger.error(f"Erro ao validar dados: {e}")

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
        JARVIS 5.0 - Inteligência de Elite

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
        try:
            docs_path = config.DOCS_DIR
            if not docs_path.exists():
                messagebox.showinfo("Documentação", "Diretório de documentação não encontrado.\nConsulte o arquivo README.md no diretório raiz.")
                return
                
            os.startfile(docs_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir documentação: {e}")

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


    def _on_delete_capture(self):
        """Exclui a captura selecionada"""
        if not self.current_capture:
            return

        confirm = messagebox.askyesno("Confirmar Exclusão", 
                                    f"Tem certeza que deseja excluir a captura '{self.current_capture.filename}'?\nIsso não pode ser desfeito.")
        
        if confirm:
            try:
                # Excluir do banco
                session = db_manager.get_session()
                # Primeiro excluir dados relacionados (Cascade deve cuidar, mas por segurança...)
                session.query(OCRResult).filter(OCRResult.capture_id == self.current_capture.id).delete()
                session.query(ExtractedData).filter(ExtractedData.capture_id == self.current_capture.id).delete()
                
                # Excluir captura
                session.query(Capture).filter(Capture.id == self.current_capture.id).delete()
                session.commit()
                db_manager.close_session(session)
                
                # Excluir arquivo físico
                try:
                    file_path = Path(self.current_capture.file_path)
                    if file_path.exists():
                        file_path.unlink()
                except Exception as e:
                    logger.warning(f"Erro ao excluir arquivo físico: {e}")
                
                # Atualizar UI
                self.current_capture = None
                self._clear_results_panel()
                self._refresh_captures_list()
                self.status_bar.set("Captura excluída com sucesso.")
                
            except Exception as e:
                logger.error(f"Erro ao excluir captura: {e}")
                messagebox.showerror("Erro", f"Falha ao excluir captura: {e}")

    def _clear_results_panel(self):
        """Limpa painel de resultados"""
        self.preview_label.configure(image=None, text="Nenhuma imagem selecionada")
        self.ocr_text.delete("1.0", tk.END)
        # Limpar Treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

class SettingsWindow(ctk.CTkToplevel):
    """Janela de configurações completa e funcional"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configurações do J.A.R.V.I.S")
        self.geometry("700x500")
        self.resizable(False, False)
        
        self.attributes("-topmost", True)
        
        # Init Variables with current config
        self._init_variables()
        
        # Layout container
        self.layout_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#101010")
        self.layout_frame.pack(fill=tk.BOTH, expand=True)

        self._create_sidebar()
        self._create_content_area()
        
        # Default Tab
        self._show_general_settings()
        
    def _init_variables(self):
        """Inicializa variáveis com valores atuais da configuração"""
        # General
        self.var_theme = ctk.StringVar(value=config.get_setting("app.theme", "dark").title())
        self.var_startup = ctk.BooleanVar(value=config.get_setting("interface.auto_start", False))
        self.var_updates = ctk.BooleanVar(value=config.get_setting("interface.check_updates", True))
        
        # AI
        self.var_ai_model = ctk.StringVar(value=config.get_setting("analysis.ai_model", "Qwen 2.5 (Local)"))
        self.var_memory_threshold = ctk.IntVar(value=config.get_setting("analysis.memory_threshold", 70))
        
        # Voice
        self.var_stt = ctk.StringVar(value=config.get_setting("voice.stt_provider", "Vosk (Offline)"))
        self.var_tts = ctk.StringVar(value=config.get_setting("voice.tts_provider", "Microsoft Edge (Hyper-Real)"))
        
        # Camera
        self.var_faceid = ctk.BooleanVar(value=config.get_setting("vision.faceid_enabled", False))
        self.var_gestures = ctk.BooleanVar(value=config.get_setting("vision.gestures_enabled", False))
        self.var_presence = ctk.BooleanVar(value=config.get_setting("vision.presence_enabled", False))
        
    def _create_sidebar(self):
        sidebar = ctk.CTkFrame(self.layout_frame, width=160, corner_radius=0, fg_color="#1a1a1b")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        title = ctk.CTkLabel(sidebar, text="SETTINGS", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00d2ff")
        title.pack(padx=20, pady=20)
        
        buttons = [
            ("⚙️ Geral", self._show_general_settings),
            ("🤖 IA & Cérebro", self._show_ai_settings),
            ("🎙️ Voz & Audio", self._show_voice_settings),
            ("📹 Câmera", self._show_camera_settings),
            ("🔌 Hardware", self._show_hardware_settings)
        ]
        
        self.nav_buttons = []
        for text, cmd in buttons:
            btn = ctk.CTkButton(
                sidebar, text=text, 
                fg_color="transparent", 
                text_color="gray90", 
                hover_color="#333", 
                anchor="w", 
                command=lambda c=cmd, t=text: self._highlight_btn(c, t)
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
            self.nav_buttons.append(btn)
            
    def _highlight_btn(self, cmd, text):
        # Reset colors (simplificado)
        cmd()

    def _create_content_area(self):
        self.content_frame = ctk.CTkFrame(self.layout_frame, fg_color="transparent")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def _create_save_button(self):
        ctk.CTkButton(self.content_frame, text="Salvar Alterações", fg_color="#28a745", hover_color="#218838", command=self._save_settings).pack(side=tk.BOTTOM, pady=20)

    def _save_settings(self):
        """Salva todas as configurações"""
        try:
            # General
            config.set_setting("app.theme", self.var_theme.get().lower())
            config.set_setting("interface.auto_start", self.var_startup.get())
            config.set_setting("interface.check_updates", self.var_updates.get())
            
            # AI
            config.set_setting("analysis.ai_model", self.var_ai_model.get())
            config.set_setting("analysis.memory_threshold", self.var_memory_threshold.get())
            
            # Voice
            config.set_setting("voice.stt_provider", self.var_stt.get())
            config.set_setting("voice.tts_provider", self.var_tts.get())
            
            # Camera
            config.set_setting("vision.faceid_enabled", self.var_faceid.get())
            config.set_setting("vision.gestures_enabled", self.var_gestures.get())
            config.set_setting("vision.presence_enabled", self.var_presence.get())
            
            messagebox.showinfo("Sucesso", "Configurações salvas e aplicadas!")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")

    def _show_general_settings(self):
        self._clear_content()
        ctk.CTkLabel(self.content_frame, text="Configurações Gerais", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        # Theme
        ctk.CTkLabel(self.content_frame, text="Tema da Interface").pack(anchor="w")
        ctk.CTkOptionMenu(self.content_frame, variable=self.var_theme, values=["Dark", "Light", "System"], command=self._change_theme).pack(anchor="w", pady=(5, 15))
        
        # Startup
        ctk.CTkCheckBox(self.content_frame, text="Iniciar com o Windows", variable=self.var_startup).pack(anchor="w", pady=10)
        ctk.CTkCheckBox(self.content_frame, text="Verificações automáticas na inicialização", variable=self.var_updates).pack(anchor="w", pady=10)
        
        self._create_save_button()
        
    def _show_ai_settings(self):
        self._clear_content()
        ctk.CTkLabel(self.content_frame, text="Inteligência Artificial", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(self.content_frame, text="Modelo de IA Padrão").pack(anchor="w")
        ctk.CTkOptionMenu(self.content_frame, variable=self.var_ai_model, values=["Qwen 2.5 (Local)", "Gemini Flash (Nuvem)", "GPT-4o (Nuvem)"]).pack(anchor="w", pady=(5, 15))
        
        ctk.CTkLabel(self.content_frame, text="Limiar de Memória Neural").pack(anchor="w", pady=(10,0))
        ctk.CTkSlider(self.content_frame, from_=0, to=100, number_of_steps=20, variable=self.var_memory_threshold).pack(fill=tk.X, pady=(5, 5))
        ctk.CTkLabel(self.content_frame, text="Defina sensibilidade da lembrança (0-100)", font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="e")
        
        self._create_save_button()

    def _show_voice_settings(self):
        self._clear_content()
        ctk.CTkLabel(self.content_frame, text="Controle de Voz", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(self.content_frame, text="Provedor STT (Escuta)").pack(anchor="w")
        ctk.CTkOptionMenu(self.content_frame, variable=self.var_stt, values=["Google Speech (Online)", "Vosk (Offline)", "Whisper (Híbrido)"]).pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(self.content_frame, text="Voz de Resposta (TTS)").pack(anchor="w")
        ctk.CTkOptionMenu(self.content_frame, variable=self.var_tts, values=["Microsoft Edge (Hyper-Real)", "Google TTS", "System Default"]).pack(anchor="w", pady=(5, 15))
        
        self._create_save_button()
        
    def _show_camera_settings(self):
        self._clear_content()
        ctk.CTkLabel(self.content_frame, text="Câmera & Visão", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkSwitch(self.content_frame, text="Ativar FaceID na inicialização", variable=self.var_faceid).pack(anchor="w", pady=10)
        ctk.CTkSwitch(self.content_frame, text="Detecção de Gestos (Mão)", variable=self.var_gestures).pack(anchor="w", pady=10)
        ctk.CTkSwitch(self.content_frame, text="Monitoramento de Presença", variable=self.var_presence).pack(anchor="w", pady=10)
        
        self._create_save_button()

    def _show_hardware_settings(self):
        self._clear_content()
        ctk.CTkLabel(self.content_frame, text="Hardware", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        import psutil
        ram = psutil.virtual_memory()
        
        info = [
            f"CPU Cores: {psutil.cpu_count(logical=False)} ({psutil.cpu_count(logical=True)} Threads)",
            f"Memória Total: {ram.total / (1024**3):.1f} GB",
            f"Processador: {platform.machine()}",
            f"Sistema: {platform.system()} {platform.release()}"
        ]
        
        for item in info:
            ctk.CTkLabel(self.content_frame, text=f"• {item}").pack(anchor="w", pady=2)
            
        ctk.CTkLabel(self.content_frame, text="\nStatus Drivers:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        from src.core.hardware_manager import hardware_manager
        status = hardware_manager.get_status()
        
        lbl_device = ctk.CTkLabel(self.content_frame, text=f"Dispositivo de Compute: {status['device'].upper()}", text_color=self.master.PRIMARY_COLOR)
        lbl_device.pack(anchor="w")
        
        self._create_save_button()

    def _change_theme(self, mode):
        ctk.set_appearance_mode(mode)


# Instância global da janela principal
main_window = MainWindow()
