from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

data = b'secret data'
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=1024,
)


key = get_random_bytes(16)
key2 = get_random_bytes(16)

cipher = AES.new(key, AES.MODE_EAX)
cipher2 = AES.new(key, AES.MODE_EAX)

ciphertext, tag = cipher.encrypt_and_digest(data)
ciphertext2, tag2 = cipher.encrypt_and_digest(data)

nonce = cipher.nonce

cipher = AES.new(key, AES.MODE_EAX, nonce)
data = cipher.decrypt_and_verify(ciphertext, tag)