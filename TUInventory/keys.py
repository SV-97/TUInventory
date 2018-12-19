from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from pathlib import Path

def generate_key(path_public, path_private):
    """Generate new RSA key-pair and save it to the given paths
    Args:
        path_public: Path where the public-key should be stored
        path_private: Path where th private-key should be stored
    """
    key = RSA.generate(4096)
    with open(path_public, "wb") as f:
        f.write(key.publickey().exportKey())
    with open(path_private, "wb") as f:
        f.write(key.exportKey())


def read_keys(path_public, path_private):
    """Read a key-pair from the given paths and build ciphers from it
    Args:
        path_public: Path where the public-key is stored
        path_private: Path where the private-key is stored
    Returns:
        (PKCS1_OAEP-cipher from public-key, PKCS1_OAEP-decipher from private-key)
    """
    path_public = Path(path_public)
    path_private = Path(path_private)
    with open(path_public, "rb") as f:
        publickey = RSA.importKey(f.read())
    with open(path_private, "rb") as f:
        privatekey = RSA.importKey(f.read())
    cipher = PKCS1_OAEP.new(publickey)
    decipher = PKCS1_OAEP.new(privatekey)
    return cipher, decipher
