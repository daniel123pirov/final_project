from Encryptor import Encryptor

cipher_hex = "0913050d194916191b0d1263121e080d1904" # ta longue chaîne
key = "avi"

try:
    decoded = Encryptor.xor_decrypt(cipher_hex, key)
    print("Texte décodé :", decoded)
except UnicodeDecodeError:
    cipher_bytes = bytes.fromhex(cipher_hex)
    key_bytes = key.encode("utf-8")

    plain_bytes = bytes([
        b ^ key_bytes[i % len(key_bytes)]
        for i, b in enumerate(cipher_bytes)
    ])
    print("Octets bruts :", plain_bytes)
    print("En hex      :", plain_bytes.hex())