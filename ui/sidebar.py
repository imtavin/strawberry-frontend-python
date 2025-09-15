import customtkinter as ctk
from ui.icons import load_icon

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_exit, on_capture):
        super().__init__(master, width=220, corner_radius=0, fg_color="#162312")
        self.grid(row=0, column=0, sticky="nswe")

        self.sidebar_label = ctk.CTkLabel(self, text="Menu", font=("Arial", 22, "bold"), text_color="white")
        self.sidebar_label.pack(pady=30)

        self.btn_mapa = ctk.CTkButton(self, text="Mapa", image=load_icon("icons/maps.png"), state="disabled")
        self.btn_mapa.pack(pady=10, fill="x", padx=20)

        self.btn_galeria = ctk.CTkButton(self, text="Galeria", image=load_icon("icons/gallery.png"), state="disabled")
        self.btn_galeria.pack(pady=10, fill="x", padx=20)

        self.btn_config = ctk.CTkButton(self, text="Configurações", image=load_icon("icons/setting.png"), state="disabled")
        self.btn_config.pack(pady=10, fill="x", padx=20)

        self.btn_bateria = ctk.CTkButton(self, text="Bateria 75%", image=load_icon("icons/battery.png"), state="disabled")
        self.btn_bateria.pack(pady=10, fill="x", padx=20)

        self.btn_exit = ctk.CTkButton(self, text="❌ Sair", command=on_exit, fg_color="#d62828")
        self.btn_exit.pack(side="bottom", pady=30, padx=20, fill="x")

        self.btn_foto = ctk.CTkButton(self, text="Capturar", image=load_icon("icons/camera.png"), command=on_capture, fg_color="#d62828")
        self.btn_foto.pack(side="bottom", pady=30, padx=20, fill="x")
