import customtkinter as ctk
from PIL import Image, ImageTk

class VideoPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#2b2b2b")
        self.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(expand=True)

    def update_frame(self, frame_rgb):
        im_pil = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=im_pil)
        self.video_label.configure(image=imgtk)
        self.video_label.image = imgtk
