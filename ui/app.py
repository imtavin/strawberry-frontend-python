# ui/app.py
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
from core.network import TCPClient, UDPClient
from core.video_stream import VideoStreamHandler
from core.commands import CommandHandler
from utils.cleanup import CleanupWorker
from ui.sidebar import Sidebar
from ui.icons import COLORS, FONTS, WINDOW_PADDING
from ui.screens.home_screen import HomeScreen
from ui.screens.gallery_screen import GalleryScreen
from ui.screens.map_screen import MapScreen
from ui.screens.settings_screen import SettingsScreen

CAPTURES_DIR = "/"

class FrontendApp(ctk.CTk):
    """
    Controlador principal da UI - otimizado para 800x400
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.title("Detector de Pragas em Morango - TCC")
        
        # Configuração específica para 800x400
        self.geometry("800x400")
        self.attributes("-fullscreen", True)
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        
        self.minsize(800, 400)
        self.maxsize(800, 400)
        
        self.config = config
        self.running = True
        self.current_capture_filename = None
        
        # Setup do backend
        self._setup_backend()
        
        # Setup da UI
        self._setup_ui()
        
        # Registrar screens
        self._register_screens()
        
        # Iniciar threads
        self._start_background_workers()
        
        # Criar diretório de capturas
        os.makedirs(CAPTURES_DIR, exist_ok=True)

    def _setup_backend(self):
        """Configura clientes de rede e handlers usando as classes core"""
        server = self.config.get("server", {})
        udp = self.config.get("udp", {})
        
        # Network clients (usando suas classes core)
        self.tcp_client = TCPClient(server.get("host"), server.get("port"))
        self.udp_client = UDPClient(udp.get("host"), udp.get("port"))
        self.udp_sock = self.udp_client.bind()
        
        # Video stream (usando sua classe core)
        self.video_stream = VideoStreamHandler(self.udp_sock, self._on_frame_received)
        
        # Command handler (usando sua classe core)
        self.commands = CommandHandler(self.tcp_client, udp.get("port"))
        
        # Cleanup worker
        self.cleanup_worker = CleanupWorker(self.video_stream.cleanup, interval=0.5)

    def _setup_ui(self):
        """Configura layout principal da UI"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.sidebar = Sidebar(
            self, 
            on_exit=self.exit_app,
            on_config=self._on_config,
            on_map=self._on_map,
            on_gallery=self._on_gallery,
            on_home=self._on_home
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        
        # Área de conteúdo principal
        self.content = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=12)
        self.content.grid(row=0, column=1, sticky="nsew", padx=WINDOW_PADDING, pady=WINDOW_PADDING)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Dicionário de screens
        self.screens = {}

    def _register_screens(self):
        """Registra todas as telas da aplicação"""
        # Home screen (vídeo principal)
        home_screen = HomeScreen(self.content, on_capture=self._on_capture_requested)
        self._register_screen("home", home_screen)
        
        # Gallery screen
        gallery_screen = GalleryScreen(self.content, captures_dir=CAPTURES_DIR)
        if hasattr(gallery_screen, 'back_btn'):
            gallery_screen.back_btn.configure(command=self._on_home)
        self._register_screen("gallery", gallery_screen)
        
        # Map screen
        map_screen = MapScreen(self.content)
        if hasattr(map_screen, 'back_btn'):
            map_screen.back_btn.configure(command=self._on_home)
        self._register_screen("map", map_screen)
        
        # Settings screen
        settings_screen = SettingsScreen(self.content, on_save=self._on_settings_save)
        if hasattr(settings_screen, 'back_btn'):
            settings_screen.back_btn.configure(command=self._on_home)
        self._register_screen("settings", settings_screen)
        
        # Mostrar tela inicial
        self.show_screen("home")

    def _register_screen(self, name: str, screen):
        """Registra uma tela no gerenciador"""
        screen.grid(row=0, column=0, sticky="nsew")
        self.screens[name] = screen
        screen.lower()

    def show_screen(self, name: str):
        """Mostra uma tela específica"""
        for screen_name, screen in self.screens.items():
            screen.lower()
        
        if name in self.screens:
            self.screens[name].lift()

    def _start_background_workers(self):
        """Inicia threads em background"""
        # Conectar TCP e registrar UDP
        threading.Thread(target=self._tcp_connect_and_register, daemon=True).start()
        
        # Loop de recebimento de vídeo (usando sua classe core)
        threading.Thread(
            target=self.video_stream.receive_loop, 
            args=(lambda: self.running,), 
            daemon=True
        ).start()
        
        # Loop de escuta TCP para resultados
        threading.Thread(target=self._tcp_result_listener, daemon=True).start()
        
        # Cleanup worker
        self.cleanup_worker.start()

    def _tcp_connect_and_register(self):
        """Conecta TCP e registra porta UDP"""
        try:
            self.tcp_client.connect()
            if hasattr(self.commands, 'register_udp'):
                self.commands.register_udp()
            print("✅ Conectado ao backend")
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")

    def _tcp_result_listener(self):
        """Escuta resultados do backend via TCP"""
        while self.running:
            try:
                if self.tcp_client.sock:
                    # Verificar se há dados disponíveis
                    self.tcp_client.sock.settimeout(1.0)
                    try:
                        data = self.tcp_client.sock.recv(1024)
                        if data:
                            result_str = data.decode('utf-8').strip()
                            print(f"📨 Resultado recebido: {result_str}")
                            self._process_backend_result(result_str)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"Erro recebendo resultado: {e}")
                        time.sleep(0.1)
                else:
                    time.sleep(1)
            except Exception as e:
                print(f"Erro no listener TCP: {e}")
                time.sleep(1)

    def _process_backend_result(self, result_str: str):
        """Processa resultado do backend"""
        try:
            # Esperado: "LABEL:CONFIDENCE" ou JSON
            if ":" in result_str:
                parts = result_str.split(":")
                if len(parts) >= 2:
                    label = parts[0]
                    confidence = parts[1]
                else:
                    label = result_str
                    confidence = "0%"
            else:
                # Tentar parsear como JSON
                try:
                    result_data = json.loads(result_str)
                    label = result_data.get("label", "Indeterminado")
                    confidence = result_data.get("confidence", "0%")
                except:
                    label = result_str
                    confidence = "0%"
            
            self._on_analysis_result({"label": label, "confidence": confidence})
            
        except Exception as e:
            print(f"Erro processando resultado: {e}")
            self._on_analysis_result({"label": "Erro", "confidence": "0%"})

    # Callbacks de navegação
    def _on_home(self):
        self.show_screen("home")

    def _on_map(self):
        self.show_screen("map")

    def _on_gallery(self):
        # Reconstruir grid da galeria ao abrir
        gallery = self.screens.get("gallery")
        if gallery and hasattr(gallery, '_build_grid'):
            gallery._build_grid()
        self.show_screen("gallery")

    def _on_config(self):
        self.show_screen("settings")

    def _on_capture_requested(self):
        """Callback quando usuário clica em Capturar"""
        # Feedback imediato
        self.show_loading()
        
        # Salvar frame atual como imagem
        def capture_worker():
            try:
                # Obter frame atual
                home_screen = self.screens.get("home")
                if hasattr(home_screen, 'get_current_frame'):
                    frame = home_screen.get_current_frame()
                    if frame:
                        # Enviar comando de captura para backend
                        if hasattr(self.commands, 'send_capture'):
                            self.commands.send_capture()  # Agora passa o filename
                        
                    else:
                        print("❌ Nenhum frame disponível")
                        self._on_analysis_result({"label": "Erro: Sem frame", "confidence": "0%"})
                else:
                    print("❌ Método get_current_frame não disponível")
                    self._on_analysis_result({"label": "Erro: UI", "confidence": "0%"})
                    
            except Exception as e:
                print(f"❌ Erro na captura: {e}")
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
            
            # Atualizar UI na thread principal
            self.after(0, lambda: self.show_result(label, confidence))
            
        except Exception as e:
            print(f"Erro processando resultado: {e}")
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
            print("✅ Configurações salvas")
        except Exception as e:
            print(f"❌ Erro salvando configurações: {e}")

    # Métodos públicos para controle de estado
    def update_frame(self, pil_image: Image.Image):
        """Atualiza frame de vídeo (chamado pelo backend)"""
        def update_ui():
            home_screen = self.screens.get("home")
            if home_screen and hasattr(home_screen, 'update_frame'):
                home_screen.update_frame(pil_image)
        
        self.after(0, update_ui)

    def show_loading(self):
        """Mostra estado de loading"""
        def show_loading_ui():
            home_screen = self.screens.get("home")
            if home_screen and hasattr(home_screen, 'show_state'):
                home_screen.show_state("loading")
        
        self.after(0, show_loading_ui)

    def show_result(self, result_text: str, confidence: str):
        """Mostra resultado da análise"""
        def show_result_ui():
            home_screen = self.screens.get("home")
            if home_screen and hasattr(home_screen, 'set_result'):
                home_screen.set_result(result_text, confidence)
                home_screen.show_state("result")
        
        self.after(0, show_result_ui)

    def show_video(self):
        """Volta para estado de vídeo"""
        def show_video_ui():
            home_screen = self.screens.get("home")
            if home_screen and hasattr(home_screen, 'show_state'):
                home_screen.show_state("video")
        
        self.after(0, show_video_ui)

    def _on_frame_received(self, frame_rgb):
        """Callback quando novo frame é recebido (da classe core VideoStreamHandler)"""
        try:
            from PIL import Image
            import numpy as np
            
            if isinstance(frame_rgb, np.ndarray):
                pil_image = Image.fromarray(frame_rgb)
            else:
                return
                
            self.update_frame(pil_image)
        except Exception as e:
            print(f"Erro processando frame: {e}")

    def exit_app(self):
        """Encerra aplicação corretamente"""
        self.running = False
        
        try:
            self.cleanup_worker.stop(join=True, timeout=1.0)
        except Exception:
            pass
            
        try:
            # Parar video stream se existir método stop
            if hasattr(self.video_stream, 'stop'):
                self.video_stream.stop()
        except Exception:
            pass
            
        try:
            if hasattr(self.tcp_client, 'close'):
                self.tcp_client.close()
        except Exception:
            pass
            
        self.destroy()

    def run(self):
        """Inicia aplicação"""
        try:
            self.mainloop()
        finally:
            self.exit_app()