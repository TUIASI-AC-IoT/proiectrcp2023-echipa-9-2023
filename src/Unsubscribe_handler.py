from Fixed_header import *

class UNSUBSCRIBE_packet(Fixed_header):
    def __init__(self, message):
        Fixed_header.__init__(self, message)
        self.variable_header = {
            'packet_id': 0,
            'properties': b''
        }
        self.topics_to_unsub = []
        self.extract_info()

    def extract_info(self):
        self.read_fixed_field()
        self.read_var_field()
        self.read_payload_field()

    def read_var_field(self):
        self.variable_header['packet_id'] = int.from_bytes(self.message[self.index:self.index + 2], 'big', signed=False)
        self.index += 2
        len = self.message[self.index]
        for i in range(self.index, self.index + len + 1):
            self.variable_header['properties'] += bytes([self.message[i]])
        self.index = self.index + len + 1
        print(self.variable_header)

    def read_payload_field(self):
        topic = b''
        while 1:
            length = int.from_bytes(self.message[self.index:self.index + 2], 'big', signed=False)
            self.index += 2
            if self.index > len(self.message):
                break
            for i in range(self.index, self.index + length):
                topic += bytes([self.message[i]])
            self.index += length
            self.topics_to_unsub.append(topic)
            topic = b''



