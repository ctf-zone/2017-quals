import asyncio
from hashlib import md5
from random import choice, randint
from threading import Thread


SALT = b"ctfzone{87a55d7e34aae098be0316df6b8035e4}"


class Event_ts(asyncio.Event):
    def set(self):
        self._loop.call_soon_threadsafe(super().set)


def threaded(event, task, hash, table):
    event.set()
    table[hash] = eval(task)


class Arifmetics:
    _sock = None
    _last = None

    def __init__(self, server, port):
        self._server = server
        self._port = port
        self._table = {}

    async def reconnect(self):
        self._sock = await asyncio.open_connection(self._server, self._port)

    async def operations(self):
        if self._sock is None:
            await self.reconnect()
        self._sock[1].write(b"supported_operations\n")
        r = await self._sock[0].read(1024)
        return r.decode().strip()

    async def generate(self):
        if self._sock is None:
            await self.reconnect()
        operations = await self.operations()
        expr = "%s %s %s" % (
            randint(1, 2**8),
            choice(operations.split()),
            randint(1, 2**7)
        )
        self._sock[1].write(b"translate %s" % expr.encode())
        r = await self._sock[0].read(102400)
        text = r.decode()
        hash = md5(r + SALT).hexdigest()
        e = Event_ts()
        Thread(target=threaded, args=(e, expr, hash, self._table)).start()
        await e.wait()
        return {"text": text, "hash": hash}

    def check(self, digest, result):
        if digest in self._table and self._table[digest] == int(result):
            return "Valid"
        else:
            return "Wrong"

    def help(self):
        return "\n".join([m for m in dir(self) if not m.startswith("_")])


if __name__ == "__main__":
    c = Arifmetics("127.0.0.1", 25000)
    c._reconnect()
