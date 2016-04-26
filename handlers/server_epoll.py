#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"
# coding:utf-8
import socket
from time import ctime
import select
import queue

HOST = ''
PORT = 21567
BUFSIZE = 1024
ADDR = ('127.0.0.1', PORT)

# 服务器端创建 socket
serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSock.bind(ADDR)
serverSock.listen(5)

timeout = 1000  # millisecond

message_queues = {}

# key state of socket io
READ_ONLY = (select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
READ_WRITE = (READ_ONLY | select.POLLOUT)

poller = select.poll()
poller.register(serverSock, READ_ONLY)

fd_to_sockets = {serverSock.fileno(): serverSock,}

while True:
    print("Waiting for next event ...")
    events = poller.poll(timeout)

    for fd, flag in events:
        s = fd_to_sockets[fd]
        if flag & (select.POLLIN | select.POLLPRI):
            if s is serverSock:
                server2client_Sock, addr = serverSock.accept()
                print("Connetion from ", addr)
                server2client_Sock.setblocking(0)

                fd_to_sockets[server2client_Sock.fileno()] = server2client_Sock
                poller.register(server2client_Sock, READ_ONLY)

                message_queues[server2client_Sock] = queue.Queue()

            else:
                server2client_Sock = s

                data = server2client_Sock.recv(BUFSIZE)

                if data:
                    print("Received data from ", server2client_Sock.getpeername())
                    data = '[%s] %s' % (ctime(), data)

                    message_queues[server2client_Sock].put(data)

                    # 将建立连接的 socket 放入到可以写的 socket 列表中
                    poller.modify(server2client_Sock, READ_WRITE)
                else:
                    poller.unregister(server2client_Sock)
                    server2client_Sock.close()
                    del message_queues[server2client_Sock]
        else:
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                print(" ", s.getpeername(), 'queue empty')
                poller.modify(s, READ_ONLY)
            else:
                print(" sending ", next_msg, " to ", s.getpeername())
                s.send(next_msg)

serverSock.close()
