"""
Sistema de comandos robusto com callbacks e timeouts 
"""
import time
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor  
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from utils.logger import command_logger

@dataclass
class Command:
    id: str
    name: str
    data: Dict[str, Any]
    timestamp: float
    callback: Optional[Callable]
    timeout: float = 30.0

class CommandHandler:
    """Manipulador de comandos com sistema de callbacks"""
    
    def __init__(self, tcp_client, udp_port=None):
        self.tcp_client = tcp_client
        self.udp_port = udp_port
        self.pending_commands: Dict[str, Command] = {}
        self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="CmdHandler") 
        command_logger.debug(f"CommandHandler inicializado (UDP port: {udp_port})")

    def _generate_command_id(self) -> str:
        """Gera ID único para comando"""
        return f"cmd_{uuid.uuid4().hex}"

    def register_udp(self):
        """Registra porta UDP no backend"""
        try:
            if self.udp_port:
                command = f"REGISTER_UDP:{self.udp_port}"
                self.tcp_client.send(command.encode('utf-8'))
                command_logger.info(f"Registro UDP enviado: {self.udp_port}")
        except Exception as e:
            command_logger.error(f"Erro no registro UDP: {e}")

    def send_capture(self, callback: Optional[Callable] = None) -> str:
        """Envia comando de captura"""
        return self._send_command("CAPTURE", {}, callback)

    def send_wifi_connect(self, ssid: str, password: str, callback: Optional[Callable] = None) -> str:
        """Envia comando de conexão Wi-Fi"""
        return self._send_command("WIFI_CONNECT", {"ssid": ssid, "password": password}, callback)

    def send_restart_service(self, callback: Optional[Callable] = None) -> str:
        """Envia comando de reinicialização de serviço"""
        return self._send_command("RESTART_SERVICE", {}, callback)

    def send_show_logs(self, lines: int = 50, callback: Optional[Callable] = None) -> str:
        """Envia comando para visualizar logs"""
        return self._send_command("SHOW_LOGS", {"lines": lines}, callback)

    def _send_command(self, command_name: str, data: Dict[str, Any], callback: Optional[Callable] = None) -> str:
        """Envia comando genérico"""
        command_id = self._generate_command_id()
        
        command = Command(
            id=command_id,
            name=command_name,
            data=data,
            timestamp=time.time(),
            callback=callback
        )
        
        self.pending_commands[command_id] = command
        
        # Constrói e envia o comando
        try:
            if command_name == "WIFI_CONNECT":
                command_str = f"WIFI_CONNECT:{command_id}:{data['ssid']}:{data['password']}"
            elif command_name == "SHOW_LOGS":
                command_str = f"SHOW_LOGS:{command_id}:{data['lines']}"
            elif command_name == "RESTART_SERVICE":
                command_str = f"RESTART_SERVICE:{command_id}"
            else:
                command_str = f"{command_name}:{command_id}"
            
            self.tcp_client.send(command_str.encode('utf-8'))
            command_logger.info(f"Comando enviado: {command_name} (ID: {command_id})")
            
            # Inicia thread de timeout
            if callback:
                self.executor.submit(self._wait_for_response, command)
            
        except Exception as e:
            command_logger.error(f"Erro enviando comando {command_name}: {e}")
            if command_id in self.pending_commands:
                del self.pending_commands[command_id]
            if callback:
                callback(False, f"Erro de envio: {e}", {})
        
        return command_id

    def _wait_for_response(self, command: Command):
        """Aguarda resposta ou timeout"""
        start_time = time.time()
        
        while time.time() - start_time < command.timeout:
            if command.id not in self.pending_commands:
                return  # Resposta recebida
            time.sleep(0.1)
        
        # Timeout
        if command.id in self.pending_commands:
            command_logger.warning(f"Timeout no comando: {command.name} (ID: {command.id})")
            if command.callback:
                command.callback(False, "Timeout", {})
            del self.pending_commands[command.id]

    def handle_response(self, command_id: str, success: bool, message: str, data: Any = None):
        """Processa resposta do backend"""
        if command_id in self.pending_commands:
            command = self.pending_commands[command_id]
            
            try:
                if command.callback:
                    command.callback(success, message, data or {})
            except Exception as e:
                command_logger.error(f"Erro no callback do comando {command.name}: {e}")
            finally:
                del self.pending_commands[command_id]
                command_logger.info(f"Resposta processada: {command.name} - {success}")
        else:
            command_logger.warning(f"Resposta para comando não encontrado: {command_id}")

    def cleanup(self):
        """Limpa recursos"""
        self.executor.shutdown(wait=False)
        self.pending_commands.clear()