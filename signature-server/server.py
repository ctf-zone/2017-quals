from curio import run, tcp_server
from crypto import Curve, Point, multiply, normalize, invmod, rand
from os import environ
from hashlib import sha1
from secrets import randbelow, compare_digest

SECRET = int(environ.get('SECRET'), 10)

HELLO_MESSAGE = b'''
-------------------------------
Welcome to ECDSA service!
'''

MENU = b'''
-------------------------------
Options:
    [S]ign message
    [Q]uit
-> '''

def sign_message(msg, SECRET):
    E = Curve(0xffffffffffffffffffffffffffffffff7fffffff,
              0xffffffffffffffffffffffffffffffff7ffffffc,
              0x1c97befc54bd7a8b65acf89f81d4d4adc565fa45)

    G = Point(E,
              0x4a96b5688ef573284664698968c38bb913cbfc82,
              0x23a628553168947d59dcc912042351377ac5fb32)

    q = 0x100000000000000000001f4c8f927aed3ca752257

    h = int(sha1(msg).hexdigest(), 16)

    while True:
        k = rand(1, q)
        Q = normalize(multiply(G, k))
        r = Q.x % q
        if r != 0:
            break

    s = invmod(k, q) * (h + r * SECRET) % q
    return (r, s, k & 0x1f)

async def handle_client(client, addr):
    await client.sendall(HELLO_MESSAGE)

    while True:
        await client.sendall(MENU)

        data = await client.recv(10000)
        if not data:
            break

        choice = data.strip().upper()

        if choice == b'S':
            await client.sendall(b'Enter message to sign: ')
            msg = await client.recv(10000)
            if not msg:
                break
            await client.sendall(b'%d, %d, %d\n' % sign_message(msg.strip(), SECRET))
        elif choice == b'Q':
            await client.sendall(b"Bye-Bye!\n")
            break

if __name__ == '__main__':
    run(tcp_server, '', 1337, handle_client)
