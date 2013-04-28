import base64
import hashlib
import binascii
from Crypto.Cipher import AES
from decimal import Decimal as D

# factor internal representation / regular float
FACTOR_FLOAT = 100000000

# factor internal representation / gox (BTC)
FACTOR_GOX_BTC = 1

# factor internal representation / gox (JPY)
FACTOR_GOX_JPY = 100000

# factor internal representation / gox (USD)
FACTOR_GOX_USD = 1000


class goxnum(object):
    def __init__(self):
        self.value = None
        self.cur = None
        self.btc = 1E8
        self.usd = 1E5
        self.jpy = 1E3
                
    @property
    def i(self):
        return int(self.value)
    
    @i.setter
    def i(self,(value,currency)):
        self.cur = currency
        if self.cur == "BTC":
            value *= self.btc
        elif self.cur == "USD":
            value *= self.usd
        elif self.cur == "JPY":
            value *= self.jpy
        self.value = value
        
    
    def s(self,decimals,value=None):
        tempvalue = value or self.value
        if self.cur == "BTC":
            tempvalue /= self.btc
        elif self.cur == "USD":
            tempvalue /= self.usd
        elif self.cur == "JPY":
            tempvalue /= self.jpy
        return ("{{:,.{0}f}}".format(decimals).format(tempvalue))
    
    @property
    def f(self):
        tempvalue = self.value
        if self.cur == "BTC":
            tempvalue /= self.btc
        elif self.cur == "USD":
            tempvalue /= self.usd
        elif self.cur == "JPY":
            tempvalue /= self.jpy
        return float(tempvalue)
    
    @f.setter
    def f(self,value):
        self.value = value
        self.cur = None
    
    @property
    def d(self):
        tempvalue = self.value
        if self.cur == "BTC":
            tempvalue /= self.btc
        elif self.cur == "USD":
            tempvalue /= self.usd
        elif self.cur == "JPY":
            tempvalue /= self.jpy        
        
        return D(str(tempvalue))
    
    @d.setter
    def d(self,value):
        self.value = value
    
    #def refresh(self):
        

def gox2internal(value, currency):
    '''
    Converts the given value from gox format
    (see https://en.bitcoin.it/wiki/MtGox/API)
    into the application's internal format.
    '''
    if currency == "BTC":
        return value * FACTOR_GOX_BTC
    if currency == "JPY":
        return value * FACTOR_GOX_JPY
    else:
        return value * FACTOR_GOX_USD


def internal2gox(value, currency):
    '''
    Converts the specified value from internal format to gox format
    '''
    if currency == "BTC":
        return value / FACTOR_GOX_BTC
    if currency == "JPY":
        return value / FACTOR_GOX_JPY
    else:
        return value / FACTOR_GOX_USD


def float2str(value, decimals=8):
    '''
    Returns currency float formatted as a string.
    '''
    return ("{{:,.{0}f}}".format(decimals).format(value))


def internal2float(value):
    '''
    Converts internal value to float.
    '''
    return value / float(FACTOR_FLOAT)


def float2internal(value):
    '''
    Converts float to internal value.
    '''
    return int(value * FACTOR_FLOAT)


def multiply_internal(valueA, valueB):
    '''
    Multiplies two values in internal format.
    '''
    return valueA * valueB / FACTOR_FLOAT


def divide_internal(valueA, valueB):
    '''
    Divides two values in internal format (value a / value b).
    '''
    return valueA * FACTOR_FLOAT / valueB


def internal2str(value, decimals=8):
    '''
    Returns currency float formatted as a string.
    '''
    return float2str(internal2float(value), decimals)


def encrypt(secret, password):
    '''
    Encrypts the specified secret using the specified password.
    '''

    # pylint: disable=E1101
    hashed_pass = hashlib.sha512(password.encode("utf-8")).digest()
    crypt_key = hashed_pass[:32]
    crypt_ini = hashed_pass[-16:]
    aes = AES.new(crypt_key, AES.MODE_OFB, crypt_ini)

    # since the secret is a base64 string we can just just pad it with
    # spaces which can easily be stripped again after decryping
    secret += " " * (16 - len(secret) % 16)
    return base64.b64encode(aes.encrypt(secret)).decode("ascii")


def decrypt(secret, password):
    '''
    Decrypts the specified key using the specified password,
    throws exception in case of failure.
    '''

    if secret == "":
        raise Exception("secret cannot be empty")

    # pylint: disable=E1101
    hashed_pass = hashlib.sha512(password.encode("utf-8")).digest()
    crypt_key = hashed_pass[:32]
    crypt_ini = hashed_pass[-16:]
    aes = AES.new(crypt_key, AES.MODE_OFB, crypt_ini)
    encrypted_secret = base64.b64decode(secret.strip().encode("ascii"))
    secret = aes.decrypt(encrypted_secret).strip()

    # is it plain ascii? (if not this will raise exception)
    dummy = secret.decode("ascii")
    # can it be decoded? correct size afterwards?
    if len(base64.b64decode(secret)) != 64:
        raise Exception("decrypted secret has wrong size")

    return secret


def assert_valid_key(key):
    '''
    Asserts that the specified key is valid,
    throws an exception otherwise.
    '''

    if key == "":
        raise Exception("key cannot be empty")

    # key must be only hex digits and have the right size
    key = key.strip()
    hex_key = key.replace("-", "").encode("ascii")
    if len(binascii.unhexlify(hex_key)) != 16:
        raise Exception("key has wrong size")
