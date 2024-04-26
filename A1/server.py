"""
File name: server.py
Created on Thu Mar 7 2024:
@author: <Benjamin Nolan>
Description: Server for sending and receiving messages over a socket
    UNE - COSC340 - A2

library requirements:
xlsxwrtiter
openpyxl

Usage: python server.py port

"""
import sys
import socket
import xlsxwriter  # dependency
import openpyxl  # dependency
import pandas as pd
import os

messages_file = 'messages.xlsx'
sessions_file = 'sessions.xlsx'


class Server:

    def __init__(self, port):
        self.host = '127.0.0.1'
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.conn, self.addr = self.sock.accept()
        # self.conn.settimeout(1)
        # self.conn.setblocking(True)
        self.messages = {}
        self.numMessages = {}
        self.sessions = []
        self.commands = ['LOGIN', 'COMPOSE', 'READ', 'EXIT']

    """
    Send Data to client
    Parameter: data
    """
    def send(self, data):
        data = data.encode('utf-8')
        self.conn.send(data)

    """
    Receive data from client
    No Parameters
    """
    def recv(self):
        data = self.conn.recv(1024).decode('utf-8')
        return data

    """
    Create user session
    Parameter: data
    """
    def login_user(self, data):

        data0 = []

        # check if excel file exists
        isExist = os.path.exists(sessions_file)

        # if exists, continue to check if the user exists
        if isExist:
            values = [data[1]]
            data0.append(values)
            df = pd.DataFrame(data0, columns=['User'])
            with pd.ExcelWriter(sessions_file) as writer:
                df.to_excel(writer, sheet_name='Sessions', header=True, index=False)
        else:
            df = pd.DataFrame(columns=['User'])
            with pd.ExcelWriter(sessions_file) as writer:
                df.to_excel(writer, sheet_name='Sessions', header=True, index=False)

    """
    Get User
    No Parameters
    """
    def get_user(self):

        #user = self.sessions[0]

        df = pd.read_excel(sessions_file)
        for i in df.index:
            user = df['User'][i]
        return user

    """
    Get Messages - when client sends command LOGIN
    Parameter: data
    """
    def get_messages(self, data):

        print('Get number of messages request')
        # -------------------------
        # non-binary-storage method
        # -------------------------
        # msgs = self.numMessages.get(data[1])
        # if msgs is None:
        #     output = self.numMessages[data[1]] = '0'
        #     return output
        # else:
        #     output = self.numMessages[data[1]]
        #     return output
        # -------------------------

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
    """
    def get_message(self, user):

        print('Read messages request')
        # -------------------------
        # non-binary-storage method
        # -------------------------
        # msgs = self.messages.get(user)
        # if msgs is None:
        #     output = 'READ ERROR'
        #     return output
        # else:
        #     output = self.messages[user]
        #     return output
        # -------------------------

        # check if excel file exists
        isExist = os.path.exists(messages_file)

        # if exists, continue to check if the user exists
        if isExist:
            df = pd.read_excel(messages_file)
            if len(df) == 0:
                return 'READ ERROR'
            else:
                for i in df.index:
                    if user == df['To'][i]:
                        # msg = str(df['From'][i]+ ':' + df['Message'][i])
                        from_user = df['From'][i]
                        # server.send(from_user)

                        msg = df['Message'][i]
                        server.send(f'\n{msg}')

        # if the excel file does not exist, create it :)
        else:
            df = pd.DataFrame(columns=['From', 'To', 'Message'])
            with pd.ExcelWriter(messages_file) as writer:
                df.to_excel(writer, sheet_name='Messages', header=True, index=False)
            return 'READ ERROR'

    """
    Compose a Message - after client sends command COMPOSE followed by a message
    Parameter: data
    """
    def compose_message(self, data):

        print('New message request')

        # -------------------------
        # non-binary-storage method
        # -------------------------
        # msgs = self.numMessages.get(data[1])
        # if msgs is None:
        #     self.numMessages[data[1]] = '1'
        # else:
        #     unpack_msg = ' '.join(str(item) for item in data[3:])
        #     self.messages[data[1]] = unpack_msg
        # -------------------------

        df_data = []
        to_user = data[1]
        from_user = self.sessions[0]
        message = data[3:]
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
    port = int(sys.argv[1])
    server = Server(port)
    print('COSC340 - A2 - bnolan9 - server')
    print('Connection received and established.')
    while True:
        data = server.recv()
        dataSplit = data.split()
        cmd = dataSplit[0].upper()
        if not data:
            break
        else:
            if cmd == 'LOGIN':
                if len(dataSplit) > 2:
                    error_msg = 'INVALID LOGIN'
                    server.send(error_msg)
                    exit()
                server.login_user(dataSplit)
                msgs = server.get_messages(dataSplit)
                server.send(msgs)
            if cmd == 'COMPOSE':
                msg = server.compose_message(dataSplit)
                server.send(msg)
            if cmd == 'READ':
                # user = server.get_user()
                user = server.get_user()
                server.get_message(user)
                # msg = server.get_message(user)
                # user = str(user).lower()
                # msgSplit = msg.split(sep=':')
                # from_user = msgSplit[0]
                # from_user = str(from_user).lower()
                # msg = ' '.join(map(str, msgSplit[1]))
                # if msg != 'READ ERROR':
                #     server.send(str(from_user+'\n'))
                #     server.send(str(msg))
                # else:
                #     server.send(msg)
            if cmd not in server.commands:
                error_msg = 'Command not found'
                server.send(error_msg)
                exit()
