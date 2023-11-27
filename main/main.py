import socket
import threading


# Control packet type
CONNECT     = 0x10
CONNACK     = 0x20
PUBLISH     = 0x30
PUBACK      = 0x40
PUBREC      = 0x50
PUBREL      = 0x60
PUBCOMP     = 0x70
SUBSCRIBE   = 0x80
SUBACK      = 0x90
UNSUBSCRIBE = 0xA0
UNSUBACK    = 0xB0
PINGREQ     = 0xC0
PINGRESP    = 0xD0
DISCONNECT  = 0xE0
AUTH        = 0xF0

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


def message_switch(fixed_header):
    if fixed_header == CONNECT:
        return CONNECT
    elif fixed_header == CONNACK:
        return CONNACK
    elif fixed_header == PUBLISH:
        return PUBLISH
    elif fixed_header == PUBACK:
        return PUBACK
    elif fixed_header == PUBREC:
        return PUBREC
    elif fixed_header == PUBREL:
        return 6
    elif fixed_header == PUBCOMP:
        return 7
    elif fixed_header == SUBSCRIBE:
        return 8
    elif fixed_header == SUBACK:
        return 9
    elif fixed_header == UNSUBSCRIBE:
        return 10
    elif fixed_header == UNSUBACK:
        return 11
    elif fixed_header == PINGREQ:
        return 12
    elif fixed_header == PINGRESP:
        return 13
    elif fixed_header == DISCONNECT:
        return 14
    elif fixed_header == AUTH:
        return 15


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

    def handle_message(self,message):
        message_type = message[0]
        message_length = message[1]

        protocol_name = bytearray()
        protocol_name.extend((message[4], message[5], message[6], message[7]))
        protocol_name = bytes(protocol_name)

        if message_type == CONNECT:
            if protocol_name == self.name:
                if message[8] == self.version:
                    print("Protocol version is v3.1.1")
                    flags = get_bits(message[9])

                else:
                    # SEND CONNACK AND CLOSE CONNECTION
                    pass
            else:
                # SEND CONNACK AND CLOSE CONNECTION
                pass
        elif message_type == CONNACK:
            # TODO
            pass


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
            message = client_socket.recv(65535)
            if not message :
                break
            self.handle_message(message)
            print(f"Received from client: {message}")
            ack_message = "Network Connection established!"
            client_socket.send(ack_message.encode('utf-8'))
        client_socket.close()



if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())

    broker = MQTTBroker()
    broker.start()

