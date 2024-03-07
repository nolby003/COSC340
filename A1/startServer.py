import socket


class Server:

    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 65432
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.conn, self.addr = self.sock.accept()
        self.conn.settimeout(1)
        self.conn.setblocking(True)
        self.messages = {}
        self.numMessages = {}
        self.sessions = []

    def send(self, data):
        data = data.encode('utf-8')
        self.conn.send(data)

    def recv(self):
        data = self.conn.recv(1024).decode('utf-8')
        # print(data)
        return data

    # def disconnect(self):
    #     self.conn.close()
    #     self.sock.close()
    #
    # def sendall(self, data):
    #     data = data.encode('utf-8')
    #     self.conn.sendall(data)

    def login_user(self, data):
        self.sessions.append(data[1])

    def get_user(self):
        user = self.sessions[0]
        # print(user)
        return user

    def get_messages(self, data):
        msgs = self.numMessages.get(data[1])
        if msgs is None:
            output = self.numMessages[data[1]] = '0'
            return output
        else:
            output = self.numMessages[data[1]]
            return output

    def get_message(self, user):
        # print(self.messages.get(user))
        msgs = self.messages.get(user)
        if msgs is None:
            output = 'READ ERROR'
            return output
        else:
            output = self.messages[user]
            return output

    def compose_message(self, data):
        msgs = self.numMessages.get(data[1])
        if msgs is None:
            self.numMessages[data[1]] = '1'
        else:
            unpack_msg = ' '.join(str(item) for item in data[3:])
            self.messages[data[1]] = unpack_msg


if __name__ == '__main__':
    server = Server()
    while True:
        data = server.recv()
        dataSplit = data.split()
        cmd = dataSplit[0].upper()
        if not data:
            break
        else:
            if cmd == 'LOGIN':
                server.login_user(dataSplit)
                msgs = server.get_messages(dataSplit)
                server.send(msgs)
            if cmd == 'COMPOSE':
                server.compose_message(dataSplit)
                msg = 'MESSAGE SENT'
                server.send(msg)
            if cmd == 'READ':
                user = server.get_user()
                msg = server.get_message(user)
                user = str(user).lower()
                combined_message = str(user + '\n' + msg)
                server.send(combined_message)
