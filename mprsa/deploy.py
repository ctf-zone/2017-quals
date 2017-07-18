#!/usr/bin/env python3
from mprsa import MPRSA

with open("flag.txt", "r") as f:
    FLAG = f.read().encode()

if __name__ == "__main__":
    mprsa = MPRSA()
    mprsa.key_gen(4096, 4)
    enc_flag = mprsa.encryption(FLAG)

    with open("data.enc", "w+") as f:
        f.write("{0}".format(enc_flag))

    with open("public.txt", "w+") as f:
        f.write("e = {0}\nn = {1}".format(*mprsa.public_key))
