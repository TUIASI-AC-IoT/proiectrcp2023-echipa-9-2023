from Fixed_header import *
class PUBREL_packet(Fixed_header):
    def __init__(self, message):
        Fixed_header.__init__(self, message)
        self.variable_header = {
            'pack_id': 0,
            'reason_code': None,
            'property_length': 0
        }
        self.extract_info()

    def extract_info(self):
        self.read_fixed_field()
        self.read_variable_header()

    def read_variable_header(self):
        self.variable_header['pack_id'] = int.from_bytes(self.message[self.index:self.index + 2], 'big', signed=False)
        self.index += 2
        self.variable_header['reason_code'] = self.message[self.index]
        self.index += 1
        if self.remaining_len > 4:
            self.variable_header['property_length'] = self.message[self.index]
            self.index += 1

class PUBREL_builder(Fixed_header):
    def __init__(self):
        Fixed_header.__init__(self)
        self.variable_header = {
            'pack_id': 0,
            'reason_code': b'',
            'property_length': 0
        }

    def build(self, pack_id):
        self.pack_type = bytes([PUBREL + 0x02])
        self.remaining_len = bytes([0x03])
        self.variable_header['pack_id'] = pack_id.to_bytes(2, 'big')
        self.variable_header['reason_code'] = bytes([0x00])
        packet = b''.join([self.pack_type, self.remaining_len,
                           self.variable_header['pack_id'],
                           self.variable_header['reason_code']])
        return packet
