import random
from socket import *
import struct
import scapy
class Server:

    def __init__(self):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.UDP_IP = '255.255.255.255'
        self.UDP_PORT = 13117
        magic_cookie = int(0xabcddcba)
        # self.server_port = random.Random().randint(1024, 65535)
        self.server_port = 5400
        message_type = int(0x2)
        self.message = struct.pack('>IBH', magic_cookie, message_type, self.server_port)  # TODO check why 8 byte instead of 7
        self.my_ip = "127.0.0.1" # TODO change to scapy.get_if_addr('eth1')

    def broadcast_message(self):
        self.tcp_socket.bind((self.my_ip, self.server_port))  # TODO check if it is correct
        self.tcp_socket.settimeout(1)
        self.tcp_socket.listen(1)
        print("Server started, listening on IP address " + self.my_ip)
        self.udp_socket.sendto(self.message, (self.UDP_IP, self.UDP_PORT))
        while True:
            try:
                # print("before")
                #accept(1 sec)
                client_socket, address = self.tcp_socket.accept()
                print("after")
            except:
                self.udp_socket.sendto(self.message, (self.UDP_IP, self.UDP_PORT))

server = Server()
server.broadcast_message()