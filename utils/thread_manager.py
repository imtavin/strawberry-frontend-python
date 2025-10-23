import threading
import time
from typing import Dict, List
from utils.logger import setup_logger

class ThreadManager:
    """Gerencia threads da aplicação com lifecycle control"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.threads: Dict[str, threading.Thread] = {}
        self.thread_lock = threading.RLock()
        self.shutdown_flag = threading.Event()
        self.system_logger = setup_logger("strawberry.system")
        self.system_logger.debug("ThreadManager inicializado")
    
    def register_thread(self, name: str, target: callable, daemon: bool = True, **kwargs):
        """Registra e inicia uma thread"""
        thread = threading.Thread(
            target=target, 
            daemon=daemon, 
            name=name,
            kwargs=kwargs
        )
        
        with self.thread_lock:
            self.threads[name] = thread
            
        thread.start()
        self.system_logger.debug(f"Thread registrada e iniciada: {name}")
        return thread
    
    def stop_all(self, timeout: float = 3.0):
        """Para todas as threads gerenciadas"""
        self.shutdown_flag.set()
        self.system_logger.info("Parando todas as threads...")
        
        with self.thread_lock:
            for name, thread in self.threads.items():
                if thread.is_alive():
                    self.system_logger.debug(f"Aguardando thread: {name}")
                    thread.join(timeout=timeout)
                    if thread.is_alive():
                        self.system_logger.warning(f"Thread {name} não finalizou a tempo")
            
            self.threads.clear()
        
        self.system_logger.info("Todas as threads paradas")