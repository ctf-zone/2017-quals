CFLAGS = -Wall -Werror

SRC = $(wildcard *.c)

pwn: $(SRC)
	gcc -o $@ $^ $(CFLAGS) -g

pwn-debug: $(SRC)
	gcc -o $@ $^ $(CFLAGS) -DDEBUG -g

pwn-strip: $(SRC)
	gcc -o $@ $^ $(CFLAGS) -s

.PHONY: pwn pwn-debug
