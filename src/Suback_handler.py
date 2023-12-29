from Fixed_header import *

class SUBACK_builder():
    def __init__(self, data):
        self.data = data
        self.pack_type = None
        self.remaining_len = None
        self.packet_id = None
        self.properties = None
        self.payload = b''

    def build(self):
        self.pack_type = bytes([SUBACK])
        self.packet_id = self.data.variable_header['packet_id'].to_bytes(2,"big")
        self.properties = bytes([0x00])
        for topic in self.data.topics:
            if topic['qos'] == 0:
                self.payload += bytes([0x00])
            elif topic['qos'] == 1:
                self.payload += bytes([0x01])
            elif topic['qos'] == 2:
                self.payload += bytes([0x02])

        print(self.pack_type,0x03,self.packet_id,self.properties,self.payload)
        packet = b''.join([self.pack_type, bytes([0x04]), self.packet_id, self.properties, self.payload])
        return bytes(packet)


