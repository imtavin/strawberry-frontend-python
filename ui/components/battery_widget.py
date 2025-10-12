# ui/widgets/battery_widget.py
import tkinter as tk
import customtkinter as ctk
from ui.icons import COLORS, ICONS

class BatteryWidget(ctk.CTkFrame):
    """Widget de bateria estilizado"""
    
    def __init__(self, master, percentage: int = 75, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.percentage = percentage
        self._build_ui()

    def _build_ui(self):
        # Container principal
        container = ctk.CTkFrame(self, fg_color=COLORS["pill_dark"], corner_radius=12)
        container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Layout horizontal
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # Ícone de bateria
        battery_icon = ICONS["battery"]((16, 12))
        if battery_icon:
            icon_label = ctk.CTkLabel(container, image=battery_icon, text="")
            icon_label.grid(row=0, column=0, padx=(8, 4), pady=4, sticky="w")
        
        # Porcentagem
        self.percentage_label = ctk.CTkLabel(
            container, 
            text=f"{self.percentage}%", 
            text_color=COLORS["text_secondary"],
            font=("Inter", 11, "bold")
        )
        self.percentage_label.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="e")
        
        # Barra de progresso visual
        self._create_visual_indicator()

    def _create_visual_indicator(self):
        """Cria indicador visual de bateria"""
        # Determinar cor baseada na porcentagem
        if self.percentage > 70:
            color = COLORS["success"]
        elif self.percentage > 30:
            color = COLORS["warning"]
        else:
            color = COLORS["accent"]
        
        # Canvas para a barra
        canvas = tk.Canvas(
            self, 
            width=40, 
            height=6, 
            highlightthickness=0,
            bg=COLORS["pill_dark"]
        )
        canvas.place(relx=0.5, rely=0.8, anchor="center")
        
        # Fundo
        canvas.create_rectangle(2, 2, 38, 4, fill=COLORS["muted"], outline="")
        
        # Preenchimento
        fill_width = max(2, int(36 * (self.percentage / 100.0)))
        canvas.create_rectangle(2, 2, 2 + fill_width, 4, fill=color, outline="")

    def set_percentage(self, percentage: int):
        """Atualiza porcentagem da bateria"""
        self.percentage = max(0, min(100, percentage))
        self.percentage_label.configure(text=f"{self.percentage}%")
        self._create_visual_indicator()