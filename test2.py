from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend


filename = "public-keyX.pub"
pubKeyDict = {}


filenumberIndex = filename.find('X')

for i in range(0,5):
    fName = filename
    fName = fName.replace('X',str(i))
    print("Reading from",fName)
    with open(fName, 'rb') as file:
        pemlines = file.read()
    public_key = load_pem_public_key(pemlines)
    pubKeyDict[i] = public_key
    
ciphertexts = []
#Test
for pubKey in pubKeyDict.values():
    Message = "PLEASE WORK".encode()
    ciphertext = pubKey.encrypt(
    Message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
    )
    ciphertexts.append(ciphertext)


filename = "private-keyX.pem"
clientNum = 1

fName = 'private-key' + str(clientNum) + '.pem'
print("Reading from",fName)
with open(fName, 'rb') as file:
    pemlines = file.read()
privateKey = load_pem_private_key(pemlines, None, default_backend())

plaintext = privateKey.decrypt(
    ciphertexts[clientNum],
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
print("plaintext  = ",plaintext)
i+=1
