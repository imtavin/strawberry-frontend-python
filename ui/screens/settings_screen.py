# ui/screens/settings_screen.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS

class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, on_save: callable, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16, *args, **kwargs)
        self.on_save = on_save
        
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

    def _on_back(self):
        # Voltar para home (será conectado no app principal)
        pass

    def _build_ui(self):
        # Container principal
        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=12)
        self.container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.9)
        
        # Título
        title = ctk.CTkLabel(
            self.container,
            text="Configurações",
            text_color=COLORS["text"],
            font=FONTS["title"]
        )
        title.pack(pady=10)
        
        # Configurações placeholder
        settings_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Exemplo de configuração
        setting1 = ctk.CTkLabel(
            settings_frame,
            text="Configuração 1: Em desenvolvimento",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"]
        )
        setting1.pack(anchor="w", pady=5)
        
        setting2 = ctk.CTkLabel(
            settings_frame,
            text="Configuração 2: Em desenvolvimento",
            text_color=COLORS["text_secondary"],
            font=FONTS["body"]
        )
        setting2.pack(anchor="w", pady=5)
        
        # Botão salvar
        save_btn = ctk.CTkButton(
            settings_frame,
            text="Salvar Configurações",
            command=self._on_save,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"]
        )
        save_btn.pack(pady=20)

    def _on_save(self):
        if callable(self.on_save):
            self.on_save({"message": "Configurações salvas"})