#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from re import findall
from sys import argv
import urllib.request


RECV_SIZE = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((argv[1], int(argv[2])))

data = client_socket.recv(RECV_SIZE)
ctext1 = [int(i) for i in findall("\(([0-9]+)\s([0-9]+)\)", data.decode())[0]]
print("[+] : Got encrypted message")

# Show menu
client_socket.recv(RECV_SIZE)

client_socket.send(b"E\n")
client_socket.recv(RECV_SIZE)

client_socket.send(b"1\n")
print("[+] : Encrypting message \"1\"")

data = client_socket.recv(RECV_SIZE)
ctext2 = [int(i) for i in findall("\(([0-9]+)\s([0-9]+)\)", data.decode())[0]]
print("[+] : Got encrypted our message")

ctext3 = "{0} {1}".format(str(ctext1[0] * ctext2[0]), str(ctext1[1] * ctext2[1]))
client_socket.recv(RECV_SIZE)
client_socket.send(b"D\n")
print("[+] : Computing (ctext1[0] * ctext2[0]), (ctext1[1] * ctext2[1])")

client_socket.recv(RECV_SIZE)
client_socket.send("{0}\n".format(ctext3).encode())

data = client_socket.recv(RECV_SIZE)

data = findall("\['ID':\s[0-9]+;\s'VOTE':\s'(ctfzone\{.*\})'\]", data.decode())
print("[+] : Got flag: {0}".format(data[0]))

client_socket.close()
