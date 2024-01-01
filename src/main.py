import socket
import threading
import sys
import re
import time

from send_message import *
from Connect_handler import CONNECT_packet
from Connack_handler import CONNACK_builder
from Subscribe_handler import  SUBSCRIBE_packet
from Suback_handler import SUBACK_builder
from Unsubscribe_handler import UNSUBSCRIBE_packet
from Unsuback_handler import  UNSUBACK_builder
from Publish_handler import PUBLISH_packet, PUBLISH_builder
from Puback_handler import PUBACK_builder, PUBACK_packet
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
    def __init__(self, queue, host='localhost', port=1883):
        self.pub_queue = queue
        self.host = host
        self.port = port
        self.name = b'MQTT'
        self.version = 0x04
        self.clients = {}

    def handle_message(self,message, client_socket, connect):
        if message[0] >> 4 == SUBSCRIBE >> 4:
            subscribe = SUBSCRIBE_packet(message)
            self.add_subscription_to_id(subscribe, connect.payload['id'])
            self.send_suback(client_socket, subscribe)
        if message[0] >> 4 == UNSUBSCRIBE >> 4:
            unsubscribe = UNSUBSCRIBE_packet(message)
            flag = self.delete_subscription_to_id(unsubscribe, connect.payload['id'])
            self.send_unsuback(client_socket, flag, unsubscribe)
        if message[0] >> 4 == PUBLISH >> 4:
            publish = PUBLISH_packet(message)
            if publish.qos_level == 0:
                pass
            elif publish.qos_level == 1:
                self.send_puback(client_socket, publish.variable_header['pack_id'])
                pass
            elif publish.qos_level == 2:
                pass

    def start(self):
        # This thread is responsible from sending publish packets
        # from the broker to the clients
        # Because all the other threads are responsible for
        # receiving from clients and the recv function is a blocking one,
        # this needs to be done on another thread
        sock_queue = Queue()
        broker_thread = threading.Thread(target=self.handle_broker_send, args=(sock_queue,self.pub_queue,))
        broker_thread.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(30)
        print(f"MQTT Broker listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = sock.accept()
            sock_queue.put(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_broker_send(self, sock_queue, pub_queue):
        sockets = []
        while True:
            while not sock_queue.empty():
                sockets.append(sock_queue.get())

            values = []
            regex = r'(?:T:|M:|Q:|R:)(.*?),'
            if not pub_queue.empty():
                values = re.findall(regex, pub_queue.get())
            if len(values) != 0:
                topic = bytes(values[0], 'utf-8')
                message = bytes(values[1], 'utf-8')
                qos = int(values[2][-1])
                if values[3] == 'True':
                    retain = 1
                elif values[3] == 'False':
                    retain = 0
                print(topic, message, qos, retain)

                if len(sockets) != 0:
                    for sock in sockets:
                        self.send_publish(sock, topic, message, qos, retain)

    def handle_client(self,client_socket):
        while True:
            try:
                message = client_socket.recv(65535)
                if not message or message[1] != len(message) - 2:
                    print("Malformed Packet")
                    break
            except:
                print("Something went wrong\n")
                break
            if message[0] == CONNECT:
                connect = CONNECT_packet(message)
                self.send_connack(client_socket, connect)
                if connect.payload['id'] in self.clients:
                    client_socket.close()
                else:
                    self.clients[connect.payload['id']] = {'subscriptions': []}
            if len(self.clients):
                self.handle_message(message, client_socket, connect) #
        client_socket.close()

    def send_puback(self, client_socket, pack_id):
        puback_builder = PUBACK_builder()
        puback_packet = puback_builder.build(pack_id)
        client_socket.send(puback_packet)

    def send_publish(self,client_socket, topic, message, qos, retain):
        publish_builder = PUBLISH_builder()
        publish_packet = publish_builder.build(topic, message, qos, retain)
        client_socket.send(publish_packet)

    def send_connack(self, client_socket, connect):
        connack_builder = CONNACK_builder(connect.variable_header)
        connack_packet = connack_builder.build()
        client_socket.send(connack_packet)

    def send_suback(self, client_socket, subscribe):
        suback_builder = SUBACK_builder(subscribe)
        suback_packet = suback_builder.build()
        client_socket.send(suback_packet)
        print(self.clients)

    def send_unsuback(self, client_socket, flag, unsubscribe):
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
    # Sending data betweend threads
    myQueue = Queue()
    app = QApplication(sys.argv)
    broker = MQTTBroker(myQueue)
    worker_thread = threading.Thread(target=broker.start)
    worker_thread.start()
    host = socket.gethostbyname(socket.gethostname())

    ex = MQTTBrokerUI(myQueue)
    ex.show()
    sys.exit(app.exec_())


