import json
import curio
import inspect
import logging
from sanic import Sanic
from sanic.response import html, redirect

from arifmetics import Arifmetics
app = Sanic(__name__)


with open("index.html") as f:
    index_tmpl = f.read()

with open("devnull.html") as f:
    devnull_tmpl = f.read()


@app.route('/')
async def index(request):
    with open("index.html") as f:
        tmpl = f.read()
    # if request.args.get("success"):
    #     return html(tmpl.format(success=True))
    # else:
    return html(tmpl)


@app.route('/dev/null', methods=["POST"])
async def devnull(request):
    return html(devnull_tmpl)


@app.websocket('/feed')
async def feed(request, ws):
    arifm = Arifmetics("127.0.0.1", 25000)
    while True:
        try:
            data = await ws.recv()
            try:
                data = json.loads(data)
                method = getattr(arifm, data["method"], None)
                if inspect.iscoroutinefunction(method):
                    res = await method(*data.get("args", []))
                else:
                    res = method(*data.get("args", []))
                data = {
                    "result": res,
                    "method": data["method"],
                    "status": "ok"
                }
            except Exception as e:
                data = {
                    "status": "error",
                    "info": str(e)
                }
            await ws.send(json.dumps(data))
        except Exception as e:
            # logging.error(error)
            raise


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

