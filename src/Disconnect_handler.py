from Fixed_header import *
class DISCONNECT_packet(Fixed_header):
    def __init__(self, message):
        Fixed_header.__init__(self, message)
        self.variable_header = {
            'reason_code': None,
            'properties': None
        }
        self.extract_info()

    def extract_info(self):
        self.read_fixed_field()
        self.read_variable_header()

    def read_variable_header(self):
        self.variable_header['reason_code'] = self.message[self.index]
        self.index += 1
        len = self.message[self.index]
        for i in range(self.index, self.index + len):
            self.variable_header['properties'] += bytes([self.message[i]])
        self.index = self.index + len

class DISCONNECT_builder(Fixed_header):
    def __init__(self):
        Fixed_header.__init__(self)
        self.variable_header = {
            'reason_code': b'',
            'properties': b''
        }

    def build(self):
        self.pack_type = bytes([DISCONNECT])
        self.remaining_len = bytes([0x02])
        self.variable_header['reason_code'] = bytes([0x00])
        self.variable_header['properties'] = bytes([0x00])

        packet = b''.join([self.pack_type,self.remaining_len,
                           self.variable_header['reason_code'],
                           self.variable_header['properties']])

        return packet
