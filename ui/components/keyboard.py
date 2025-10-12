# frontend/ui/components/keyboard.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS
from utils.logger import ui_logger

class VirtualKeyboard(ctk.CTkToplevel):
    def __init__(self, target_entry=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.target_entry = target_entry
        self.shift_active = False
        
        self._setup_window()
        self._create_keyboard()
        
    def _setup_window(self):
        """Configura a janela do teclado"""
        self.title("Teclado Virtual")
        self.geometry("580x220")  # Um pouco menor
        self.resizable(False, False)
        self.configure(fg_color=COLORS["panel"])
        self.attributes("-topmost", True)
        
        # Centralizar na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = self.winfo_screenheight() - self.winfo_height() - 50
        self.geometry(f"+{x}+{y}")
        
    def _create_keyboard(self):
        """Cria o layout do teclado"""
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["panel"])
        main_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Linha 1: Números
        row1_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        row1_frame.pack(fill="x", pady=1)
        
        row1_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "⌫"]
        for key in row1_keys:
            btn_color = COLORS["accent"] if key == "⌫" else COLORS["neutral"]
            btn_hover = COLORS["accent_hover"] if key == "⌫" else COLORS["neutral_hover"]
            
            btn = ctk.CTkButton(
                row1_frame,
                text=key,
                width=45,
                height=35,
                command=lambda k=key: self._key_press(k),
                fg_color=btn_color,
                hover_color=btn_hover,
                text_color=COLORS["text"],
                font=FONTS["body"]
            )
            btn.pack(side="left", padx=1)
        
        # Linha 2: Letras QWERTY
        row2_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        row2_frame.pack(fill="x", pady=1)
        
        row2_keys = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
        for key in row2_keys:
            btn = ctk.CTkButton(
                row2_frame,
                text=key,
                width=45,
                height=35,
                command=lambda k=key: self._key_press(k),
                fg_color=COLORS["pill"],
                hover_color=COLORS["pill_hover"],
                text_color=COLORS["text"],
                font=FONTS["body"]
            )
            btn.pack(side="left", padx=1)
        
        # Linha 3: Letras ASDF
        row3_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        row3_frame.pack(fill="x", pady=1)
        
        row3_keys = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
        for key in row3_keys:
            btn = ctk.CTkButton(
                row3_frame,
                text=key,
                width=45,
                height=35,
                command=lambda k=key: self._key_press(k),
                fg_color=COLORS["pill"],
                hover_color=COLORS["pill_hover"],
                text_color=COLORS["text"],
                font=FONTS["body"]
            )
            btn.pack(side="left", padx=1)
        
        # Linha 4: Letras ZXCV e teclas especiais
        row4_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        row4_frame.pack(fill="x", pady=1)
        
        # Shift
        shift_btn = ctk.CTkButton(
            row4_frame,
            text="⇧",
            width=50,
            height=35,
            command=self._toggle_shift,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            text_color=COLORS["text"],
            font=FONTS["body"]
        )
        shift_btn.pack(side="left", padx=1)
        
        row4_keys = ["z", "x", "c", "v", "b", "n", "m", ",", ".", "-"]
        for key in row4_keys:
            btn = ctk.CTkButton(
                row4_frame,
                text=key,
                width=45,
                height=35,
                command=lambda k=key: self._key_press(k),
                fg_color=COLORS["pill"],
                hover_color=COLORS["pill_hover"],
                text_color=COLORS["text"],
                font=FONTS["body"]
            )
            btn.pack(side="left", padx=1)
        
        # Linha 5: Teclas especiais
        row5_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        row5_frame.pack(fill="x", pady=1)
        
        # Espaço
        space_btn = ctk.CTkButton(
            row5_frame,
            text="Espaço",
            width=180,
            height=35,
            command=lambda: self._key_press(" "),
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"],
            text_color=COLORS["text"],
            font=FONTS["body"]
        )
        space_btn.pack(side="left", padx=1)
        
        # Arroba
        at_btn = ctk.CTkButton(
            row5_frame,
            text="@",
            width=45,
            height=35,
            command=lambda: self._key_press("@"),
            fg_color=COLORS["pill"],
            hover_color=COLORS["pill_hover"],
            text_color=COLORS["text"],
            font=FONTS["body"]
        )
        at_btn.pack(side="left", padx=1)
        
        # Underscore
        underscore_btn = ctk.CTkButton(
            row5_frame,
            text="_",
            width=45,
            height=35,
            command=lambda: self._key_press("_"),
            fg_color=COLORS["pill"],
            hover_color=COLORS["pill_hover"],
            text_color=COLORS["text"],
            font=FONTS["body"]
        )
        underscore_btn.pack(side="left", padx=1)
        
        # Fechar
        close_btn = ctk.CTkButton(
            row5_frame,
            text="Fechar",
            width=70,
            height=35,
            command=self.destroy,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"],
            font=FONTS["body"]
        )
        close_btn.pack(side="right", padx=1)
        
    def _key_press(self, key):
        """Processa pressionamento de tecla"""
        if not self.target_entry:
            return
            
        current_text = self.target_entry.get()
        
        if key == "⌫":  # Backspace
            new_text = current_text[:-1]
        else:
            # Aplicar shift se ativo
            if self.shift_active and key.isalpha():
                key = key.upper()
            new_text = current_text + key
            
            # Desativar shift após uma tecla
            if self.shift_active:
                self.shift_active = False
        
        self.target_entry.delete(0, "end")
        self.target_entry.insert(0, new_text)
        
    def _toggle_shift(self):
        """Alterna estado do shift"""
        self.shift_active = not self.shift_active
        
    def show(self):
        """Mostra o teclado"""
        self.deiconify()
        self.lift()
        self.focus_force()