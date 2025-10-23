# screen_manager.py
import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from utils.logger import ui_logger

class ScreenManager:
    """Gerencia transições entre telas com cache e lifecycle"""
    
    def __init__(self, master):
        self.master = master
        self.screens: Dict[str, ctk.CTkFrame] = {}
        self.current_screen: Optional[str] = None
        self.screen_stack = []
        
    def register_screen(self, name: str, screen_class: type, *args, **kwargs):
        """Registra uma tela - mesma interface que antes"""
        if name in self.screens:
            ui_logger.warning(f"Tela {name} já registrada. Substituindo.")
            
        screen = screen_class(self.master, *args, **kwargs)
        screen.grid(row=0, column=0, sticky="nsew")
        self.screens[name] = screen
        screen.lower()  # Esconde por padrão
        
        ui_logger.debug(f"Tela registrada: {name}")
        return screen

    def show_screen(self, name: str):
        """Mostra tela específica - mesma interface que antes"""
        if name not in self.screens:
            ui_logger.error(f"Tela não registrada: {name}")
            return

        # Esconde tela atual
        if self.current_screen:
            self.screens[self.current_screen].lower()

        # Mostra nova tela
        self.screens[name].lift()
        self.current_screen = name
        ui_logger.info(f"Tela ativa: {name}")

    def get_screen(self, name: str) -> Optional[ctk.CTkFrame]:
        """Obtém referência para uma tela"""
        return self.screens.get(name)

    def show_previous(self):
        """Volta para tela anterior (se houver histórico)"""
        if len(self.screen_stack) > 1:
            self.screen_stack.pop()  # Remove atual
            previous = self.screen_stack.pop()  # Pega anterior
            self.show_screen(previous)