# frontend/main.py
import socket
import threading
import time
import json
import struct
import cv2
import numpy as np
from PIL import Image, ImageTk
import customtkinter as ctk
import os

# -------------------------
# Configuração
# -------------------------
with open("config.json") as f:
    CONFIG = json.load(f)

TCP_HOST = CONFIG["server"]["host"]
TCP_PORT = CONFIG["server"]["port"]
UDP_HOST = CONFIG.get("udp", {}).get("host", TCP_HOST)
UDP_PORT = CONFIG.get("udp", {}).get("port", 5005)
# Tamanho máximo de payload UDP que o backend usará para fragmentar.
# O recv pode receber até 65535, mas o backend fragmenta conforme max_packet_size.
MAX_UDP_PACKET = CONFIG.get("udp", {}).get("max_packet_size", 4096)

RECONNECT_INITIAL_BACKOFF = 0.5
RECONNECT_MAX_BACKOFF = 5.0

# Tempo máximo (s) que vamos manter fragments incompletos antes de descartá-los
FRAME_FRAGMENT_TIMEOUT = 2.0

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


# -------------------------
# Função utilitária ícones
# -------------------------
def load_icon(path, size=(30, 30)):
    if not os.path.exists(path):
        return None
    img = Image.open(path)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)


# -------------------------
# Frontend principal
# -------------------------
class FrontendApp(ctk.CTk):
    HEADER_FMT = "!IHH"  # frame_id:uint32, total:uint16, index:uint16
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    def __init__(self):
        super().__init__()
        self.title("Detector de Pragas em Morango - TCC")
        self.attributes("-fullscreen", True)

        # Threads e sockets
        self.tcp_client = None
        self.udp_client = None
        self.running = True

        # Estrutura para reconstrução de frames UDP:
        # { frame_id: {"total": int, "parts": [None]*total, "received": int, "last_seen": timestamp} }
        self.frame_buffers = {}
        self.buffers_lock = threading.Lock()

        # Layout
        self._build_ui()

        # Conecta TCP e UDP
        # roda em threads para não bloquear a UI
        threading.Thread(target=self.connect_tcp, daemon=True).start()
        threading.Thread(target=self.connect_udp, daemon=True).start()

        # Thread de recepção UDP
        threading.Thread(target=self.udp_receive_loop, daemon=True).start()

        # Thread de limpeza de buffers antigos
        threading.Thread(target=self._cleanup_worker, daemon=True).start()

    # -------------------------
    # UI
    # -------------------------
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#162312")
        self.sidebar.grid(row=0, column=0, sticky="nswe")

        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="Menu", font=("Arial", 22, "bold"), text_color="white")
        self.sidebar_label.pack(pady=30)

        # Mapa
        self.btn_mapa = ctk.CTkButton(self.sidebar, text="  Mapa", image=load_icon("icons/maps.png"),
                                      state="disabled", anchor="w", fg_color="#d62828", hover_color="#b81f1f")
        self.btn_mapa.pack(pady=10, fill="x", padx=20)

        # Galeria
        self.btn_galeria = ctk.CTkButton(self.sidebar, text="  Galeria", image=load_icon("icons/gallery.png"),
                                         state="disabled", anchor="w", fg_color="#d62828", hover_color="#b81f1f")
        self.btn_galeria.pack(pady=10, fill="x", padx=20)

        # Configuracao
        self.btn_config = ctk.CTkButton(self.sidebar, text="  Configurações", image=load_icon("icons/setting.png"),
                                        state="disabled", anchor="w", fg_color="#d62828", hover_color="#b81f1f")
        self.btn_config.pack(pady=10, fill="x", padx=20)

        # Bateria
        self.btn_bateria = ctk.CTkButton(self.sidebar, text="  Bateria 75%", image=load_icon("icons/battery.png"),
                                         state="disabled", anchor="w", fg_color="#d62828", hover_color="#b81f1f")
        self.btn_bateria.pack(pady=10, fill="x", padx=20)

        # Botão sair
        self.btn_exit = ctk.CTkButton(self.sidebar, text="❌ Sair", command=self.exit_app, fg_color="#d62828",
                                      hover_color="#b81f1f")
        self.btn_exit.pack(side="bottom", pady=30, padx=20, fill="x")

        # Frame vídeo
        self.video_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.video_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(expand=True)

        # Botão captura
        self.btn_foto = ctk.CTkButton(
            self.video_frame,
            text="Capturar",
            command=self.send_capture,
            width=220,
            height=60,
            fg_color="#d62828",
            hover_color="#b81f1f",
            font=("Arial", 18, "bold")
        )
        self.btn_foto.place(relx=0.5, rely=0.92, anchor="center")

    # -------------------------
    # Conexões TCP e UDP
    # -------------------------
    def connect_tcp(self):
        backoff = RECONNECT_INITIAL_BACKOFF
        while self.running and self.tcp_client is None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((TCP_HOST, TCP_PORT))
                sock.settimeout(None)
                self.tcp_client = sock
                print(f"✅ TCP conectado: {TCP_HOST}:{TCP_PORT}")

                # envia registro UDP para o backend (porta que o frontend está usando)
                # se o bind UDP ainda não estiver pronto, aguarda um instante
                time.sleep(0.1)
                try:
                    udp_port = UDP_PORT
                    self.tcp_client.sendall(f"REGISTER_UDP:{udp_port}".encode())
                    print(f"📨 Enviado REGISTER_UDP:{udp_port}")
                except Exception as e:
                    print(f"⚠️ Falha ao enviar REGISTER_UDP: {e}")

                return
            except Exception as e:
                print(f"⚠️ TCP falhou: {e}. Tentando em {backoff:.1f}s...")
                time.sleep(backoff)
                backoff = min(RECONNECT_MAX_BACKOFF, backoff * 1.7)

    def connect_udp(self):
        # Cria socket UDP que vai receber pacotes (frontend atua como "server" UDP)
        while self.running and self.udp_client is None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # bind em todas interfaces (0.0.0.0) ou em UDP_HOST específico
                sock.bind((UDP_HOST, UDP_PORT))
                self.udp_client = sock
                print(f"🖧 UDP conectado em {UDP_HOST}:{UDP_PORT}")
                return
            except Exception as e:
                print(f"❌ Falha UDP bind: {e}. Tentando de novo em 0.5s...")
                time.sleep(0.5)

    # -------------------------
    # Loop de recepção UDP
    # -------------------------
    def udp_receive_loop(self):
        # Recebe pacotes e monta frames conforme cabeçalho
        # recv buffer máximo: 65535 bytes (tamanho máximo UDP)
        while self.running:
            if self.udp_client is None:
                time.sleep(0.05)
                continue
            try:
                data, addr = self.udp_client.recvfrom(65535)
                if len(data) <= self.HEADER_SIZE:
                    print("⚠️ Pacote UDP menor que o cabeçalho — ignorando")
                    continue

                # Parse header
                try:
                    header = data[:self.HEADER_SIZE]
                    frame_id, total, index = struct.unpack(self.HEADER_FMT, header)
                    chunk = data[self.HEADER_SIZE:]
                except Exception as e:
                    print(f"⚠️ Erro ao desempacotar cabeçalho UDP: {e}")
                    continue

                # Guarda parte no buffer correspondente ao frame_id
                with self.buffers_lock:
                    buf = self.frame_buffers.get(frame_id)
                    if buf is None:
                        # inicializa buffer
                        if total == 0 or total > 65535:
                            print(f"⚠️ total inválido no header: {total} — ignorando frame {frame_id}")
                            continue
                        parts = [None] * total
                        buf = {"total": total, "parts": parts, "received": 0, "last_seen": time.time()}
                        self.frame_buffers[frame_id] = buf

                    # proteção contra index fora do intervalo
                    if index < 0 or index >= buf["total"]:
                        print(f"⚠️ Índice fora do intervalo: frame={frame_id} index={index} total={buf['total']}")
                        continue

                    if buf["parts"][index] is None:
                        buf["parts"][index] = chunk
                        buf["received"] += 1
                        buf["last_seen"] = time.time()

                    # Se completou o frame, reconstrói e exibe
                    if buf["received"] == buf["total"]:
                        try:
                            frame_bytes = b"".join(buf["parts"])
                            # remove do dicionário antes de processar (para liberar lock rapidamente)
                            del self.frame_buffers[frame_id]
                        except Exception as e:
                            print(f"⚠️ Erro ao juntar partes do frame {frame_id}: {e}")
                            continue

                        # Decodifica JPEG e atualiza UI
                        self._handle_complete_frame(frame_id, frame_bytes)

            except Exception as e:
                # não exibir spam quando fechando/timeout — log genérico
                if self.running:
                    print(f"⚠️ Erro no loop UDP: {e}")
                time.sleep(0.01)

    def _handle_complete_frame(self, frame_id, frame_bytes):
        try:
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                print(f"⚠️ Falha ao decodificar frame {frame_id} (cv2.imdecode retornou None)")
                return
            # Converte BGR -> RGB para exibir com PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Atualiza UI no thread principal via after()
            self.after(0, lambda: self.update_video_from_array(frame_rgb))
        except Exception as e:
            print(f"⚠️ Erro ao processar frame {frame_id}: {e}")

    # -------------------------
    # Atualiza frame na UI (executado no main thread)
    # -------------------------
    def update_video_from_array(self, frame_rgb_array):
        try:
            im_pil = Image.fromarray(frame_rgb_array)
            imgtk = ImageTk.PhotoImage(image=im_pil)
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk
        except Exception as e:
            print(f"⚠️ Erro ao atualizar UI com frame: {e}")

    # -------------------------
    # Worker que remove buffers velhos para não consumir memória
    # -------------------------
    def _cleanup_worker(self):
        while self.running:
            now = time.time()
            with self.buffers_lock:
                to_delete = []
                for fid, buf in list(self.frame_buffers.items()):
                    if now - buf["last_seen"] > FRAME_FRAGMENT_TIMEOUT:
                        to_delete.append(fid)
                for fid in to_delete:
                    print(f"🧹 Limpando fragmento incompleto frame {fid} (timeout)")
                    del self.frame_buffers[fid]
            time.sleep(0.5)

    # -------------------------
    # Comandos TCP
    # -------------------------
    def send_capture(self):
        if self.tcp_client is None:
            # tenta reconectar rápido
            threading.Thread(target=self.connect_tcp, daemon=True).start()
        try:
            if self.tcp_client:
                self.tcp_client.sendall(b"CAPTURE")
                print("📸 Comando CAPTURE enviado")
            else:
                print("⚠️ TCP não está conectado — impossível enviar CAPTURE")
        except Exception as e:
            print(f"❌ Erro TCP ao enviar comando: {e}")
            try:
                self.tcp_client.close()
            except Exception:
                pass
            self.tcp_client = None

    # -------------------------
    # Fechar app
    # -------------------------
    def exit_app(self):
        self.running = False
        try:
            if self.tcp_client:
                self.tcp_client.close()
        except Exception:
            pass
        try:
            if self.udp_client:
                self.udp_client.close()
        except Exception:
            pass
        # dá um tempo para threads encerrarem
        time.sleep(0.05)
        self.destroy()


if __name__ == "__main__":
    app = FrontendApp()
    app.mainloop()
