import struct
from socket import *


class Client:
    def __init__(self, team_name):
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.my_ip = "0.0.0.0"  # TODO change to scapy.get_if_addr('eth1')
        self.team_name = team_name

    def looking_for_server(self):
        self.udp_client_socket.bind(('', 13117))
        # while True:
        try:
            print("Client started, listening for offer requests...")
            packed_message, address = self.udp_client_socket.recvfrom(4096)
            magic_cookie, message_type, server_port = struct.unpack('>IBH', packed_message)
            if hex(int(magic_cookie)) != hex(2882395322) or int(message_type) != 2:
                return  # TODO think what to to do
            self.connected_to_server(address[0], server_port)
        except Exception as e:
            pass

    def connected_to_server(self, address, server_port):
        print("Received offer from " + address + ", attempting to connect...")
        self.tcp_socket.connect(("127.0.0.1", server_port))
        team_name_bytes = str.encode(self.team_name+"\n")
        self.tcp_socket.send(team_name_bytes)

client = Client("Snoku")
client1 = Client("Snoku1")
client2 = Client("Snoku2")
client.looking_for_server()
client1.looking_for_server()
client2.looking_for_server()
