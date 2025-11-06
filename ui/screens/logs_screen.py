import customtkinter as ctk
from ui.icons import COLORS, FONTS
from utils.logger import ui_logger
import threading
import time
from datetime import datetime

class LogsScreen(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16, *args, **kwargs)
        
        # Configurar grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._auto_scroll = True
        self._is_auto_refresh = False
        self._refresh_interval = 2000  # 2 segundos
        
        self._build_ui()
        self._setup_bindings()

    def _build_ui(self):
        """Constrói a interface da tela de logs"""
        # Botão voltar NO TOPO
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
        
        # Container principal
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # ===== HEADER COM CONTROLES =====
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame,
            text="Logs do Sistema",
            text_color=COLORS["text"],
            font=FONTS["title"]
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Controles
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=1, sticky="e")
        
        # Auto-refresh
        self.auto_refresh_var = ctk.BooleanVar(value=False)
        auto_refresh_cb = ctk.CTkCheckBox(
            controls_frame,
            text="Auto-refresh",
            variable=self.auto_refresh_var,
            command=self._toggle_auto_refresh,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=FONTS["body_small"]
        )
        auto_refresh_cb.pack(side="left", padx=(0, 10))
        
        # Auto-scroll
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        auto_scroll_cb = ctk.CTkCheckBox(
            controls_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            command=self._toggle_auto_scroll,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=FONTS["body_small"]
        )
        auto_scroll_cb.pack(side="left", padx=(0, 10))
        
        # Botão atualizar
        self.refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Atualizar",
            width=100,
            height=32,
            command=self._refresh_logs,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        self.refresh_btn.pack(side="left", padx=(0, 10))
        
        # Botão copiar
        self.copy_btn = ctk.CTkButton(
            controls_frame,
            text="📋 Copiar",
            width=80,
            height=32,
            command=self._copy_logs,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        self.copy_btn.pack(side="left")
        
        # ===== ÁREA DE LOGS =====
        logs_container = ctk.CTkFrame(
            self.main_container, 
            fg_color=COLORS["pill_dark"], 
            corner_radius=12
        )
        logs_container.grid(row=1, column=0, sticky="nsew")
        logs_container.grid_rowconfigure(0, weight=1)
        logs_container.grid_columnconfigure(0, weight=1)
        
        # Widget de texto para logs
        self.logs_text = ctk.CTkTextbox(
            logs_container,
            wrap="word",
            fg_color=COLORS["bg"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            font=("Consolas", 11),  # Fonte monoespaçada para melhor leitura
            activate_scrollbars=True
        )
        self.logs_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # ===== STATUS BAR =====
        status_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto. Clique em Atualizar para carregar os logs.",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"],
            anchor="w"
        )
        self.status_label.pack(side="left")
        
        self.lines_label = ctk.CTkLabel(
            status_frame,
            text="0 linhas",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"]
        )
        self.lines_label.pack(side="right")

    def _setup_bindings(self):
        """Configura bindings para eventos"""
        # Bind para detectar scroll manual e desativar auto-scroll
        self.logs_text.bind("<MouseWheel>", self._on_manual_scroll)
        self.logs_text.bind("<Button-4>", self._on_manual_scroll)  # Linux
        self.logs_text.bind("<Button-5>", self._on_manual_scroll)  # Linux

    def _on_manual_scroll(self, event):
        """Desativa auto-scroll quando usuário faz scroll manual"""
        if self.auto_scroll_var.get():
            # Verifica se o usuário está scrollando para cima (não no final)
            try:
                # Pega a posição atual do viewport
                self.logs_text.update_idletasks()
                # Se não estiver no final, desativa auto-scroll
                if not self._is_at_bottom():
                    self.auto_scroll_var.set(False)
                    self.status_label.configure(text="Auto-scroll desativado (scroll manual detectado)")
            except:
                pass
        return "break"

    def _is_at_bottom(self):
        """Verifica se o scroll está no final"""
        try:
            # Pega a posição atual do scrollbar vertical
            scrollbar = self.logs_text._scrollbar_y
            if scrollbar.winfo_exists():
                pos = scrollbar.get()
                return pos[1] >= 0.99  # 99% para baixo considerado "no final"
        except:
            pass
        return True

    def _toggle_auto_refresh(self):
        """Alterna auto-refresh"""
        self._is_auto_refresh = self.auto_refresh_var.get()
        if self._is_auto_refresh:
            self._start_auto_refresh()
            self.status_label.configure(text="Auto-refresh ativado")
        else:
            self.status_label.configure(text="Auto-refresh desativado")

    def _toggle_auto_scroll(self):
        """Alterna auto-scroll"""
        self._auto_scroll = self.auto_scroll_var.get()
        status = "ativado" if self._auto_scroll else "desativado"
        self.status_label.configure(text=f"Auto-scroll {status}")
        
        if self._auto_scroll:
            self.logs_text.see("end")

    def _start_auto_refresh(self):
        """Inicia o auto-refresh em thread separada"""
        def auto_refresh_loop():
            while self._is_auto_refresh and self.winfo_exists():
                try:
                    self.after(0, self._refresh_logs)
                    time.sleep(self._refresh_interval / 1000)
                except:
                    break
        
        if self._is_auto_refresh:
            threading.Thread(target=auto_refresh_loop, daemon=True).start()

    def _refresh_logs(self):
        """Atualiza os logs"""
        try:
            self.status_label.configure(text="Solicitando logs...")
            self.refresh_btn.configure(state="disabled")
            
            app = self._get_app_instance()
            if hasattr(app, 'commands') and hasattr(app.commands, 'send_show_logs'):
                app.commands.send_show_logs(
                    lines=100,  # Mais linhas para a tela dedicada
                    callback=self._on_logs_response
                )
            else:
                self.status_label.configure(text="Erro: Sistema de logs indisponível")
                
        except Exception as e:
            ui_logger.error(f"Erro ao solicitar logs: {e}")
            self.status_label.configure(text=f"Erro: {str(e)}")
        finally:
            self.after(1000, lambda: self.refresh_btn.configure(state="normal"))

    def _on_logs_response(self, success: bool, message: str, data: dict):
        """Processa a resposta dos logs"""
        try:
            if success:
                logs_content = data.get('logs', message) if data else message
                self._update_logs_display(logs_content)
                self.status_label.configure(text=f"Logs atualizados - {datetime.now().strftime('%H:%M:%S')}")
            else:
                self.status_label.configure(text=f"Erro ao obter logs: {message}")
                
        except Exception as e:
            ui_logger.error(f"Erro no processamento de logs: {e}")
            self.status_label.configure(text=f"Erro no processamento: {str(e)}")

    def _update_logs_display(self, logs_content: str):
        """Atualiza a exibição dos logs"""
        try:
            # Habilita edição temporariamente
            self.logs_text.configure(state="normal")
            
            # Limpa conteúdo anterior
            self.logs_text.delete("1.0", "end")
            
            # Insere novos logs
            self.logs_text.insert("1.0", logs_content)
            
            # Desabilita edição (somente leitura)
            self.logs_text.configure(state="disabled")
            
            # Auto-scroll para o final se habilitado
            if self._auto_scroll:
                self.logs_text.see("end")
            
            # Atualiza contador de linhas
            lines = len(logs_content.split('\n'))
            self.lines_label.configure(text=f"{lines} linhas")
            
        except Exception as e:
            ui_logger.error(f"Erro ao atualizar exibição de logs: {e}")

    def _copy_logs(self):
        """Copia logs para a área de transferência"""
        try:
            logs_content = self.logs_text.get("1.0", "end-1c")
            if logs_content.strip():
                self.clipboard_clear()
                self.clipboard_append(logs_content)
                
                # Feedback visual
                original_text = self.copy_btn.cget("text")
                self.copy_btn.configure(text="✓ Copiado!")
                self.status_label.configure(text="Logs copiados para área de transferência")
                
                self.after(2000, lambda: self.copy_btn.configure(text="📋 Copiar"))
            else:
                self.status_label.configure(text="Nenhum log para copiar")
                
        except Exception as e:
            ui_logger.error(f"Erro ao copiar logs: {e}")
            self.status_label.configure(text=f"Erro ao copiar: {str(e)}")

    def _get_app_instance(self):
        """Obtém a instância do app principal"""
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

    def _on_back(self):
        """Volta para a tela anterior"""
        try:
            app = self._get_app_instance()
            if hasattr(app, 'show_screen'):
                app.show_screen("settings")  # Ou a tela que fez sentido no seu fluxo
        except Exception as e:
            ui_logger.error(f"Erro ao voltar: {e}")

    def on_show(self):
        """Chamado quando a tela é mostrada"""
        self._refresh_logs()
        if self._is_auto_refresh:
            self.status_label.configure(text="Auto-refresh ativado")

    def on_hide(self):
        """Chamado quando a tela é ocultada"""
        self._is_auto_refresh = False
        self.auto_refresh_var.set(False)