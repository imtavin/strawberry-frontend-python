import threading
import time

class CommandHandler:
    def __init__(self, tcp_client, udp_port):
        self.tcp_client = tcp_client
        self.udp_port = udp_port
        self.registered = False

    def register_udp(self):
        """
        Envia para o backend a porta UDP onde este frontend está ouvindo.
        Deve ser chamado logo após a conexão TCP.
        """
        try:
            msg = f"REGISTER_UDP:{self.udp_port}".encode()
            self.tcp_client.send(msg)
            self.registered = True
            print(f"📨 Enviado REGISTER_UDP:{self.udp_port}")
        except Exception as e:
            print(f"⚠️ Falha ao enviar REGISTER_UDP: {e}")

    def send_capture(self):
        """
        Envia comando de captura para o backend.
        """
        try:
            self.tcp_client.send(b"CAPTURE")
            print("📸 Comando CAPTURE enviado")
        except Exception as e:
            print(f"❌ Erro TCP ao enviar CAPTURE: {e}")
