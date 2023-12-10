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
        print(value)
        encoded_bytes.append(encoded_byte)

        if value == 0:
            break
    return encoded_bytes


class CONNECT_packet():
    def __init__(self,message):
        self.index = 0
        self.message = message
        self.type = None
        self.len = None
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
        self.will_topic_len = None
        self.will_topic = b''
        self.will_message_len = None
        self.will_message = None
        self.username_len = None
        self.username = b''
        self.password_len = None
        self.password = b''

    def extract_info(self):
        message = self.message
        self.type = message[0] >> 4
        self.len = message[1]
        self.name_len = int(bytearray([message[2], message[3]]).hex())

        for i in range(4,self.name_len + 4):
            self.name += bytes([message[i]])
        self.name = self.name.decode('utf-8')
        self.index = self.name_len + 4

        self.version = message[self.index]

        self.flags = message[self.index + 1]
        self.get_flags()

        self.__get_keep_alive(self.index)

        self.__get_id(self.index)

        self.__get_will(self.index)

        self.__get_username(self.index)

        self.__get_password(self.index)

        self.print_all()

    def __get_keep_alive(self,index):
        if self.message[index + 2] != 0:
            self.keep_alive = int(bytearray([self.message[index + 2], self.message[index + 3]]).hex())
        else:
            self.keep_alive = self.message[index + 3]
        self.index = index + 4

    def __get_id(self,index):
        if self.message[index] != 0:
            self.id_len = int(bytearray([self.message[index], self.message[index + 1]]).hex())
        else:
            self.id_len = self.message[index + 1]
        index = index + 2
        if self.id_len:
            for i in range(index, index+self.id_len):
                self.id += bytes([self.message[i]])
            self.id = self.id.decode('utf-8')
        self.index = index + self.id_len

    def __get_will(self,index):
        if self.will_flag == 1:
            if self.message[index] != 0:
                self.will_topic_len = int(bytearray([self.message[index], self.message[index + 1]]).hex())
            else:
                self.will_topic_len = self.message[index + 1]
            index = index + 2
            if self.will_topic_len != 0:
                for i in range(index, index+self.will_topic_len):
                    self.will_topic += bytes([self.message[i]])
                self.will_topic = self.will_topic.decode('utf-8')
            index = index + self.will_topic_len

            if self.message[index] != 0:
                self.will_message_len = int(bytearray([self.message[index], self.message[index + 1]]).hex())
            else:
                self.will_message_len = self.message[index + 1]
            index = index + 2
            if self.will_message_len != 0:
                for i in range(index, index+self.will_message_len):
                    self.will_message += bytes([self.message[i]])
                self.will_message = self.will_message.decode('utf-8')
            self.index = index + self.will_message_len

    def __get_username(self,index):
        if self.username_flag == 1:
            if self.message[index] != 0:
                self.username_len = int(bytearray([self.message[index], self.message[index + 1]]).hex())
            else:
                self.username_len = self.message[index + 1]
            index = index + 2
            if self.username_len != 0:
                for i in range(index, index+self.username_len):
                    self.username += bytes([self.message[i]])
                self.username = self.username.decode('utf-8')
            self.index = index + self.username_len

    def __get_password(self,index):
        if self.password_flag == 1:
            if self.message[index] != 0:
                self.password_len = int(bytearray([self.message[index], self.message[index + 1]]).hex())
            else:
                self.password_len = self.message[index + 1]
            index = index + 2
            if self.password_len != 0:
                for i in range(index, index+self.password_len):
                    self.password += bytes([self.message[i]])
                self.password = self.password.decode('utf-8')
            self.index = index + self.password_len

    def get_flags(self):
        flags = self.flags
        self.username_flag = (flags & 0b10000000) >> 7
        self.password_flag = (flags & 0b01000000) >> 6
        self.will_retain = (flags & 0b00100000) >> 5
        self.qos_level = (flags & 0b00011000) >> 3
        self.will_flag = (flags & 0b00000100) >> 2
        self.clean_session = (flags & 0b00000010) >> 1
        self.reserved = (flags & 0b00000001)

    def print_all(self):
        print(f'Message = {self.message}\n'
              f'Type = {self.type}\n'
              f'Message length = {self.len}\n'
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
              f'Cleas Session = {self.clean_session}\n'
              f'Reserved = {self.reserved}\n')
