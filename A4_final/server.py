"""
File name: server.py
Created: Mar 7 2024
Modified: May 19 2024
@author: <Benjamin Nolan>
Description: Server for sending and receiving messages over a socket
    UNE - COSC340 - A4_2

library requirements:
    xlsxwrtiter
    openpyxl
    pandas

Usage: python server.py port secret_code

Please run requirements.py to ensure the above library requirements are installed.

Note: to md5 hash a password please use: python md5gen.py

"""
import sys
import socket

import cryptography.fernet
import xlsxwriter  # dependency
import openpyxl  # dependency
import pandas as pd
import os
import hashlib
from hashlib import md5
from cryptography.fernet import Fernet

messages_file = 'messages.xlsx'
sessions_file = 'sessions.xlsx'


class Server:

    def __init__(self, port, sKey, fKey):
        self.host = '127.0.0.1'
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", self.port))
        self.sock.listen()
        print(f'Server started on port: {port}')
        self.conn, self.addr = self.sock.accept()
        print(f'Client connected on: {self.addr}')
        self.sKey = sKey
        self.fKey = fKey

    """
    db of users and passwords (md5 hashed)
    """

    Users = {
        "bob": "81dc9bdb52d04dc20036dbd8313ed055",  # 1234
        "alice": "e10adc3949ba59abbe56e057f20f883e",  # 123456
    }

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
    Returns: md5 hash value
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
        print(f'Sending Raw message: {data}')

        # create MD5 hash head of message
        number = Server.get_skey()  # get number from key
        md5_hash = Server.generate_md5_hash(number)  # generate MD5 hash
        print('sent hash', format(md5_hash))

        # create fernet encyption
        full_message = (f'{md5_hash} {number} {data}').encode()  # create full message (sending hash + message)
        cipher_suite = Fernet(Server.get_fkey())
        full_message = cipher_suite.encrypt(full_message)
        print(f'Encrypted message sent: {full_message}')

        self.conn.send(full_message)

        # data = data.encode('utf-8')
        # self.conn.send(data)

    """
    Receive data from client
    No Parameters
    """

    def recv(self):

        message = self.conn.recv(1024)
        print(f'Received Encrypted message: {message}')

        # create fernet decryption
        try:
            cipher_suite = Fernet(Server.get_fkey())
            message = cipher_suite.decrypt(message).decode()
            print(f'Decrypted message: {message}')

        except Exception as e:
            return None

        # check md5 hash for matching and validation
        hash_value, _, message_body = message.partition(' ')
        print('received hash:', format(hash_value))  # 674f3c2c1a8a6f90461e8a66fb5550ba

        # if hash matches
        if Server.verify_md5_hash(message_body[:4], hash_value):
            print('Client: ', message_body[4:])
            messageStrip = message_body[4:].split(sep="'")
            messageStrip = messageStrip[1].split(sep=" ")
            return messageStrip
        else:
            print('Incorrect token received / No Message received.')
            return (f'Incorrect token received / No Message received.')

        # data = self.conn.recv(1024).decode('utf-8')
        # print(data)
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

    """
    Check correct auth coming through
    Create user session if validated
    Parameters: username and password
        Password is pre-md5 hashed 
    """

    @classmethod
    def login_user(self, un, pwd):

        data0 = []

        # check if sessions excel file exists
        isSfileExist = os.path.exists(sessions_file)
        if isSfileExist is False:
            df = pd.DataFrame(columns=['User'])
            with pd.ExcelWriter(sessions_file) as writer:
                df.to_excel(writer, sheet_name='Sessions', header=True, index=False)

        # check for correct auth
        try:
            if pwd in Server.Users[un]:
                checkAuth = True
            else:
                checkAuth = False

            if checkAuth:
                # create session
                values = [un]
                data0.append(values)
                df = pd.DataFrame(data0, columns=['User'])
                with pd.ExcelWriter(sessions_file) as writer:
                    df.to_excel(writer, sheet_name='Sessions', header=True, index=False)

                return un

        except KeyError as e:
            print("Invalid credentials.")
            return None

    """
    Get User
    No Parameters
    Return: usename
    """

    def get_user(self):

        df = pd.read_excel(sessions_file)
        for i in df.index:
            user = df['User'][i]
        return user

    """
    Get Messages - when client sends command LOGIN
    Parameter: data
    Returns: count of messages
    """

    @classmethod
    def get_messages(self, data):

        print('Get number of messages request')

        user = data[1]
        data = []

        # check if excel file exists
        isExist = os.path.exists(messages_file)

        # if exists, continue to check if the user exists
        if isExist:
            df = pd.read_excel(messages_file)
            if len(df) == 0:
                return '0'
            else:
                count = 0
                for i in df.index:
                    if user == df['To'][i]:
                        count += 1
                return str(count)

        # if the excel file does not exist, create it :)
        else:
            df = pd.DataFrame(columns=['From', 'To', 'Message'])
            with pd.ExcelWriter(messages_file) as writer:
                df.to_excel(writer, sheet_name='Messages', header=True, index=False)
            return '0'

    """
    Get Message - when client sends command READ
    Parameter: user
    Returns: messages or READ ERROR
    """

    def get_message(self, user):

        print('Read messages request')

        # check if excel file exists
        isExist = os.path.exists(messages_file)

        # if exists, continue
        if isExist:
            df = pd.read_excel(messages_file)
            # if no messages exist, sent client an error message
            if len(df) == 0:
                error_msg = 'READ ERROR'
                server.send(error_msg)
            else:
                for i in df.index:
                    if user == df['To'][i]:
                        # get 'from' user and message
                        from_user = df['From'][i]
                        msg = df['Message'][i]
                        # send to client
                        server.send(f'From {from_user}\n{msg}')

                        # remove message when read - temp comment
                        new_df = df[df['Message'] != msg]
                        with pd.ExcelWriter(messages_file) as writer:
                            new_df.to_excel(writer, sheet_name='Messages', header=True, index=False)
        # if the excel file does not exist, create it
        else:
            df = pd.DataFrame(columns=['From', 'To', 'Message'])
            with pd.ExcelWriter(messages_file) as writer:
                df.to_excel(writer, sheet_name='Messages', header=True, index=False)
                error_msg = 'READ ERROR'
                server.send(error_msg)

    """
    Compose a Message - after client sends command COMPOSE
    Parameter: data
    Returns: MESSAGE SENT or MESSAGE FAILED
    """

    def compose_message(self, to, message):

        print('New message request')

        df_data = []
        to_user = to
        from_user = server.get_user()
        message = message
        sep = ' '
        res = sep.join(message)
        message = res
        values = [from_user, to_user, message]
        df_data.append(values)

        # check if excel file exists
        isExist = os.path.exists(messages_file)
        if isExist:
            # want to extract all current data to preserve
            infile = pd.read_excel(messages_file)
            existing_data = []
            existing_data_df = pd.DataFrame(infile, columns=['From', 'To', 'Message'])

            new_data_df = pd.DataFrame(df_data, columns=['From', 'To', 'Message'])

            # merge existing data with new data before overwriting
            df = pd.concat([existing_data_df, new_data_df])

            with pd.ExcelWriter(messages_file) as writer:
                df.to_excel(writer, sheet_name='Messages', header=True, index=False)
                return 'MESSAGE SENT'
        # if the excel file does not exist, create it :)
        else:
            df = pd.DataFrame(columns=['From', 'To', 'Message'])
            with pd.ExcelWriter(messages_file) as writer:
                df.to_excel(writer, sheet_name='Messages', header=True, index=False)
            return 'MESSAGE FAILED'


