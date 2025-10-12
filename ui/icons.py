# ui/icons.py
import os
from typing import Optional, Tuple
from PIL import Image, ImageTk
import customtkinter as ctk

# Cores atualizadas baseadas no feedback da designer
COLORS = {
    "bg": "#0a0a0a",
    "sidebar": "#1a1a1a", 
    "panel": "#141414",
    "panel_light": "#1e1e1e",
    "pill": "#2a2a2a",
    "pill_hover": "#3a3a3a",
    "pill_dark": "#1a1a1a",
    "border": "#333333",
    "text": "#ffffff",
    "text_secondary": "#b0b0b0",
    "muted": "#666666",
    
    # Cores principais (reduzidas para evitar sobrecarga)
    "accent": "#ff4757",  # Vermelho/rosa - usado com moderação
    "accent_hover": "#ff3742",
    
    # Verde mais escuro para aplicar
    "success": "#1e7b4c",  # Verde escuro
    "success_hover": "#2a9d64",
    
    # Azul para salvar
    "primary": "#1e6fa8",  # Azul
    "primary_hover": "#2a8fce",
    
    # Cores neutras para outros elementos
    "neutral": "#404040",
    "neutral_hover": "#505050",
    
    # Removemos warning_hover, info_hover para simplificar
}

# Fontes mantidas
FONTS = {
    "title": ("Inter", 16, "bold"),
    "subtitle": ("Inter", 14, "bold"),
    "menu": ("Inter", 12, "bold"),
    "body_bold": ("Inter", 11, "bold"),
    "body_small": ("Inter", 10),
    "body": ("Inter", 11),
    "pill": ("Inter", 10, "bold"),
    "small": ("Inter", 9),
}

WINDOW_PADDING = 8
SIDEBAR_WIDTH = 180
CAPTURE_BTN_SIZE = (160, 40)

# Cache de ícones e funções auxiliares mantidas...
_icon_cache = {}

def resource_path(rel_path: str) -> str:
    """Resolve caminho dos recursos"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    possible_paths = [
        os.path.join(base_dir, "icons", rel_path),
        os.path.join(base_dir, "assets", rel_path),
        os.path.join(base_dir, rel_path),
        rel_path
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    print(f" Arquivo não encontrado: {rel_path}")
    return rel_path

def load_icon(path: str, size: Tuple[int, int] = (20, 20)) -> Optional[ctk.CTkImage]:
    """Carrega ícone como CTkImage com cache"""
    cache_key = f"{path}_{size[0]}x{size[1]}"
    
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    
    try:
        full_path = resource_path(path)
        if not os.path.exists(full_path):
            image = Image.new('RGBA', size, (255, 255, 255, 0))
        else:
            image = Image.open(full_path)
            image = image.resize(size, Image.LANCZOS)
        
        ctk_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=size
        )
        
        _icon_cache[cache_key] = ctk_image
        return ctk_image
        
    except Exception as e:
        print(f"Erro carregando ícone {path}: {e}")
        image = Image.new('RGBA', size, (255, 255, 255, 0))
        ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=size)
        return ctk_image

# Ícones pré-carregados
ICONS = {
    "strawberry": lambda size=(28, 28): load_icon("strawberry.png", size),
    "camera": lambda size=(16, 16): load_icon("camera.png", size),
    "gallery": lambda size=(16, 16): load_icon("gallery.png", size),
    "maps": lambda size=(16, 16): load_icon("maps.png", size),
    "setting": lambda size=(16, 16): load_icon("setting.png", size),
    "battery": lambda size=(16, 12): load_icon("battery.png", size),
    "home": lambda size=(16, 16): load_icon("home.png", size) or load_icon("strawberry.png", size),
}