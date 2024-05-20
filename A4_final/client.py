"""
File name: client.py
Created: Mar 7 2024
Modified: May 19 2024
@author: <Benjamin Nolan>
Description: Client for sending and receiving messages over a socket
    UNE - COSC340 - A4_2

Usage: python client.py host port secret_code fernet_code

Note: please run server.py as normal initially so that the Fernet key generated can be obtained and passed
    as a parameter for client-side connection.

Please run requirements.py to ensure the above library requirements are installed.

Note: to md5 hash a password please use: python md5gen.py

"""
import sys
import socket
import hashlib
from hashlib import md5
from cryptography.fernet import Fernet


class Client(object):

    def __init__(self, host, port, sKey, fKey):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f'Connected to server on {host}:{port}')
        self.sKey = sKey
        self.fKey = fKey
        self.debug = 0  # change to 1 if you want to see some print statements for the security functions

    """
    Verify MD5 hash sent by client
    Parameters: secret key number and hash
    Returns: boolean
    """

    @staticmethod
    def verify_md5_hash(number, hash_value):
        return hashlib.md5(str(number).encode()).hexdigest() == hash_value

    """
    Generate MD5 hash from given number to be sent to Client
    Parameter: secret key number
    Returns: md5 hash
    """

    @staticmethod
    def generate_md5_hash(number):
        return hashlib.md5(str(number).encode()).hexdigest()

    """
     Send Data to client
     Parameter: data
     """

    def send(self, data):

        data = data.encode('utf-8')
        if self.debug == 1:
            print(f'Sending Raw message: {data}')

        # create MD5 hash head of message
        number = Client.get_skey()  # get number from key
        md5_hash = Client.generate_md5_hash(number)  # generate MD5 hash
        if self.debug == 1:
            print('sent hash', format(md5_hash))  # 674f3c2c1a8a6f90461e8a66fb5550ba

        # create fernet encyption
        full_message = (f'{md5_hash} {number} {data}').encode()  # create full message (sending hash + message)
        cipher_suite = Fernet(Client.get_fkey())
        full_message = cipher_suite.encrypt(full_message)
        if self.debug == 1:
            print(f'Encrypted message sent: {full_message}')

        self.sock.sendall(full_message)  # full message sent to server in bytes

        # data = data.encode('utf-8')
        # self.sock.send(data)

    """
    Receive data from client
    No Parameters
    """

    def recv(self):

        message = self.sock.recv(1024)
        if self.debug == 1:
            print(f'Received Encrypted message: {message}')

        # create fernet decryption
        cipher_suite = Fernet(Client.get_fkey())
        message = cipher_suite.decrypt(message).decode()
        if self.debug == 1:
            print(f'Decrypted message: {message}')

        # check md5 hash for matching and validation
        hash_value, _, message_body = message.partition(' ')
        if self.debug == 1:
            print('received hash:', format(hash_value))
            print('message body', format(message_body))

        # if hash matches
        if Client.verify_md5_hash(message_body[:4], hash_value):
            messageStrip = message_body[4:].split("'")
            if self.debug == 1:
                print(messageStrip[1][:4])  # From
            if messageStrip[1][:4] == 'From':
                messageStrip = messageStrip[1].split(sep="\\n")
                print(messageStrip)
                print(f'{messageStrip[0]}\n{messageStrip[1]}')
            elif messageStrip[1] == 'Invalid credentials.':
                print(f'Server: {messageStrip[1]}')
            elif messageStrip[1] == 'Invalid Command':
                print(f'Server: {messageStrip[1]}')
            elif int(messageStrip[1]) >= 0:
                print(f'Server: {messageStrip[1]}')
            # print(f'Server: {messageStrip}')

            return (messageStrip)
        else:
            print('Incorrect token received / No Message received.')
            return (f'Incorrect token received / No Message received.')

        # data = self.sock.recv(1024).decode('utf-8')
        # print(f'Server: {data}')
        # return data

    # setters and getters for shared and fernet keys
    @classmethod
    def set_skey(self, sKey):
        self.sKey = sKey

    @classmethod
    def get_skey(self):
        return self.sKey

    @classmethod
    def get_fkey(self):
        return self.fKey

    @classmethod
    def set_fkey(self, fkey):
        self.fKey = fkey


if __name__ == '__main__':

    # define parameter arguments
    host = sys.argv[1]
    port = int(sys.argv[2])
    sKey = int(sys.argv[3])
    fKey = sys.argv[4]

    # init client
    client = Client(host, port, sKey, fKey)

    # set MD5 hash key
    client.set_skey(sKey)

    # set Fernet key
    client.set_fkey(fKey)

    while True:

        # promt user to enter a command
        cmd = input('Enter command (LOGIN, READ, COMPOSE, EXIT): ')
        cmd = cmd.upper()

        if cmd == 'EXIT':
            msg = f'EXIT'
            client.send(msg)
            print('Disconnected from server')
            exit()

        if cmd == 'LOGIN':
            un = input('Enter username: ')
            pw = input('Enter password: ')
            pw = client.generate_md5_hash(pw)
            msg = (f'LOGIN {un} {pw}')
            client.send(msg)

        if cmd == 'COMPOSE':
            to = input('Message to: ')
            msg = input('Message: ')
            data = (f'COMPOSE {to} {msg}')
            client.send(data)

        if cmd == 'READ':
            msg = (f'READ')
            client.send(msg)

        if cmd not in ['LOGIN', 'READ', 'COMPOSE', 'EXIT']:
            print('Invalid command')
            data = (f'Invalid command')
            client.send(data)
        data = client.recv()  # listen for server-side receipt of data
