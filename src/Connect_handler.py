from Fixed_header import Fixed_header

class CONNECT_packet(Fixed_header):
    def __init__(self, message):
        Fixed_header.__init__(self, message)
        self.name_len = None
        self.name = b''
        self.version = None

        self.flags = None
        self.username_flag = None
        self.password_flag = None
        self.will_retain = None
        self.qos_level = None
        self.will_flag = None
        self.clean_session = None
        self.reserved = None

        self.keep_alive = None
        self.id_len = None
        self.id = b''
        self.will_prop_len = None
        self.will_prop = None
        self.will_topic_len = None
        self.will_topic = b''
        self.will_message_len = None
        self.will_message = b''
        self.username_len = None
        self.username = b''
        self.password_len = None
        self.password = b''

    def extract_info(self):
        message = self.message
        self.read_fixed_field()
        self.read_var_field()
        self.read_payload_field()

    def read_payload_field(self):
        self.id_len,self.index = self.get_len_field(self.index)
        if self.id_len != 0:
            self.id = self.message[self.index:self.index+self.id_len].decode('utf-8')
            self.index += self.id_len
        self.index = self.read_will_properties(self.index)

        self.will_topic_len, self.index = self.get_len_field(self.index)
        if self.will_topic_len != 0:
            self.will_topic = self.message[self.index:self.index+self.will_topic_len].decode('utf-8')
            self.index += self.will_topic_len

        self.will_message_len, self.index = self.get_len_field(self.index)
        if self.will_message_len != 0:
            self.will_message = self.message[self.index:self.index+self.will_message_len].decode('utf-8')
            self.index += self.will_message_len

        self.username_len, self.index = self.get_len_field(self.index)
        if self.username_len != 0:
            self.username = self.message[self.index:self.index+self.username_len].decode('utf-8')
            self.index += self.username_len

        self.password_len, self.index = self.get_len_field(self.index)
        if self.password_len != 0:
            self.password = self.message[self.index:self.index + self.password_len].decode('utf-8')
            self.index += self.password_len

    def read_will_properties(self,index):
        if self.message[index] == 0:
            print("Will properties field is NULL")
            return index + 1
        else:
            # nu am vazut pachete cu will properties > 0
            pass

    def read_var_field(self):

        self.index = self.__get_name(self.index)
        self.index = self.__get_flags(self.index)
        self.index = self.__get_keep_alive(self.index)
        self.index = self.__get_properties(self.index)


    def __get_properties(self,index):
        if self.message[index] == 0:
            print("Properties field is NULL")
            return index + 1
        else :
            # nu am vazut pachete cu properties
            pass

    def __get_name(self, index):
        self.name_len = int.from_bytes(self.message[index:index + 2], "big", signed=False)
        index += 2
        for i in range(index, index + self.name_len):
            self.name += bytes([self.message[i]])
        index += self.name_len
        self.version = self.message[index]
        return index + 1

    def __get_keep_alive(self,index):
        self.keep_alive = int.from_bytes(self.message[index:index + 2], "big", signed=False)
        return index + 2


    def __get_flags(self, index):
        flags = self.message[index]
        self.username_flag = (flags & 0b10000000) >> 7
        self.password_flag = (flags & 0b01000000) >> 6
        self.will_retain = (flags & 0b00100000) >> 5
        self.qos_level = (flags & 0b00011000) >> 3
        self.will_flag = (flags & 0b00000100) >> 2
        self.clean_session = (flags & 0b00000010) >> 1
        self.reserved = (flags & 0b00000001)
        return index + 1

    def get_len_field(self,index):
        len = int.from_bytes(self.message[self.index:self.index + 2], "big", signed=False)
        return len, index + 2

    def print_all(self):
        print(f'Message = {self.message}\n'
              f'Type = {self.pack_type}\n'
              f'Message length = {self.remaining_len}\n'
              f'Protocol name length = {self.name_len}\n'
              f'Protocol name = {self.name}\n'
              f'Protocol version = {self.version}\n')

        print("Protocol flags : ")
        self.print_flags()

        print(f'Keep alive  = {self.keep_alive}\n'
              f'Id length = {self.id_len}\n'
              f'Id = {self.id}\n'
              f'Will topic length = {self.will_topic_len}\n'
              f'Will topic = {self.will_topic}\n'
              f'Will message length = {self.will_message_len}\n'
              f'Will message = {self.will_message}\n'
              f'Username length = {self.username_len}\n'
              f'Username = {self.username}\n'
              f'Password length = {self.password_len}\n'
              f'Password = {self.password}\n')

    def print_flags(self):
        print(f'Username flag = {self.username_flag}\n'
              f'Password flag = {self.password_flag}\n'
              f'Will retain = {self.will_retain}\n'
              f'QoS level = {self.qos_level}\n'
              f'Will flag = {self.will_flag}\n'
              f'Clean Session = {self.clean_session}\n'
              f'Reserved = {self.reserved}\n')




def get_bits(byte):
    bits = format(byte, 'b')
    while len(bits) < 8:
        bits = '0' + bits
    return bits


def decode_variable_byte_integer(encoded_bytes):
    multiplier = 1
    value = 0
    index = 0

    while True:
        encoded_byte = encoded_bytes[index]
        decoded_value = encoded_byte & 0x7F
        value += decoded_value * multiplier

        if multiplier > 128 * 128 * 128:
            raise ValueError("Malformed Variable Byte Integer")

        multiplier *= 128
        index += 1

        if not (encoded_byte & 0x80):
            break

    return value, index


def encode_variable_byte_integer(value):
    encoded_bytes = bytearray(0)

    while True:
        encoded_byte = int(value % 128)
        value = int(value / 128)
        if value > 0:
            encoded_byte = encoded_byte | 0x80
        encoded_bytes.append(encoded_byte)

        if value == 0:
            break
    return encoded_bytes
