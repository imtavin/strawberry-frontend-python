# ui/screens/gallery_screen.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS, ICONS
import os
from PIL import Image, ImageTk

class GalleryScreen(ctk.CTkFrame):
    def __init__(self, master, captures_dir: str, *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16, *args, **kwargs)
        self.captures_dir = captures_dir
        
        # Botão voltar
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
        
        self._build_ui()

    def _on_back(self):
        # Voltar para home (será conectado no app principal)
        pass

    def _build_ui(self):
        # Container principal
        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=12)
        self.container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.9)
        
        # Título
        title = ctk.CTkLabel(
            self.container,
            text="Galeria de Capturas",
            text_color=COLORS["text"],
            font=FONTS["title"]
        )
        title.pack(pady=10)
        
        # Frame para as imagens
        self.images_frame = ctk.CTkScrollableFrame(
            self.container, 
            fg_color=COLORS["bg"]
        )
        self.images_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._build_grid()

    def _build_grid(self):
        """Constrói a grade de imagens"""
        # Limpar frame existente
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        
        # Verificar se o diretório existe
        if not os.path.exists(self.captures_dir):
            label = ctk.CTkLabel(
                self.images_frame,
                text="Nenhuma captura encontrada",
                text_color=COLORS["muted"],
                font=FONTS["body"]
            )
            label.pack(pady=50)
            return
        
        # Listar arquivos de imagem
        image_files = [f for f in os.listdir(self.captures_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:
            label = ctk.CTkLabel(
                self.images_frame,
                text="Nenhuma imagem na galeria",
                text_color=COLORS["muted"],
                font=FONTS["body"]
            )
            label.pack(pady=50)
            return
        
        # Criar grid de imagens (2 colunas)
        row_frame = None
        for i, image_file in enumerate(image_files):
            if i % 2 == 0:
                row_frame = ctk.CTkFrame(self.images_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)
            
            self._create_image_preview(row_frame, image_file)

    def _create_image_preview(self, parent, image_file):
        """Cria preview de uma imagem"""
        try:
            filepath = os.path.join(self.captures_dir, image_file)
            
            # Carregar e redimensionar imagem
            image = Image.open(filepath)
            image.thumbnail((150, 150))  # Thumbnail pequeno para preview
            photo = ImageTk.PhotoImage(image)
            
            # Frame da imagem
            image_frame = ctk.CTkFrame(parent, fg_color=COLORS["pill_dark"], corner_radius=8, width=160, height=180)
            image_frame.pack(side="left", padx=5, pady=5)
            image_frame.pack_propagate(False)
            
            # Label da imagem
            image_label = ctk.CTkLabel(image_frame, image=photo, text="")
            image_label.image = photo  # Manter referência
            image_label.pack(padx=5, pady=5)
            
            # Nome do arquivo
            name_label = ctk.CTkLabel(
                image_frame, 
                text=image_file[:20] + "..." if len(image_file) > 20 else image_file,
                text_color=COLORS["text_secondary"],
                font=FONTS["small"],
                wraplength=150
            )
            name_label.pack(pady=(0, 5))
            
        except Exception as e:
            print(f"Erro carregando imagem {image_file}: {e}")