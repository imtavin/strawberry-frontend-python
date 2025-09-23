# ui/screens/home_screen.py
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Callable, Optional
from ui.icons import COLORS, FONTS, ICONS
from ui.widgets.capture_button import CaptureButton
from ui.widgets.battery_widget import BatteryWidget

class VideoState(ctk.CTkFrame):
    """Estado de vídeo com layout centralizado e bonito"""
    
    def __init__(self, parent, on_capture: Callable, *args, **kwargs):
        super().__init__(parent, fg_color=COLORS["panel_light"], *args, **kwargs)
        self.on_capture = on_capture
        self._build_ui()

    def _build_ui(self):
        # Container centralizado
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        
        # Área do vídeo com borda estilizada
        video_container = ctk.CTkFrame(
            main_container, 
            fg_color=COLORS["bg"], 
            corner_radius=16,
            border_width=2,
            border_color=COLORS["pill_dark"]
        )
        video_container.pack(fill="both", expand=True, pady=(0, 20))
        
        self.video_label = ctk.CTkLabel(
            video_container, 
            text="",
            fg_color=COLORS["bg"],
            corner_radius=14
        )
        self.video_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
        
        # Container do botão centralizado
        button_container = ctk.CTkFrame(main_container, fg_color="transparent")
        button_container.pack(fill="x", pady=10)
        
        self.capture_btn = CaptureButton(button_container, command=self._on_click_capture)
        self.capture_btn.pack(anchor="center")

    def _on_click_capture(self):
        self.capture_btn.disable()
        if callable(self.on_capture):
            try:
                self.on_capture()
            except Exception as e:
                print("Erro no on_capture:", e)
                self.capture_btn.enable()

    def update_frame_image(self, pil_image):
        try:
            # # Redimensionar imagem para caber no container
            # target_width = 800
            # target_height = 450
            
            # pil_image = pil_image.resize((target_width, target_height), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(pil_image)
            
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk
            
        except Exception as e:
            print("Falha ao atualizar frame:", e)

    def enable_capture(self):
        self.capture_btn.enable()

class LoadingState(ctk.CTkFrame):
    """Tela de loading animada"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, fg_color=COLORS["panel_light"], *args, **kwargs)
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ícone de loading (usando morango)
        strawberry_icon = ICONS["strawberry"]((64, 64))
        if strawberry_icon:
            icon_label = ctk.CTkLabel(container, image=strawberry_icon, text="")
            icon_label.pack(pady=(0, 20))
        
        # Texto com animação
        self.loading_label = ctk.CTkLabel(
            container,
            text="Analisando imagem",
            text_color=COLORS["text"],
            font=FONTS["subtitle"]
        )
        self.loading_label.pack(pady=5)
        
        # Pontinhos animados
        self.dots_label = ctk.CTkLabel(
            container,
            text="•",
            text_color=COLORS["accent"],
            font=("Inter", 24)
        )
        self.dots_label.pack()
        
        self.dot_count = 0
        self.animate_dots()

    def animate_dots(self):
        """Anima os pontinhos de loading"""
        dots = "•" * (self.dot_count % 4)
        self.dots_label.configure(text=dots)
        self.dot_count += 1
        self.after(500, self.animate_dots)

class ResultState(ctk.CTkFrame):
    """Tela de resultado"""
    
    def __init__(self, parent, on_back: Callable = None, *args, **kwargs):
        super().__init__(parent, fg_color=COLORS["panel_light"], *args, **kwargs)
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        
        # Botão voltar
        self.back_btn = ctk.CTkButton(
            main_container,
            text="← Voltar",
            width=100,
            height=36,
            corner_radius=18,
            fg_color=COLORS["pill_dark"],
            hover_color=COLORS["pill"],
            text_color=COLORS["text_secondary"],
            font=FONTS["body"],
            command=self._on_back
        )
        self.back_btn.pack(anchor="nw", pady=(0, 30))

        # Container do resultado
        result_container = ctk.CTkFrame(main_container, fg_color="transparent")
        result_container.pack(fill="both", expand=True)
        
        # Ícone de resultado
        result_icon = ICONS["strawberry"]((80, 80))
        if result_icon:
            icon_label = ctk.CTkLabel(result_container, image=result_icon, text="")
            icon_label.pack(pady=(0, 30))

        # Pills de resultado
        pills_container = ctk.CTkFrame(result_container, fg_color="transparent")
        pills_container.pack(anchor="center", pady=20)
        
        self.result_pill = ctk.CTkLabel(
            pills_container,
            text="Resultado: —",
            width=280,
            height=52,
            corner_radius=26,
            fg_color=COLORS["pill"],
            text_color=COLORS["bg"],
            font=FONTS["pill"]
        )
        self.result_pill.pack(pady=10)
        
        self.conf_pill = ctk.CTkLabel(
            pills_container,
            text="Confiança: —",
            width=200,
            height=44,
            corner_radius=22,
            fg_color=COLORS["success"],
            text_color="#ffffff",
            font=FONTS["body"]
        )
        self.conf_pill.pack(pady=5)

    def _on_back(self):
        if callable(self.on_back):
            self.on_back()

    def set_result(self, text: str, confidence: str):
        self.result_pill.configure(text=f"Resultado: {text}")
        self.conf_pill.configure(text=f"Confiança: {confidence}")

class HomeScreen(ctk.CTkFrame):
    """Tela principal com layout moderno"""
    
    def __init__(self, master, on_capture: Callable, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=20, *args, **kwargs)
        
        # Frame interno com sombra simulada
        self.inner = ctk.CTkFrame(
            self, 
            fg_color=COLORS["panel_light"], 
            corner_radius=16
        )
        self.inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.96)
        
        # Widget de bateria no canto
        self.battery = BatteryWidget(self.inner, percentage=82)
        self.battery.place(relx=0.95, rely=0.03, anchor="ne")

        # Estados
        self.video_state = VideoState(self.inner, on_capture=on_capture)
        self.loading_state = LoadingState(self.inner)
        self.result_state = ResultState(self.inner, on_back=lambda: self.show_state("video"))

        # Posicionar estados
        for state in [self.video_state, self.loading_state, self.result_state]:
            state.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9)

        self.states = {
            "video": self.video_state,
            "loading": self.loading_state,
            "result": self.result_state
        }

        self.show_state("video")

    def show_state(self, state_name: str):
        """Mostra um estado específico"""
        for state in self.states.values():
            state.lower()
        
        if state_name in self.states:
            self.states[state_name].lift()

    def update_frame(self, pil_image):
        """Atualiza frame de vídeo"""
        self.video_state.update_frame_image(pil_image)

    def set_result(self, text: str, confidence: str):
        """Define resultado da análise"""
        self.result_state.set_result(text, confidence)
        self.show_state("result")
        self.video_state.enable_capture()