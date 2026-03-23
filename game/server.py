"""
Serveur de jeu — gère le tirage et diffuse les numéros aux clients via sockets.
Tourne dans un thread séparé pour ne pas bloquer l'UI Flet.
"""

import socket
import threading
import json
import random
from typing import List, Callable, Optional


class GameServer:
    def __init__(self, port: int = 9999):
        self.port = port
        self.drawn: List[int] = []
        self.remaining = list(range(1, 91))
        self.clients: List[socket.socket] = []
        self._lock = threading.Lock()
        self._server_socket: Optional[socket.socket] = None
        self._running = False
        self.on_draw: Optional[Callable[[int], None]] = None  # callback UI

    # ── Gestion du serveur ──────────────────────────────────────────────────

    def start(self):
        """Démarre le serveur dans un thread daemon."""
        self._running = True
        t = threading.Thread(target=self._accept_loop, daemon=True)
        t.start()

    def stop(self):
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass

    def _accept_loop(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(("0.0.0.0", self.port))
        self._server_socket.listen(20)
        self._server_socket.settimeout(1.0)
        while self._running:
            try:
                conn, _ = self._server_socket.accept()
                with self._lock:
                    self.clients.append(conn)
                    # Envoyer l'historique complet au nouveau client
                    self._send_to(conn, {"type": "history", "drawn": self.drawn})
                threading.Thread(target=self._client_loop, args=(conn,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception:
                break

    def _client_loop(self, conn: socket.socket):
        """Écoute les messages du client (ex : QUINE)."""
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
        except Exception:
            pass
        finally:
            with self._lock:
                if conn in self.clients:
                    self.clients.remove(conn)

    def _send_to(self, conn: socket.socket, msg: dict):
        try:
            conn.sendall((json.dumps(msg) + "\n").encode())
        except Exception:
            pass

    def _broadcast(self, msg: dict):
        with self._lock:
            dead = []
            for c in self.clients:
                try:
                    c.sendall((json.dumps(msg) + "\n").encode())
                except Exception:
                    dead.append(c)
            for c in dead:
                self.clients.remove(c)

    # ── Tirage ──────────────────────────────────────────────────────────────

    def draw_number(self) -> Optional[int]:
        """Tire un numéro unique. Retourne None si épuisé."""
        if not self.remaining:
            return None
        num = random.choice(self.remaining)
        self.remaining.remove(num)
        self.drawn.append(num)
        self._broadcast({"type": "draw", "number": num, "drawn": self.drawn})
        if self.on_draw:
            self.on_draw(num)
        return num

    def reset(self):
        self.drawn.clear()
        self.remaining = list(range(1, 91))
        self._broadcast({"type": "reset"})

    def get_local_ip(self) -> str:
        """Retourne l'IP locale de la machine."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


# ── Client de jeu ──────────────────────────────────────────────────────────

class GameClient:
    def __init__(self, host: str, port: int = 9999):
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None
        self._running = False
        self.on_draw: Optional[Callable[[int, List[int]], None]] = None
        self.on_history: Optional[Callable[[List[int]], None]] = None
        self.on_reset: Optional[Callable[[], None]] = None
        self.on_connect_error: Optional[Callable[[str], None]] = None

    def connect(self) -> bool:
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(5)
            self._sock.connect((self.host, self.port))
            self._sock.settimeout(None)
            self._running = True
            t = threading.Thread(target=self._recv_loop, daemon=True)
            t.start()
            return True
        except Exception as e:
            if self.on_connect_error:
                self.on_connect_error(str(e))
            return False

    def disconnect(self):
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass

    def _recv_loop(self):
        buf = ""
        try:
            while self._running:
                chunk = self._sock.recv(4096).decode()
                if not chunk:
                    break
                buf += chunk
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    if line.strip():
                        self._handle_message(json.loads(line))
        except Exception:
            pass

    def _handle_message(self, msg: dict):
        t = msg.get("type")
        if t == "draw" and self.on_draw:
            self.on_draw(msg["number"], msg["drawn"])
        elif t == "history" and self.on_history:
            self.on_history(msg["drawn"])
        elif t == "reset" and self.on_reset:
            self.on_reset()
