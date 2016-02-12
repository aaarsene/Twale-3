#!/usr/bin/python3

from socket import *
from threading import Thread
import sys
import pickle

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

addr = ('127.0.0.1', 12345)

s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

class DialogConnection(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Connection", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.nickname = "John Doe"

        box = self.get_content_area()
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)
        grid.set_border_width(18)
        box.add(grid)

        self.labelNick = Gtk.Label()
        self.labelNick.set_markup('<span color="#888A85">Nickname</span>')
        self.labelNick.set_alignment(xalign=1, yalign=0.5)
        self.entryNick = Gtk.Entry()
        self.labelIP = Gtk.Label()
        self.labelIP.set_markup('<span color="#888A85">Broadcast Address</span>')
        self.labelIP.set_alignment(xalign=1, yalign=0.5)
        self.entryIP = Gtk.Entry()
        self.entryIP.set_max_length(15)

        grid.attach(self.labelNick, 0, 0, 1, 1)
        grid.attach(self.entryNick, 1, 0, 1, 1)
        grid.attach(self.labelIP, 0, 1, 1, 1)
        grid.attach(self.entryIP, 1, 1, 1, 1)

        self.show_all()

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Twale 3")
        self.set_default_size(480,360)
        self.paned = Gtk.Paned()
        self.add(self.paned)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.paned.add2(self.vbox)

        self.nickname = "Unknown"

        self.create_nicklist()
        self.create_receiver()
        self.vbox.pack_start(Gtk.HSeparator(), False, False, 0)
        self.create_sender()

        self.show_all()

        dialog = DialogConnection(self)
        dialog.run()

        self.nickname = dialog.entryNick.get_text()
        self.ownNick.set_label(self.nickname)
        global addr
        addr = (dialog.entryIP.get_text(), 12345)

        s.bind(addr)
        dialog.destroy()

        Thread(target=self.recv).start()

        self.send((self.nickname, "join"))

    def create_receiver(self):
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_hexpand(True)
        scrolledWindow.set_vexpand(True)
        self.vbox.pack_start(scrolledWindow, True, True, 0)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textbuffer = self.textview.get_buffer()
        scrolledWindow.add(self.textview)

    def create_sender(self):
        self.box = Gtk.Box(spacing=6)
        self.box.set_border_width(6)
        self.vbox.pack_start(self.box, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.connect("key-press-event", self.key_press)
        self.box.pack_start(self.entry, True, True, 0)

    def create_nicklist(self):
        self.nickPanel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.paned.add1(self.nickPanel)
        self.ownNick = Gtk.Button.new_with_label(self.nickname)
        self.ownNick.set_border_width(6)
        self.nickPanel.pack_end(self.ownNick, False, False, 0)
        self.nickPanel.pack_end(Gtk.HSeparator(), False, False, 0)

    def key_press(self, widget, event):
        if event.keyval == 65293 and self.entry.get_text():
            data = (self.nickname, "msg", self.entry.get_text())
            self.send(data)
            self.entry.set_text("")
            return True
        return False

    def send(self, data):
        msg = pickle.dumps(data)
        s.sendto(msg, addr)

    def recv(self):
        while True:
            try:
                msg = s.recvfrom(1024)
            except:
                sys.exit(0)
            if msg[1]:
                data = pickle.loads(msg[0])
                if (data[1] == "msg"):
                    end_iter = self.textbuffer.get_end_iter()
                    self.textbuffer.insert(end_iter, data[0] + " : " + data[2] + "\n")
                elif (data[1] == "join"):
                    end_iter = self.textbuffer.get_end_iter()
                    self.textbuffer.insert(end_iter, data[0] + " joined the chat" + "\n")
                elif (data[1] == "leave"):
                    end_iter = self.textbuffer.get_end_iter()
                    self.textbuffer.insert(end_iter, data[0] + " left the chat" + "\n")


    def change_nickname(self, nickname):
        if self.nickname != nickname:
            self.send(self.nickname + " is now known as " + nickname)
            self.nickname = nickname

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

win.send((win.nickname, "leave"))

# Faut pas demander pourquoi mais ces deux lignes aident à quitter
addr = ('127.0.0.1', 12345)
s.connect(addr)

s.shutdown(SHUT_RDWR)
s.close()
