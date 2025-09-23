# ui/screens/map_screen.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS

class MapScreen(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16, *args, **kwargs)
        
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
            text="Mapa de Ocorrências", 
            font=FONTS["title"], 
            text_color=COLORS["text"]
        )
        title.pack(anchor="nw", padx=16, pady=12)
        
        # Placeholder do mapa
        lbl = ctk.CTkLabel(
            self.container, 
            text="Mapa (placeholder). Integre serviço de mapas se desejar.",
            wraplength=600, 
            text_color=COLORS["muted"],
            font=FONTS["body"]
        )
        lbl.pack(padx=16, pady=20)