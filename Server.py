import random
from socket import *
import struct
import scapy
cs = socket(AF_INET, SOCK_DGRAM)
cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
UDP_IP = '255.255.255.255'
UDP_PORT = 13117
magic_cookie = int(0xabcddcba)
server_port = random.Random().randint(1024,65535)
message_type = int(0x2)
message = struct.pack('IHB', magic_cookie,server_port,message_type)
cs.sendto(message, (UDP_IP, UDP_PORT))
