import socket


class Client(object):

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 65432))
        self.sock.settimeout(1)

    def send(self, data):
        data = data.encode('utf-8')
        self.sock.send(data)

    def recv(self):
        data = self.sock.recv(1024).decode('utf-8')
        print(f'Server: {data}')
        return data

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
