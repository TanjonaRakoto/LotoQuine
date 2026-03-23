"""
Vue d'accueil — choix Admin (Hôte) ou Client (Joueur).
"""

import flet as ft
from views.components import (
    BG_DARK, BG_CARD, COLOR_ACCENT, COLOR_DRAWN, TEXT_PRIMARY, TEXT_MUTED,
    BORDER_COLOR
)


class HomeView:
    def __init__(self, page: ft.Page, navigate):
        self.page = page
        self.navigate = navigate

    def build(self) -> ft.Container:
        def go_admin(e):
            self.navigate("admin")

        # --- Client connection form ---
        host_field = ft.TextField(
            label="IP de l'hôte (ex: 192.168.1.10)",
            border_color=COLOR_ACCENT,
            focused_border_color=COLOR_DRAWN,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            bgcolor="#1a1a35",
            border_radius=10,
            text_size=14,
        )
        name_field = ft.TextField(
            label="Votre prénom",
            border_color=COLOR_ACCENT,
            focused_border_color=COLOR_DRAWN,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            bgcolor="#1a1a35",
            border_radius=10,
            text_size=14,
        )
        nb_cartons = ft.Dropdown(
            label="Nombre de cartons",
            value="1",
            options=[ft.dropdown.Option("1"), ft.dropdown.Option("2"), ft.dropdown.Option("3")],
            border_color=COLOR_ACCENT,
            focused_border_color=COLOR_DRAWN,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            bgcolor="#1a1a35",
            border_radius=10,
            text_size=14,
        )
        error_text = ft.Text("", color="#ff5252", size=12)

        def go_client(e):
            host = host_field.value.strip()
            name = name_field.value.strip()
            if not host:
                error_text.value = "⚠ Entrez l'adresse IP de l'hôte"
                error_text.update()
                return
            if not name:
                error_text.value = "⚠ Entrez votre prénom"
                error_text.update()
                return
            self.navigate("client",
                          host=host,
                          player_name=name,
                          nb_cartons=int(nb_cartons.value))

        # ── Layout ──
        return ft.Container(
            expand=True,
            bgcolor=BG_DARK,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(height=40),

                    # Logo / titre
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🎱", size=64),
                            ft.Text("LOTO QUINE",
                                    size=36, weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY, font_family="Oswald", style=ft.TextStyle(letter_spacing=6)),
                            ft.Text("Jeu en réseau local",
                                    size=14, color=TEXT_MUTED, font_family="Rajdhani"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        padding=ft.padding.symmetric(vertical=20),
                    ),

                    ft.Container(height=10),

                    # Bouton Admin
                    ft.Container(
                        width=320,
                        content=ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color=TEXT_PRIMARY),
                                ft.Text("MODE ADMIN  (Hôte)", color=TEXT_PRIMARY,
                                        font_family="Oswald", size=16, weight=ft.FontWeight.W_600),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                            style=ft.ButtonStyle(
                                bgcolor={ft.ControlState.DEFAULT: COLOR_ACCENT,
                                         ft.ControlState.HOVERED: "#9c6fff"},
                                shape=ft.RoundedRectangleBorder(radius=12),
                                padding=ft.padding.symmetric(vertical=18),
                                shadow_color=f"{COLOR_ACCENT}88",
                                elevation={ft.ControlState.PRESSED: 0, ft.ControlState.DEFAULT: 8},
                            ),
                            on_click=go_admin,
                            expand=True,
                        ),
                    ),

                    ft.Container(height=30),
                    ft.Divider(color=BORDER_COLOR, thickness=1),
                    ft.Container(height=10),

                    ft.Text("— REJOINDRE UNE PARTIE —",
                            size=12, color=TEXT_MUTED, font_family="Oswald", style=ft.TextStyle(letter_spacing=3)),

                    ft.Container(height=10),

                    # Formulaire client
                    ft.Container(
                        width=320,
                        padding=ft.padding.all(20),
                        border_radius=14,
                        bgcolor=BG_CARD,
                        border=ft.border.all(1, BORDER_COLOR),
                        content=ft.Column([
                            host_field,
                            ft.Container(height=8),
                            name_field,
                            ft.Container(height=8),
                            nb_cartons,
                            ft.Container(height=4),
                            error_text,
                            ft.Container(height=8),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.PLAY_ARROW, color=TEXT_PRIMARY),
                                    ft.Text("JOUER", color=TEXT_PRIMARY,
                                            font_family="Oswald", size=16,
                                            weight=ft.FontWeight.W_600),
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                style=ft.ButtonStyle(
                                    bgcolor={ft.ControlState.DEFAULT: "#00a896",
                                             ft.ControlState.HOVERED: "#00c4b0"},
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    padding=ft.padding.symmetric(vertical=16),
                                    elevation={ft.ControlState.PRESSED: 0, ft.ControlState.DEFAULT: 6},
                                ),
                                on_click=go_client,
                                expand=True,
                            ),
                        ], spacing=0),
                    ),

                    ft.Container(height=40),
                ],
            ),
        )
