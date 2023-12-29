from Fixed_header import *

class SUBSCRIBE_packet(Fixed_header):
    def __init__(self, message):
        Fixed_header.__init__(self, message)
        self.variable_header = {
            'packet_id' : 0,
            'properties' : b''
        }
        self.topics = []
        self.extract_info()

    def extract_info(self):
        self.read_fixed_field()
        self.read_var_field()
        self.read_payload_field()

    def read_var_field(self):
        self.variable_header['packet_id'] = int.from_bytes(self.message[self.index:self.index + 2], 'big', signed = False)
        self.index += 2
        len = self.message[self.index]
        for i in range(self.index, self.index + len + 1):
            self.variable_header['properties'] += bytes([self.message[i]])
        self.index = self.index + len + 1


    def read_payload_field(self):
        topic = {
            'length': 0,
            'name': b'',
            'retain_handle': None,
            'retain_published': None,
            'no_local': None,
            'qos': None
        }
        while 1:
            topic['length'] = int.from_bytes(self.message[self.index:self.index + 2], 'big', signed = False)
            self.index += 2
            if self.index > len(self.message):
                break
            for i in range(self.index,self.index + topic['length']):
                topic['name'] += bytes([self.message[i]])
            self.index += topic['length']
            options = self.message[self.index]
            topic['retain_handle']      = (options & 0b00110000) >> 4
            topic['retain_published']   = (options & 0b00001000) >> 3
            topic['no_local']           = (options & 0b00000100) >> 2
            topic['qos']                = (options & 0b00000011)
            self.index += 1
            self.topics.append(topic.copy())
            topic['name'] = b''

