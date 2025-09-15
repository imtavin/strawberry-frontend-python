import os
from PIL import Image
import customtkinter as ctk

def load_icon(path, size=(30, 30)):
    if not os.path.exists(path):
        return None
    img = Image.open(path)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)
