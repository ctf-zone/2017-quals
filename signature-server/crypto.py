from secrets import randbelow

def rand(a, b):
    while True:
        x = randbelow(b)
        if x > a:
            break
    return x

def xgcd(a, b):
    if a == 0: return 0, 1, b
    if b == 0: return 1, 0, a

    px, ppx = 0, 1
    py, ppy = 1, 0

    while b:
        q = a // b
        a, b = b, a % b
        x = ppx - q * px
        y = ppy - q * py
        ppx, px = px, x
        ppy, py = py, y

    return ppx, ppy, a

def invmod(a, n):
    if n < 2:
        raise ValueError("modulus must be greater than 1")

    x, y, g = xgcd(a, n)

    if g != 1:
        raise ValueError("no invmod for given @a and @n")
    else:
        return x % n

class Curve:
    def __init__(self, N, a, b):
        self.N = N
        self.a = a
        self.b = b

    def __str__(self):
        return 'Elliptic curve: y^2 = x^3 + {a}*x + {b} over Finite Field of size {N}'.format(a=self.a, b=self.b, N=self.N)

    def discriminant(self):
        return (4 * (self.a ** 3) + 27 * (self.b ** 2)) % self.N

class Point:
    def __init__(self, E, x, y, z=1):
        self.E = E
        self.x = x
        self.y = y
        self.z = z

    @property
    def N(self):
        return self.E.N

    @property
    def a(self):
        return self.E.a

    def __str__(self):
        return 'Point: ({x}, {y}, {z})'.format(x=self.x, y=self.y, z=self.z)

def is_on_curve(E, P):
    Q = normalize(P)
    return (Q.y ** 2 - Q.x ** 3 - E.a * Q.x - E.b) % E.N == 0

def normalize(P):
    zi = invmod(P.z, P.N)
    return Point(P.E, (zi * P.x) % P.N, (zi * P.y) % P.N, 1)

def double(P):
    if P.y == 0:
        return Point(P.E, 0, 1, 0)
    w = (P.a * (P.z ** 2) + 3 * (P.x ** 2)) % P.N
    s = (P.y * P.z) % P.N
    b = (P.x * P.y * s) % P.N
    h = ((w ** 2) - 8 * b) % P.N
    x = (2 * h * s) % P.N
    y = (w * (4 * b - h) - 8 * (P.y ** 2) * (s ** 2)) % P.N
    z = (8 * (s ** 3)) % P.N
    return Point(P.E, x, y, z)

def add(P, Q):
    u1 = (Q.y * P.z) % P.N
    u2 = (P.y * Q.z) % P.N
    v1 = (Q.x * P.z) % P.N
    v2 = (P.x * Q.z) % P.N
    if (v1 == v2):
        if (u1 != u2):
            return Point(P.E, 0, 1, 0)
        else:
            return double(P)
    u = (u1 - u2) % P.N
    v = (v1 - v2) % P.N
    w = (P.z * Q.z) % P.N
    a = ((u ** 2) * w - (v ** 3) - 2 * (v ** 2) * v2) % P.N
    x = (v * a) % P.N
    y = (u * ((v ** 2) * v2 - a) - (v ** 3) * u2) % P.N
    z = ((v ** 3) * w) % P.N
    return Point(P.E, x, y, z)

def multiply(P, d):
    X1 = P
    X2 = double(P)
    for b in bin(d)[3:]:
        if b == '0':
            X2 = add(X1, X2)
            X1 = double(X1)
        else:
            X1 = add(X1, X2)
            X2 = double(X2)
    return X1
