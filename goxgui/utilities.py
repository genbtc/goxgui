import base64
import hashlib
import binascii
from Crypto.Cipher import AES
import sys
import os
import platform
from goxapi import float2int,int2float,int2str

# factor internal representation / regular float
FACTOR_FLOAT = 1E8

# factor internal representation / gox (BTC)
FACTOR_GOX_BTC = 1

# factor internal representation / gox (JPY)
FACTOR_GOX_JPY = 1E5

# factor internal representation / gox (USD)
FACTOR_GOX_USD = 1E3

# this symbol will be used as bitcoin symbol
BITCOIN_SYMBOL = unichr(3647)

def gox2str(value,currency,decimals=8):
    '''Converts straight from gox internal format to string'''
    if currency == 'USD':
        temp = value / 1E5
    elif currency == 'BTC':
        temp = value / 1E8
    elif currency == 'JPY' or currency == 'SEK':
        temp = value / 1E3
    else:
        temp = value / 1E5
    return ('{{:,.{0}f}}'.format(decimals).format(temp))

def gox2float(value,currency):
    return int2float(value,currency)

def float2gox(value,currency):
    return float2int(value,currency)
    
def gox2internal(value, currency):
    '''
    Converts the given value from gox format
    (see https://en.bitcoin.it/wiki/MtGox/API)
    into the application's internal format.
    '''
    if currency == 'USD':
        return value * FACTOR_GOX_USD
    elif currency == 'BTC':
        return value * FACTOR_GOX_BTC
    elif currency in 'JPY SEK':
        return value * FACTOR_GOX_JPY
    else:
        return value * FACTOR_GOX_USD

def internal2gox(value, currency):
    '''
    Converts the specified value from internal format to gox format
    '''
    if currency == 'USD':
        return value / FACTOR_GOX_USD
    elif currency == 'BTC':
        return value / FACTOR_GOX_BTC
    elif currency in 'JPY SEK':
        return value / FACTOR_GOX_JPY
    else:
        return value / FACTOR_GOX_USD

def float2str(value, decimals=8):
    '''
    Returns currency float formatted as a string.
    '''
    return ('{{:,.{0}f}}'.format(decimals).format(value))


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
    hashed_pass = hashlib.sha512(password.encode('utf-8')).digest()
    crypt_key = hashed_pass[:32]
    crypt_ini = hashed_pass[-16:]
    aes = AES.new(crypt_key, AES.MODE_OFB, crypt_ini)

    # since the secret is a base64 string we can just just pad it with
    # spaces which can easily be stripped again after decryping
    secret += ' ' * (16 - len(secret) % 16)
    return base64.b64encode(aes.encrypt(secret)).decode('ascii')


def decrypt(secret, password):
    '''
    Decrypts the specified key using the specified password,
    throws exception in case of failure.
    '''

    if secret == '':
        raise Exception('secret cannot be empty')

    # pylint: disable=E1101
    hashed_pass = hashlib.sha512(password.encode('utf-8')).digest()
    crypt_key = hashed_pass[:32]
    crypt_ini = hashed_pass[-16:]
    aes = AES.new(crypt_key, AES.MODE_OFB, crypt_ini)
    encrypted_secret = base64.b64decode(secret.strip().encode('ascii'))
    secret = aes.decrypt(encrypted_secret).strip()

    # is it plain ascii? (if not this will raise exception)
    dummy = secret.decode('ascii')
    # can it be decoded? correct size afterwards?
    if len(base64.b64decode(secret)) != 64:
        raise Exception('decrypted secret has wrong size')

    return secret


def assert_valid_key(key):
    '''
    Asserts that the specified key is valid,
    throws an exception otherwise.
    '''

    if key == '':
        raise Exception('key cannot be empty')

    # key must be only hex digits and have the right size
    key = key.strip()
    hex_key = key.replace('-', '').encode('ascii')
    if len(binascii.unhexlify(hex_key)) != 16:
        raise Exception('key has wrong size')


def assert_valid_secret(secret):
    '''
    Asserts that the specified secret is valid,
    throws an exception otherwise.
    '''
    result = decrypt(encrypt(secret, 'foo'), 'foo')
    if result != secret:
        raise Exception('encryption / decryption test failed.')


def resource_path(relative_path):
    '''
    Get absolute path to resource, works for dev and for PyInstaller.
    Taken from: http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile # @IgnorePep8
    '''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS2', os.getcwd())
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, relative_path)


def platform_is_mac():
    '''
    Returns true if the current platform is mac.
    '''
    return platform.system() == 'Darwin'
