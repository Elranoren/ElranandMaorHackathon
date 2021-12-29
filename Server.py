import random
import threading
import time
from socket import *
import struct
import scapy
from scapy.arch import get_if_addr


class Server:

    def __init__(self):
        """
        This is the constructor of the Server
        """
        self.score_board = {}
        self.best_team = ""
        self.question_dict = {}
        for i in range(10):
            for j in range(10):
                if i + j < 10:
                    temp_question = f"How much is {i}+{j}?"
                    if temp_question not in self.question_dict:
                        self.question_dict[temp_question] = i + j
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.UDP_IP = '255.255.255.255'
        self.UDP_PORT = 13117
        magic_cookie = int(0xabcddcba)
        self.server_port = random.Random().randint(1024, 65535)
        # self.server_port = 5400
        message_type = int(0x2)
        self.message = struct.pack('>IBH', magic_cookie, message_type,
                                   self.server_port)
        self.my_ip = get_if_addr("eth1")
        self.was_answered = False
        self.lock = threading.Lock()
        self.winning_team = ""
        self.tcp_socket.bind(('', self.server_port))

    def broadcast_message(self):
        """
        This function is responsible to send udp broadcast to everyone and try to connect clients with the connection_players function
        """
        self.tcp_socket.settimeout(1)
        self.tcp_socket.listen(2)
        print("Server started, listening on IP address " + self.my_ip)
        self.udp_socket.sendto(self.message, (self.UDP_IP, self.UDP_PORT))
        self.connection_players()

    def connection_players(self):
        """
        This function is responsible to connect the clients to the server using TCP and when  there are 2 clients connected then
        we go to game mode and start a game between the 2 clients and announce the winner.
        """
        connected_clients = []
        while len(connected_clients) < 2:
            try:
                # print("before")
                # accept(1 sec)
                client_socket, address = self.tcp_socket.accept()
                # if address[0] != '172.18.0.14':
                #     continue
                # if len(connected_clients) == 1:
                #     try:
                #         ready_to_read, ready_to_write, in_error = select([connected_clients[0][0],], [connected_clients[0][0],], [], 2)
                #     except:
                #         connected_clients.pop(0)
                # print("after")
                team_name_bytes = client_socket.recv(1024)
                team_name = team_name_bytes.decode()
                new_client = (client_socket, address, team_name)
                # print(new_client)
                connected_clients.append(new_client)
                # print("after2")
            except:
                self.udp_socket.sendto(self.message, (self.UDP_IP, self.UDP_PORT))
        # print("out of while")
        self.start_game(connected_clients[:2])

    def start_game(self, connected_clients):
        """
        This function starts the game after 2 clients connected to the server and if after 10 seconds the server didnt got any response then
        it sends a message for Draw otherwise it sends message with the winning team
        """
        try:
            question_keys = list(self.question_dict.keys())
            index = random.randint(0, len(question_keys) - 1)
            question = question_keys[index]
            answer = self.question_dict[question]
            self.winning_team = ""
            self.was_answered = False
            # time.sleep(10)
            welcome_message = f"""Welcome to Quick Maths.
Player 1: {connected_clients[0][2]}Player 2: {connected_clients[1][2]}==
Please answer the following question as fast as you can:
{question}"""
            print(welcome_message)
            thread1 = threading.Thread(target=self.handle_client, args=(
                connected_clients[0][0], connected_clients[0][1], connected_clients[0][2], welcome_message, answer,
                connected_clients[1][2]))
            thread2 = threading.Thread(target=self.handle_client, args=(
                connected_clients[1][0], connected_clients[1][1], connected_clients[1][2], welcome_message, answer,
                connected_clients[0][2]))
            thread1.start()
            thread2.start()
            # thread1.join()
            # thread2.join()
            while thread1.is_alive() and thread2.is_alive():
                time.sleep(0.1)
            # recive result from one of the clients and then:
            summary_message = f"""Game over!
            The correct answer was {answer}!

            Congratulations to the winner: {self.winning_team}"""
            if self.winning_team != "Draw" and self.winning_team != "":
                win_tem = self.winning_team.strip("\n")
                if win_tem in self.score_board:
                    self.score_board[win_tem] += 1
                else:
                    self.score_board[win_tem] = 1
                print(self.score_board)
            if len(self.score_board) > 0:
                self.best_team = max(self.score_board, key=self.score_board.get)
                print("The best team so far is: " + self.best_team)
            summary_message_bytes = str.encode(summary_message)
            for client_socket, address, team_name in connected_clients:
                client_socket.sendall(summary_message_bytes)
                # client_socket.close()
            print("Game over, sending out offer requests...")
            self.broadcast_message()
        except Exception as e:
            # print(e)
            self.broadcast_message()

    def handle_client(self, client_socket, address, my_team_name, welcome_message, answer, their_team_name):
        """
        This function is used for open threads for each connected client and handling the game between this clients
        """
        try:
            question_bytes = str.encode(welcome_message)
            client_socket.sendall(question_bytes)
            client_socket.settimeout(10)
            client_answer = client_socket.recv(1024)
            self.lock.acquire()
            if self.was_answered:
                self.lock.release()
                return
            self.was_answered = True
            client_answer_str = client_answer.decode()
            if client_answer_str == str(answer):
                self.winning_team = my_team_name
            else:
                self.winning_team = their_team_name
            self.lock.release()
        except timeout as e:
            self.winning_team = "Draw"


server = Server()
server.broadcast_message()
