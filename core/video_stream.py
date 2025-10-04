import socket
import time
import threading
import struct
import cv2
import numpy as np
from utils.logger import video_logger

# =========================
#  UDP (fragmentado)
# =========================
class VideoStreamUDP:
    HEADER_FMT = "!IHH"  # frame_id:uint32, total:uint16, index:uint16
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    def __init__(self, udp_port: int, max_packet: int = 4096, timeout: float = 2.0, frame_callback=None):
        self.listen_port = int(udp_port)
        self.max_packet = int(max_packet)
        self.timeout = float(timeout)

        self._cb_jpeg = None
        self._cb_rgb = frame_callback

        self.sock = None
        self.buffers = {}
        self.buffers_lock = threading.Lock()

        self._stop = threading.Event()
        self._recv_th = None
        self._clean_th = None
        
        video_logger.debug(f"VideoStreamUDP inicializado: porta={udp_port}, max_packet={max_packet}")

    def on_frame(self, cb):
        """Registra callback que recebe bytes JPEG."""
        self._cb_jpeg = cb
        video_logger.debug("Callback de frame registrado para UDP")

    def start(self):
        if self._recv_th and self._recv_th.is_alive():
            video_logger.warning("VideoStreamUDP já está rodando")
            return
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(("0.0.0.0", self.listen_port))
            self._stop.clear()
            self._recv_th = threading.Thread(target=self._receive_loop, daemon=True, name="UDP-Receiver")
            self._recv_th.start()
            self._clean_th = threading.Thread(target=self._cleanup_loop, daemon=True, name="UDP-Cleanup")
            self._clean_th.start()
            video_logger.info(f"VideoStreamUDP iniciado na porta {self.listen_port}")
        except Exception as e:
            video_logger.error(f"Erro ao iniciar VideoStreamUDP: {e}")
            raise

    def stop(self):
        video_logger.info("Parando VideoStreamUDP...")
        self._stop.set()
        try:
            if self.sock:
                self.sock.close()
                video_logger.debug("Socket UDP fechado")
        except Exception as e:
            video_logger.debug(f"Erro ao fechar socket UDP: {e}")
        self.sock = None

    def _receive_loop(self):
        video_logger.debug("Loop de recepção UDP iniciado")
        frames_received = 0
        
        while not self._stop.is_set():
            try:
                data, addr = self.sock.recvfrom(65535)
                if len(data) <= self.HEADER_SIZE:
                    continue
                    
                frame_id, total, index = struct.unpack(self.HEADER_FMT, data[:self.HEADER_SIZE])
                chunk = data[self.HEADER_SIZE:]

                with self.buffers_lock:
                    buf = self.buffers.get(frame_id)
                    if buf is None:
                        if total == 0 or total > 65535:
                            continue
                        buf = {"total": total, "parts": [None]*total, "received": 0, "last_seen": time.time()}
                        self.buffers[frame_id] = buf

                    if 0 <= index < buf["total"] and buf["parts"][index] is None:
                        buf["parts"][index] = chunk
                        buf["received"] += 1
                        buf["last_seen"] = time.time()

                    if buf["received"] == buf["total"]:
                        frame_bytes = b"".join(buf["parts"])
                        del self.buffers[frame_id]
                        frames_received += 1
                        
                        if frames_received % 100 == 0:
                            video_logger.debug(f"Frames UDP recebidos: {frames_received}")
                            
                        self._emit(frame_bytes)

            except OSError:
                break
            except Exception as e:
                video_logger.error(f"Erro no receive_loop (UDP): {e}")

        video_logger.info(f"Loop de recepção UDP finalizado - total de frames: {frames_received}")

    def _cleanup_loop(self):
        video_logger.debug("Loop de cleanup UDP iniciado")
        while not self._stop.is_set():
            self._cleanup_expired()
            time.sleep(0.5)
        video_logger.debug("Loop de cleanup UDP finalizado")

    def _cleanup_expired(self):
        now = time.time()
        with self.buffers_lock:
            expired = [fid for fid, buf in self.buffers.items() if now - buf["last_seen"] > self.timeout]
            if expired:
                video_logger.debug(f"Limpando {len(expired)} frames UDP expirados")
                for fid in expired:
                    del self.buffers[fid]

    def _emit(self, jpeg_bytes: bytes):
        # 1) entrega JPEG para quem registrou via on_frame()
        if self._cb_jpeg:
            try:
                self._cb_jpeg(jpeg_bytes)
            except Exception as e:
                video_logger.error(f"Erro no callback JPEG (UDP): {e}")

        # 2) compat: se quiser imagem RGB já decodificada
        if self._cb_rgb:
            try:
                nparr = np.frombuffer(jpeg_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self._cb_rgb(frame_rgb)
            except Exception as e:
                video_logger.error(f"Erro ao decodificar frame (UDP): {e}")


# =========================
#  TCP (CameraServer JPEG)
# =========================
class VideoStreamTCP:
    def __init__(self, host: str, port: int, reconnect_sec: float = 2.0, frame_callback=None):
        self.host = host
        self.port = int(port)
        self.reconnect_sec = float(reconnect_sec)

        self._cb_jpeg = None
        self._cb_rgb = frame_callback

        self._stop = threading.Event()
        self._th = None
        self._sock = None
        
        video_logger.debug(f"VideoStreamTCP inicializado: {host}:{port}")

    def on_frame(self, cb):
        """Registra callback que recebe bytes JPEG."""
        self._cb_jpeg = cb
        video_logger.debug("Callback de frame registrado para TCP")

    def start(self):
        if self._th and self._th.is_alive():
            video_logger.warning("VideoStreamTCP já está rodando")
            return
            
        self._stop.clear()
        self._th = threading.Thread(target=self._loop, daemon=True, name="TCP-Stream")
        self._th.start()
        video_logger.info(f"VideoStreamTCP iniciado para {self.host}:{self.port}")

    def stop(self):
        video_logger.info("Parando VideoStreamTCP...")
        self._stop.set()
        try:
            if self._sock:
                self._sock.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            video_logger.debug(f"Erro no shutdown do socket TCP: {e}")
        try:
            if self._sock:
                self._sock.close()
        except Exception as e:
            video_logger.debug(f"Erro ao fechar socket TCP: {e}")
        self._sock = None

    def _recvn(self, n):
        data = bytearray()
        while len(data) < n and not self._stop.is_set():
            chunk = self._sock.recv(n - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        return bytes(data)

    def _emit(self, jpeg_bytes: bytes):
        # 1) JPEG cru
        if self._cb_jpeg:
            try:
                self._cb_jpeg(jpeg_bytes)
            except Exception as e:
                video_logger.error(f"Erro no callback JPEG (TCP): {e}")

        # 2) RGB decodificado (compat)
        if self._cb_rgb:
            try:
                nparr = np.frombuffer(jpeg_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self._cb_rgb(frame_rgb)
            except Exception as e:
                video_logger.error(f"Erro ao decodificar frame (TCP): {e}")

    def _loop(self):
        video_logger.debug("Loop principal TCP iniciado")
        frames_received = 0
        connection_attempts = 0
        
        while not self._stop.is_set():
            try:
                connection_attempts += 1
                video_logger.info(f"Tentativa de conexão TCP #{connection_attempts} com {self.host}:{self.port}")
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.host, self.port))
                s.settimeout(None)
                self._sock = s
                
                video_logger.info(f"✅ Conectado ao servidor de vídeo TCP")
                connection_attempts = 0  # reset counter on success

                while not self._stop.is_set():
                    header = self._recvn(4)
                    if header is None:
                        video_logger.warning("Conexão TCP fechada pelo servidor")
                        break
                    (nbytes,) = struct.unpack("!I", header)
                    jpg = self._recvn(nbytes)
                    if jpg is None:
                        video_logger.warning("Stream TCP interrompido")
                        break
                    
                    frames_received += 1
                    if frames_received % 100 == 0:
                        video_logger.debug(f"Frames TCP recebidos: {frames_received}")
                        
                    self._emit(jpg)

            except socket.timeout:
                video_logger.warning(f"Timeout na conexão TCP com {self.host}:{self.port}")
            except OSError as e:
                if not self._stop.is_set():
                    video_logger.warning(f"Erro de conexão TCP: {e}. Reconectando em {self.reconnect_sec}s...")
                    time.sleep(self.reconnect_sec)
            except Exception as e:
                video_logger.error(f"Erro inesperado no loop TCP: {e}")
                if not self._stop.is_set():
                    time.sleep(self.reconnect_sec)
            finally:
                try:
                    if self._sock:
                        self._sock.close()
                except Exception as e:
                    video_logger.debug(f"Erro ao fechar socket: {e}")
                self._sock = None
                
                if not self._stop.is_set():
                    video_logger.info(f"Tentando reconexão TCP em {self.reconnect_sec}s...")
                    time.sleep(self.reconnect_sec)

        video_logger.info(f"Loop TCP finalizado - total de frames recebidos: {frames_received}")