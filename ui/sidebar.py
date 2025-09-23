# ui/sidebar.py
import customtkinter as ctk
from ui.icons import COLORS, FONTS, SIDEBAR_WIDTH, ICONS
from ui.widgets.battery_widget import BatteryWidget

class Sidebar(ctk.CTkFrame):
    """Sidebar moderna com ícones e layout aprimorado"""
    
    def __init__(self, master, on_exit, on_config, on_map, on_gallery, on_home, *args, **kwargs):
        super().__init__(
            master, 
            width=SIDEBAR_WIDTH, 
            corner_radius=0, 
            fg_color=COLORS["sidebar"], 
            *args, **kwargs
        )
        
        self.grid_propagate(False)
        self.pack_propagate(False)
        
        self._build_ui(on_exit, on_config, on_map, on_gallery, on_home)

    def _build_ui(self, on_exit, on_config, on_map, on_gallery, on_home):
        # Cabeçalho com logo
        self._create_header()
        
        # Menu principal
        self._create_menu(on_home, on_map, on_gallery)
        
        # Espaçador
        ctk.CTkFrame(self, fg_color="transparent", height=20).pack(fill="x")
        
        # Status e configurações
        self._create_footer(on_config, on_exit)

    def _create_header(self):
        """Cria cabeçalho com logo"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=100)
        header_frame.pack(fill="x", pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Logo do morango
        strawberry_icon = ICONS["strawberry"]((48, 48))
        if strawberry_icon:
            logo_label = ctk.CTkLabel(
                header_frame, 
                image=strawberry_icon, 
                text="",
                fg_color="transparent"
            )
            logo_label.pack(pady=(10, 5))
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame,
            text="Strawberry AI",
            text_color=COLORS["text"],
            font=FONTS["title"]
        )
        title_label.pack(pady=(0, 5))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Detector de Pragas",
            text_color=COLORS["text_secondary"],
            font=FONTS["small"]
        )
        subtitle_label.pack()

    def _create_menu(self, on_home, on_map, on_gallery):
        """Cria menu de navegação"""
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.pack(fill="x", padx=15, pady=10)
        
        # Botões do menu
        menu_items = [
            ("Home", ICONS["home"](), on_home),
            ("Mapa", ICONS["maps"](), on_map),
            ("Galeria", ICONS["gallery"](), on_gallery),
        ]
        
        for text, icon, command in menu_items:
            btn = ctk.CTkButton(
                menu_frame,
                text=f"  {text}",
                image=icon,
                width=200,
                height=42,
                corner_radius=21,
                fg_color=COLORS["pill_dark"],
                hover_color=COLORS["pill"],
                text_color=COLORS["text"],
                font=FONTS["menu"],
                anchor="w",
                command=command
            )
            btn.pack(fill="x", pady=5)

    def _create_footer(self, on_config, on_exit):
        """Cria rodapé com bateria e ações"""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", padx=15, pady=15)
        
        # Status da bateria
        status_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 10))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Status do Sistema",
            text_color=COLORS["text_secondary"],
            font=FONTS["small"]
        )
        status_label.pack(anchor="w")
        
        # Widget de bateria
        self.battery_widget = BatteryWidget(status_frame, percentage=82)
        self.battery_widget.pack(anchor="w", pady=(5, 0))
        
        # Botões de ação
        action_items = [
            ("Configurações", ICONS["setting"](), on_config),
            ("Sair", None, on_exit),
        ]
        
        for text, icon, command in action_items:
            btn = ctk.CTkButton(
                footer_frame,
                text=f"  {text}" if icon else text,
                image=icon,
                width=120,
                height=36,
                corner_radius=18,
                fg_color=COLORS["pill_dark"],
                hover_color=COLORS["accent"] if text == "Sair" else COLORS["pill"],
                text_color=COLORS["text_secondary"],
                font=FONTS["body"],
                anchor="w",
                command=command
            )
            btn.pack(fill="x", pady=2)

    def update_battery(self, percentage: int):
        """Atualiza status da bateria"""
        self.battery_widget.set_percentage(percentage)