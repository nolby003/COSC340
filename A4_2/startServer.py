import socket

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class Server:

    def __init__(self):
        self.host = ""
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

    # Generate keys
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    # Serialize public key to share with the client
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


    # Load the server's private key
    with open("private_key.pem", "rb") as key_file:
        private_key = load_pem_private_key(key_file.read(), password=None, backend=default_backend())

    def decrypt_message(encrypted_message, private_key):
        return private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()

    def send(self, data):
        data = data.encode('utf-8')
        self.conn.send(data)

    def recv(self):
        data = self.conn.recv(1024).decode('utf-8')
        data = server.decrypt_message(data, self.private_key)
        print(data)
        return data

    @staticmethod
    def decrypt_message(encrypted_message, private_key):
        # Decrypt message
        original_message = private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return original_message.decode()

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
