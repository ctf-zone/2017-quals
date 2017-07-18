#!/usr/bin/env python3
from curio import run, tcp_server
from elgamal import Elgamal, ElgamalException

MENU = b"""
-------------------------------
Options:
    [E]ncrypt message
    [D]ecrypt message
    [Q]uit

-> """


async def hello_message(client, elg):
    message = "Last vote: ({0} {1})\n".format(*elg.encrypted_flag)
    await client.sendall(message.encode())


async def encrypt_worker(client, elg):
    await client.sendall("Input your HEX message for encrypt: ".encode())
    data = await client.recv(2048)
    try:
        ctext = elg.encrypt(elg.encode_str(data.rstrip()))
    except Exception as e:
        await client.sendall("Error: {0}\n".format(e).encode())
    else:
        if ctext:
            await client.sendall("Your encrypted message:\n({0} {1})\n".format(ctext[0], ctext[1]).encode())
        else:
            await client.sendall("None - Message too long\n".encode())


async def decrypt_worker(client, elg):
    await client.sendall("Input your message for decrypt, format: C1 C2: ".encode())
    data = await client.recv(2048)
    try:
        ctext = data.decode().rstrip().split(" ")
        c1, c2 = int(ctext[0]), int(ctext[1])
        ptext = elg.decrypt(c1, c2)
    except IndexError:
        await client.sendall("Error: value error, format: C1 C2\n".encode())
    except ElgamalException:
        await client.sendall("None - can not decrypt another user's message\n".encode())
    except Exception as e:
        await client.sendall("Error: {0}\n".format(e).encode())
    else:
        if ptext:
            ptext = elg.decode_str(ptext)
            if ptext == elg.flag:
                await client.sendall("['ID': 13; 'VOTE': '{0}']".format("ctfzone{" + ptext + "}").encode())
            else:
                await client.sendall("Your decrypted message:\n{0}\n".format(ptext).encode())
        else:
            await client.sendall("None\n".encode())


async def handle_client(client, addr):
    print("Connection from", addr)
    elg = Elgamal(key_size=256)
    await hello_message(client, elg)
    while True:
        await client.sendall(MENU)
        data = await client.recv(256)
        if not data:
            break

        choise = data.strip().upper()
        if choise == b"E":
            await encrypt_worker(client, elg)
        elif choise == b"D":
            await decrypt_worker(client, elg)
        elif choise == b"Q":
            await client.sendall(b"Bye-Bye!\n")
            break
    print("Connection closed")


if __name__ == "__main__":
    run(tcp_server, "", 1337, handle_client)