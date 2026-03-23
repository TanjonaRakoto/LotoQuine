"""
Logique de génération des cartons de Loto Quine (format français).
- 3 lignes × 9 colonnes
- 5 numéros par ligne, 4 cases vides
- Col 1: 1-9, Col 2: 10-19, ..., Col 9: 80-90
- Numéros triés de haut en bas dans chaque colonne
"""

import random
from typing import List, Optional

# Plages de numéros par colonne (index 0-8)
COLUMN_RANGES = [
    (1, 9),    # col 0
    (10, 19),  # col 1
    (20, 29),  # col 2
    (30, 39),  # col 3
    (40, 49),  # col 4
    (50, 59),  # col 5
    (60, 69),  # col 6
    (70, 79),  # col 7
    (80, 90),  # col 8
]


def generate_carton() -> List[List[Optional[int]]]:
    """
    Génère un carton valide de 3 lignes × 9 colonnes.
    Chaque ligne contient exactement 5 numéros et 4 cases vides (None).
    Les numéros d'une colonne sont triés du haut vers le bas.
    Retourne une matrice [ligne][colonne].
    """
    # Étape 1 : choisir quelles colonnes ont des numéros sur chaque ligne
    # On doit avoir 5 numéros par ligne et couvrir toutes les colonnes au moins partiellement
    # Contrainte : chaque colonne peut avoir 1, 2 ou 3 numéros (max 3, car 3 lignes)
    # Total numéros = 15 (5×3). Répartis sur 9 colonnes => certaines en ont 2.

    column_counts = _distribute_column_counts()

    # Étape 2 : pour chaque colonne, tirer les numéros
    column_numbers: List[List[int]] = []
    for col, (low, high) in enumerate(COLUMN_RANGES):
        count = column_counts[col]
        nums = sorted(random.sample(range(low, high + 1), count))
        column_numbers.append(nums)

    # Étape 3 : construire la grille ligne par ligne
    # Pour chaque colonne, distribuer ses numéros sur les lignes
    grid: List[List[Optional[int]]] = [[None] * 9 for _ in range(3)]

    for col in range(9):
        nums = column_numbers[col]
        # Choisir aléatoirement quelles lignes reçoivent ces numéros
        rows = sorted(random.sample(range(3), len(nums)))
        for row, num in zip(rows, nums):
            grid[row][col] = num

    # Étape 4 : vérifier 5 numéros par ligne, sinon réessayer
    for row in range(3):
        count = sum(1 for v in grid[row] if v is not None)
        if count != 5:
            return generate_carton()  # retry

    return grid


def _distribute_column_counts() -> List[int]:
    """
    Distribue 15 numéros sur 9 colonnes :
    chaque colonne a 1, 2 ou 3 numéros.
    Contrainte : chaque ligne aura exactement 5 numéros.
    On génère plusieurs fois jusqu'à obtenir une distribution valide.
    """
    for _ in range(1000):
        counts = [random.randint(1, 3) for _ in range(9)]
        if sum(counts) == 15:
            return counts
    # Fallback déterministe : 6 colonnes à 2, 3 colonnes à 1 → total = 15
    base = [1, 2, 1, 2, 2, 1, 2, 2, 2]
    random.shuffle(base)
    return base


def carton_to_flat(carton: List[List[Optional[int]]]) -> List[Optional[int]]:
    """Aplatit le carton en liste de 27 éléments (row-major)."""
    return [cell for row in carton for cell in row]


def get_all_numbers(carton: List[List[Optional[int]]]) -> List[int]:
    """Retourne tous les numéros présents sur un carton."""
    return [cell for row in carton for cell in row if cell is not None]
