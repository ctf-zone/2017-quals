#!/usr/bin/python3
from Crypto.Util import number
from random import randrange
from cipher import Cipher


class ElGamal(Cipher):
    def __init__(self, keys=None, exponential_mode=False):
        self.exponential_mode = exponential_mode
        self.keys = keys

    def generate_keys(self, key_size=1024):
        p = None
        while p is None:
            try:
                p = number.getPrime(key_size)
            except Exception as err:
                print(err)

        alpha = randrange(1, p)
        d = randrange(2, p - 1)
        beta = pow(alpha, d, p)

        self.keys = {"pub": {
            "p": p,
            "alpha": alpha,
            "beta": beta},
            "priv": {
                "d": d
            }
        }

        return self.keys

    def set_deterministic(self, km=None):
        if km is None:
            pub = Cipher.get_public_key(self)
            i = randrange(2, pub["p"] - 1)
            km = pow(pub["beta"], i, pub["p"])
        Cipher.add_to_public_key(self, "km", km)
        return km

    def encrypt(self, m):
        assert self.__is_int(m)

        pub = Cipher.get_public_key(self)

        assert "p" in pub
        assert "alpha" in pub
        assert "beta" in pub

        p = pub["p"]
        alpha = pub["alpha"]
        beta = pub["beta"]
        km = pub["km"] if "km" in pub else None

        if self.exponential_mode:
            if m < 0:
                x = self.__modinv(pow(alpha, -m, p), p)
            else:
                x = pow(alpha, m, p)
        else:
            x = m

        if not km:
            i = randrange(2, p - 1)
            ke = pow(alpha, i, p)
            km = pow(beta, i, p)

            c = (x * km) % p
            return c, ke
        else:
            c = (x * km) % p
            return c

    def decrypt(self, x):
        pub = Cipher.get_public_key(self)
        priv = Cipher.get_private_key(self)

        assert "p" in pub
        assert "d" in priv

        p = pub["p"]
        d = priv["d"]
        if (type(x) == list or type(x) == tuple) and len(x) == 2:
            c = x[0]
            ke = x[1]
        else:
            c = x
        km = pub["km"] if "km" in pub else pow(ke, d, p)

        inv = self.__modinv(km, p)

        return c * inv % p

    def generate_lookup_table(self, a=0, b=10 ** 3):
        pub = Cipher.get_public_key(self)

        alpha = pub["alpha"]
        p = pub["p"]

        table = {}
        for i in xrange(a, b):
            c = pow(alpha, i, p)
            table[c] = i
        return table

    def __modinv(self, x, p):
        return pow(x, p - 2, p)

    def __is_int(self, x):
        try:
            int(x)
            return True
        except:
            return False
