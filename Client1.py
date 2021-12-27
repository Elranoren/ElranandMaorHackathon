
import struct
import threading
import time
from multiprocessing import Process
from socket import *
import getch
# import keyword

# from pynput import keyboard


class Client1:
    def __init__(self, team_name):
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.my_ip = "0.0.0.0"  # TODO change to scapy.get_if_addr('eth1')
        self.team_name = team_name

    def looking_for_server(self):
        self.udp_client_socket.bind(('', 13117))
        while True:
            try:
                print("Client started, listening for offer requests...")
                packed_message, address = self.udp_client_socket.recvfrom(4096)
                magic_cookie, message_type, server_port = struct.unpack('>IBH', packed_message)
                if address[0]!='172.18.0.14' or hex(int(magic_cookie)) != hex(2882395322) or int(message_type) != 2:
                    continue  # TODO think what to to do
                self.connected_to_server(address[0], server_port)
            except Exception as e:
                print(e)
                pass

    def connected_to_server(self, address, server_port):
        print("Received offer from " + address + ", attempting to connect...")
        self.tcp_socket.connect((address, server_port))
        team_name_bytes = str.encode(self.team_name+"\n")
        self.tcp_socket.send(team_name_bytes)
        self.game_mode()

    def game_mode(self):
        question_bytes = self.tcp_socket.recv(1024)
        question = question_bytes.decode()
        print(question)
        # client_answer = keyboard.Listener(on_press=self.on_press)
        # client_answer.start()  # start to listen on a separate thread
        # client_answer.join()
        client_answer = getch.getch()
        client_answer_bytes = str.encode(client_answer)
        self.tcp_socket.send(client_answer_bytes)
        server_result_bytes = self.tcp_socket.recv(1024)
        server_result = server_result_bytes.decode()
        print(server_result)
        self.looking_for_server()

    def our_getch(self):
        import termios
        import sys, tty
        def _getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        return _getch()

    def on_press(key):
        if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:  # keys of interest
            # self.keys.append(k)  # store it in global-like variable
            print('Key pressed: ' + key)
            return False  # stop listener; remove this if want more keys
# c1 = Client("Snoku")
# c2 = Client("Snoku1")
# p1 = Process(target=c1.looking_for_server).start()
# time.sleep(2)
# p2 = Process(target=c2.looking_for_server).start()
# p1.join()
# p2.join()
# GOOD down!
# c1 = Client("Snoku")
# c2 = Client("Snoku1")
# c3 = Client("Snoku2")
# p1 = threading.Thread(target=c1.looking_for_server)
# p1.start()
# p2 = threading.Thread(target=c2.looking_for_server)
# p2.start()
# p3 = threading.Thread(target=c3.looking_for_server)
# p3.start()
# p1.join()
# p2.join()
# p3.join()

# GOOD Up!
# client1 = Client("Snoku1")
# client2 = Client("Snoku2")
# client.looking_for_server()
# client1.looking_for_server()
# client2.looking_for_server()
Client1("Snoku").looking_for_server()