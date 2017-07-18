#!/usr/bin/env python3
from mprsa import MPRSA
from re import findall
from gmpy2 import mpq
from deploy import FLAG

def convergents_win(cf):
    r, s, P, q = 0, 1, 1, 0
    for c in cf:
        r, s, P, q = P, q, c * P + r, c * q + s
        yield P, q


def contfrac_win(P, q):
    while q:
        n = P // q
        yield n
        q, P = P - q * n, q


def contfrac(P, q):
    while q:
        m = P // q
        yield m
        q, P = P - q * m, q


def win(e, n):
    limitD = int(pow(0.33 * mpq(n), 0.25))
    myM = 1000
    contf = list(convergents_win(contfrac_win(e, n)))
    for i in range(len(contf)):
        current = contf[i]
        if current[1] > limitD:
            break
        isC = pow(myM, e, n)
        myM2 = pow(isC, current[1], n)
        if myM == myM2:
            return int(current[0]), int(current[1])
    return 0, 0


with open("data.enc", "r") as f:
    c = int(f.read().rstrip())

with open("public.txt", "r") as f:
    pk = f.read()
    n = int(findall(r"n\s+\=\s+([0-9]+)", pk)[0])
    e = int(findall(r"e\s+\=\s+([0-9]+)", pk)[0])

d = win(e, n)[1]
if d != 0:
    mprsa = MPRSA()
    mprsa.import_keys((e, n), (d, n))
    ptext = mprsa.decryption(c)
    if FLAG == ptext:
        print("[+] : Got flag\n{0}".format(ptext.decode()))
    else:
        print("[-] Failed to find secret flag")
else:
    print("[-] Failed to find secret flag")
