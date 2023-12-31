import socket
import threading
from Connect_handler import CONNECT_packet
from Connack_handler import CONNACK_builder
from Subscribe_handler import  SUBSCRIBE_packet
from Suback_handler import SUBACK_builder
from Unsubscribe_handler import UNSUBSCRIBE_packet
from Unsuback_handler import  UNSUBACK_builder
from Publish_handler import PUBLISH_packet, PUBLISH_builder
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


# noinspection PyUnboundLocalVariable
class MQTTBroker:
    def __init__(self,host = 'localhost', port = 1883):
        self.host = host
        self.port = port
        self.name = b'MQTT'
        self.version = 0x04
        self.clients = {}

    def handle_message(self,message, client_socket, connect):
        if message[0] >> 4 == SUBSCRIBE >> 4:
            subscribe = SUBSCRIBE_packet(message)
            self.add_subscription_to_id(subscribe, connect.payload['id'])
            self.send_suback(subscribe, client_socket)
        if message[0] >> 4 == UNSUBSCRIBE >> 4:
            unsubscribe = UNSUBSCRIBE_packet(message)
            flag = self.delete_subscription_to_id(unsubscribe, connect.payload['id'])
            self.send_unsuback(flag, unsubscribe, client_socket)
        if message[0] >> 4 == PUBLISH >> 4:
            publish = PUBLISH_packet(message)
            self.send_publish(client_socket)
        if 1: # daca este apasat butonul de send din interfata
            # self.send_publish(client_socket)
            pass

    def start(self):
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(30)
            print(f"MQTT Broker listening on {self.host}:{self.port}")

            client_socket, client_address = sock.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def connect(self, message , client_socket):
        connect = CONNECT_packet(message)
        self.send_connack(connect, client_socket)
        if connect.payload['id'] in self.clients:
            client_socket.close()
        else:
            self.clients[connect.payload['id']] = {'subscriptions': []}

    def handle_client(self,client_socket):
        while True:
            try:
                message = client_socket.recv(65535) #iso/osi
                if not message or message[1] != len(message) - 2:
                    print("Malformed Packet")
                    break
            except:
                print("Something went wrong\n")
                break
            if message[0] == CONNECT:
                connect = CONNECT_packet(message)
                self.send_connack(connect, client_socket)
                if connect.payload['id'] in self.clients:
                    client_socket.close()
                else:
                    self.clients[connect.payload['id']] = {'subscriptions': []}
            if len(self.clients):
                self.handle_message(message, client_socket, connect) #
        client_socket.close()

    def send_publish(self,client_socket):
        publish_builder = PUBLISH_builder()
        publish_packet = publish_builder.build(1)
        client_socket.send(publish_packet)

    def send_connack(self, connect, client_socket):
        connack_builder = CONNACK_builder(connect.variable_header)
        connack_packet = connack_builder.build()
        client_socket.send(connack_packet)

    def send_suback(self, subscribe, client_socket):
        suback_builder = SUBACK_builder(subscribe)
        suback_packet = suback_builder.build()
        client_socket.send(suback_packet)
        print(self.clients)

    def send_unsuback(self, flag, unsubscribe, client_socket):
        unsuback_builder = UNSUBACK_builder(unsubscribe)
        unsuback_packet = unsuback_builder.build(flag)
        client_socket.send(unsuback_packet)
        print(self.clients)

    def add_subscription_to_id(self,subscribe, id):
        self.clients[id]['subscriptions'].append(subscribe.topics[-1]['name'])

    def delete_subscription_to_id(self, unsubscribe, id):
        c_list = []
        topic_found = False
        for topic in self.clients[id]['subscriptions']:
            if topic not in unsubscribe.topics_to_unsub:
                c_list.append(topic)
            else:
                topic_found = True
        self.clients[id]['subscriptions'] = c_list
        return  topic_found

if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())

    broker = MQTTBroker()
    broker.start()

