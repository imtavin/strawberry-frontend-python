import socket
import time
import threading
import struct
import cv2
import numpy as np

# =========================
#  UDP (fragmentado)
# =========================
class VideoStreamUDP:
    HEADER_FMT = "!IHH"  # frame_id:uint32, total:uint16, index:uint16
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    def __init__(self, udp_port: int, max_packet: int = 4096, timeout: float = 2.0, frame_callback=None):
        """
        udp_port: porta local para bind e receber os datagramas
        max_packet: tamanho de fragmento usado no backend (informativo)
        timeout: tempo para expirar frames incompletos
        frame_callback(frame_rgb): callback opcional (imagem já decodificada RGB)
        """
        self.listen_port = int(udp_port)
        self.max_packet = int(max_packet)
        self.timeout = float(timeout)

        self._cb_jpeg = None          # callback para JPEG bytes (via on_frame)
        self._cb_rgb = frame_callback # callback para imagem RGB (compatibilidade)

        self.sock = None
        self.buffers = {}
        self.buffers_lock = threading.Lock()

        self._stop = threading.Event()
        self._recv_th = None
        self._clean_th = None

    # ---------- API comum ----------
    def on_frame(self, cb):
        """Registra callback que recebe bytes JPEG."""
        self._cb_jpeg = cb

    def start(self):
        if self._recv_th and self._recv_th.is_alive():
            return
        # cria socket e binda
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.listen_port))
        self._stop.clear()
        self._recv_th = threading.Thread(target=self._receive_loop, daemon=True)
        self._recv_th.start()
        self._clean_th = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._clean_th.start()

    def stop(self):
        self._stop.set()
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        self.sock = None

    # ---------- Internals ----------
    def _receive_loop(self):
        while not self._stop.is_set():
            try:
                data, _ = self.sock.recvfrom(65535)
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
                        self._emit(frame_bytes)

            except OSError:
                # socket fechado durante stop()
                break
            except Exception as e:
                print(f"⚠️ Erro no receive_loop (UDP): {e}")

    def _cleanup_loop(self):
        while not self._stop.is_set():
            self._cleanup_expired()
            time.sleep(0.5)

    def _cleanup_expired(self):
        now = time.time()
        with self.buffers_lock:
            old = [fid for fid, buf in self.buffers.items() if now - buf["last_seen"] > self.timeout]
            for fid in old:
                # print(f"🧹 Limpando frame {fid} (timeout)")
                del self.buffers[fid]

    def _emit(self, jpeg_bytes: bytes):
        # 1) entrega JPEG para quem registrou via on_frame()
        if self._cb_jpeg:
            try:
                self._cb_jpeg(jpeg_bytes)
            except Exception as e:
                print(f"⚠️ Erro no callback JPEG (UDP): {e}")

        # 2) compat: se quiser imagem RGB já decodificada
        if self._cb_rgb:
            try:
                nparr = np.frombuffer(jpeg_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self._cb_rgb(frame_rgb)
            except Exception as e:
                print(f"⚠️ Erro ao decodificar frame (UDP): {e}")


# =========================
#  TCP (CameraServer JPEG)
# =========================
class VideoStreamTCP:
    """
    Protocolo: [4 bytes tamanho big-endian] [JPEG bytes]
    API compatível com UDP: on_frame(cb), start(), stop()
    """
    def __init__(self, host: str, port: int, reconnect_sec: float = 2.0, frame_callback=None):
        self.host = host
        self.port = int(port)
        self.reconnect_sec = float(reconnect_sec)

        self._cb_jpeg = None          # callback para JPEG bytes (via on_frame)
        self._cb_rgb = frame_callback # callback para imagem RGB (compat)

        self._stop = threading.Event()
        self._th = None
        self._sock = None

    # ---------- API comum ----------
    def on_frame(self, cb):
        """Registra callback que recebe bytes JPEG."""
        self._cb_jpeg = cb

    def start(self):
        if self._th and self._th.is_alive():
            return
        self._stop.clear()
        self._th = threading.Thread(target=self._loop, daemon=True)
        self._th.start()

    def stop(self):
        self._stop.set()
        try:
            if self._sock:
                self._sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            if self._sock:
                self._sock.close()
        except Exception:
            pass
        self._sock = None

    # ---------- Internals ----------
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
                print(f"⚠️ Erro no callback JPEG (TCP): {e}")

        # 2) RGB decodificado (compat)
        if self._cb_rgb:
            try:
                nparr = np.frombuffer(jpeg_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self._cb_rgb(frame_rgb)
            except Exception as e:
                print(f"⚠️ Erro ao decodificar frame (TCP): {e}")

    def _loop(self):
        while not self._stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.host, self.port))
                s.settimeout(None)
                self._sock = s

                while not self._stop.is_set():
                    header = self._recvn(4)
                    if header is None:
                        break
                    (nbytes,) = struct.unpack("!I", header)
                    jpg = self._recvn(nbytes)
                    if jpg is None:
                        break
                    self._emit(jpg)

            except OSError:
                # reconexão
                if not self._stop.is_set():
                    time.sleep(self.reconnect_sec)
            except Exception as e:
                print(f"⚠️ Erro no loop TCP: {e}")
                if not self._stop.is_set():
                    time.sleep(self.reconnect_sec)
            finally:
                try:
                    if self._sock:
                        self._sock.close()
                except Exception:
                    pass
                self._sock = None
                if not self._stop.is_set():
                    time.sleep(self.reconnect_sec)
