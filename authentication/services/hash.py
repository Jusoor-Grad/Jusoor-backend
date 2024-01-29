import hashlib

def hash_string(string: str) -> str:
    """Hash the given string using the SHA256 algorithm"""
    return hashlib.sha256(string.encode()).hexdigest()