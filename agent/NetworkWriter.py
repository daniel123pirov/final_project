from Iwriter import IWriter
import requests
from Encryptor import Encryptor
import logging



class NetworkWriter(IWriter):
    def __init__(self, base_url: str):
        self.base_url = base_url

    def send_data(self, data: str, machine_name: str) -> None:
        payload = {
            "machine_name": machine_name,
            "data": data
        }
        # try:
        response = requests.post(self.base_url + "/api/save_data", json=payload, timeout=5)
        return response.raise_for_status()

        # except requests.exceptions.RequestException as e:
        #     logging.error(f"Failed to send data: {e}")


# דוגמת שימוש
if __name__ == "__main__":
    writer = NetworkWriter("http://127.0.0.1:5000")
    encryp = Encryptor.xor_encrypt("hello world", "avi")
    print(writer.send_data(encryp ,"Machine01"))