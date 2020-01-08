from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import uuid
import base64

raw_key = "Z#!P5SZ67HOsU4!e"


def get_random_iv(str_size=16):
    return str(uuid.uuid4()).replace('-', '')[0:str_size]


def encrypt(content):
    def _pad(text):
        padding = AES.block_size - len(text) % AES.block_size
        return text + (padding * chr(padding)).encode('utf-8')

    content = _pad(content.encode('utf-8'))
    iv = get_random_iv(AES.block_size).encode()

    cipher = AES.new(raw_key.encode('utf-8'), AES.MODE_CBC, iv)
    data = cipher.encrypt(content)
    data = b2a_hex(data)
    data = base64.b64encode(iv + data)

    return data


def decrypt(content):
    def _unpad(s):
        padding = ord(s[len(s) - 1:])
        return s[:-1 * padding]

    content = base64.b64decode(content)
    iv = content[:AES.block_size]
    content = content[AES.block_size:]
    content = a2b_hex(content)

    cipher = AES.new(raw_key.encode('utf-8'), AES.MODE_CBC, iv)
    content = _unpad(cipher.decrypt(content))
    return content.decode()
#
#
# a = 'zpzhou!@#$%^&*()_+'
# b = encrypt(a)
# print(b)
# c = decrypt(b)
# print(c)
