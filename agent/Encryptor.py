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
        print(cipher_hex)  # הדפסה לפי הבקשה
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

if __name__ == "__main__":
    # ta chaîne hexadécimale
    cipher_hex = "021b0d4115021b0d4115021b0d4100496b0c5608411f49125649411c49465608411f49415608410349150e561b411f4900560b00150212060802134912560c41564911561041154909560841040c566309131b3a3428223d3a31372a242b3223372a2a253920352c3c2d2b2035223226282233346b7c3223372a2a253920352c3c2d2b2035223226282233343a3428223d3a31372a242b0913050d19493a050108101d3e04343a050108101d3e04342c37490f1f1a091b081b1718b6efbec3a1f2b6e4b6e0b6d4bef1a1f16b6b"

    # ta clé (change si nécessaire)
    key = "avi"

    # ⚠️ appel via la classe Encryptor
    decoded = Encryptor.xor_decrypt(cipher_hex, key)
    print("Texte décodé :")
    print(decoded)