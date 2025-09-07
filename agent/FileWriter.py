from Iwriter import IWriter
import os
import datetime

class FileWriter(IWriter):
    def send_data(self, data: str, machine_name: str) -> None:
        """
        כותב את המידע לקובץ listening.txt
        כל שורה מכילה את התאריך, השעה והתוכן.
        """
        # תאריך ושעה נוכחיים
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.datetime.now().strftime("%H:%M:%S")

        filename = "DANIEL.txt"   # <-- שם קובץ קבוע

        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"[{date_str} {time_str}] {data}\n")
            f.flush()                # ריקון הבאפר (שמירת הנתונים מיידית)
            os.fsync(f.fileno())     # כפיית כתיבה לדיסק