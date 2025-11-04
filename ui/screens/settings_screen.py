# frontend/ui/screens/settings_screen.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS
import subprocess
import threading
import json
from utils.logger import ui_logger
from ui.components.keyboard import VirtualKeyboard

class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, on_save: callable, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16, *args, **kwargs)
        self.on_save = on_save
        self.raspberry_info = {}
        
        # Configurar grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Acessar configurações do app principal
        self.config_dict = self._get_app_config()
        self.keyboard_window = None
        
        # Botão voltar NO TOPO - usando grid
        self.back_btn = ctk.CTkButton(
            self,
            text="← Voltar",
            width=70,
            height=28,
            corner_radius=12,
            fg_color=COLORS["pill_dark"],
            hover_color=COLORS["pill"],
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"],
            command=self._on_back
        )
        self.back_btn.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        self._build_ui()

    def _get_app_config(self):
        """Obtém configurações do app principal de forma segura"""
        try:
            # Navega até o app principal
            app = self.master
            while hasattr(app, 'master') and app.master:
                app = app.master
                if hasattr(app, 'config'):
                    return app.config
            return {}
        except Exception as e:
            ui_logger.warning(f"Não foi possível acessar configurações: {e}")
            return {}

    def _build_ui(self):
        # Container principal com scroll - usando grid
        self.main_container = ctk.CTkScrollableFrame(
            self, 
            fg_color=COLORS["bg"], 
            corner_radius=12,
            scrollbar_button_color=COLORS["neutral"],
            scrollbar_button_hover_color=COLORS["neutral_hover"]
        )
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # ===== SEÇÃO: INFORMAÇÕES DO SISTEMA =====
        self._build_system_info_section()
        
        # ===== SEÇÃO: CONFIGURAÇÕES DE REDE =====
        self._build_network_section()
        
        # ===== SEÇÃO: CONFIGURAÇÕES DE WI-FI =====
        self._build_wifi_section()
        
        # ===== SEÇÃO: CONFIGURAÇÕES DE CÂMERA =====
        self._build_camera_section()
        
        # ===== SEÇÃO: SISTEMA =====
        self._build_system_section()
        
        # ===== BOTÕES DE AÇÃO =====
        self._build_action_buttons()

    def _build_system_info_section(self):
        """Seção de informações do sistema"""
        info_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["pill_dark"], corner_radius=8)
        info_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        # Título com ícone menor
        title_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=12, pady=(8, 6))
        
        ctk.CTkLabel(
            title_frame,
            text="Informações do Sistema",
            text_color=COLORS["text"],
            font=FONTS["subtitle"]
        ).pack(side="left")
        
        # Container para informações
        content_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=12, pady=(0, 10))
        
        # Hostname
        hostname_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        hostname_frame.pack(fill="x", pady=4)
        
        ctk.CTkLabel(
            hostname_frame,
            text="Hostname:",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            width=80,
            anchor="w"
        ).pack(side="left")
        
        self.hostname_label = ctk.CTkLabel(
            hostname_frame,
            text="Carregando...",
            text_color=COLORS["text"],
            font=FONTS["body"],
            anchor="w"
        )
        self.hostname_label.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # IP Privado
        private_ip_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        private_ip_frame.pack(fill="x", pady=4)
        
        ctk.CTkLabel(
            private_ip_frame,
            text="IP Local:",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            width=80,
            anchor="w"
        ).pack(side="left")
        
        self.private_ip_label = ctk.CTkLabel(
            private_ip_frame,
            text="Carregando...",
            text_color=COLORS["text"],
            font=FONTS["body"],
            anchor="w"
        )
        self.private_ip_label.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # Botão para copiar IP
        copy_ip_btn = ctk.CTkButton(
            private_ip_frame,
            text="Copiar",
            width=60,
            height=24,
            command=self._copy_ip_to_clipboard,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        copy_ip_btn.pack(side="right", padx=(5, 0))

    def _build_network_section(self):
        """Seção de configurações de rede"""
        network_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["pill_dark"], corner_radius=8)
        network_frame.pack(fill="x", padx=10, pady=8)
        
        # Título
        title_frame = ctk.CTkFrame(network_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=12, pady=(8, 6))
        
        ctk.CTkLabel(
            title_frame,
            text="Configurações de Rede",
            text_color=COLORS["text"],
            font=FONTS["subtitle"]
        ).pack(side="left")
        
        # Transporte de Vídeo
        transport_frame = ctk.CTkFrame(network_frame, fg_color="transparent")
        transport_frame.pack(fill="x", padx=12, pady=8)
        
        ctk.CTkLabel(
            transport_frame,
            text="Transporte de Vídeo:",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            anchor="w"
        ).pack(side="left")
        
        video_config = self.config_dict.get("video", {})
        default_transport = video_config.get("transport", "tcp")
        
        self.transport_var = ctk.StringVar(value=default_transport)
        self.transport_combo = ctk.CTkComboBox(
            transport_frame,
            values=["tcp", "udp"],
            variable=self.transport_var,
            width=100,
            height=30,
            state="readonly",
            fg_color=COLORS["pill"],
            border_color=COLORS["border"],
            button_color=COLORS["neutral"],
            dropdown_fg_color=COLORS["panel"],
            dropdown_hover_color=COLORS["pill"]
        )
        self.transport_combo.pack(side="right")

    def _build_wifi_section(self):
        """Seção de configuração Wi-Fi"""
        wifi_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["pill_dark"], corner_radius=8)
        wifi_frame.pack(fill="x", padx=10, pady=8)
        
        # Título
        title_frame = ctk.CTkFrame(wifi_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=12, pady=(8, 6))
        
        ctk.CTkLabel(
            title_frame,
            text="Conexão Wi-Fi",
            text_color=COLORS["text"],
            font=FONTS["subtitle"]
        ).pack(side="left")
        
        # SSID
        ssid_frame = ctk.CTkFrame(wifi_frame, fg_color="transparent")
        ssid_frame.pack(fill="x", padx=12, pady=6)
        
        ctk.CTkLabel(
            ssid_frame,
            text="Nome da Rede:",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.ssid_var = ctk.StringVar()
        self.ssid_entry = ctk.CTkEntry(
            ssid_frame,
            textvariable=self.ssid_var,
            placeholder_text="Digite o SSID",
            fg_color=COLORS["pill"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            height=32,
            placeholder_text_color=COLORS["text_secondary"]
        )
        self.ssid_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        # Botão teclado para SSID
        ssid_keyboard_btn = ctk.CTkButton(
            ssid_frame,
            text="⌨",
            width=32,
            height=32,
            command=lambda: self._open_keyboard(self.ssid_entry),
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body"]
        )
        ssid_keyboard_btn.pack(side="right")
        
        # Senha
        password_frame = ctk.CTkFrame(wifi_frame, fg_color="transparent")
        password_frame.pack(fill="x", padx=12, pady=6)
        
        ctk.CTkLabel(
            password_frame,
            text="Senha:",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            width=100,
            anchor="w"
        ).pack(side="left")
        
        self.password_var = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(
            password_frame,
            textvariable=self.password_var,
            placeholder_text="Digite a senha",
            show="•",
            fg_color=COLORS["pill"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            height=32,
            placeholder_text_color=COLORS["text_secondary"]
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        # Botão teclado para senha
        password_keyboard_btn = ctk.CTkButton(
            password_frame,
            text="⌨",
            width=32,
            height=32,
            command=lambda: self._open_keyboard(self.password_entry),
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body"]
        )
        password_keyboard_btn.pack(side="right", padx=(0, 5))
        
        # Botão mostrar/ocultar senha
        toggle_password_btn = ctk.CTkButton(
            password_frame,
            text="👁",
            width=32,
            height=32,
            command=self._toggle_password_visibility,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        toggle_password_btn.pack(side="right")
        
        # Status da conexão Wi-Fi
        self.wifi_status_label = ctk.CTkLabel(
            wifi_frame,
            text="",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"],
            anchor="w"
        )
        self.wifi_status_label.pack(anchor="w", padx=12, pady=(2, 0))
        
        # Botão conectar Wi-Fi
        wifi_btn = ctk.CTkButton(
            wifi_frame,
            text="Conectar à Rede Wi-Fi",
            command=self._connect_wifi,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body"],
            height=34
        )
        wifi_btn.pack(fill="x", padx=12, pady=(8, 10))

    def _build_camera_section(self):
        """Seção de configurações de câmera"""
        camera_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["pill_dark"], corner_radius=8)
        camera_frame.pack(fill="x", padx=10, pady=8)
        
        # Título
        title_frame = ctk.CTkFrame(camera_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=12, pady=(8, 6))
        
        ctk.CTkLabel(
            title_frame,
            text="Configurações de Câmera",
            text_color=COLORS["text"],
            font=FONTS["subtitle"]
        ).pack(side="left")
        
        # FPS
        fps_frame = ctk.CTkFrame(camera_frame, fg_color="transparent")
        fps_frame.pack(fill="x", padx=12, pady=8)
        
        ctk.CTkLabel(
            fps_frame,
            text="Frames por Segundo:",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            anchor="w"
        ).pack(side="left")
        
        camera_config = self.config_dict.get("camera", {})
        default_fps = camera_config.get("target_fps", 15)
        
        self.fps_var = ctk.StringVar(value=str(default_fps))
        self.fps_combo = ctk.CTkComboBox(
            fps_frame,
            values=["10", "15", "20", "25", "30"],
            variable=self.fps_var,
            width=100,
            height=30,
            state="readonly",
            fg_color=COLORS["pill"],
            border_color=COLORS["border"],
            button_color=COLORS["neutral"]
        )
        self.fps_combo.pack(side="right")

    def _build_system_section(self):
        """Seção de sistema"""
        system_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["pill_dark"], corner_radius=8)
        system_frame.pack(fill="x", padx=10, pady=8)
        
        # Título
        title_frame = ctk.CTkFrame(system_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=12, pady=(8, 6))
        
        ctk.CTkLabel(
            title_frame,
            text="Sistema",
            text_color=COLORS["text"],
            font=FONTS["subtitle"]
        ).pack(side="left")
        
        # Botão Reiniciar Serviço
        restart_btn = ctk.CTkButton(
            system_frame,
            text="Reiniciar Serviço",
            command=self._restart_service,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body"],
            height=32
        )
        restart_btn.pack(fill="x", padx=12, pady=6)
        
        # Botão Logs do Sistema
        logs_btn = ctk.CTkButton(
            system_frame,
            text="Visualizar Logs",
            command=self._show_system_logs,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body"],
            height=32
        )
        logs_btn.pack(fill="x", padx=12, pady=(0, 10))

    def _build_action_buttons(self):
        """Botões de ação principais"""
        action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=15)
        
        # Botão Aplicar (verde escuro)
        apply_btn = ctk.CTkButton(
            action_frame,
            text="Aplicar Configurações",
            command=self._on_apply,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            font=FONTS["body_bold"],
            height=38
        )
        apply_btn.pack(side="left", padx=5, expand=True)
        
        # Botão Salvar (azul)
        save_btn = ctk.CTkButton(
            action_frame,
            text="Salvar Configurações",
            command=self._on_save,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=FONTS["body_bold"],
            height=38
        )
        save_btn.pack(side="right", padx=5, expand=True)

    def _open_keyboard(self, target_entry):
        """Abre o teclado virtual"""
        try:
            if self.keyboard_window and self.keyboard_window.winfo_exists():
                self.keyboard_window.destroy()
            
            self.keyboard_window = VirtualKeyboard(target_entry=target_entry)
            self.keyboard_window.show()
            
        except Exception as e:
            ui_logger.error(f"Erro ao abrir teclado virtual: {e}")

    def _toggle_password_visibility(self):
        """Alterna entre mostrar e ocultar senha"""
        current_show = self.password_entry.cget("show")
        if current_show == "•":
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")

    def update_raspberry_info(self, raspberry_info: dict):
        """Atualiza a exibição com as informações da Raspberry"""
        try:
            self.raspberry_info = raspberry_info
            
            # Atualizar hostname
            hostname = raspberry_info.get('hostname', 'Desconhecido')
            self.hostname_label.configure(text=hostname)
            
            # Atualizar IPs
            private_ip = raspberry_info.get('private_ip', raspberry_info.get('ip', 'Indisponível'))
            self.private_ip_label.configure(text=private_ip)
            
        except Exception as e:
            ui_logger.error(f"Erro ao atualizar informações da Raspberry na UI: {e}")

    def _copy_ip_to_clipboard(self, ip_type: str = "private"):
        """Copia o IP para a área de transferência"""
        try:
            ip = self.raspberry_info.get('private_ip', '')
            if ip and ip != 'Indisponível':
                self.clipboard_clear()
                self.clipboard_append(ip)
                # Feedback visual
                original_text = self.private_ip_label.cget("text")
                self.private_ip_label.configure(text=f"{ip} (Copiado!)")
                self.after(2000, lambda: self.private_ip_label.configure(text=original_text))
        except Exception as e:
            ui_logger.error(f"Erro ao copiar IP: {e}")

    def _connect_wifi(self):
        """Conecta à rede Wi-Fi especificada"""
        ssid = self.ssid_var.get().strip()
        password = self.password_var.get().strip()
        
        if not ssid:
            self._show_wifi_status("Por favor, digite o nome da rede", False)
            return
            
        # Enviar comando para o backend via command handler
        try:
            app = self._get_app_instance()
            if hasattr(app, 'commands') and hasattr(app.commands, 'send_wifi_connect'):
                # Usar command handler se disponível
                app.commands.send_wifi_connect(ssid, password)
                self._show_wifi_status("Conectando...", None)
                ui_logger.info(f"Tentando conectar ao Wi-Fi: {ssid}")
            elif hasattr(app, 'tcp_client'):
                # Fallback: enviar comando direto via TCP
                command = f"WIFI_CONNECT:{ssid}:{password}"
                app.tcp_client.send(command.encode('utf-8'))
                self._show_wifi_status("Conectando...", None)
            else:
                ui_logger.error("Nenhum método de conexão disponível")
                self._show_wifi_status("Erro: Sistema indisponível", False)
                
        except Exception as e:
            ui_logger.error(f"Erro ao conectar Wi-Fi: {e}")
            self._show_wifi_status(f"Erro: {str(e)}", False)

    def _show_wifi_status(self, status: str, success: bool = None):
        """Mostra status da conexão Wi-Fi"""
        def update_ui():
            self.wifi_status_label.configure(text=status)
            
            if success is True:
                self.wifi_status_label.configure(text_color=COLORS["success"])
                # Limpar campos em caso de sucesso
                self.ssid_var.set("")
                self.password_var.set("")
            elif success is False:
                self.wifi_status_label.configure(text_color=COLORS["accent"])
            else:
                self.wifi_status_label.configure(text_color=COLORS["text_secondary"])
        
        self.after(0, update_ui)

    def _restart_service(self):
        """Reinicia o serviço da aplicação"""
        def restart():
            try:
                ui_logger.info("Reiniciando serviço...")
                app = self._get_app_instance()
                if hasattr(app, 'commands') and hasattr(app.commands, 'send_restart_service'):
                    app.commands.send_restart_service()
                elif hasattr(app, 'tcp_client'):
                    app.tcp_client.send("RESTART_SERVICE".encode('utf-8'))
                else:
                    ui_logger.error("Nenhum método de reinício disponível")
            except Exception as e:
                ui_logger.error(f"Erro ao enviar comando de reinício: {e}")
        
        threading.Thread(target=restart, daemon=True).start()

    def _show_system_logs(self):
        """Mostra logs do sistema"""
        try:
            app = self._get_app_instance()
            if hasattr(app, 'commands') and hasattr(app.commands, 'send_show_logs'):
                app.commands.send_show_logs()
            elif hasattr(app, 'tcp_client'):
                app.tcp_client.send("SHOW_LOGS".encode('utf-8'))
            else:
                ui_logger.error("Nenhum método para logs disponível")
        except Exception as e:
            ui_logger.error(f"Erro ao solicitar logs: {e}")

    def _get_app_instance(self):
        """Obtém a instância do app principal de forma segura"""
        try:
            app = self.master
            while hasattr(app, 'master') and app.master:
                app = app.master
                if hasattr(app, 'commands') or hasattr(app, 'tcp_client'):
                    return app
            return self.master
        except Exception as e:
            ui_logger.error(f"Erro ao obter app instance: {e}")
            return self.master

    def _on_save(self):
        """Salva as configurações permanentemente"""
        try:
            new_settings = {
                "video": {
                    "transport": self.transport_var.get()
                },
                "camera": {
                    "target_fps": int(self.fps_var.get())
                }
            }
            
            if callable(self.on_save):
                self.on_save(new_settings)
                ui_logger.info("Configurações salvas com sucesso")
                self._show_wifi_status("Configurações salvas com sucesso!", True)
            else:
                ui_logger.error("Callback on_save não disponível")
                
        except Exception as e:
            ui_logger.error(f"Erro ao salvar configurações: {e}")
            self._show_wifi_status(f"Erro ao salvar: {str(e)}", False)

    def _on_apply(self):
        """Aplica as configurações sem salvar permanentemente"""
        # Por enquanto, aplica e salva (pode ser modificado para só aplicar)
        self._on_save()

    def _on_back(self):
        """Volta para a tela anterior"""
        if self.keyboard_window and self.keyboard_window.winfo_exists():
            self.keyboard_window.destroy()
        
        # Navegar para home através do app principal
        try:
            app = self._get_app_instance()
            if hasattr(app, 'show_screen'):
                app.show_screen("home")
        except Exception as e:
            ui_logger.error(f"Erro ao voltar para home: {e}")

    def on_show(self):
        """Chamado quando a tela é mostrada - atualiza informações"""
        try:
            # Solicitar informações atualizadas da Raspberry
            app = self._get_app_instance()
            if hasattr(app, 'tcp_client'):
                app.tcp_client.send("GET_INFO".encode('utf-8'))
                ui_logger.debug("Solicitando informações atualizadas da Raspberry")
        except Exception as e:
            ui_logger.debug(f"Erro ao solicitar info na exibição: {e}")