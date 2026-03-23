# 🎱 Loto Quine Local

Application de Loto Quine (Bingo français) fonctionnant en réseau local Wi-Fi.
Développée en Python avec le framework **Flet**.

---

## 📁 Structure du projet

```
loto_quine/
├── main.py                  # Point d'entrée Flet
├── requirements.txt
├── game/
│   ├── __init__.py
│   ├── carton.py            # Génération des cartons (format français 3×9)
│   └── server.py            # GameServer (Admin) + GameClient (Joueur)
└── views/
    ├── __init__.py
    ├── components.py         # Widgets réutilisables (CartonWidget, boules…)
    ├── home_view.py          # Vue d'accueil
    ├── admin_view.py         # Vue Admin (tirage)
    └── client_view.py        # Vue Client (jeu)
```

---

## 🚀 Installation & Lancement

### Prérequis
- Python 3.10+ (testé 3.12)
- `pip install flet`

### Lancer l'application
```bash
cd loto_quine
pip install -r requirements.txt
python main.py
```

---

## 🎮 Utilisation

### Mode Admin (Hôte)
1. Lancer `python main.py` sur la machine hôte.
2. Appuyer sur **MODE ADMIN**.
3. L'IP locale s'affiche à l'écran (ex: `192.168.1.10:9999`).
4. Communiquer cette IP aux joueurs.
5. Appuyer sur **TIRER UN NUMÉRO** pour chaque tirage.

### Mode Client (Joueur)
1. Lancer `python main.py` sur son appareil (même Wi-Fi).
2. Saisir l'IP de l'hôte, son prénom, et le nombre de cartons (1–3).
3. Appuyer sur **JOUER**.
4. Cocher les numéros sur ses cartons en cliquant dessus.
5. Appuyer sur **GAGNER / QUINE** dès qu'une ligne est complète.

---

## 🃏 Format des cartons

| Règle | Détail |
|-------|--------|
| Format | 3 lignes × 9 colonnes |
| Numéros par ligne | 5 numéros (4 cases vides) |
| Col 1 | 1–9 |
| Col 2 | 10–19 |
| … | … |
| Col 9 | 80–90 |
| Tri | De haut en bas dans chaque colonne |

---

## 📱 Export APK (Android)

```bash
pip install flet
flet build apk
```

Voir la [documentation Flet](https://flet.dev/docs/publish/android) pour les prérequis Android SDK.

---

## 🔧 Architecture réseau

- **Protocole** : TCP Sockets Python (port 9999 par défaut)
- **Format** : JSON newline-delimited
- **Messages** :
  - `{"type": "draw", "number": N, "drawn": [...]}` — nouveau tirage
  - `{"type": "history", "drawn": [...]}` — envoyé au nouveau client
  - `{"type": "reset"}` — réinitialisation de la partie

---

## 🎨 Palette UI

| Rôle | Couleur |
|------|---------|
| Fond | `#0d0d1a` (noir profond) |
| Accent | `#7c4dff` (violet) |
| Tiré | `#00e5ff` (cyan) |
| Coché | `#f5a623` (orange doré) |
| Quine | `#00e676` (vert) |
