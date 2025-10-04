import threading
import time
from utils.logger import command_logger

class CommandHandler:
    def __init__(self, tcp_client, udp_port):
        self.tcp_client = tcp_client
        self.udp_port = udp_port
        self.registered = False
        command_logger.debug(f"CommandHandler inicializado (UDP port: {udp_port})")

    def register_udp(self):
        """
        Envia para o backend a porta UDP onde este frontend está ouvindo.
        Deve ser chamado logo após a conexão TCP.
        """
        try:
            msg = f"REGISTER_UDP:{self.udp_port}".encode()
            self.tcp_client.send(msg)
            self.registered = True
            command_logger.info(f"Registro UDP enviado: porta {self.udp_port}")
        except Exception as e:
            command_logger.error(f"Falha ao enviar REGISTER_UDP: {e}")

    def send_capture(self):
        """
        Envia comando de captura para o backend.
        """
        try:
            self.tcp_client.send(b"CAPTURE")
            command_logger.info("Comando CAPTURE enviado para backend")
        except Exception as e:
            command_logger.error(f"Erro TCP ao enviar CAPTURE: {e}")