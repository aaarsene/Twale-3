#!/usr/bin/python3

from socket import *
from threading import Thread
import sys

addr = ('192.168.0.255', 12345)

s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind(addr)

def recv():
    while True:
        msg = s.recvfrom(1024)
        if not msg: sys.exit(0)
        print(msg[0].decode())

Thread(target=recv).start()
while True:
    msg = input("> ")
    if not msg: break
    s.sendto(bytes(msg, "utf-8"), addr)

s.close()
