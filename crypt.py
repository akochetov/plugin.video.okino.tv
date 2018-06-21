import base64

import binascii
import json

from pyaes.aes import AESModeOfOperationCBC
from pyaes.blockfeeder import Encrypter

partner_id = 5058
domain_id = 521684
video_token = 'ba5b045f465a0629'
e = '7d9e4a87b9aab04009aafc33445cfe225d0ab95d0215aa02ee7a4a2741bf5431'
d = '8156109e46b295466542f3587f35f0fe'
n = '583db51205db81b2050b54eb8d222bae'
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'

def get_chiper(partner_id,domain_id,video_token,e,n,d,agent):
    _mw_adb = False

    def pad(s):
        block_size = 16
        return s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)


    def unpad(s):
        return s[0:-ord(s[-1])]


    class EncryptedData:
        def __init__(self):
            pass

        def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))


    t = EncryptedData()
    t.a = partner_id
    t.b = domain_id
    t.c = _mw_adb
    t.d = d
    t.e = video_token
    t.f = agent

    r = t.toJSON()

    key = e
    iv = n
    line = ""

    encr = AESModeOfOperationCBC(binascii.a2b_hex(key), binascii.a2b_hex(iv))
    encrypter = Encrypter(encr)
    ciphertext = bytes()
    ciphertext += encrypter.feed(r)
    ciphertext += encrypter.feed()

    return base64.standard_b64encode(ciphertext)

print ("Cipher1 (CBC): ")
print (get_chiper(partner_id,domain_id,video_token,e,n,d,agent))

