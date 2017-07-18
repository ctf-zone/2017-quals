#!/usr/bin/env python3
from elgamal_cipher import ElGamal
from random import randrange
import hashlib


class ElgamalException(Exception):
    pass


class Elgamal(object):
    def __init__(self, key_size):
        self.cipher = ElGamal()
        self.key_size = key_size
        self.cipher.generate_keys(self.key_size)

        self.secret = b"20cb6dc50637daf556517795a02c0bf5"
        m = hashlib.md5()
        m.update(self.secret)

        # Will be fc575129f3935d5b456ed55ef8173574
        self.flag = m.hexdigest()
        self.encrypted_flag = self.encrypt(self.encode_str(self.flag))

    def keygen(self, key_size):
        self.cipher.generate_keys(key_size=key_size)
        p = self.cipher.get_public_key()["p"]
        r = randrange(2, p)
        self.cipher.set_deterministic(r)

    def decrypt(self, c, k):
        m = self.cipher.decrypt(x=[c, k])
        if self.encrypted_flag[0] == c and self.encrypted_flag[1] == k:
            raise ElgamalException()
        return m

    def encrypt(self, m):
        if m.bit_length() > self.key_size:
            return None
        c, k = self.cipher.encrypt(m)
        return c, k

    @staticmethod
    def encode_str(text):
        return int(text, 16)

    @staticmethod
    def decode_str(text):
        return format(int(text), "x")

    def get_flag(self):
        return self.flag
