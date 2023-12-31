from Fixed_header import *

class CONNACK_builder(Fixed_header):
    def __init__(self, data):
        self.data = data
        self.index = None
        self.pack_type = None
        self.pack_flags = b'00'
        self.remaining_len = None
        self.session_present = None
        self.reason_code = None
        self.properties = None

    def set_pack_type(self, val):
        self.pack_type = val
        return self

    def set_remaining_len(self, val):
        self.remaining_len = val
        return self

    def set_session_present(self, val):
        self.session_present = val
        return self

    def set_reason_code(self, val):
        self.reason_code = val
        return self

    def set_properties(self):
        pass
        # TODO
        # I need to look on the entire property system, and maybe code
        # a property buffer builder


    def build(self):
        # build the self.message before returning
        self.pack_type = CONNACK
        if self.data['clean_session'] == 1:
            self.session_present = 0x00
            self.reason_code = 0x00
        elif self.data['clean_session'] == 0 and self.data['qos_level'] == 1 or self.data['qos_level'] == 2:
            self.session_present = 0X01
            self.reason_code = 0x00
        else:
            self.session_present = 0X00
            self.reason_code = 0x00

        self.properties = 0x00

        packet = bytearray([self.pack_type, 0x03, self.session_present, self.reason_code, self.properties])
        return packet


