#!/usr/bin/env python

import socket
import time

host='127.0.0.1'
port=65432

accepted_commands=['LOGIN', 'COMPOSE', "READ", "EXIT"]
messages={}

class MS:

    @staticmethod
    def socket_init():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()

            while True:
                conn, addr = s.accept()
                # print(conn)
                # print(addr)
                try:
                    while True:
                        data = conn.recv(1024)  # receive data from client
                        if not data:
                            break
                        else:
                            data_dec = str(data.decode()).upper()  # decode data
                            x = data_dec.split()  # split to get arguments
                            print(len(data_dec))
                            vals = []
                            for v in x:
                                vals.append(x[v])
                            print(vals)
                            cmd = vals[0]  # command e.g LOGIN, COMPOSE, READ
#                            val = x[1].lower()  # value e.g. bob, alice
#                            val2 = x[2].lower()  # value e.g. composed message
                            while cmd != 'EXIT':  # while loop to keep program running until client sends EXIT
                                numArgs = len(x)  # get number of arguments

                                # check number of arguments to ensure we are receiving 1 or 2 arguments and not less or more
                                if numArgs < 1 or numArgs > 2:
                                    print("Not enough or too many arguments, must be 1 or 2")
                                    exit()

                                elif numArgs == 1 or numArgs == 2:
                                    for c in accepted_commands:
                                        if cmd == c:
                                            if cmd == 'LOGIN':
                                                if vals[1] not in messages.keys():
                                                    messages[vals[1]] = 0
                                                    response = str(messages[vals[1]]).encode()
                                            elif cmd == 'COMPOSE':
                                                if vals[1] not in messages.keys():
                                                    messages[vals[1]] = 1
                                                    response = str('MESSAGE SENT').encode()
                                conn.sendall(response)
                finally:
                    conn.close()
MS.socket_init()

