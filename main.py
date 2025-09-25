import json
import os
import traceback
from ui.app import FrontendApp 

CONFIG_PATH = "config.json"

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
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # aplica defaults sem sobrescrever valores já existentes
    cfg = _deep_merge(cfg, DEFAULTS)

    # override opcional via variável de ambiente (útil p/ testes)
    env_transport = os.getenv("VIDEO_TRANSPORT")
    if env_transport:
        cfg["video"]["transport"] = env_transport.lower().strip()

    # saneamento simples
    if cfg["video"]["transport"] not in ("udp", "tcp"):
        print(f"⚠️  VIDEO_TRANSPORT inválido: {cfg['video']['transport']}. Voltando para 'udp'.")
        cfg["video"]["transport"] = "udp"

    return cfg

def main():
    try:
        config = load_config(CONFIG_PATH)
        print(
            f"🎛️  Frontend iniciando | video.transport={config['video']['transport']} "
            + (f"| tcp={config['video']['tcp_host']}:{config['video']['tcp_port']}"
               if config['video']['transport']=='tcp' else "")
        )
        app = FrontendApp(config)  # o FrontendApp agora escolhe UDP/TCP internamente
        app.run()
    except Exception as e:
        print("Fatal error starting application:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
