"""
Componente de diálogo para exibição de logs do sistema
"""
import customtkinter as ctk
from typing import Optional, Callable
from utils.logger import ui_logger
from ui.icons import COLORS, FONTS

class LogsDialog(ctk.CTkToplevel):
    """
    Diálogo modal para exibição e gerenciamento de logs do sistema
    """
    
    def __init__(
        self, 
        parent, 
        title: str = "Logs do Sistema",
        initial_logs: str = "",
        on_refresh: Optional[Callable] = None,
        *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self.on_refresh = on_refresh
        self._auto_scroll = True
        
        # Configuração da janela
        self.title(title)
        self.geometry("800x600")
        self.minsize(600, 400)
        self.resizable(True, True)
        
        # Define como modal
        self.transient(parent)
        self.grab_set()
        
        # Foca nesta janela
        self.focus_set()
        
        # Configura protocolo de fechamento
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Configuração de estilo
        self.configure(fg_color=COLORS["bg"])
        
        self._create_widgets()
        self._layout_widgets()
        
        # Carrega logs iniciais
        if initial_logs:
            self.set_logs(initial_logs)
        
        # Centraliza na tela
        self._center_on_parent()
        
        ui_logger.info("Diálogo de logs inicializado")

    def _create_widgets(self):
        """Cria todos os widgets do diálogo"""
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color=COLORS["panel"], 
            corner_radius=12
        )
        
        # Header
        self.header_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="transparent"
        )
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Logs do Sistema",
            text_color=COLORS["text"],
            font=FONTS["title"]
        )
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Últimas atividades e eventos do sistema",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"]
        )
        
        # Controles
        self.controls_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        
        # Botão atualizar
        self.refresh_btn = ctk.CTkButton(
            self.controls_frame,
            text="🔄 Atualizar",
            width=100,
            height=32,
            command=self._on_refresh,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        
        # Botão copiar
        self.copy_btn = ctk.CTkButton(
            self.controls_frame,
            text="📋 Copiar",
            width=90,
            height=32,
            command=self._on_copy,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        
        # Botão limpar
        self.clear_btn = ctk.CTkButton(
            self.controls_frame,
            text="🗑️ Limpar",
            width=80,
            height=32,
            command=self._on_clear,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        
        # Checkbox auto-scroll
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        self.auto_scroll_cb = ctk.CTkCheckBox(
            self.controls_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            command=self._on_auto_scroll_toggle,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=FONTS["body_small"]
        )
        
        # Área de logs
        self.logs_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["pill_dark"],
            corner_radius=8
        )
        
        # Widget de texto para logs com scrollbar
        self.text_widget = ctk.CTkTextbox(
            self.logs_frame,
            wrap="word",
            fg_color=COLORS["bg"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            font=("Consolas", 12),  # Fonte monoespaçada para logs
            activate_scrollbars=True
        )
        
        # Footer
        self.footer_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        
        self.status_label = ctk.CTkLabel(
            self.footer_frame,
            text="Pronto",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"]
        )
        
        self.lines_label = ctk.CTkLabel(
            self.footer_frame,
            text="0 linhas",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"]
        )
        
        # Botão fechar
        self.close_btn = ctk.CTkButton(
            self.footer_frame,
            text="Fechar",
            width=100,
            height=36,
            command=self._on_close,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=FONTS["body"]
        )

    def _layout_widgets(self):
        """Layout dos widgets no diálogo"""
        
        # Frame principal
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))
        self.title_label.pack(anchor="w")
        self.subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Controles
        self.controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Botões de controle (esquerda)
        left_controls = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        left_controls.pack(side="left")
        
        self.refresh_btn.pack(side="left", padx=(0, 10))
        self.copy_btn.pack(side="left", padx=(0, 10))
        self.clear_btn.pack(side="left", padx=(0, 20))
        self.auto_scroll_cb.pack(side="left")
        
        # Área de logs
        self.logs_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.logs_frame.grid_rowconfigure(0, weight=1)
        self.logs_frame.grid_columnconfigure(0, weight=1)
        
        self.text_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Footer
        self.footer_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Status e linhas à esquerda
        left_footer = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        left_footer.pack(side="left")
        
        self.status_label.pack(side="left", padx=(0, 15))
        self.lines_label.pack(side="left")
        
        # Botão fechar à direita
        self.close_btn.pack(side="right")

    def _center_on_parent(self):
        """Centraliza o diálogo em relação ao parent"""
        self.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}")

    def set_logs(self, logs: str, source: str = "Sistema"):
        """Define o conteúdo dos logs"""
        try:
            # Habilita edição temporariamente
            self.text_widget.configure(state="normal")
            
            # Limpa conteúdo anterior
            self.text_widget.delete("1.0", "end")
            
            # Insere novos logs
            self.text_widget.insert("1.0", logs)
            
            # Desabilita edição
            self.text_widget.configure(state="disabled")
            
            # Auto-scroll para o final se habilitado
            if self._auto_scroll:
                self.text_widget.see("end")
            
            # Atualiza status
            lines = len(logs.split('\n'))
            self.lines_label.configure(text=f"{lines} linhas")
            self.status_label.configure(text=f"Logs de {source}")
            
            ui_logger.debug(f"Logs atualizados: {lines} linhas")
            
        except Exception as e:
            ui_logger.error(f"Erro ao definir logs: {e}")
            self.status_label.configure(text=f"Erro: {str(e)}")

    def append_logs(self, new_logs: str):
        """Adiciona logs ao conteúdo existente"""
        try:
            self.text_widget.configure(state="normal")
            
            # Vai para o final
            self.text_widget.insert("end", new_logs)
            
            self.text_widget.configure(state="disabled")
            
            if self._auto_scroll:
                self.text_widget.see("end")
                
            # Atualiza contador de linhas
            current_content = self.text_widget.get("1.0", "end-1c")
            lines = len(current_content.split('\n'))
            self.lines_label.configure(text=f"{lines} linhas")
            
        except Exception as e:
            ui_logger.error(f"Erro ao adicionar logs: {e}")

    def clear_logs(self):
        """Limpa todos os logs"""
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", "end")
            self.text_widget.configure(state="disabled")
            
            self.lines_label.configure(text="0 linhas")
            self.status_label.configure(text="Logs limpos")
            
            ui_logger.info("Logs limpos")
            
        except Exception as e:
            ui_logger.error(f"Erro ao limpar logs: {e}")

    def get_logs(self) -> str:
        """Retorna o conteúdo atual dos logs"""
        try:
            return self.text_widget.get("1.0", "end-1c")
        except Exception as e:
            ui_logger.error(f"Erro ao obter logs: {e}")
            return ""

    def _on_refresh(self):
        """Callback para botão atualizar"""
        try:
            self.status_label.configure(text="Atualizando...")
            self.refresh_btn.configure(state="disabled")
            
            if self.on_refresh:
                self.on_refresh()
            else:
                # Atualização local - apenas força scroll para o final
                if self._auto_scroll:
                    self.text_widget.see("end")
                self.status_label.configure(text="Atualizado")
                
            ui_logger.debug("Logs atualizados")
            
        except Exception as e:
            ui_logger.error(f"Erro ao atualizar logs: {e}")
            self.status_label.configure(text=f"Erro: {str(e)}")
        finally:
            self.refresh_btn.configure(state="normal")

    def _on_copy(self):
        """Callback para botão copiar"""
        try:
            logs_content = self.get_logs()
            if logs_content:
                self.clipboard_clear()
                self.clipboard_append(logs_content)
                
                # Feedback visual
                original_text = self.copy_btn.cget("text")
                self.copy_btn.configure(text="✓ Copiado!")
                self.status_label.configure(text="Logs copiados para área de transferência")
                
                self.after(2000, lambda: self.copy_btn.configure(text=original_text))
                
                ui_logger.debug("Logs copiados para clipboard")
            else:
                self.status_label.configure(text="Nenhum log para copiar")
                
        except Exception as e:
            ui_logger.error(f"Erro ao copiar logs: {e}")
            self.status_label.configure(text=f"Erro ao copiar: {str(e)}")

    def _on_clear(self):
        """Callback para botão limpar"""
        try:
            self.clear_logs()
        except Exception as e:
            ui_logger.error(f"Erro ao limpar logs: {e}")

    def _on_auto_scroll_toggle(self):
        """Callback para toggle do auto-scroll"""
        self._auto_scroll = self.auto_scroll_var.get()
        status = "habilitado" if self._auto_scroll else "desabilitado"
        self.status_label.configure(text=f"Auto-scroll {status}")
        
        if self._auto_scroll:
            self.text_widget.see("end")

    def _on_close(self):
        """Callback para fechar o diálogo"""
        try:
            ui_logger.info("Fechando diálogo de logs")
            self.grab_release()
            self.destroy()
        except Exception as e:
            ui_logger.error(f"Erro ao fechar diálogo: {e}")

    def show(self):
        """Mostra o diálogo (apenas para compatibilidade)"""
        self.wait_window()

