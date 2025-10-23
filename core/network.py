from enum import Enum
import json
import socket
import time
from utils.logger import network_logger
from typing import Any, Dict, Optional, Callable

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class TCPClient:
    def __init__(self, host, port, reconnect_delay=2):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self.reconnect_delay = reconnect_delay
        self._connected = False
        self._message_handlers: list[Callable] = []
        network_logger.debug(f"TCPClient inicializado: {host}:{port}")

    def add_message_handler(self, handler: Callable):
        """Adiciona handler para mensagens recebidas"""
        self._message_handlers.append(handler)

    def connect(self):
        """Conecta ao servidor TCP"""
        network_logger.info(f"Conectando ao backend em {self.host}:{self.port}...")
        while not self._connected:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)  # Timeout para conexão
                sock.connect((self.host, self.port))
                
                # Configurações de socket
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
                self.sock = sock
                self._connected = True
                
                network_logger.info(f"✅ TCP conectado em {self.host}:{self.port}")
                return
                
            except socket.timeout:
                network_logger.warning(f"Timeout conectando em {self.host}:{self.port}")
            except ConnectionRefusedError:
                network_logger.warning(f"Conexão recusada em {self.host}:{self.port}")
            except Exception as e:
                network_logger.warning(f"⚠️ Erro TCP: {e}")
            
            network_logger.info(f"Tentando novamente em {self.reconnect_delay}s...")
            time.sleep(self.reconnect_delay)

    def send(self, data: bytes):
        """Envia dados via TCP"""
        if not self._connected or not self.sock:
            network_logger.debug("Socket TCP não conectado, tentando reconectar...")
            self._connected = False
            self.connect()
            
        try:
            self.sock.sendall(data)
            network_logger.debug(f"Dados enviados via TCP: {len(data)} bytes")
        except BrokenPipeError:
            network_logger.error("❌ Conexão quebrada, reconectando...")
            self._connected = False
            self.connect()
            self.sock.sendall(data)  # Tenta enviar novamente após reconectar
        except Exception as e:
            network_logger.error(f"❌ Falha ao enviar via TCP: {e}")
            self._connected = False

    def send_command(self, command: str, data: Dict[str, Any] = None) -> bool:
        """Envia comando para o backend"""
        if self.state != ConnectionState.CONNECTED or not self.tcp_socket:
            network_logger.warning("Tentativa de envio sem conexão")
            return False
            
        try:
            message = {
                "type": "command",
                "command": command,
                "timestamp": time.time()
            }
            
            if data:
                message["data"] = data
                
            message_str = json.dumps(message) + "\n"
            self.tcp_socket.sendall(message_str.encode('utf-8'))
            network_logger.debug(f"Comando enviado: {command}")
            return True
            
        except Exception as e:
            network_logger.error(f"Erro enviando comando: {e}")
            self.state = ConnectionState.ERROR
            return False

    def receive_loop(self, callback: Callable):
        """
        Loop de recebimento de mensagens (deve rodar em thread separada)
        """
        buffer = b""
        
        while self._connected and self.sock:
            try:
                # Configura timeout para não bloquear indefinidamente
                self.sock.settimeout(1.0)
                
                data = self.sock.recv(4096)
                if not data:
                    network_logger.warning("Conexão fechada pelo servidor")
                    self._connected = False
                    break
                    
                buffer += data
                
                # Processa mensagens completas (separadas por \n)
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line.strip():
                        try:
                            message = line.decode('utf-8').strip()
                            callback(message)
                        except UnicodeDecodeError:
                            network_logger.warning("Mensagem com encoding inválido recebida")
                        except Exception as e:
                            network_logger.error(f"Erro processando mensagem: {e}")
                            
            except socket.timeout:
                continue  # Timeout é normal, continua o loop
            except Exception as e:
                network_logger.error(f"Erro no loop de recebimento: {e}")
                self._connected = False
                break
        
        # Tenta reconectar se desconectado
        if not self._connected:
            network_logger.info("Tentando reconexão...")
            time.sleep(self.reconnect_delay)
            self.connect()

    def close(self):
        """Fecha a conexão"""
        self._connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            finally:
                self.sock = None
        network_logger.info("Conexão TCP fechada")
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