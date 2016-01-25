#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"

from functools import partial
import select
import socket


class Server:
    def __init__(self):
        self._sock = socket.socket()
        self._poll = select.poll()
        self._handlers = {}
        self._fd_events = {}

    def start(self):
        sock = self._sock
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind(('', 8000))
        sock.listen(100)

        handlers = self._handlers
        poll = self._poll
        self.add_handler(sock.fileno(), self._accept, select.POLLIN)

        while True:
            poll_events = poll.poll(1)
            for fd, event in poll_events:
                handler = handlers.get(fd)
                if handler:
                    handler()

    def _accept(self):
        for i in range(100):
            try:
                conn, address = self._sock.accept()
            except OSError:
                break
            else:
                conn.setblocking(0)
                fd = conn.fileno()
                self.add_handler(fd, partial(self._read, conn), select.POLLIN)

    def _read(self, conn):
        fd = conn.fileno()
        self.remove_handler(fd)
        try:
            conn.recv(1024)
        except:
            conn.close()
            raise
        else:
            self.add_handler(fd, partial(self._write, conn), select.POLLOUT)

    def _write(self, conn):
        fd = conn.fileno()
        self.remove_handler(fd)
        try:
            conn.send(b'HTTP 1.0 200 OK\r\n\r\nhello world')
        finally:
            conn.close()

    def add_handler(self, fd, handler, event):
        self._handlers[fd] = handler
        self.register(fd, event)

    def remove_handler(self, fd):
        self._handlers.pop(fd, None)
        self.unregister(fd)

    def register(self, fd, event):
        if fd in self._fd_events:
            raise IOError("fd %s already registered" % fd)
        self._poll.register(fd, event)
        self._fd_events[fd] = event

    def unregister(self, fd):
        event = self._fd_events.pop(fd, None)
        if event is not None:
            self._poll.unregister(fd)


Server().start()