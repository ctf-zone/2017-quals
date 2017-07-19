import re
from curio import run, tcp_server
from pyfiglet import Figlet


def supported_operations():
    return {"+", "-", "*", "//"}


def translate(s):
    return Figlet().renderText(s)


reg = re.compile(r"\d+\s?(%s)\s?\d+" % "|".join("\%s" % c for c in supported_operations()))


async def echo_client(client, addr):
    while True:
        data = await client.recv(100000)

        op = data.decode().split(" ", 1)[0].strip()
        if op == "translate":
            expr = data.decode().split(" ", 1)[-1].strip()
            if reg.match(expr):
                res = translate(expr)
            else:
                res = "ERROR Not supported expression"
        elif op == "supported_operations":
            res = " ".join(supported_operations())
        else:
            res = "ERROR no such method"
        await client.sendall((res + "\n").encode())


if __name__ == '__main__':
    run(tcp_server, '', 25000, echo_client)
