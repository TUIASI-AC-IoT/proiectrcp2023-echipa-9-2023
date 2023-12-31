from defines import *

class UNSUBACK_builder():
    def __init__(self,data):
        self.data = data
        self.pack_type = None
        self.remaining_len = 0
        self.pack_id = None
        self.properties = bytes([0x00])
        self.payload = b''

    def build(self,topic_found = False):
        self.pack_type = bytes([UNSUBACK])
        self.pack_id = self.data.variable_header['packet_id'].to_bytes(2,"big")
        if topic_found:
            self.payload = bytes([0x00])
        else:
            self.payload = bytes([0x11])
        packet = b''.join([self.pack_type, bytes([0x04]), self.pack_id, self.properties, self.payload])
        return packet

