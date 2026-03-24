"""
Loto Quine Local — Application principale
Point d'entrée : lance l'app Flet multi-vues.
"""

import sys
import os

# Fix imports pour Android (Flet empaquette dans un répertoire spécial)
_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

import flet as ft
from views.home_view import HomeView
from views.admin_view import AdminView
from views.client_view import ClientView
from game.server import GameServer


def main(page: ft.Page):
    page.title = "🎱 Loto Quine"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0d0d1a"
    page.padding = 0

    # window.width/height ignorés sur mobile, mais utiles sur desktop
    try:
        page.window.width = 420
        page.window.height = 860
    except Exception:
        pass

    # Polices via CDN — nécessite Internet au premier lancement
    page.fonts = {
        "Oswald": "https://fonts.gstatic.com/s/oswald/v53/TK3iWkUHHAIjg752HT8Gl-1PKw.woff2",
        "Rajdhani": "https://fonts.gstatic.com/s/rajdhani/v15/LDI2apCSOBg7S-QT7pa8FMO5m-4.woff2",
    }
    page.theme = ft.Theme(font_family="Rajdhani")

    game_server = GameServer()

    def navigate(view_name: str, **kwargs):
        page.controls.clear()
        if view_name == "home":
            page.controls.append(HomeView(page, navigate).build())
        elif view_name == "admin":
            page.controls.append(AdminView(page, navigate, game_server).build())
        elif view_name == "client":
            page.controls.append(
                ClientView(page, navigate,
                           host=kwargs.get("host", ""),
                           player_name=kwargs.get("player_name", "Joueur"),
                           nb_cartons=kwargs.get("nb_cartons", 1)).build()
            )
        page.update()

    navigate("home")


ft.run(main)
