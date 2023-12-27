from Fixed_header import *

class CONNACK_builder(Fixed_header):
    def __init__(self,session_present = False, return_code = 0):
        Fixed_header.__init__(self)
        self.session_present = session_present
        self.reason_code = return_code
        self.properties = None

    def set_session_present(self, val):
        self.session_present = val

    def set_reason_code(self,val):
        self.reason_code = val

    def build(self):
        flags = 0x00
        if self.session_present:
            flags |= 0x01

        packet = bytearray([CONNACK,0x02,flags,self.reason_code,0x00])
        return bytes(packet)

