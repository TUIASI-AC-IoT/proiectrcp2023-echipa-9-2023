from Fixed_header import *
class PINGREQ_packet(Fixed_header):
    def __init__(self, message):
        Fixed_header.__init__(self, message)
        self.read_fixed_field()


class PINGRESP_builder(Fixed_header):
    def __init__(self):
        Fixed_header.__init__(self)

    def build(self):
        self.pack_type = bytes([PINGRESP])
        self.remaining_len = bytes([0x00])
        packet = b''.join([self.pack_type, self.remaining_len])
        return packet
