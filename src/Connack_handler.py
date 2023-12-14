
class CONNACK_packet:
    def __init__(self):
        self.message = b''
        self.type = 0x20
        self.len = b'' #Variable byte integer
        self.session_present = None
        self.reason_code = None
        self. property_len = None


