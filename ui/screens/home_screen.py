# ui/screens/home_screen.py
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image, ImageTk
from typing import Callable, Optional
from ui.icons import COLORS, FONTS, ICONS
from ui.components.capture_button import CaptureButton
from ui.components.battery_widget import BatteryWidget

class VideoState(ctk.CTkFrame):
    """Estado de vídeo com botão sobreposto"""
    
    def __init__(self, parent, on_capture: Callable, *args, **kwargs):
        super().__init__(parent, fg_color=COLORS["panel_light"], *args, **kwargs)
        self.on_capture = on_capture
        self.current_image = None
        self._build_ui()

    def _build_ui(self):
        # Container do vídeo que ocupa toda a área
        self.video_container = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg"], 
            corner_radius=12,
            border_width=1,
            border_color=COLORS["pill_dark"]
        )
        self.video_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.98)
        
        # Label do vídeo que ocupa todo o container
        self.video_label = ctk.CTkLabel(
            self.video_container, 
            text="Aguardando vídeo...",
            fg_color=COLORS["bg"],
            corner_radius=10,
            text_color=COLORS["text_secondary"],
            font=FONTS["body"]
        )
        self.video_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.99, relheight=0.99)
        
        # Botão de captura SOBREPOSTO no canto inferior direito
        self.capture_btn = CaptureButton(
            self.video_container, 
            command=self._on_click_capture
        )
        self.capture_btn.place(relx=0.55, rely=0.95, anchor="se")

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
            self.current_image = pil_image  # Guardar referência para captura
            
            # Redimensionar para ocupar TODO o espaço disponível
            container_width = self.video_label.winfo_width()
            container_height = self.video_label.winfo_height()
            
            # Usar dimensões reais se disponíveis, senão usar estimativas
            if container_width < 10:  # Se ainda não foi renderizado
                container_width = 580
                container_height = 320
            
            # Manter aspect ratio
            img_ratio = pil_image.width / pil_image.height
            target_ratio = container_width / container_height
            
            if img_ratio > target_ratio:
                # Imagem mais larga - preencher altura
                new_height = container_height
                new_width = int(container_height * img_ratio)
            else:
                # Imagem mais alta - preencher largura
                new_width = container_width
                new_height = int(container_width / img_ratio)
            
            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

            ctk_img = CTkImage(light_image=resized_image, size=(new_width, new_height))
            
            self.video_label.configure(image=ctk_img, text="")
            self.video_label.image = ctk_img
            
        except Exception as e:
            print("Falha ao atualizar frame:", e)
            self.video_label.configure(text="Erro no vídeo")

    def enable_capture(self):
        self.capture_btn.enable()

    def get_current_frame(self):
        """Retorna o frame atual para captura"""
        return self.current_image


class LoadingState(ctk.CTkFrame):
    """Tela de loading compacta"""
    
    def __init__(self, parent, on_back: Callable = None, *args, **kwargs):
        super().__init__(parent, fg_color=COLORS["panel_light"], *args, **kwargs)
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Botão voltar no canto superior esquerdo
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
        self.back_btn.place(relx=0.02, rely=0.03, anchor="nw")
        
        # Ícone de loading menor
        strawberry_icon = ICONS["strawberry"]((48, 48))
        if strawberry_icon:
            icon_label = ctk.CTkLabel(container, image=strawberry_icon, text="")
            icon_label.pack(pady=(0, 15))
        
        # Texto menor
        self.loading_label = ctk.CTkLabel(
            container,
            text="Analisando imagem",
            text_color=COLORS["text"],
            font=FONTS["subtitle"]
        )
        self.loading_label.pack(pady=3)
        
        # Pontinhos animados
        self.dots_label = ctk.CTkLabel(
            container,
            text="•",
            text_color=COLORS["accent"],
            font=("Inter", 20)
        )
        self.dots_label.pack()
        
        self.dot_count = 0
        self.animate_dots()

    def _on_back(self):
        if callable(self.on_back):
            self.on_back()

    def animate_dots(self):
        """Anima os pontinhos de loading"""
        dots = "•" * (self.dot_count % 4)
        self.dots_label.configure(text=dots)
        self.dot_count += 1
        self.after(500, self.animate_dots)


