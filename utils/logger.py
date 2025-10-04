import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

class CustomFormatter(logging.Formatter):
    """Formatação colorida para console"""
    
    # Cores ANSI
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[34;20m"
    magenta = "\x1b[35;20m"
    cyan = "\x1b[36;20m"
    reset = "\x1b[0m"
    
    # Formatos
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    FORMATS = {
        logging.DEBUG: cyan + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

def setup_logger(name, log_level=logging.INFO, log_to_file=True):
    """Configura um logger com console e arquivo"""
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Evitar logs duplicados
    if logger.handlers:
        return logger
    
    # Formatter para arquivo (sem cores)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # Handler para arquivo
    if log_to_file:
        # Criar diretório de logs se não existir
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Arquivo com data
        log_file = log_dir / f"strawberry_frontend_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Arquivo guarda tudo
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Loggers específicos para cada módulo do frontend
frontend_logger = setup_logger("strawberry.frontend")
ui_logger = setup_logger("strawberry.ui")
network_logger = setup_logger("strawberry.network")
video_logger = setup_logger("strawberry.video")
command_logger = setup_logger("strawberry.commands")

def log_frontend_start():
    """Log de informações do frontend"""
    import platform
    import psutil
    
    frontend_logger.info("=" * 50)
    frontend_logger.info("🎮 Strawberry AI Frontend Iniciando")
    frontend_logger.info(f"📋 Sistema: {platform.system()} {platform.release()}")
    frontend_logger.info(f"🐍 Python: {platform.python_version()}")
    frontend_logger.info(f"💾 RAM: {psutil.virtual_memory().percent}% utilizada")
    frontend_logger.info("=" * 50)