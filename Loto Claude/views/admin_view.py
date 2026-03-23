"""
Vue Admin — tirage des numéros, historique, diffusion réseau.
"""

import flet as ft
from game.server import GameServer
from views.components import (
    BG_DARK, BG_CARD, COLOR_ACCENT, COLOR_DRAWN, COLOR_WIN, TEXT_PRIMARY,
    TEXT_MUTED, BORDER_COLOR, big_number_display, number_ball
)


class AdminView:
    def __init__(self, page: ft.Page, navigate, server: GameServer):
        self.page = page
        self.navigate = navigate
        self.server = server
        self._current_num_ref: ft.Ref = ft.Ref[ft.Container]()
        self._history_row: ft.Ref = ft.Ref[ft.Row]()
        self._status_text: ft.Ref = ft.Ref[ft.Text]()
        self._counter_text: ft.Ref = ft.Ref[ft.Text]()
        self._draw_btn: ft.Ref = ft.Ref[ft.ElevatedButton]()
        self._last_num_container = None
        self._history_grid = None

    def build(self) -> ft.Container:
        # Démarrer le serveur
        self.server.start()
        ip = self.server.get_local_ip()

        # ── Widgets réactifs ──
        self._last_num_container = big_number_display(None)
        self._history_grid = ft.Row(
            wrap=True, spacing=6, run_spacing=6,
            alignment=ft.MainAxisAlignment.CENTER
        )
        status = ft.Text(f"✅ Serveur actif — IP : {ip}:{self.server.port}",
                         size=12, color=COLOR_WIN, text_align=ft.TextAlign.CENTER)
        counter = ft.Text("0 / 90 numéros tirés",
                          size=13, color=TEXT_MUTED, font_family="Oswald")

        self._status_text_ref = status
        self._counter_text_ref = counter

        def draw(e):
            if len(self.server.drawn) >= 90:
                status.value = "🏁 Tous les numéros ont été tirés !"
                status.color = "#ff5252"
                status.update()
                return
            num = self.server.draw_number()
            if num is None:
                return
            # Mettre à jour le grand affichage
            self._last_num_container.content.value = str(num)
            self._last_num_container.update()
            # Historique
            ball = number_ball(num, size=38, color=COLOR_ACCENT)
            self._history_grid.controls.insert(0, ball)
            self._history_grid.update()
            # Compteur
            counter.value = f"{len(self.server.drawn)} / 90 numéros tirés"
            counter.update()

        def reset_game(e):
            self.server.reset()
            self._last_num_container.content.value = "—"
            self._last_num_container.update()
            self._history_grid.controls.clear()
            self._history_grid.update()
            counter.value = "0 / 90 numéros tirés"
            counter.update()
            status.value = f"✅ Partie réinitialisée — IP : {ip}:{self.server.port}"
            status.color = COLOR_WIN
            status.update()

        def go_home(e):
            self.server.stop()
            self.navigate("home")

        # ── Layout ──
        return ft.Container(
            expand=True,
            bgcolor=BG_DARK,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[

                    # Header
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=16, vertical=14),
                        content=ft.Row([
                            ft.IconButton(ft.Icons.ARROW_BACK,
                                          icon_color=TEXT_MUTED, on_click=go_home),
                            ft.Text("ADMIN — TIRAGE", size=20, font_family="Oswald",
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, style=ft.TextStyle(letter_spacing=3)),
                            ft.Container(width=40),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ),

                    # Status
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Container(
                            padding=ft.padding.all(10),
                            border_radius=8,
                            bgcolor="#001a12",
                            border=ft.border.all(1, COLOR_WIN + "55"),
                            content=status,
                        ),
                    ),

                    ft.Container(height=20),

                    # Grand numéro
                    self._last_num_container,

                    ft.Container(height=6),
                    counter,

                    ft.Container(height=24),

                    # Bouton tirer
                    ft.Container(
                        width=280,
                        content=ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CASINO, color=TEXT_PRIMARY, size=24),
                                ft.Text("TIRER UN NUMÉRO", color=TEXT_PRIMARY,
                                        font_family="Oswald", size=18,
                                        weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=2)),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                            style=ft.ButtonStyle(
                                bgcolor={ft.ControlState.DEFAULT: COLOR_ACCENT,
                                         ft.ControlState.HOVERED: "#9c6fff",
                                         ft.ControlState.PRESSED: "#5c1fff"},
                                shape=ft.RoundedRectangleBorder(radius=14),
                                padding=ft.padding.symmetric(vertical=20),
                                shadow_color=f"{COLOR_ACCENT}99",
                                elevation={ft.ControlState.PRESSED: 2, ft.ControlState.DEFAULT: 12},
                            ),
                            on_click=draw,
                            expand=True,
                        ),
                    ),

                    ft.Container(height=12),

                    # Bouton reset
                    ft.Container(
                        width=280,
                        content=ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.REFRESH, color="#ff5252", size=18),
                                ft.Text("NOUVELLE PARTIE", color="#ff5252",
                                        font_family="Oswald", size=14, style=ft.TextStyle(letter_spacing=1)),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, "#ff5252"),
                                shape=ft.RoundedRectangleBorder(radius=12),
                                padding=ft.padding.symmetric(vertical=14),
                            ),
                            on_click=reset_game,
                            expand=True,
                        ),
                    ),

                    ft.Container(height=24),
                    ft.Divider(color=BORDER_COLOR),

                    # Historique
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        content=ft.Column([
                            ft.Text("HISTORIQUE DES TIRAGES",
                                    size=12, color=TEXT_MUTED, font_family="Oswald", style=ft.TextStyle(letter_spacing=3)),
                            ft.Container(height=10),
                            self._history_grid,
                        ]),
                    ),

                    ft.Container(height=30),
                ],
            ),
        )
