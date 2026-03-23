"""
Vue Client — cartons de jeu, tirage en temps réel, bouton QUINE.
"""

import flet as ft
import threading
from game.server import GameClient
from game.carton import generate_carton
from views.components import (
    BG_DARK, BG_CARD, COLOR_ACCENT, COLOR_DRAWN, COLOR_WIN, COLOR_CHECKED,
    TEXT_PRIMARY, TEXT_MUTED, BORDER_COLOR,
    CartonWidget, big_number_display, number_ball
)


class ClientView:
    def __init__(self, page: ft.Page, navigate,
                 host: str, player_name: str, nb_cartons: int):
        self.page = page
        self.navigate = navigate
        self.host = host
        self.player_name = player_name
        self.nb_cartons = nb_cartons
        self.client = GameClient(host)
        self.drawn: list = []
        self._carton_widgets: list[CartonWidget] = []
        self._last_num_container = None
        self._recent_row = None
        self._conn_status = None
        self._quine_banner = None

    def build(self) -> ft.Container:
        # Générer les cartons
        grids = [generate_carton() for _ in range(self.nb_cartons)]
        self._carton_widgets = [
            CartonWidget(g, self.player_name, i, on_quine=self._on_quine)
            for i, g in enumerate(grids)
        ]

        # Widgets réactifs
        self._last_num_container = big_number_display(None)
        self._recent_row = ft.Row(
            [], spacing=6, alignment=ft.MainAxisAlignment.CENTER
        )
        self._conn_status = ft.Text(
            "⏳ Connexion...", size=12, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER
        )
        self._quine_banner = ft.Container(
            visible=False,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=12,
            gradient=ft.LinearGradient(
                colors=[COLOR_WIN, "#00b84a"],
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
            ),
            content=ft.Text("🎉 QUINE ! Félicitations !",
                            size=20, weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY, font_family="Oswald",
                            text_align=ft.TextAlign.CENTER),
            animate=ft.Animation(400, ft.AnimationCurve.EASE_IN),
        )

        # Cartons widgets construits
        carton_containers = [cw.build() for cw in self._carton_widgets]

        def go_home(e):
            self.client.disconnect()
            self.navigate("home")

        def claim_quine(e):
            self._show_quine_banner()

        # Connecter le client
        self._setup_client()

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
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        content=ft.Row([
                            ft.IconButton(ft.Icons.ARROW_BACK,
                                          icon_color=TEXT_MUTED, on_click=go_home),
                            ft.Text(f"🎱 {self.player_name.upper()}",
                                    size=18, font_family="Oswald",
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, style=ft.TextStyle(letter_spacing=2)),
                            ft.Container(width=40),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ),

                    # Status connexion
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=self._conn_status,
                    ),

                    ft.Container(height=12),

                    # Grand numéro tiré
                    self._last_num_container,
                    ft.Container(height=6),
                    ft.Text("DERNIER NUMÉRO", size=10, color=TEXT_MUTED,
                            font_family="Oswald", style=ft.TextStyle(letter_spacing=3)),

                    ft.Container(height=12),

                    # Derniers 4 numéros
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Column([
                            ft.Text("4 DERNIERS NUMÉROS", size=10, color=TEXT_MUTED,
                                    font_family="Oswald", style=ft.TextStyle(letter_spacing=2)),
                            ft.Container(height=6),
                            self._recent_row,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    ),

                    ft.Container(height=16),
                    ft.Divider(color=BORDER_COLOR),
                    ft.Container(height=12),

                    # Quine banner
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=16),
                        content=self._quine_banner,
                    ),

                    # Bouton QUINE
                    ft.Container(
                        width=300,
                        content=ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.EMOJI_EVENTS,
                                        color=TEXT_PRIMARY, size=22),
                                ft.Text("GAGNER / QUINE !", color=TEXT_PRIMARY,
                                        font_family="Oswald", size=18,
                                        weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=1)),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                            style=ft.ButtonStyle(
                                bgcolor={ft.ControlState.DEFAULT: "#cc8800",
                                         ft.ControlState.HOVERED: COLOR_WIN,
                                         ft.ControlState.PRESSED: "#008844"},
                                shape=ft.RoundedRectangleBorder(radius=14),
                                padding=ft.padding.symmetric(vertical=18),
                                shadow_color="#cc880099",
                                elevation={ft.ControlState.PRESSED: 2, ft.ControlState.DEFAULT: 10},
                            ),
                            on_click=claim_quine,
                            expand=True,
                        ),
                    ),

                    ft.Container(height=16),
                    ft.Text("VOS CARTONS", size=11, color=TEXT_MUTED,
                            font_family="Oswald", style=ft.TextStyle(letter_spacing=3)),
                    ft.Container(height=8),

                    # Cartons
                    *[ft.Container(
                        padding=ft.padding.symmetric(horizontal=12),
                        content=cc,
                    ) for cc in carton_containers],

                    ft.Container(height=30),
                ],
            ),
        )

    # ── Callbacks réseau ────────────────────────────────────────────────────

    def _setup_client(self):
        self.client.on_draw = self._on_draw
        self.client.on_history = self._on_history
        self.client.on_reset = self._on_reset
        self.client.on_connect_error = self._on_error

        def connect_thread():
            ok = self.client.connect()
            def update_ui():
                if ok:
                    self._conn_status.value = f"✅ Connecté à {self.host}"
                    self._conn_status.color = COLOR_WIN
                else:
                    self._conn_status.value = f"❌ Impossible de joindre {self.host}"
                    self._conn_status.color = "#ff5252"
                try:
                    self._conn_status.update()
                except Exception:
                    pass
            self.page.run_thread(update_ui) if hasattr(self.page, 'run_thread') else None
            try:
                self._conn_status.update()
            except Exception:
                pass

        t = threading.Thread(target=connect_thread, daemon=True)
        t.start()

    def _on_draw(self, num: int, drawn: list):
        self.drawn = drawn
        drawn_set = set(drawn)
        self._last_num_container.content.value = str(num)
        self._update_recent(drawn)
        for cw in self._carton_widgets:
            cw.update_drawn(drawn_set)
        try:
            self._last_num_container.update()
        except Exception:
            pass

    def _on_history(self, drawn: list):
        self.drawn = drawn
        drawn_set = set(drawn)
        if drawn:
            self._last_num_container.content.value = str(drawn[-1])
        self._update_recent(drawn)
        for cw in self._carton_widgets:
            cw.update_drawn(drawn_set)
        try:
            self._last_num_container.update()
        except Exception:
            pass
        self._conn_status.value = f"✅ Connecté à {self.host}"
        self._conn_status.color = COLOR_WIN
        try:
            self._conn_status.update()
        except Exception:
            pass

    def _on_reset(self):
        self.drawn = []
        self._last_num_container.content.value = "—"
        self._recent_row.controls.clear()
        for cw in self._carton_widgets:
            cw.update_drawn(set())
            cw.checked.clear()
        self._quine_banner.visible = False
        try:
            self._last_num_container.update()
            self._recent_row.update()
            self._quine_banner.update()
        except Exception:
            pass

    def _on_error(self, msg: str):
        try:
            self._conn_status.value = f"❌ Erreur : {msg}"
            self._conn_status.color = "#ff5252"
            self._conn_status.update()
        except Exception:
            pass

    def _update_recent(self, drawn: list):
        recent = drawn[-4:][::-1]
        self._recent_row.controls.clear()
        for i, n in enumerate(recent):
            self._recent_row.controls.append(
                number_ball(n, size=40 if i == 0 else 32,
                            color=COLOR_DRAWN if i == 0 else "#2a3a5a")
            )
        try:
            self._recent_row.update()
        except Exception:
            pass

    def _on_quine(self):
        self._show_quine_banner()

    def _show_quine_banner(self):
        self._quine_banner.visible = True
        try:
            self._quine_banner.update()
        except Exception:
            pass
