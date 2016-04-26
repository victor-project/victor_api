#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"
#coding:utf-8
import socket
from time import ctime
import select
import Queue

HOST = ''
PORT = 21567
BUFSIZE = 1024
ADDR = ('127.0.0.1', PORT)

# 服务器端创建 socket
serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSock.bind(ADDR)
serverSock.listen(5)

inputs = [serverSock]

outputs = []

timeout = 20

message_queues = {}

while inputs:
    print "doing select ..."

    readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)

    for s in readable:

        if s is serverSock:
            server2client_Sock, addr = serverSock.accept()
            print " Connection from "
            server2client_Sock.setblocking(0)
            inputs.append(server2client_Sock)

            message_queues[server2client_Sock] = Queue.Queue()

        else:
            server2client_Sock = s

            data = server2client_Sock.recv(BUFSIZE)

            # 如果数据接收完，则退出 recv, 进入到下一个连接
            if data:
                # server2client_Sock.send('[%s] %s' % (ctime(), data))
                print "Received data from ", server2client_Sock.getpeername()
                data = '[%s] %s' % (ctime(), data)

                message_queues[server2client_Sock].put(data)


                # 将建立连接的 socket 放入到可以写的 socket 列表中
                if server2client_Sock not in outputs:
                    outputs.append(server2client_Sock)
            else:
                if server2client_Sock in outputs:
                    outputs.remove(server2client_Sock)

                inputs.remove(server2client_Sock)

                server2client_Sock.close()

                del message_queues[server2client_Sock]

    if s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except Queue.Empty:
            print " " , s.getpeername() , 'queue empty'
            outputs.remove(s)
        else:
            print " sending " , next_msg , " to ", s.getpeername()
            s.send(next_msg)

serverSock.close()