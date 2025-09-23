# ui/icons.py
import os
from typing import Optional, Tuple
from PIL import Image, ImageTk
import customtkinter as ctk

# Cores atualizadas para um visual mais moderno
COLORS = {
    "bg": "#0a0a0a",
    "sidebar": "#1a1a1a", 
    "panel": "#141414",
    "panel_light": "#1e1e1e",
    "pill": "#ffffff",
    "pill_hover": "#f0f0f0",
    "pill_dark": "#2a2a2a",
    "text": "#ffffff",
    "text_secondary": "#b0b0b0",
    "muted": "#666666",
    "accent": "#ff4757",
    "accent_hover": "#ff3742",
    "success": "#2ed573",
    "warning": "#ffa502",
}

FONTS = {
    "title": ("Inter", 20, "bold"),
    "subtitle": ("Inter", 16, "bold"),
    "menu": ("Inter", 14, "bold"),
    "body": ("Inter", 13),
    "pill": ("Inter", 12, "bold"),
    "small": ("Inter", 11),
}

WINDOW_PADDING = 15
SIDEBAR_WIDTH = 260
CAPTURE_BTN_SIZE = (200, 52)

# Cache de ícones
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
    
    print(f"⚠️ Arquivo não encontrado: {rel_path}")
    return rel_path

def load_icon(path: str, size: Tuple[int, int] = (24, 24)) -> Optional[ctk.CTkImage]:
    """Carrega ícone como CTkImage com cache"""
    cache_key = f"{path}_{size[0]}x{size[1]}"
    
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    
    try:
        full_path = resource_path(path)
        if not os.path.exists(full_path):
            # Criar ícone placeholder se não existir
            print(f"Ícone não encontrado: {full_path}")
            image = Image.new('RGBA', size, (255, 255, 255, 0))
        else:
            image = Image.open(full_path)
            image = image.resize(size, Image.LANCZOS)
        
        # Criar versões light e dark
        ctk_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=size
        )
        
        _icon_cache[cache_key] = ctk_image
        return ctk_image
        
    except Exception as e:
        print(f"Erro carregando ícone {path}: {e}")
        # Retornar ícone placeholder
        image = Image.new('RGBA', size, (255, 255, 255, 0))
        ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=size)
        return ctk_image

# Ícones pré-carregados
ICONS = {
    "strawberry": lambda size=(32, 32): load_icon("strawberry.png", size),
    "camera": lambda size=(20, 20): load_icon("camera.png", size),
    "gallery": lambda size=(20, 20): load_icon("gallery.png", size),
    "maps": lambda size=(20, 20): load_icon("maps.png", size),
    "setting": lambda size=(20, 20): load_icon("setting.png", size),
    "battery": lambda size=(20, 16): load_icon("battery.png", size),
    "home": lambda size=(20, 20): load_icon("home.png", size) or load_icon("strawberry.png", size),
}