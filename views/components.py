"""
Composants UI partagés — carton interactif, boule de numéro, palette.
"""

import flet as ft
from typing import List, Optional, Callable
from game.carton import get_all_numbers

# ── Palette ──────────────────────────────────────────────────────────────────
BG_DARK       = "#0d0d1a"
BG_CARD       = "#13132b"
BG_CELL_EMPTY = "#1a1a35"
BG_CELL_NUM   = "#1e1e40"
COLOR_CHECKED = "#f5a623"   # orange doré = coché
COLOR_DRAWN   = "#00e5ff"   # cyan = tiré par admin
COLOR_ACCENT  = "#7c4dff"   # violet = accents
COLOR_WIN     = "#00e676"   # vert = quine
TEXT_PRIMARY  = "#ffffff"
TEXT_MUTED    = "#666699"
BORDER_COLOR  = "#2a2a5a"


def number_ball(num: int, size: int = 52, color: str = COLOR_ACCENT) -> ft.Container:
    """Boule de numéro stylisée."""
    return ft.Container(
        width=size, height=size,
        border_radius=size // 2,
        bgcolor=color,
        alignment=ft.Alignment(0, 0),
        shadow=ft.BoxShadow(blur_radius=12, color=f"{color}66"),
        content=ft.Text(
            str(num),
            size=size * 0.38,
            weight=ft.FontWeight.BOLD,
            color=TEXT_PRIMARY,
            font_family="Oswald",
        ),
    )


# ── Carton Widget ─────────────────────────────────────────────────────────────

class CartonWidget:
    """
    Carton de Loto Quine interactif.
    grid: List[List[Optional[int]]] — 3 lignes × 9 colonnes
    drawn_numbers: set des numéros tirés (mis à jour dynamiquement)
    """

    def __init__(self,
                 grid: List[List[Optional[int]]],
                 player_name: str = "",
                 carton_index: int = 0,
                 on_quine: Optional[Callable] = None):
        self.grid = grid
        self.player_name = player_name
        self.carton_index = carton_index
        self.on_quine = on_quine
        self.checked: set = set()   # numéros cochés manuellement
        self.drawn: set = set()     # numéros tirés par l'admin
        self._cells: dict = {}      # (row, col) -> ft.Container ref
        self._built = False

    def build(self) -> ft.Container:
        rows_ui = []
        for r in range(3):
            cells = []
            for c in range(9):
                val = self.grid[r][c]
                cell = self._make_cell(r, c, val)
                self._cells[(r, c)] = cell
                cells.append(cell)
            rows_ui.append(
                ft.Row(cells, spacing=3, alignment=ft.MainAxisAlignment.CENTER)
            )

        header = ft.Row([
            ft.Text(f"Carton {self.carton_index + 1}",
                    size=13, color=TEXT_MUTED, font_family="Oswald",
                    weight=ft.FontWeight.W_600),
        ], alignment=ft.MainAxisAlignment.CENTER)

        self._built = True
        return ft.Container(
            padding=ft.padding.all(10),
            border_radius=12,
            bgcolor=BG_CARD,
            border=ft.border.all(1, BORDER_COLOR),
            shadow=ft.BoxShadow(blur_radius=16, color="#00000066"),
            content=ft.Column([header, *rows_ui], spacing=3,
                               horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        )

    def _make_cell(self, row: int, col: int, val: Optional[int]) -> ft.Container:
        if val is None:
            return ft.Container(
                width=36, height=36,
                border_radius=4,
                bgcolor=BG_CELL_EMPTY,
            )

        is_checked = val in self.checked
        is_drawn   = val in self.drawn
        bg = COLOR_CHECKED if is_checked else (COLOR_DRAWN if is_drawn else BG_CELL_NUM)

        def on_click(e, v=val, r=row, cc=col):
            self._toggle(v, r, cc)

        return ft.Container(
            width=36, height=36,
            border_radius=4,
            bgcolor=bg,
            alignment=ft.Alignment(0, 0),
            border=ft.border.all(1, "#ffffff22"),
            on_click=on_click,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            content=ft.Text(
                str(val),
                size=12,
                weight=ft.FontWeight.BOLD,
                color=TEXT_PRIMARY,
                font_family="Oswald",
            ),
        )

    def _toggle(self, val: int, row: int, col: int):
        if val in self.checked:
            self.checked.discard(val)
        else:
            self.checked.add(val)
        self._refresh_cell(row, col, val)

    def _refresh_cell(self, row: int, col: int, val: int):
        cell = self._cells.get((row, col))
        if not cell:
            return
        is_checked = val in self.checked
        is_drawn   = val in self.drawn
        cell.bgcolor = COLOR_CHECKED if is_checked else (COLOR_DRAWN if is_drawn else BG_CELL_NUM)
        try:
            cell.update()
        except Exception:
            pass

    def update_drawn(self, drawn_set: set):
        """Met à jour les numéros tirés et rafraîchit les cellules."""
        self.drawn = drawn_set
        for r in range(3):
            for c in range(9):
                val = self.grid[r][c]
                if val is not None:
                    self._refresh_cell(r, c, val)

    def check_quine(self) -> bool:
        """Vérifie si une ligne est complète (quine)."""
        for row in self.grid:
            nums = [v for v in row if v is not None]
            if nums and all(v in self.drawn or v in self.checked for v in nums):
                return True
        return False

    def check_full_house(self) -> bool:
        """Vérifie si le carton est complet."""
        all_nums = get_all_numbers(self.grid)
        return all(v in self.drawn or v in self.checked for v in all_nums)


# ── Derniers numéros (bande) ──────────────────────────────────────────────────

def last_numbers_strip(numbers: List[int], max_show: int = 4) -> ft.Row:
    """Affiche les N derniers numéros tirés en ligne."""
    recent = numbers[-max_show:][::-1]
    balls = []
    for i, n in enumerate(recent):
        alpha = max(40, 255 - i * 50)
        color = f"#{alpha:02x}00e5ff"[1:] if i > 0 else COLOR_DRAWN
        balls.append(number_ball(n, size=42 if i == 0 else 34,
                                 color=COLOR_DRAWN if i == 0 else "#334466"))
    return ft.Row(balls, spacing=6, alignment=ft.MainAxisAlignment.CENTER)


# ── Grand affichage du numéro ─────────────────────────────────────────────────

def big_number_display(num: Optional[int]) -> ft.Container:
    label = str(num) if num is not None else "—"
    return ft.Container(
        width=120, height=120,
        border_radius=60,
        gradient=ft.RadialGradient(colors=[COLOR_ACCENT, "#3d00b3"]),
        alignment=ft.Alignment(0, 0),
        shadow=ft.BoxShadow(blur_radius=30, color=f"{COLOR_ACCENT}88"),
        content=ft.Text(label, size=52, weight=ft.FontWeight.BOLD,
                        color=TEXT_PRIMARY, font_family="Oswald"),
        animate=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
    )
