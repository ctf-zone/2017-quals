FROM openjdk:8
ADD ./build/distributions/crypto-400.tar /usr/src/
COPY ./keys /usr/src/crypto-400/keys

WORKDIR /usr/src/crypto-400
CMD ["./bin/crypto-400", "start", "-keysdir", "./keys"]

