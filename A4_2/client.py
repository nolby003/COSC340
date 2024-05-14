"""
File name: client.py
Created: Thu Mar 7 2024
Redesigned: Tue May 14 2024
@author: <Benjamin Nolan>
Description: Client for sending and receiving messages over a socket
    UNE - COSC340 - A4

Usage: python client.py host port

Please run requirements.py to ensure the above library requirements are installed.


Adding secure messages
"""
import sys
import socket

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class Client(object):

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # Load the server's public key
        with open("public_key.pem", "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

        def encrypt_message(message, public_key):
            return public_key.encrypt(
                message.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

    def send(self, data):
        # data = data.encode('utf-8')
        data = client.encrypt_message(data, self.public_key)
        self.sock.send(data)

    def recv(self):
        data = self.sock.recv(1024).decode('utf-8')
        print(f'Server: {data}')
        return data


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    client = Client(host, port)
    # print('COSC340 - A2 - bnolan9 - client')
    print('Available commands: LOGIN, COMPOSE, READ, EXIT')
    print('Please login.')
    while True:
        imp = input('Client: ')
        # imp = imp.upper()
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
            # msg = input('Client: ')
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
        if cmd not in ['LOGIN', 'COMPOSE', 'READ', 'EXIT']:
            error_msg = 'Invalid command'
            client.send(error_msg)
            print('Invalid command.')
            exit()
        data = client.recv()