# NetworkWriter.py
from Iwriter import IWriter
import requests
from Encryptor import Encryptor

class NetworkWriter(IWriter):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def send_data(self, data_hex: str, machine_name: str) -> None:
        # impose le format transport: ENC:<hex>
        cipher = data_hex
        if not cipher.startswith("ENC:"):
            cipher = "ENC:" + cipher

        payload = {"machine_name": machine_name, "data": cipher}
        r = requests.post(self.base_url + "/api/save_data", json=payload, timeout=5)
        r.raise_for_status()  # lève en cas d'erreur HTTP

# Exemple d’utilisation directe
if __name__ == "__main__":
    writer = NetworkWriter("http://127.0.0.1:5001")
    # ta clé “avi” (ou autre)
    data_hex = Encryptor.xor_encrypt_hex("hello world", "avi")
    writer.send_data(data_hex, "Machine01")
    print("ok")