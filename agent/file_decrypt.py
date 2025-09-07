import sys
import os

def xor_decrypt(data: bytes, key: str) -> bytes:
    """
    פענוח XOR על bytes
    מחזיר את הבייטים המפוענחים
    """
    key_bytes = key.encode()
    decrypted_bytes = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)])
    return decrypted_bytes

def main():
    if len(sys.argv) != 3:
        print(f"שימוש: python {sys.argv[0]} <נתיב_קובץ_מוצפן> <מפתח_XOR>")
        sys.exit(1)

    file_path = sys.argv[1]
    key = sys.argv[2]

    if not os.path.isfile(file_path):
        print("שגיאה: הקובץ לא קיים")
        sys.exit(1)

    # קריאת הקובץ המוצפן
    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    # פענוח
    decrypted_bytes = xor_decrypt(encrypted_data, key)

    # שמירה לקובץ חדש
    output_file = os.path.splitext(file_path)[0] + "_decrypted.txt"
    with open(output_file, "wb") as f:
        f.write(decrypted_bytes)

    print(f"הפענוח הסתיים. הפלט נשמר ב-{output_file}")
    print("פתח את הקובץ בעורך שתומך ב-UTF-8 כדי לראות את התוכן.")

if __name__ == "__main__":
    main()
