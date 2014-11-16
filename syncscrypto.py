from Crypto.PublicKey import RSA
import struct
import zlib
import base64
import binascii

class SyncsCrypto(object):
    def __init__(self):
        self.pub_file = "publickey.pub"
        self.private_file = "privatekey.pub"

    def rsa_genkey(self):
        #create key
        rsaKey = RSA.generate(2048)
        pubkey = rsaKey.publickey()
        f = open(self.pub_file, "wb")
        f.write(pubkey.exportKey())
        f.close()

        f = open(self.private_file, "wb")
        f.write(rsaKey.exportKey())
        f.close()


    def rsa_loadkey(self):
        #load key
        f = open(self.pub_file, "rb")
        rsa = RSA.importKey(f.read())
        f.close()

        f = open(self.private_file, "rb")
        rsa = RSA.importKey(f.read())
        f.close()
        
        return rsa


    def rsa_encrypt(self, buff, rsa):
        #encrypt
        buff = buff.encode("utf-8")
        return rsa.encrypt(buff, rsa)
    

    def rsa_decrypt(self, buff, rsa):
        #decrypt
        return rsa.decrypt(buff)


    def crc32_file(self, filename):
        try:
            fp = open(filename, "rb")
        except IOError:
            print ("Unable to open file " + filename)
            return None

        buf = fp.read()
        fp.close()

        #prev = binascii.crc32(buf) & 0xFFFFFFFF
        prev = struct.pack('!l', zlib.crc32(buf))

        return binascii.hexlify(prev)


    def rc4crypt(self, data, key):
        x = 0
        box = bytearray(range(256))
        for i in range(256):
            x = (x + box[i] + ord(key[i % len(key)])) % 256
            box[i], box[x] = box[x], box[i]
        x = 0
        y = 0
        out = []
        for char in data:
            x = (x + 1) % 256
            y = (y + box[x]) % 256
            box[x], box[y] = box[y], box[x]
            out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

        return ''.join(out)


    def base64encode(self, buff):
        return base64.b64encode(buff)#.encode("utf-8"))


    def base64decode(self, buff):
        return base64.b64decode(buff).decode("utf-8")

"""
pub_file = "publickey.pub"
private_file = "privatekey.pub"
#rsa_genkey(pub_file, private_file)
message = "hoank1@viettel.com.vn"
rsa = rsa_loadkey(pub_file, private_file)

dataencrypt = rsa_encrypt(message.encode("utf-8"), rsa)
print (rsa_decrypt(dataencrypt, rsa))

buff = "ngutyen khanh hoa"
dd = rc4crypt(buff, message)
dd = base64.b64encode(dd.encode("utf-8"))

print (dd)

print (rc4crypt(base64.b64decode(dd).decode("utf-8"), message))
"""