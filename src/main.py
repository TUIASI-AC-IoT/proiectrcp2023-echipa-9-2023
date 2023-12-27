import socket
import threading
from Connect_handler import CONNECT_packet
from Connack_handler import CONNACK_builder
from Fixed_header import *

# Connect packet example
# x10\x0C\x00\x04\x4d\x51\x54\x54\x04\x02\x00\x3C\x00\x00...
#  |   |   |   |   |   |   |   |   |   |   |   |   |   |
#  |   |   |   |   |   |   |   |   |   |   |   |   +---+---- Client ID (0)
#  |   |   |   |   |   |   |   |   |   |   |   |   PAYLOAD STARTS
#  |   |   |   |   |   |   |   |   |   |   +---+------------ Keep Alive (60)
#  |   |   |   |   |   |   |   |   |   +-------------------- Connect Flags (In the example the only flag set is Clean Session Flag)
#  |   |   |   |   |   |   |   |   +------------------------ Version (v3.1.1)
#  |   |   |   |   +---+---+---+---------------------------- M Q T T (Protocol Name)
#  |   |   +---+-------------------------------------------- Protocol Name Length (4)
#  |   +---------------------------------------------------- Msg Length (12)
#  +-------------------------------------------------------- Message Type (Connect Command)


def get_bits(byte):
    bits = format(byte, 'b')
    while len(bits) < 8:
        bits = '0' + bits
    return bits


class MQTTBroker:
    def __init__(self,host = 'localhost', port = 1883):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.name = b'MQTT'
        self.version = 0x04
        self.clients = {}

    def handle_message(self,message, client_socket):
        connack_builder = CONNACK_builder(return_code=0)
        if (message[0]) == CONNECT:
            connect = CONNECT_packet(message)
            connect.extract_info()
            connect.print_all()
            if 1: # daca pachetul connect e in regula TODO
                connack_packet = connack_builder.build()
                client_socket.send(connack_packet)
            if connect.id in self.clients:
                client_socket.close()
            else:
                self.clients[connect.id] = {'subscriptions': []}
            print(self.clients)
            # TODO

    def start(self):
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(30)
        print(f"MQTT Broker listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self,client_socket):
        while True:
            message = client_socket.recv(65535) #iso/osi
            if not message :
                break
            self.handle_message(message, client_socket) #
            #print(f"Received from client: {message}")
            ack_message = "Network Connection established!"
            client_socket.send(ack_message.encode('utf-8'))
        client_socket.close()

if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())

    broker = MQTTBroker()
    broker.start()