class ResultState(ctk.CTkFrame):
    """Tela de resultado compacta"""
    
    def __init__(self, parent, on_back: Callable = None, *args, **kwargs):
        super().__init__(parent, fg_color=COLORS["panel_light"], *args, **kwargs)
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.85)
        
        # Botão voltar no canto superior esquerdo
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
        self.back_btn.place(relx=0.02, rely=0.03, anchor="nw")

        # Container do resultado compacto
        result_container = ctk.CTkFrame(main_container, fg_color="transparent")
        result_container.pack(fill="both", expand=True)
        
        # Ícone de resultado menor
        result_icon = ICONS["strawberry"]((60, 60))
        if result_icon:
            icon_label = ctk.CTkLabel(result_container, image=result_icon, text="")
            icon_label.pack(pady=(0, 20))

        # Pills de resultado menores
        pills_container = ctk.CTkFrame(result_container, fg_color="transparent")
        pills_container.pack(anchor="center", pady=15)
        
        self.result_pill = ctk.CTkLabel(
            pills_container,
            text="Resultado: —",
            width=220,
            height=44,
            corner_radius=22,
            fg_color=COLORS["pill"],
            text_color=COLORS["bg"],
            font=FONTS["pill"]
        )
        self.result_pill.pack(pady=8)
        
        self.conf_pill = ctk.CTkLabel(
            pills_container,
            text="Confiança: —",
            width=160,
            height=36,
            corner_radius=18,
            fg_color=COLORS["success"],
            text_color="#ffffff",
            font=FONTS["body"]
        )
        self.conf_pill.pack(pady=4)

    def _on_back(self):
        if callable(self.on_back):
            self.on_back()

    def set_result(self, text: str, confidence: str):
        """Define o resultado da análise, traduzido e formatado com cores dinâmicas."""
        try:
            conf_value = float(confidence)
        except:
            conf_value = 0.0

        label = (text or "").strip().lower()

        # Define texto e cor do resultado
        if label in ["unknown", "não identificado", "nao identificado", ""]:
            display_text = "Não identificado"
            pill_color = "#4FC3F7"
        else:
            display_text = f"{text.capitalize()}"
            pill_color = "#4FC3F7"

        # Define cor da pílula de confiança conforme valor
        if conf_value >= 80:
            conf_color = COLORS["success"]
        elif conf_value >= 60:
            conf_color = COLORS["warning"] if "warning" in COLORS else "#e6b800"
        else:
            conf_color = COLORS["accent"]

        # Atualiza elementos visuais
        self.result_pill.configure(text=f"Resultado: {display_text}", fg_color=pill_color)
        self.conf_pill.configure(
            text=f"Confiança: {conf_value:.1f}%", fg_color=conf_color
        )


class HomeScreen(ctk.CTkFrame):
    """Tela principal otimizada para 800x480"""
    
    def __init__(self, master, on_capture: Callable, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16, *args, **kwargs)
        
        # Frame interno mais compacto
        self.inner = ctk.CTkFrame(
            self, 
            fg_color=COLORS["panel_light"], 
            corner_radius=12
        )
        self.inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.96)
        
        # Widget de bateria menor no canto
        self.battery = BatteryWidget(self.inner, percentage=82)
        self.battery.place(relx=0.96, rely=0.03, anchor="ne")

        # Estados
        self.video_state = VideoState(self.inner, on_capture=on_capture)
        self.loading_state = LoadingState(self.inner, on_back=lambda: self.show_state("video"))
        self.result_state = ResultState(self.inner, on_back=lambda: self.show_state("video"))

        # Posicionar estados
        for state in [self.video_state, self.loading_state, self.result_state]:
            state.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.98)

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

    def get_current_frame(self):
        """Retorna o frame atual para captura"""
        return self.video_state.get_current_frame()
