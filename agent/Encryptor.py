# Encryptor.py

class Encryptor:
    @staticmethod
    def xor_encrypt_hex(plain: str, key: str, encoding: str = "utf-8") -> str:
        if not key:
            raise ValueError("key is empty")
        data = plain.encode(encoding)
        k = key.encode(encoding)
        out = bytes([b ^ k[i % len(k)] for i, b in enumerate(data)])
        return out.hex()