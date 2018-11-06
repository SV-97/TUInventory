from Crypto.PublicKey import RSA

# 27.2 - S. 481

key = RSA.generate(4096)
with open("publickey", "wb") as f:
    f.write(key.publickey().exportKey())
with open("privatekey", "wb") as f:
    f.write(key.exportKey())

from Crypto.Cipher import PKCS1_OAEP

with open("publickey", "rb") as f:
    publickey = RSA.importKey(f.read())
with open("privatekey", "rb") as f:
    privatekey = RSA.importKey(f.read())


cipher = PKCS1_OAEP.new(publickey)
decipher = PKCS1_OAEP.new(privatekey)
text = "True"
ciphertext = cipher.encrypt(text.encode())
if decipher.decrypt(ciphertext) == text.encode():
    print("True")