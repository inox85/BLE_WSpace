import sys
import socket
import threading
import json


class ServerThread(threading.Thread):
    def __init__(self, host, port, c_finder):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket = None
        self.data_to_send = dict()
        self.finder = c_finder

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            response_json = json.dumps(self.finder.get_informations())
            client_socket.sendall(response_json.encode())
            client_socket.close()
