#!/usr/bin/python3

from socket import *
from threading import Thread
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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

def send(msg):
    s.sendto(bytes(msg, "utf-8"), addr)

Thread(target=recv).start()

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Twale 3")

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.vbox.set_border_width(12)
        self.add(self.vbox)

        self.create_sender()

    def create_sender(self):
        self.box = Gtk.Box(spacing=6)
        self.vbox.pack_start(self.box, True, True, 0)

        self.entry = Gtk.Entry()
        self.box.pack_start(self.entry, True, True, 0)

        self.button = Gtk.Button(label="Envoyer")
        self.button.connect("clicked", self.on_button_clicked)
        self.box.pack_start(self.button, True, True, 0)

    def on_button_clicked(self, widget):
        if self.entry.get_text():
            send(self.entry.get_text())
            self.entry.set_text("")

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

s.close()
