"""
File name: client.py
Created on Thu Mar 7 2024:
@author: <Benjamin Nolan>
Description: Client for sending and receiving messages over a socket
    UNE - COSC340 - A2

Usage: python client.py host port
"""
import sys
import socket
# port 65432


class Client(object):

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.settimeout(1)
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
    print('COSC340 - A2 - bnolan9 - client')
    print('Available commands: LOGIN, COMPOSE, READ, EXIT')
    print('Please login.')
    while True:
        imp = input('Client: ')
        imp = imp.upper()
        imp2 = imp.split()
        cmd = imp2[0]
        if len(imp2) > 1:
            val = imp2[1]
        if cmd == 'EXIT':
            exit()
        if cmd == 'LOGIN':
            data = imp
            client.send(data)
        if cmd == 'COMPOSE':
            msg = input('Client: ')
            data = (cmd + ' ' + val + ' : ' + msg)
            client.send(data)
        if cmd == 'READ':
            data = 'READ'
            client.send(data)
        if cmd not in client.commands:
            print('Invalid command.')
            exit()
        data = client.recv()