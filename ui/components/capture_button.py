# ui/widgets/capture_button.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS, ICONS

class CaptureButton(ctk.CTkButton):
    """Botão de captura compacto para 800x400"""
    
    def __init__(self, master, command=None, width=140, height=45, *args, **kwargs):
        # Ícone da câmera menor
        camera_icon = ICONS["camera"]()
        
        super().__init__(
            master,
            text=" Capturar" if camera_icon else "Capturar",
            image=camera_icon,
            width=width,      # Usar o parâmetro width
            height=height,    # Usar o parâmetro height
            corner_radius=20,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            font=FONTS["pill"],
            command=command,
            *args, **kwargs
        )
        
        self.configure(border_width=0)

    def disable(self):
        """Desabilita o botão"""
        self.configure(
            state="disabled", 
            fg_color=COLORS["muted"],
            hover_color=COLORS["muted"]
        )

    def enable(self):
        """Habilita o botão"""
        self.configure(
            state="normal", 
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"]
        )