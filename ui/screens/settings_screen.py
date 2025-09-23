# ui/screens/settings_screen.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS

class SettingsScreen(ctk.CTkFrame):
    """Basic settings screen. Extend with app-specific settings persisted to config.json as needed."""
    def __init__(self, master, on_save=None, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], *args, **kwargs)
        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=12)
        self.container.place(relx=0.012, rely=0.012, relwidth=0.976, relheight=0.976)
        title = ctk.CTkLabel(self.container, text="Configurações", font=FONTS["title"], text_color=COLORS["pill"])
        title.pack(anchor="nw", padx=16, pady=12)
        self.on_save = on_save
        # Example setting: server host
        self.server_host = ctk.CTkEntry(self.container, placeholder_text="Server host")
        self.server_host.pack(padx=16, pady=8)
        self.server_port = ctk.CTkEntry(self.container, placeholder_text="Server port")
        self.server_port.pack(padx=16, pady=8)
        save_btn = ctk.CTkButton(self.container, text="Salvar", command=self._save)
        save_btn.pack(padx=16, pady=16, anchor="w")

    def _save(self):
        if callable(self.on_save):
            try:
                self.on_save({
                    "server": {"host": self.server_host.get(), "port": int(self.server_port.get() or 0)}
                })
            except Exception as e:
                print("Erro salvando configuracoes:", e)
