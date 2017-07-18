from sys import argv
from sage.all import *
from socket import create_connection
from hashlib import sha1

sock = create_connection((argv[1], int(argv[2])))

# Skip hello and menu
sock.recv(100)

data = []

for i in xrange(50):
    # Skip menu
    sock.recv(100)
    sock.send('s\n')
    # Skip 'Enter message to sign: '
    sock.recv(1000)
    msg = '%d' % i
    sock.send(msg + '\n')
    d = sock.recv(1000)
    r, s, a = tuple(map(int, d.split(',')))
    h = int(sha1(msg).hexdigest(), 16)
    data.append((h, r, s, a))

q = 0x100000000000000000001f4c8f927aed3ca752257
l = 5
N = len(data)

def Babai_closest_vector(M, G, target):
    small = target
    for _ in xrange(1):
        for i in reversed(range(M.nrows())):
            c = ((small * G[i]) / (G[i] * G[i])).round()
            small -=  M[i] * c
    return target - small

u = []
t = []

for (h, r, s, a) in data:
    si = inverse_mod(Integer(s), q)
    li = inverse_mod(2 ** l, q)
    ti = li * (r * si) % q
    ui = li * (a - si * h) % q
    t.append(ti)
    u.append(ui)

d = QQ(q) / (2 ** (l + 1))

L = Matrix(QQ, N+1, N+1)

for i in xrange(N):
    L[i, i] = q

for i in xrange(N):
    L[N, i] = t[i]

L[N, N] = QQ(1) / (2 ** (l + 1))

M = L.LLL()
G = M.gram_schmidt()[0]

for i in xrange(N):
    u[i] += d
u.append(0)

target = vector(QQ, u)
res = Babai_closest_vector(M, G, target)
x = (res[-1] * (2 ** (l + 1))) % q

print 'ctfzone{%s}' % hex(x).decode('hex')

sock.close()
