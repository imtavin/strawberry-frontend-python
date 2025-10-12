import threading
import os
import time
import json
import socket
from datetime import datetime
import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from PIL import Image, ImageTk

# Importar das classes core existentes
from core.network import TCPClient
from core.video_stream import VideoStreamUDP, VideoStreamTCP
from core.commands import CommandHandler
from utils.cleanup import CleanupWorker
from ui.sidebar import Sidebar
from ui.icons import COLORS, FONTS, WINDOW_PADDING
from ui.screens.home_screen import HomeScreen
from ui.screens.gallery_screen import GalleryScreen
from ui.screens.map_screen import MapScreen
from ui.screens.settings_screen import SettingsScreen

# Importar loggers
from utils.logger import ui_logger, network_logger, video_logger, command_logger

CAPTURES_DIR = "/"


class FrontendApp(ctk.CTk):
    """
    Controlador principal da UI - otimizado para 800x480
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self._rxbuf = b""
        self.title("Detector de Pragas em Morango - TCC")
        
        ui_logger.info("Inicializando aplicação frontend")

        # Configuração específica para 800x480
        self.geometry("800x480")
        self.attributes("-fullscreen", True)
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])

        self.minsize(800, 480)
        self.maxsize(800, 480)

        self.config = config
        self.running = True
        self.current_capture_filename = None

        # Setup do backend (TCP/UDP + vídeo)
        self._setup_backend()

        # Setup da UI
        self._setup_ui()

        # Registrar screens
        self._register_screens()

        # Armazenar informações da Raspberry
        self.raspberry_info = {
            "ip": "Buscando...",
            "hostname": "Desconhecido",
            "last_update": None
        }

        # Iniciar threads
        self._start_background_workers()

        # Criar diretório de capturas
        os.makedirs(CAPTURES_DIR, exist_ok=True)
        
        ui_logger.info("Aplicação frontend inicializada com sucesso")

    # ============================
    # Backend / Rede / Vídeo
    # ============================
    def _setup_backend(self):
        """Configura clientes de rede e handlers usando as classes core"""
        server = self.config.get("server", {})
        udp_cfg = self.config.get("udp", {})
        video_cfg = self.config.get("video", {}) or {}

        network_logger.info("Configurando conexões de rede...")

        # Cliente TCP (comandos e resultados)
        self.tcp_client = TCPClient(server.get("host"), server.get("port"))

        # Command handler (usando sua classe core) — mantém a API existente
        self.commands = CommandHandler(self.tcp_client, udp_cfg.get("port") or udp_cfg.get("listen_port"))

        # Seleção do transporte de vídeo
        transport = (video_cfg.get("transport") or "udp").lower()

        if transport == "tcp":
            # TCP-JPEG: conecta no CameraServer do backend
            tcp_host = video_cfg.get("tcp_host", "127.0.0.1")
            tcp_port = int(video_cfg.get("tcp_port", 5050))
            self.video_stream = VideoStreamTCP(
                host=tcp_host,
                port=tcp_port,
                frame_callback=self._on_frame_received
            )
            self._video_transport = "tcp"
            video_logger.info(f"Vídeo configurado via TCP: {tcp_host}:{tcp_port}")
        else:
            # UDP (padrão): recebe datagramas fragmentados e remonta
            udp_port = int(udp_cfg.get("listen_port") or udp_cfg.get("port") or 5005)
            max_packet = int(udp_cfg.get("max_packet_size", 4096))
            self.video_stream = VideoStreamUDP(
                udp_port=udp_port,
                max_packet=max_packet,
                frame_callback=self._on_frame_received
            )
            self._video_transport = "udp"
            video_logger.info(f"Vídeo configurado via UDP: porta {udp_port} (max_packet={max_packet})")

        # Cleanup worker (opcional): só se o stream expuser .cleanup()
        self.cleanup_worker = None
        if hasattr(self.video_stream, "cleanup") and callable(getattr(self.video_stream, "cleanup")):
            self.cleanup_worker = CleanupWorker(self.video_stream.cleanup, interval=0.5)
            ui_logger.debug("Cleanup worker configurado")

    # ============================
    # UI
    # ============================
    def _setup_ui(self):
        """Configura layout principal da UI"""
        ui_logger.debug("Configurando interface do usuário")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = Sidebar(
            self,
            on_exit=self.exit_app,
            on_config=self._on_config,
            on_map=self._on_map,
            on_gallery=self._on_gallery,
            on_home=self._on_home,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # Área de conteúdo principal
        self.content = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=12)
        self.content.grid(row=0, column=1, sticky="nsew", padx=WINDOW_PADDING, pady=WINDOW_PADDING)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Dicionário de screens
        self.screens = {}
        
        ui_logger.debug("UI configurada com sucesso")

    def _register_screens(self):
        """Registra todas as telas da aplicação"""
        ui_logger.debug("Registrando telas da aplicação")
        
        # Home screen (vídeo principal)
        home_screen = HomeScreen(self.content, on_capture=self._on_capture_requested)
        self._register_screen("home", home_screen)

        # Gallery screen
        gallery_screen = GalleryScreen(self.content, captures_dir=CAPTURES_DIR)
        if hasattr(gallery_screen, "back_btn"):
            gallery_screen.back_btn.configure(command=self._on_home)
        self._register_screen("gallery", gallery_screen)

        # Map screen
        map_screen = MapScreen(self.content)
        if hasattr(map_screen, "back_btn"):
            map_screen.back_btn.configure(command=self._on_home)
        self._register_screen("map", map_screen)

        # Settings screen
        settings_screen = SettingsScreen(self.content, on_save=self._on_settings_save)
        if hasattr(settings_screen, "back_btn"):
            settings_screen.back_btn.configure(command=self._on_home)
        self._register_screen("settings", settings_screen)

        # Mostrar tela inicial
        self.show_screen("home")
        
        ui_logger.info("Todas as telas registradas")

    def _register_screen(self, name: str, screen):
        """Registra uma tela no gerenciador"""
        screen.grid(row=0, column=0, sticky="nsew")
        self.screens[name] = screen
        screen.lower()
        
        ui_logger.debug(f"Tela registrada: {name}")

    def show_screen(self, name: str):
        """Mostra uma tela específica"""
        ui_logger.debug(f"Alternando para tela: {name}")
        
        for _, screen in self.screens.items():
            screen.lower()
        if name in self.screens:
            self.screens[name].lift()
            ui_logger.info(f"Tela ativa: {name}")

    # ============================
    # Threads / ciclo de vida
    # ============================
    def _start_background_workers(self):
        """Inicia threads em background"""
        ui_logger.debug("Iniciando threads em background")
        
        # Conectar TCP e (se UDP) registrar porta
        threading.Thread(target=self._tcp_connect_and_register, daemon=True).start()

        # Iniciar recepção de vídeo (a classe do stream cuida do loop internamente)
        self.video_stream.start()

        # Loop de escuta TCP para resultados
        threading.Thread(target=self._tcp_result_listener, daemon=True).start()

        # Cleanup worker (só se disponível)
        if self.cleanup_worker:
            self.cleanup_worker.start()
            
        ui_logger.info("Threads em background iniciadas")

    def _tcp_connect_and_register(self):
        """Conecta TCP e, se transporte for UDP, registra porta UDP"""
        try:
            network_logger.info("Conectando ao backend via TCP...")
            self.tcp_client.connect()

            if self._video_transport == "udp":
                # Caso seu CommandHandler tenha método register_udp(), use-o.
                if hasattr(self.commands, "register_udp") and callable(getattr(self.commands, "register_udp")):
                    try:
                        self.commands.register_udp()
                        network_logger.info("Registro UDP enviado com sucesso")
                    except Exception as e:
                        network_logger.error(f"Falha no register_udp(): {e}")
                else:
                    # Fallback: mandar o comando explicitamente
                    udp_cfg = self.config.get("udp", {})
                    udp_port = int(udp_cfg.get("listen_port") or udp_cfg.get("port") or 5005)
                    try:
                        self.tcp_client.send(f"REGISTER_UDP:{udp_port}".encode("utf-8"))
                        network_logger.info(f"Comando REGISTER_UDP enviado: {udp_port}")
                    except Exception as e:
                        network_logger.error(f"Falha ao enviar REGISTER_UDP:{udp_port}: {e}")

        except Exception as e:
            network_logger.error(f"Erro na conexão: {e}")

    def _tcp_result_listener(self):
        """Escuta resultados do backend via TCP"""
        network_logger.info("Iniciando listener de resultados TCP")
        
        while self.running:
            try:
                if self.tcp_client.sock:
                    # Verificar se há dados disponíveis
                    self.tcp_client.sock.settimeout(1.0)
                    try:
                        data = self.tcp_client.sock.recv(1024)
                        if data:
                            result_str = data.decode('utf-8').strip()
                            network_logger.debug(f"Resultado recebido: {result_str}")
                            self._process_backend_result(result_str)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        network_logger.error(f"Erro recebendo resultado: {e}")
                        time.sleep(0.1)
                else:
                    time.sleep(1)
            except Exception as e:
                network_logger.error(f"Erro no listener TCP: {e}")
                time.sleep(1)

    # ============================
    # Processamento de resultados
    # ============================
    def _process_backend_result(self, result_str: str):
        """Processa resultado do backend (JSON preferencial; fallback 'LABEL:CONF')."""
        try:
            # 1) tente JSON primeiro
            data = json.loads(result_str)
            label = data.get("label", "Indeterminado")
            conf = data.get("confidence", 0)

            # Verificar se é informação da Raspberry
            if isinstance(data, dict) and data.get("type") == "raspberry_info":
                self._on_raspberry_info_received(data)
                return
        except Exception:
            # 2) fallback: "LABEL:CONF" (uma única vez para não quebrar rótulos com ':')
            if ":" in result_str:
                label_part, conf_part = result_str.split(":", 1)
                label = label_part.strip()
                conf_str = conf_part.strip().strip("%").replace(",", ".")
                try:
                    conf = float(conf_str)
                except Exception:
                    conf = conf_str  # deixa como string se não for número
            else:
                label = result_str.strip()
                conf = 0

        # Normaliza confiança para texto amigável
        if isinstance(conf, (int, float)):
            conf_text = f"{conf:.1%}" if 0.0 <= conf <= 1.0 else f"{conf:.1f}%"
        else:
            conf_text = str(conf)

        command_logger.info(f"Resultado processado: {label} ({conf_text})")
        self._on_analysis_result({"label": label, "confidence": conf_text})

    def _on_raspberry_info_received(self, raspberry_data: dict):
        """Processa informações da Raspberry recebidas do backend"""
        try:
            self.raspberry_info = {
                "ip": raspberry_data.get("ip", "Indisponível"),
                "hostname": raspberry_data.get("hostname", "Desconhecido"),
                "last_update": raspberry_data.get("timestamp")
            }
            
            ui_logger.info(f"Informações da Raspberry recebidas: {self.raspberry_info['ip']}")
            
            # Atualizar a tela de configurações se estiver visível
            self._update_settings_display()
            
        except Exception as e:
            ui_logger.error(f"Erro ao processar informações da Raspberry: {e}")

    def _update_settings_display(self):
        """Atualiza a exibição na tela de configurações"""
        try:
            settings_screen = self.screens.get("settings")
            if settings_screen and hasattr(settings_screen, "update_raspberry_info"):
                self.after(0, lambda: settings_screen.update_raspberry_info(self.raspberry_info))
        except Exception as e:
            ui_logger.debug(f"Erro ao atualizar display de configurações: {e}")

    # ============================
    # Navegação
    # ============================
    def _on_home(self):
        ui_logger.debug("Navegando para tela Home")
        self.show_screen("home")

    def _on_map(self):
        ui_logger.debug("Navegando para tela Mapa")
        self.show_screen("map")

    def _on_gallery(self):
        ui_logger.debug("Navegando para tela Galeria")
        # Reconstruir grid da galeria ao abrir
        gallery = self.screens.get("gallery")
        if gallery and hasattr(gallery, "_build_grid"):
            gallery._build_grid()
        self.show_screen("gallery")

    def _on_config(self):
        ui_logger.debug("Navegando para tela Configurações")
        self.show_screen("settings")

    # ============================
    # Ações
    # ============================
    def _on_capture_requested(self):
        """Callback quando usuário clica em Capturar"""
        ui_logger.info("Captura solicitada pelo usuário")
        # Feedback imediato
        self.show_loading()

        # Salvar frame atual como imagem
        def capture_worker():
            try:
                # Obter frame atual
                home_screen = self.screens.get("home")
                if hasattr(home_screen, "get_current_frame"):
                    frame = home_screen.get_current_frame()
                    if frame:
                        # Enviar comando de captura para backend
                        if hasattr(self.commands, "send_capture"):
                            self.commands.send_capture()
                            command_logger.info("Comando CAPTURE enviado para backend")
                    else:
                        ui_logger.warning("Nenhum frame disponível para captura")
                        self._on_analysis_result({"label": "Erro: Sem frame", "confidence": "0%"})
                else:
                    ui_logger.error("Método get_current_frame não disponível")
                    self._on_analysis_result({"label": "Erro: UI", "confidence": "0%"})

            except Exception as e:
                ui_logger.error(f"Erro na captura: {e}")
                self._on_analysis_result({"label": f"Erro: {str(e)}", "confidence": "0%"})

        threading.Thread(target=capture_worker, daemon=True).start()

    def _on_analysis_result(self, payload):
        """Processa resultado da análise"""
        try:
            if isinstance(payload, dict):
                label = payload.get("label", "Indeterminado")
                confidence = str(payload.get("confidence", "—"))
            else:
                label = str(payload)
                confidence = "—"

            ui_logger.info(f"Exibindo resultado: {label} ({confidence})")
            # Atualizar UI na thread principal
            self.after(0, lambda: self.show_result(label, confidence))

        except Exception as e:
            ui_logger.error(f"Erro processando resultado: {e}")
            self.after(0, lambda: self.show_result("Erro", "0%"))

    def _on_settings_save(self, new_settings):
        """Salva configurações"""
        try:
            with open("config.json", "r+", encoding="utf-8") as f:
                config = json.load(f)
                config.update(new_settings)
                f.seek(0)
                json.dump(config, f, indent=2)
                f.truncate()
            ui_logger.info("Configurações salvas com sucesso")
        except Exception as e:
            ui_logger.error(f"Erro salvando configurações: {e}")

    # ============================
    # Integração com a HomeScreen
    # ============================
    def update_frame(self, pil_image: Image.Image):
        """Atualiza frame de vídeo (chamado pelo backend)"""

        def update_ui():
            home_screen = self.screens.get("home")
            if home_screen and hasattr(home_screen, "update_frame"):
                home_screen.update_frame(pil_image)

        self.after(0, update_ui)

    def show_loading(self):
        """Mostra estado de loading"""

        def show_loading_ui():
            home_screen = self.screens.get("home")
            if home_screen and hasattr(home_screen, "show_state"):
                home_screen.show_state("loading")

        self.after(0, show_loading_ui)

    def show_result(self, result_text: str, confidence: str):
        """Mostra resultado da análise"""

        def show_result_ui():
            home_screen = self.screens.get("home")
            if home_screen and hasattr(home_screen, "set_result"):
                home_screen.set_result(result_text, confidence)
                home_screen.show_state("result")

        self.after(0, show_result_ui)

    def show_video(self):
        """Volta para estado de vídeo"""

        def show_video_ui():
            home_screen = self.screens.get("home")
            if home_screen and hasattr(home_screen, "show_state"):
                home_screen.show_state("video")

        self.after(0, show_video_ui)

    def _on_frame_received(self, frame_rgb):
        """Callback quando novo frame é recebido (dos streams UDP/TCP)"""
        try:
            from PIL import Image
            import numpy as np

            if isinstance(frame_rgb, np.ndarray):
                pil_image = Image.fromarray(frame_rgb)
            else:
                return

            self.update_frame(pil_image)
        except Exception as e:
            video_logger.error(f"Erro processando frame: {e}")

    # ============================
    # Encerramento
    # ============================
    def exit_app(self):
        """Encerra aplicação corretamente"""
        ui_logger.info("Encerrando aplicação frontend...")
        self.running = False

        try:
            if self.cleanup_worker:
                self.cleanup_worker.stop(join=True, timeout=1.0)
                ui_logger.debug("Cleanup worker parado")
        except Exception as e:
            ui_logger.debug(f"Erro parando cleanup worker: {e}")

        try:
            if hasattr(self.video_stream, "stop"):
                self.video_stream.stop()
                video_logger.info("Video stream parado")
        except Exception as e:
            video_logger.error(f"Erro parando video stream: {e}")

        try:
            if hasattr(self.tcp_client, "close"):
                self.tcp_client.close()
                network_logger.info("Cliente TCP fechado")
        except Exception as e:
            network_logger.error(f"Erro fechando cliente TCP: {e}")

        ui_logger.info("Aplicação frontend encerrada")
        self.destroy()

    def run(self):
        """Inicia aplicação"""
        ui_logger.info("Iniciando loop principal da aplicação")
        try:
            self.mainloop()
        except Exception as e:
            ui_logger.critical(f"Erro no loop principal: {e}")
        finally:
            self.exit_app()