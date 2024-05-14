"""
File name: server.py
Created on Thu Mar 7 2024:
@author: <Benjamin Nolan>
Description: Server for sending and receiving messages over a socket
    UNE - COSC340 - A2

library requirements:
    xlsxwrtiter
    openpyxl
    pandas

Usage: python server.py port

Please run requirements.py to ensure the above library requirements are installed.

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

    def __init__(self):
        # self.host = ""  # listen on any address
        # self.port = port
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.bind((self.host, self.port))
        # self.sock.listen()
        # self.conn, self.addr = self.sock.accept()
        # self.commands = ['LOGIN', 'COMPOSE', 'READ', 'EXIT']
        # blocked to allow for server keep-alive
        pass

    # """
    # Send Data to client
    # Parameter: data
    # """
    # @staticmethod
    # def send(data):
    #     data = data.encode('utf-8')
    #     self.conn.send(data)

    # """
    # Receive data from client
    # No Parameters
    # """
    # def recv(self):
    #     data = self.conn.recv(1024).decode('utf-8')
    #     return data

    """
    Create user session
    Parameter: data
    """

    @staticmethod
    def login_user(data):

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

    @staticmethod
    def get_user():

        print('Get User Requested.')
        df = pd.read_excel(sessions_file)
        for i in df.index:
            user = df['User'][i]
        return user

    """
    Get Messages - when client sends command LOGIN
    Parameter: data
    """

    @staticmethod
    def get_messages(data):

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
    """

    @staticmethod
    def get_message(user):

        print('Read messages request')

        # check if excel file exists
        isExist = os.path.exists(messages_file)

        # if exists, continue
        if isExist:
            df = pd.read_excel(messages_file)
            # if no messages exist, sent client an error message
            if len(df) == 0:
                error_msg = 'READ ERROR'
                conn.send(error_msg.encode('utf-8'))
                return None
            else:
                for i in df.index:
                    if user == df['To'][i]:

                        # get 'from' user and message
                        from_user = df['From'][i]
                        msg = df['Message'][i]

                        # send to client
                        msg_p1 = str(from_user).encode('utf-8')
                        msg_p2 = str(msg).encode('utf-8')
                        conn.send(msg_p1)
                        conn.send(msg_p2)
                        # conn.send(f'{from_user}\n, {msg}')

                        # remove message when read
                        new_df = df[df['Message'] != msg]
                        with pd.ExcelWriter(messages_file) as writer:
                            new_df.to_excel(writer, sheet_name='Messages', header=True, index=False)
                            return None
        # if the excel file does not exist, create it
        else:
            df = pd.DataFrame(columns=['From', 'To', 'Message'])
            with pd.ExcelWriter(messages_file) as writer:
                df.to_excel(writer, sheet_name='Messages', header=True, index=False)
                error_msg = 'READ ERROR'
                conn.send(error_msg.encode('utf-8'))
                return None
        return None

    """
    Compose a Message - after client sends command COMPOSE followed by a message
    Parameter: data
    """

    @staticmethod
    def compose_message(data):

        print('New message request')

        df_data = []
        to_user = data[1]

        from_user = server.get_user()

        message = data[2:]
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

    # for server keep-alive
    port = int(sys.argv[1])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("", port))
        server_socket.listen(5)
        print(f"Server started on port {port}")

        while True:
            conn, addr = server_socket.accept()
            print(f'Connection received and established by client at {addr}')
            server = Server
            data = conn.recv(1024).decode('utf-8')
            dataSplit = data.split()
            cmd = dataSplit[0]
            if not data:
                break
            else:
                if cmd == 'EXIT':
                    exit()
                if cmd == 'LOGIN':
                    if len(dataSplit) > 2:
                        error_msg = 'INVALID LOGIN'
                        # server.send(error_msg)
                        conn.send(error_msg.encode('utf-8'))
                    server.login_user(dataSplit)
                    msgs = server.get_messages(dataSplit)
                    conn.send(msgs.encode('utf-8'))
                if cmd == 'COMPOSE':
                    msg = server.compose_message(dataSplit)
                    conn.send(msg.encode('utf-8'))
                if cmd == 'READ':
                    user = server.get_user()
                    server.get_message(user)
                if cmd not in ['LOGIN', 'COMPOSE', 'READ', 'EXIT']:
                    error_msg = 'Command not found'
                    conn.send(error_msg.encode('utf-8'))
                    exit()
