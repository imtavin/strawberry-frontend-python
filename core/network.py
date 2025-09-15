import socket
import time

class TCPClient:
    def __init__(self, host, port, reconnect_delay=2):
        self.host = host
        self.port = port
        self.sock = None
        self.reconnect_delay = reconnect_delay

    def connect(self):
        while self.sock is None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.host, self.port))
                self.sock = sock
                print(f"✅ TCP conectado em {self.host}:{self.port}")
                return
            except Exception as e:
                print(f"⚠️ Erro TCP: {e}. Tentando em {self.reconnect_delay}s...")
                time.sleep(self.reconnect_delay)

    def send(self, data: bytes):
        if not self.sock:
            self.connect()
        try:
            self.sock.sendall(data)
        except Exception as e:
            print(f"❌ Falha ao enviar via TCP: {e}")
            self.sock = None  # força reconexão


class UDPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def bind(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        self.sock = sock
        print(f"🖧 UDP conectado em {self.host}:{self.port}")
        return self.sock