if __name__ == '__main__':

    # define parameter arguments
    port = int(sys.argv[1])
    sKey = int(sys.argv[2])  # secret key passed as second parameter

    # set MD5 hash key
    Server.set_skey(sKey)

    # set Fernet key
    fKey = Fernet.generate_key().decode()
    Server.set_fkey(fKey)
    print(f'Fernet key is: {fKey}')

    # init server
    server = Server(port, sKey, fKey)

    while True:
        data = server.recv()  # listen for client-side receipt of data
        print(data)
        if data is None:
            cmd = None
        else:
            cmd = data[0]
            print(cmd)
            cmd = cmd.upper()
        if not data or cmd is None:
            break
        else:

            if cmd == 'EXIT':
                print('Client disconnected')

            if cmd == 'LOGIN':
                if len(data) > 3:
                    error_msg = (f'INVALID LOGIN')
                    server.send(error_msg)
                un = server.login_user(data[1], data[2])
                if un is None:
                    error_msg = (f'Invalid credentials.')
                    server.send(error_msg)
                else:
                    msgs = Server.get_messages(un)
                    server.send(msgs)

            if cmd == 'COMPOSE':
                msg = server.compose_message(data[1], data[2])
                server.send(msg)

            if cmd == 'READ':
                user = server.get_user()
                server.get_message(user)

            if cmd not in ['LOGIN', 'READ', 'COMPOSE', 'EXIT']:
                print('Invalid command')
                error_msg = (f'Invalid Command')
                server.send(error_msg)
