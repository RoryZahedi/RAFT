from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048,)
public_key = private_key.public_key()
private_keyList = 4*[private_key]

print(5 * [private_key])