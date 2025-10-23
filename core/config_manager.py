import json
import os
from typing import Dict, Any, Optional
from utils.logger import frontend_logger

class ConfigManager:
    """Gerenciador centralizado de configuração com caching"""
    
    _instance = None
    _config_cache: Optional[Dict[str, Any]] = None
    
    DEFAULTS = {
        "video": {
            "transport": "udp",
            "tcp_host": "127.0.0.1", 
            "tcp_port": 5050
        },
        "network": {
            "timeout": 2.0,
            "max_packet_size": 4096
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def load_config(cls, path: str = "config.json") -> Dict[str, Any]:
        """Carrega configuração com cache e validação"""
        if cls._config_cache is not None:
            return cls._config_cache.copy()
            
        if not os.path.exists(path):
            error_msg = f"Arquivo de configuração não encontrado: {path}"
            frontend_logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Merge recursivo com defaults
            config = cls._deep_merge(config, cls.DEFAULTS)
            
            # Validação de configuração
            cls._validate_config(config)
            
            cls._config_cache = config
            frontend_logger.info("Configuração carregada e validada com sucesso")
            return config.copy()
            
        except Exception as e:
            frontend_logger.error(f"Erro ao carregar configuração: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor da configuração usando dot notation (ex: 'video.transport')"""
        if self._config_cache is None:
            # Se não foi carregado, tenta carregar com path padrão
            self.load_config()
        
        keys = key.split('.')
        value = self._config_cache
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def get_all(self) -> Dict[str, Any]:
        """Retorna toda a configuração (para compatibilidade)"""
        if self._config_cache is None:
            self.load_config()
        return self._config_cache.copy()

    @staticmethod
    def _deep_merge(destination: Dict, source: Dict) -> Dict:
        """Merge recursivo de dicionários"""
        for key, value in source.items():
            if (key in destination and isinstance(destination[key], dict) 
                and isinstance(value, dict)):
                ConfigManager._deep_merge(destination[key], value)
            else:
                destination.setdefault(key, value)
        return destination
    
    @staticmethod
    def _validate_config(config: Dict[str, Any]):
        """Valida configuração crítica"""
        video_cfg = config.get("video", {})
        transport = video_cfg.get("transport", "udp")
        
        if transport not in ("udp", "tcp"):
            frontend_logger.warning(f"Transporte inválido: {transport}. Usando UDP.")
            video_cfg["transport"] = "udp"
        
        # Override por environment variable
        env_transport = os.getenv("VIDEO_TRANSPORT")
        if env_transport and env_transport.lower() in ("udp", "tcp"):
            video_cfg["transport"] = env_transport.lower()
            frontend_logger.info(f"Transporte sobrescrito por env: {env_transport}")

    # Propriedade para compatibilidade com código existente
    @property
    def config(self) -> Dict[str, Any]:
        """Acesso direto ao dicionário de configuração"""
        if self._config_cache is None:
            self.load_config()
        return self._config_cache