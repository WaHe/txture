from hashlib import sha256
from time import time
from base64 import b64encode

expiration_delay = 5400  # number of seconds it takes for a link to expire


def create_hash(phone_number, expiration_time, password, secret_key):
    m = sha256()
    m.update(phone_number)
    m.update(expiration_time)
    m.update(password)
    m.update(secret_key)
    return b64encode(m.digest())


def create_queries(phone_number, password, secret_key):
    expiration_time = str(int(time()) + expiration_delay)
    return expiration_time, create_hash(phone_number, expiration_time, password, secret_key)


def test_hash(phone_number, expiration_time, password, request_hash, secret_key):
    # Make sure this link hasn't expired
    try:
        exp_time = int(expiration_time)
        if exp_time < int(time()):
            return False
    except ValueError:
        return False
    # Make sure the hash is valid
    test = create_hash(phone_number, expiration_time, password, secret_key)
    if test != request_hash:
        return False
    return True
