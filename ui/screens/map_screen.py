# ui/screens/map_screen.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS

class MapScreen(ctk.CTkFrame):
    """Placeholder map screen. Replace map widget if you integrate real map SDK later."""
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], *args, **kwargs)
        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=12)
        self.container.place(relx=0.012, rely=0.012, relwidth=0.976, relheight=0.976)
        title = ctk.CTkLabel(self.container, text="Mapa", font=FONTS["title"], text_color=COLORS["pill"])
        title.pack(anchor="nw", padx=16, pady=12)
        lbl = ctk.CTkLabel(self.container, text="Mapa (placeholder). Integre serviço de mapas se desejar.",
                           wraplength=800, text_color=COLORS["muted"])
        lbl.pack(padx=16, pady=20)
