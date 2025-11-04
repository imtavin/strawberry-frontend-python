# ui/screens/map_screen.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS

class MapScreen(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16, *args, **kwargs)
        
        # Configurar grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Botão voltar NO TOPO - usando grid
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
        self.back_btn.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        self._build_ui()

    def _on_back(self):
        # O comando será configurado pelo FrontendApp
        pass

    def _build_ui(self):
        # Container principal - usando grid
        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=12)
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Título
        title = ctk.CTkLabel(
            self.container, 
            text="Mapa de Ocorrências", 
            font=FONTS["title"], 
            text_color=COLORS["text"]
        )
        title.grid(row=0, column=0, sticky="nw", padx=16, pady=12)
        
        # Placeholder do mapa
        lbl = ctk.CTkLabel(
            self.container, 
            text="Mapa (placeholder). Integre serviço de mapas se desejar.",
            wraplength=600, 
            text_color=COLORS["muted"],
            font=FONTS["body"]
        )
        lbl.grid(row=1, column=0, sticky="nsew", padx=16, pady=20)