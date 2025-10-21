import json
import os
import traceback
from ui.app import FrontendApp 
from utils.logger import frontend_logger, log_frontend_start

from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


DEFAULTS = {
    "video": {
        "transport": "udp",       # "udp" ou "tcp"
        "tcp_host": "127.0.0.1",
        "tcp_port": 5050
    }
}

def _deep_merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict):
            dst.setdefault(k, {})
            _deep_merge(dst[k], v)
        else:
            dst.setdefault(k, v)
    return dst

def load_config(path: str):
    if not os.path.exists(path):
        error_msg = f"Arquivo de configuração não encontrado: {path}"
        frontend_logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        # aplica defaults sem sobrescrever valores já existentes
        cfg = _deep_merge(cfg, DEFAULTS)

        # override opcional via variável de ambiente (útil p/ testes)
        env_transport = os.getenv("VIDEO_TRANSPORT")
        if env_transport:
            cfg["video"]["transport"] = env_transport.lower().strip()
            frontend_logger.info(f"Transporte de vídeo sobrescrito por variável de ambiente: {env_transport}")

        # saneamento simples
        if cfg["video"]["transport"] not in ("udp", "tcp"):
            frontend_logger.warning(f"VIDEO_TRANSPORT inválido: {cfg['video']['transport']}. Usando 'udp' como padrão.")
            cfg["video"]["transport"] = "udp"

        frontend_logger.info(f"Configuração carregada: transporte={cfg['video']['transport']}")
        return cfg
        
    except Exception as e:
        frontend_logger.error(f"Erro ao carregar configuração: {e}")
        raise

def main():
    try:
        # Log de inicialização
        log_frontend_start()
        
        config = load_config(CONFIG_PATH)
        
        frontend_logger.info(
            f"Frontend iniciando | video.transport={config['video']['transport']} "
            + (f"| tcp={config['video']['tcp_host']}:{config['video']['tcp_port']}"
               if config['video']['transport']=='tcp' else "")
        )
        
        app = FrontendApp(config)
        frontend_logger.info("Aplicação frontend criada, iniciando loop principal...")
        app.run()
        
    except Exception as e:
        frontend_logger.critical(f"Erro fatal ao iniciar aplicação: {e}")
        frontend_logger.debug(traceback.format_exc())
        traceback.print_exc()

if __name__ == "__main__":
    main()