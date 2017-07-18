# Build

```sh
./gradlew build
./gradlew distTar
```

# Usage

## Generate keys

```sh
./gradlew run -PappArgs="['genkeys', '-outdir', './keys']"
```

## Encrypt data

```sh
./gradlew run -PappArgs="['encrypt', '-keysdir', './keys', 'ctfzone{4r3_y0u_r34dy_f0r_p057-qu4n7um_w0r1d?}']"
```

## Start server

```sh
./gradlew run -PappArgs="['start', '-keysdir', './keys']"
```

# Docker

## Build

Before this you need to build distributive and generate keys.

```sh
docker build -t pq-messenger .
```

## Run

```sh
docker run -d -p 1337:1337 --name pq-messenger pq-messenger
```
