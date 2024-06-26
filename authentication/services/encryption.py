"""
File used to define the encryption services
"""
from abc import ABC, abstractmethod

import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from jusoor_backend.settings import env


class EncryptionService(ABC):
    """
    Abstract class used to define any encryption service
    """

    @abstractmethod
    def __init__(self, key: str) -> None:
        super().__init__()

    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """
        Produce a ciphertext from the given plaintext
        """
        pass

    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        pass

    @abstractmethod
    def _pad(plain_text: str) -> str:
        """
        Pad the string to be encrypted to a multiple of block_size
        """
        pass

    @abstractmethod
    def _unpad(plain_text: str) -> str:
        """
        Remove the padding from the decrypted string
        """
        pass


class AES256EncryptionService(EncryptionService):
    """AES256-based encryption service"""

    def __init__(self, key: str = None) -> None:

        if key is None:
            key = env('ENCRYPTION_KEY')
        
        self.block_size = AES.block_size
        # getting a 256-bit digest from the given key
        self.key = hashlib.sha256(key.encode()).digest()
        

    def encrypt(self, plaintext: str) -> str:
        # NOTE: utf-8 encoding is needed for padding and plaintext beforehand to support multi-byte encoding
        # languages like arabic
        plaintext = self._pad(plaintext.encode('utf-8'))
        # random initialization vector of length block_size
        iv = Random.new().read(self.block_size)
        # creating the cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_text = cipher.encrypt(plaintext)
        
        # append text to random init vector ans udes base64 encoding
        return b64encode(iv + encrypted_text).decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        ciphertext = b64decode(ciphertext)
        # extract the initialization vector
        iv = ciphertext[:self.block_size]
        # create the cipher and decrypt the text
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[self.block_size:]).decode('utf-8')
        return self._unpad(plain_text=plaintext)

    def _pad(self, plain_text: str) -> str:
        """padding the plaintext to be a multiple of block_size"""
        number_of_bytes_to_pad = self.block_size - len(plain_text) % self.block_size
        # the character used for padding is the ascii 
        # representation of the number of bytes to pad (dynamic)
        # NOTE: this value can be zero, in this case the padding is not applied
        ascii_string = chr(number_of_bytes_to_pad).encode('utf-8')
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plainttext = plain_text + padding_str
        return padded_plainttext

    @staticmethod
    def _unpad(plain_text: str) -> str:
        """Remove the padding from the decrypted string to retrieve the correct format"""
        last_character = plain_text[len(plain_text) - 1:]
        return plain_text[: -ord(last_character)]




