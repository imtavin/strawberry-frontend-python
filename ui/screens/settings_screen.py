import customtkinter as ctk
from ui.icons import COLORS, FONTS
import subprocess
import threading
from utils.logger import ui_logger
class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, on_save: callable, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16, *args, **kwargs)
        self.on_save = on_save
        self.raspberry_info = {}
        self.config = master.config  # Acesso às configurações atuais
        
        # Botão voltar
        self.back_btn = ctk.CTkButton(
            self,
            text="← Voltar",
            width=80,
            height=32,
            corner_radius=16,
            fg_color=COLORS["pill_dark"],
            hover_color=COLORS["pill"],
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            command=self._on_back
        )
        self.back_btn.place(relx=0.02, rely=0.03, anchor="nw")
        
        self._build_ui()

    def _build_ui(self):
        # Container principal com scroll
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"], corner_radius=12)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.9)
        
        # ===== SEÇÃO: INFORMAÇÕES DA RASPBERRY =====
        info_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["pill_dark"])
        info_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="🔧 Informações da Raspberry",
            text_color=COLORS["accent"],
            font=FONTS["subtitle"]
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Hostname
        self.hostname_label = ctk.CTkLabel(
            info_frame,
            text="Hostname: Carregando...",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            anchor="w"
        )
        self.hostname_label.pack(fill="x", padx=15, pady=2)
        
        # IP para SSH
        self.ip_label = ctk.CTkLabel(
            info_frame,
            text="IP para SSH: Carregando...",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_bold"],
            anchor="w"
        )
        self.ip_label.pack(fill="x", padx=15, pady=2)
        
        # Botão para copiar IP
        copy_ip_btn = ctk.CTkButton(
            info_frame,
            text="📋 Copiar IP",
            width=100,
            height=28,
            command=self._copy_ip_to_clipboard,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=FONTS["body_small"]
        )
        copy_ip_btn.pack(anchor="e", padx=15, pady=5)
        
        # ===== SEÇÃO: CONFIGURAÇÕES DE CÂMERA =====
        camera_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["pill_dark"])
        camera_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            camera_frame,
            text="📷 Configurações de Câmera",
            text_color=COLORS["accent"],
            font=FONTS["subtitle"]
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # FPS
        fps_frame = ctk.CTkFrame(camera_frame, fg_color="transparent")
        fps_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            fps_frame,
            text="FPS:",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"]
        ).pack(side="left")
        
        self.fps_var = ctk.StringVar(value="15")
        fps_combo = ctk.CTkComboBox(
            fps_frame,
            values=["10", "15", "20", "25", "30"],
            variable=self.fps_var,
            width=120,
            state="readonly"
        )
        fps_combo.pack(side="right")
        
        # ===== SEÇÃO: SISTEMA =====
        system_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["pill_dark"])
        system_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            system_frame,
            text="⚙️ Sistema",
            text_color=COLORS["accent"],
            font=FONTS["subtitle"]
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Botão Reiniciar Serviço
        restart_btn = ctk.CTkButton(
            system_frame,
            text="🔄 Reiniciar Serviço",
            command=self._restart_service,
            fg_color=COLORS["warning"],
            hover_color=COLORS["warning_hover"],
            font=FONTS["body"]
        )
        restart_btn.pack(fill="x", padx=15, pady=5)
        
        # Botão Logs do Sistema
        logs_btn = ctk.CTkButton(
            system_frame,
            text="📊 Ver Logs",
            command=self._show_system_logs,
            fg_color=COLORS["info"],
            hover_color=COLORS["info_hover"],
            font=FONTS["body"]
        )
        logs_btn.pack(fill="x", padx=15, pady=5)
        
        # ===== BOTÕES DE AÇÃO =====
        action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=20)
        
        # Botão Salvar
        save_btn = ctk.CTkButton(
            action_frame,
            text="💾 Salvar Configurações",
            command=self._on_save,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=FONTS["body_bold"],
            height=40
        )
        save_btn.pack(side="left", padx=5, expand=True)
        
        # Botão Aplicar
        apply_btn = ctk.CTkButton(
            action_frame,
            text="⚡ Aplicar",
            command=self._on_apply,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            font=FONTS["body"],
            height=40
        )
        apply_btn.pack(side="right", padx=5, expand=True)

    def update_raspberry_info(self, raspberry_info: dict):
        """Atualiza a exibição com as informações da Raspberry"""
        try:
            self.raspberry_info = raspberry_info
            
            # Atualizar hostname
            hostname = raspberry_info.get('hostname', 'Desconhecido')
            self.hostname_label.configure(text=f"Hostname: {hostname}")
            
            # Atualizar IP
            ip = raspberry_info.get('ip', 'Indisponível')
            self.ip_label.configure(text=f"IP para SSH: {ip}")
            
        except Exception as e:
            ui_logger.error(f"Erro ao atualizar informações da Raspberry na UI: {e}")

    def _copy_ip_to_clipboard(self):
        """Copia o IP para a área de transferência"""
        try:
            ip = self.raspberry_info.get('ip', '')
            if ip and ip != 'Indisponível':
                self.clipboard_clear()
                self.clipboard_append(ip)
                # Feedback visual
                self.ip_label.configure(text=f"IP para SSH: {ip} ✅ COPIADO!")
                self.after(2000, lambda: self.ip_label.configure(text=f"IP para SSH: {ip}"))
        except Exception as e:
            ui_logger.error(f"Erro ao copiar IP: {e}")

    def _restart_service(self):
        """Reinicia o serviço da aplicação"""
        def restart():
            try:
                # Comando para reiniciar o serviço (ajuste conforme seu setup)
                subprocess.run(["sudo", "systemctl", "restart", "strawberry-ai"], check=True)
            except Exception as e:
                ui_logger.error(f"Erro ao reiniciar serviço: {e}")
        
        threading.Thread(target=restart, daemon=True).start()

    def _show_system_logs(self):
        """Mostra logs do sistema"""
        try:
            # Abre o arquivo de log mais recente
            subprocess.Popen(["sudo", "tail", "-f", "/var/log/strawberry-ai.log"])
        except Exception as e:
            ui_logger.error(f"Erro ao abrir logs: {e}")

    def _on_save(self):
        """Salva as configurações permanentemente"""
        new_settings = {
            "video": {
                "transport": self.transport_var.get()
            },
            "camera": {
                "resolution": self.resolution_var.get(),
                "target_fps": int(self.fps_var.get())
            }
        }
        
        if callable(self.on_save):
            self.on_save(new_settings)

    def _on_apply(self):
        """Aplica as configurações sem salvar permanentemente"""
        # Aqui você pode implementar a aplicação em tempo real
        # Por enquanto, apenas salva
        self._on_save()

    def _on_back(self):
        pass