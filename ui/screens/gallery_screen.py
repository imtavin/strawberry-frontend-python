# ui/screens/gallery_screen.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS
from PIL import Image, ImageTk
import os

class GalleryScreen(ctk.CTkFrame):
    """Simple gallery screen that shows a grid of captured images from ./captures/ (if present)."""

    def __init__(self, master, captures_dir="captures", *args, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], *args, **kwargs)
        self.captures_dir = captures_dir
        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=12)
        self.container.place(relx=0.012, rely=0.012, relwidth=0.976, relheight=0.976)
        self.title = ctk.CTkLabel(self.container, text="Galeria", font=FONTS["title"], text_color=COLORS["pill"])
        self.title.pack(anchor="nw", padx=16, pady=12)
        self.grid_frame = ctk.CTkFrame(self.container, fg_color=COLORS["bg"])
        self.grid_frame.pack(expand=True, fill="both", padx=16, pady=12)
        self._build_grid()

    def _build_grid(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        # find files
        if not os.path.exists(self.captures_dir):
            os.makedirs(self.captures_dir, exist_ok=True)
        imgs = [os.path.join(self.captures_dir, f) for f in os.listdir(self.captures_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not imgs:
            lbl = ctk.CTkLabel(self.grid_frame, text="Nenhuma captura encontrada.", text_color=COLORS["muted"])
            lbl.pack(pady=20)
            return

        # simple grid layout: 3 columns
        cols = 3
        thumb_w = 240
        r = 0
        c = 0
        for p in imgs:
            try:
                im = Image.open(p)
                im.thumbnail((thumb_w, thumb_w))
                imgtk = ImageTk.PhotoImage(im)
                lbl = ctk.CTkLabel(self.grid_frame, image=imgtk, text="")
                lbl.image = imgtk
                lbl.grid(row=r, column=c, padx=8, pady=8)
                c += 1
                if c >= cols:
                    c = 0
                    r += 1
            except Exception as e:
                print("Erro carregando imagem da galeria:", e)
