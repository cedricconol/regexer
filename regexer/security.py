import hashlib

def hasher(text):
    hash = hashlib.md5(text.encode())
    hashed = hash.hexdigest()
    
    return hashed