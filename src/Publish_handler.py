import random

from Fixed_header import *

class PUBLISH_packet(Fixed_header):
        def __init__(self, message):
            Fixed_header.__init__(self, message)
            self.dup_flag = None
            self.qos_level = None
            self.retain_flag = None
            self.variable_header = {
                'topic_len': None,
                'topic_name': b'',
                'packet_id': 0,
                'properties': b'',
                'payload_format': None,
                'expiry_interval': None,
                'topic_alias': None,
                'response_topic': None,
                'correlation_data': None,
                'user_property': None,
                'sub_id': None,
                'content_type': None
            }
            self.payload = b''
            self.extract_info()

        def extract_info(self):
            self.read_fixed_field()
            self.extract_flags()
            self.read_var_field()
            self.read_payload()

        def extract_flags(self):
            bits = (format(self.pack_flags, f'0{4}b'))
            if bits[0] == '1':
                self.dup_flag = 1
            else:
                self.dup_flag = 0
            if bits[1] == '0' and bits[2] == '0':
                self.qos_level = 0
            elif bits[1] == '0' and bits[2] == '1':
                self.qos_level = 1
            elif bits[1] == '1' and bits[2] == '0':
                self.qos_level = 2
            elif bits[1] == '1' and bits[2] == '1':
                print('MALFORMED PACKET!')
            if bits[3] == '1':
                self.retain_flag = 1
            else:
                self.retain_flag = 0

        def read_var_field(self):
            name = b''
            len = int.from_bytes(self.message[self.index:self.index + 2], 'big', signed = False)
            self.index += 2
            for i in range(self.index, self.index + len):
                name += bytes([self.message[i]])
            self.variable_header['topic_name'] = name
            self.index += len
            if self.qos_level == 0:
                self.variable_header['packet_id'] = None
            elif self.qos_level == 1 or self.qos_level == 2:
                self.variable_header['packet_id'] = int.from_bytes(self.message[self.index:self.index + 2], 'big', signed = False)
                self.index += 2
            self.index = self.__get_properties(self.index)


        def __get_properties(self, index):
            if self.message[index] == 0:
                print("Properties field is NULL")
                return index + 1
            else:
                properties = b''
                prop_len = self.message[index]
                for i in range(index + 1, index + prop_len + 1):
                    properties += bytes([self.message[i]])
                self.variable_header['properties'] = properties
                self.__extract_property(properties)
                return index + prop_len + 1

        def __extract_property(self, properties):
            correlation = b''
            response = b''
            idx = 0
            for id in properties:
                idx += 1
                if id == PAYLOAD_FORMAT_INDICATOR:
                    payload_format = properties[idx]
                    self.variable_header['payload_format'] = payload_format
                elif id == SESSION_EXPIRY_INTERVAL:
                    expiry = int.from_bytes(properties[idx:idx + 4], "big",
                                              signed=False)
                    self.variable_header['expiry_interval'] = expiry
                elif id == TOPIC_ALIAS:
                    alias = int.from_bytes(properties[idx:idx + 2], "big",
                                                   signed=False)
                    self.variable_header['topic_alias'] = alias
                elif id == RESPONSE_TOPIC:
                    response_len = int.from_bytes(properties[idx:idx + 2], "big",
                                                 signed=False)
                    aux = idx + 2
                    for i in range(aux, aux + response_len):
                        response += bytes([properties[i]])
                    self.variable_header['response_topic'] = response
                elif id == CORRELATION_DATA:
                    correlation_len = int.from_bytes(properties[idx:idx + 2], "big",
                                                  signed=False)
                    aux = idx + 2
                    for i in range(aux, aux + correlation_len):
                        correlation += bytes([properties[i]])
                    self.variable_header['correlation_data'] = correlation
                elif id == USER_PROPERTY:
                    pass
                elif id == SUBSCRIPTION_IDENTIFIER:
                    pass
                elif id == CONTENT_TYPE:
                    pass

        def read_payload(self):
            self.payload = self.message[self.index:]

# The properties field of a publish packet built and sent by the broker
# will be 0x00

class PUBLISH_builder(Fixed_header):
    def __init__(self):
        Fixed_header.__init__(self)
        self.topic_len = 0
        self.topic = b''
        self.pack_id = 0
        self.properties = bytes([0x00])
        self.payload = b''

    def build(self, dup):
        self.pack_type = 0x3
        # dup = dup, valoare data ca parametru
        # daca dup = 0 pachetul a fost trimis pentru prima data
        # daca dup = 1 pachetul a mai fost trimis inainte
        dup = 0
        qos = 0  # valoare luata din interfata grafica
        retain = 1  # valoare luata din interfata grafica
        self.pack_flags = (self.pack_type << 4) + (dup << 3) + (qos << 1) + retain
        self.pack_flags = self.pack_flags.to_bytes(1,'big',signed=False)
        self.topic = b'unteni'  # valoare luata din interfata grafica
        if qos == 0:
            self.pack_id = None
            msg_id_len = 0
        else:
            self.pack_id = random.randint(1, 65535)
            msg_id_len = 2
        self.payload = b'ce faci dosica?'
        self.topic_len = len(self.topic)
        msg_len = 2 + self.topic_len + msg_id_len + len(self.payload)
        self.remaining_len = self.encode_variable_byte_integer(msg_len)

        if qos != 0:
            packet = b''.join([self.pack_flags, self.remaining_len, self.topic_len.to_bytes(2, 'big'), self.topic,
                               self.pack_id.to_bytes(2, 'big'), bytes([0]), self.payload])
        else:
            packet = b''.join([self.pack_flags, self.remaining_len, self.topic_len.to_bytes(2, 'big'), self.topic,
                                bytes([0]), self.payload])
        return packet
