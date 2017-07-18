# Start

```sh
SECRET=x python server.py
```

# Docker

## Build

```sh
docker build -t signature-server .
```

## Run

```sh
docker run -d \
    -p 1337:1337 \
    --restart=always \
    -e SECRET=509180828780457295905677127542596834069749904181 \
    --name signature-server \
    signature-server
```
