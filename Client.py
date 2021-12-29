import struct
import threading
import time
from multiprocessing import Process
from socket import *
import getch


class Client:
    def __init__(self, team_name):
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.team_name = team_name
        self.udp_client_socket.bind(('', 13117))

    def looking_for_server(self):

        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        while True:
            try:
                print("Client started, listening for offer requests...")
                packed_message, address = self.udp_client_socket.recvfrom(4096)
                magic_cookie, message_type, server_port = struct.unpack('>IBH', packed_message)
                # if address[0]!='172.18.0.146' or hex(int(magic_cookie)) != hex(2882395322) or int(message_type) != 2:
                #     continue  # TODO think what to to do address[0]!='172.18.0.146' or
                self.connected_to_server(address[0], server_port)
            except Exception as e:
                # print(e)
                pass

    def connected_to_server(self, address, server_port):
        print("Received offer from " + address + ", attempting to connect...")
        self.tcp_socket.connect((address, server_port))
        team_name_bytes = str.encode(self.team_name + "\n")
        self.tcp_socket.send(team_name_bytes)
        self.game_mode()

    def game_mode(self):
        question_bytes = self.tcp_socket.recv(1024)
        question = question_bytes.decode()
        print(question)
        getch_thread = Process(target=self.getch_handler)
        getch_thread.start()
        server_result_bytes = self.tcp_socket.recv(1024)
        getch_thread.kill()
        server_result = server_result_bytes.decode()
        print(server_result)
        self.tcp_socket.close()
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        print("Server disconnected, listening for offer requests...")
        self.looking_for_server()

    def getch_handler(self):
        client_answer = getch.getch()
        client_answer_bytes = str.encode(client_answer)
        self.tcp_socket.send(client_answer_bytes)


Client("SchnitzelBehala").looking_for_server()