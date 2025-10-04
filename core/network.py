import socket
import time
from utils.logger import network_logger

class TCPClient:
    def __init__(self, host, port, reconnect_delay=2):
        self.host = host
        self.port = port
        self.sock = None
        self.reconnect_delay = reconnect_delay
        network_logger.debug(f"TCPClient inicializado: {host}:{port}")

    def connect(self):
        network_logger.info(f"Conectando ao backend em {self.host}:{self.port}...")
        while self.sock is None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.host, self.port))
                self.sock = sock
                network_logger.info(f"✅ TCP conectado em {self.host}:{self.port}")
                return
            except Exception as e:
                network_logger.warning(f"⚠️ Erro TCP: {e}. Tentando em {self.reconnect_delay}s...")
                time.sleep(self.reconnect_delay)

    def send(self, data: bytes):
        if not self.sock:
            network_logger.debug("Socket TCP não conectado, tentando reconectar...")
            self.connect()
        try:
            self.sock.sendall(data)
            network_logger.debug(f"Dados enviados via TCP: {len(data)} bytes")
        except Exception as e:
            network_logger.error(f"❌ Falha ao enviar via TCP: {e}")
            self.sock = None  # força reconexão


class UDPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        network_logger.debug(f"UDPClient inicializado: {host}:{port}")

    def bind(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        self.sock = sock
        network_logger.info(f"🖧 UDP conectado em {self.host}:{self.port}")
        return self.sock