import socket

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class Client(object):

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 65432))
        self.sock.settimeout(1)

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

    @staticmethod
    def encrypt_message(message, public_key_pem):
        public_key = serialization.load_pem_public_key(public_key_pem)
        # Encrypt message
        encrypted = public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted


    # def close(self):
    #     self.sock.close()
    #     self.sock = None


if __name__ == '__main__':
    client = Client()
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
            # print(data)
            client.send(data)
        if cmd == 'READ':
            data = 'READ'
            client.send(data)
        data = client.recv()
