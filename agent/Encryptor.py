class Encryptor:
    @staticmethod
    def xor_encrypt(text: str, key: str, encoding: str = "utf-8") -> str:
        """
        מצפין טקסט ב-XOR עם מפתח שהוא מחרוזת.
        מחזיר טקסט מוצפן בפורמט הקס.
        """
        if not key:
            raise ValueError("המפתח לא יכול להיות ריק")
        data = text.encode(encoding)
        key_bytes = key.encode(encoding)

        cipher_bytes = bytes([
            b ^ key_bytes[i % len(key_bytes)]
            for i, b in enumerate(data)
        ])

        cipher_hex = cipher_bytes.hex()
        return cipher_hex

    @staticmethod
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