class LogsViewer(ctk.CTkFrame):
    """
    Componente embutido para visualização de logs (para uso em telas)
    """
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self._auto_scroll = True
        
        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self):
        """Cria widgets do viewer embutido"""
        
        # Header compacto
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Logs do Sistema",
            text_color=COLORS["text"],
            font=FONTS["subtitle"]
        )
        
        # Controles compactos
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.refresh_btn = ctk.CTkButton(
            self.controls_frame,
            text="🔄",
            width=40,
            height=28,
            command=self._on_refresh,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        
        self.copy_btn = ctk.CTkButton(
            self.controls_frame,
            text="📋",
            width=40,
            height=28,
            command=self._on_copy,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        
        self.clear_btn = ctk.CTkButton(
            self.controls_frame,
            text="🗑️",
            width=40,
            height=28,
            command=self._on_clear,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            font=FONTS["body_small"]
        )
        
        # Área de logs compacta
        self.logs_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["pill_dark"],
            corner_radius=8
        )
        
        self.text_widget = ctk.CTkTextbox(
            self.logs_frame,
            wrap="word",
            fg_color=COLORS["bg"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            font=("Consolas", 11),
            activate_scrollbars=True
        )
        
        # Status
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Pronto",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"]
        )
        
        self.lines_label = ctk.CTkLabel(
            self.status_frame,
            text="0 linhas",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"]
        )

    def _layout_widgets(self):
        """Layout do viewer embutido"""
        
        # Header
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.title_label.pack(side="left")
        
        # Controles à direita do header
        self.controls_frame.pack(side="right")
        self.refresh_btn.pack(side="left", padx=(5, 0))
        self.copy_btn.pack(side="left", padx=(5, 0))
        self.clear_btn.pack(side="left", padx=(5, 0))
        
        # Área de logs
        self.logs_frame.pack(fill="both", expand=True)
        self.logs_frame.grid_rowconfigure(0, weight=1)
        self.logs_frame.grid_columnconfigure(0, weight=1)
        
        self.text_widget.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        
        # Status
        self.status_frame.pack(fill="x", pady=(5, 0))
        self.status_label.pack(side="left")
        self.lines_label.pack(side="right")

    # Métodos compatíveis com LogsDialog
    def set_logs(self, logs: str, source: str = "Sistema"):
        """Define o conteúdo dos logs"""
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", logs)
            self.text_widget.configure(state="disabled")
            
            if self._auto_scroll:
                self.text_widget.see("end")
            
            lines = len(logs.split('\n'))
            self.lines_label.configure(text=f"{lines} linhas")
            self.status_label.configure(text=f"Logs de {source}")
            
        except Exception as e:
            ui_logger.error(f"Erro ao definir logs: {e}")

    def append_logs(self, new_logs: str):
        """Adiciona logs ao conteúdo existente"""
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", new_logs)
            self.text_widget.configure(state="disabled")
            
            if self._auto_scroll:
                self.text_widget.see("end")
                
            current_content = self.text_widget.get("1.0", "end-1c")
            lines = len(current_content.split('\n'))
            self.lines_label.configure(text=f"{lines} linhas")
            
        except Exception as e:
            ui_logger.error(f"Erro ao adicionar logs: {e}")

    def clear_logs(self):
        """Limpa todos os logs"""
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", "end")
            self.text_widget.configure(state="disabled")
            
            self.lines_label.configure(text="0 linhas")
            self.status_label.configure(text="Logs limpos")
            
        except Exception as e:
            ui_logger.error(f"Erro ao limpar logs: {e}")

    def get_logs(self) -> str:
        """Retorna o conteúdo atual dos logs"""
        try:
            return self.text_widget.get("1.0", "end-1c")
        except Exception as e:
            ui_logger.error(f"Erro ao obter logs: {e}")
            return ""

    def _on_refresh(self):
        """Callback para atualizar"""
        if self._auto_scroll:
            self.text_widget.see("end")
        self.status_label.configure(text="Atualizado")

    def _on_copy(self):
        """Callback para copiar"""
        try:
            logs_content = self.get_logs()
            if logs_content:
                self.clipboard_clear()
                self.clipboard_append(logs_content)
                
                original_text = self.copy_btn.cget("text")
                self.copy_btn.configure(text="✓")
                self.status_label.configure(text="Copiado!")
                
                self.after(2000, lambda: self.copy_btn.configure(text="📋"))
                
        except Exception as e:
            ui_logger.error(f"Erro ao copiar logs: {e}")

    def _on_clear(self):
        """Callback para limpar"""
        self.clear_logs()