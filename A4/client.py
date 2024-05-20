"""
File name: client.py
Created on Thu Mar 7 2024:
@author: <Benjamin Nolan>
Description: Client for sending and receiving messages over a socket
    UNE - COSC340 - A4

Usage: python client.py host port

Please run requirements.py to ensure the above library requirements are installed.

Modyifying from A2 to allow multiple client connections and keep server alive.

"""
import sys
import socket


# port 65432


class Client(object):

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.commands = ['LOGIN', 'COMPOSE', 'READ', 'EXIT']

    def send(self, data):
        data = data.encode('utf-8')
        self.sock.send(data)

    def recv(self):
        data = self.sock.recv(1024).decode('utf-8')
        print(f'Server: {data}')
        return data


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    client = Client(host, port)
    print('Available commands: LOGIN, COMPOSE, READ, EXIT')
    print('Please login.')
    while True:
        imp = input('Client: ')
        imp2 = imp.split()
        cmd = imp2[0]
        if len(imp2) > 1:
            val = imp2[1]
        if cmd == 'EXIT':
            data = 'EXIT'
            client.send(data)
            exit()
        if cmd == 'LOGIN':
            data = imp
            client.send(data)
            print('Available commands: COMPOSE, READ, EXIT')
        if cmd == 'COMPOSE':
            msg = imp2[2:]
            sep = ' '
            res = sep.join(msg)
            msg = res
            data = (cmd + ' ' + val + ' ' + msg)
            client.send(data)
        if cmd == 'READ':
            data = 'READ'
            client.send(data)
            print('Available commands: COMPOSE, READ, EXIT')
        if cmd not in client.commands:
            error_msg = 'Invalid command'
            client.send(error_msg)
            print('Invalid command.')
            exit()
        data = client.recv()
