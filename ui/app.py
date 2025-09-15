import customtkinter as ctk
import threading
from core.network import TCPClient, UDPClient
from core.video_stream import VideoStreamHandler
from core.commands import CommandHandler
from ui.sidebar import Sidebar
from ui.video_panel import VideoPanel
from utils.cleanup import CleanupWorker

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class FrontendApp(ctk.CTk):
    def __init__(self, config):
        super().__init__()
        self.title("Detector de Pragas em Morango - TCC")
        self.attributes("-fullscreen", True)

        self.config = config
        self.running = True

        # Network
        self.tcp_client = TCPClient(config["server"]["host"], config["server"]["port"])
        udp_client = UDPClient(config["udp"]["host"], config["udp"]["port"])
        self.udp_sock = udp_client.bind()
        self.video_stream = VideoStreamHandler(self.udp_sock, self._update_video)

        self.cleanup_worker = CleanupWorker(self.video_stream.cleanup, interval=0.5)
        self.cleanup_worker.start()

        # Commands (usa TCP + udp_port)
        self.commands = CommandHandler(self.tcp_client, config["udp"]["port"])

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.sidebar = Sidebar(self, on_exit=self.exit_app, on_capture=self.send_capture)
        self.video_panel = VideoPanel(self)

        # Threads
        threading.Thread(target=self._tcp_connect_and_register, daemon=True).start()
        threading.Thread(target=self.video_stream.receive_loop, args=(lambda: self.running,), daemon=True).start()

    def _tcp_connect_and_register(self):
        self.tcp_client.connect()
        self.commands.register_udp()

    def _update_video(self, frame_rgb):
        self.after(0, lambda: self.video_panel.update_frame(frame_rgb))

    def send_capture(self):
        self.commands.send_capture()

    def exit_app(self):
        try:
            self.cleanup_worker.stop(join=True, timeout=1.0)
        except Exception:
            pass
        self.running = False
        self.destroy()
