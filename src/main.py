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
from Pubrec_handler import PUBREC_packet, PUBREC_builder
from Pubrel_handler import PUBREL_packet, PUBREL_builder
from Pubcomp_handler import PUBCOMP_packet, PUBCOMP_builder
from Ping_handler import PINGREQ_packet, PINGRESP_builder
from Disconnect_handler import DISCONNECT_packet, DISCONNECT_builder
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
        self.data = 0
        self.disconnect_flag = 0

    def handle_message(self, message, client_socket, connect):
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
            self.data = self.prepare_to_send(publish)

            if publish.qos_level == 0:
                self.send(self.data)

            elif publish.qos_level == 1:
                self.send(self.data)
                self.send_puback(client_socket, publish.variable_header['pack_id'])

            elif publish.qos_level == 2:
                # self.prepare_to_send(publish)
                self.send_pubrec(client_socket, publish.variable_header['pack_id'])
        if message[0] >> 4 == PUBREL >> 4:
            pubrel = PUBREL_packet(message)
            print(pubrel.variable_header['pack_id'])
            self.send_pubcomp(client_socket, pubrel.variable_header['pack_id'])
            self.send(self.data)
            self.data = 0
        if message[0] >> 4 == PINGREQ >> 4:
            pingreq = PINGREQ_packet(message)
            self.send_pingresp(client_socket)
        if message[0] >> 4 == DISCONNECT >> 4:
            disconnect = DISCONNECT_packet(message)
            if disconnect.variable_header['reason_code'] == 0x00:
                del self.clients[connect.payload['id']]
                self.disconnect_flag = 1
            elif disconnect.variable_header['reason_code'] == 0x04:
                # disconnect with will message
                pass

    def start(self):
        # This thread is responsible from sending publish packets
        # from the broker to the clients
        # Because all the other threads are responsible for
        # receiving from clients and the recv function is a blocking one,
        # this needs to be done on another thread
        sock_queue = Queue()
        broker_thread = threading.Thread(target=self.handle_broker_send, args=(sock_queue, self.pub_queue,))
        broker_thread.start()


        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(30)
            print(f"MQTT Broker listening on {self.host}:{self.port}")

            client_socket, client_address = sock.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, sock_queue,))
            client_thread.start()

    def prepare_to_send(self, publish):
        topic = publish.variable_header['topic'].decode("utf-8")
        print(topic)
        mess = publish.payload
        qos = publish.qos_level
        retain = publish.retain_flag
        data = f"T:{topic},M:{mess},Q:{qos},R:{retain},"
        return data

    def send(self, data):
        self.pub_queue.put(data)

    def handle_broker_send(self, sock_queue, pub_queue):
        sockets = []
        retain = 0
        while True:
            while not sock_queue.empty():
                sockets.append(sock_queue.get()) # sock_queue = (socket, client_id)
            values = []
            regex = r'(?:T:|M:|Q:|R:)(.*?),'
            if not pub_queue.empty():
                values = re.findall(regex, pub_queue.get())
            if len(values) != 0:
                topic = bytes(values[0], 'utf-8')
                message = bytes(values[1], 'utf-8')
                qos = int(values[2][-1])
                print(values)
                if values[3] == 'True':
                    retain = 1
                elif values[3] == 'False':
                    retain = 0

                if len(sockets) != 0:
                    for sock in sockets:
                        for client in self.clients:
                            print(topic, self.clients[client]['subscriptions'])
                            if sock[1] == client and topic in self.clients[client]['subscriptions']:
                                pack_id = self.send_publish(sock[0], topic, message, qos, retain)
                                if qos == 2:
                                    self.send_pubrel(sock[0], pack_id)

    def handle_client(self, client_socket, sock_queue):
        while True:
            try:
                if self.disconnect_flag:
                    break
                message = client_socket.recv(65535)
                if not message or message[1] != len(message) - 2:
                    print("Malformed Packet")
                    break
            except Exception as error :
                print("An exception occurred:",error)
                break
            if message[0] == CONNECT:
                connect = CONNECT_packet(message)
                if self.authenticate(connect.payload['username'], connect.payload['password']):
                    sock_queue.put((client_socket, connect.payload['id']))
                    self.send_connack(client_socket, connect)
                    if connect.payload['id'] in self.clients:
                        client_socket.close()
                    else:
                        self.clients[connect.payload['id']] = {'subscriptions': []}
                else:
                    self.send_connack_with_error(client_socket)
                    break
            if len(self.clients):
                self.handle_message(message, client_socket, connect)
        client_socket.close()

    def authenticate(self, username, password):
        valid_users = {
            "user": "password",
            "vlad": "vlad",
            "octavian": "octavian"
        }
        if username in valid_users and valid_users[username] == password:
            return True
        else:
            return False

    def send_pingresp(self, client_socket):
        pingresp_builder = PINGRESP_builder()
        pingresp_packet = pingresp_builder.build()
        client_socket.send(pingresp_packet)

    def send_pubrel(self, client_socket, pack_id):
        pubrel_builder = PUBREL_builder()
        pubrel_packet = pubrel_builder.build(pack_id)
        client_socket.send(pubrel_packet)

    def send_pubcomp(self, client_socket, pack_id):
        pubcomp_builder = PUBCOMP_builder()
        pubcomp_packet = pubcomp_builder.build(pack_id)
        client_socket.send(pubcomp_packet)

    def send_pubrec(self, client_socket, pack_id):
        pubrec_builder = PUBREC_builder()
        pubrec_packet = pubrec_builder.build(pack_id)
        client_socket.send(pubrec_packet)

    def send_puback(self, client_socket, pack_id):
        puback_builder = PUBACK_builder()
        puback_packet = puback_builder.build(pack_id)
        client_socket.send(puback_packet)

    def send_publish(self,client_socket, topic, message, qos, retain):
        publish_builder = PUBLISH_builder()
        pack_id, publish_packet = publish_builder.build(topic, message, qos, retain)
        client_socket.send(publish_packet)
        return pack_id

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

    def send_connack_with_error(self, client_socket):
        connack_error_packet = bytes([0x20, 0x02, 0x00, 0x05])
        client_socket.send(connack_error_packet)

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


