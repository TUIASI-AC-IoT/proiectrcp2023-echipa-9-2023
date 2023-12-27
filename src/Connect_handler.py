from Fixed_header import *

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
        self.prop_len = 0
        self.properties = b''
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

        self.expiry_interval = None
        self.recv_max = None
        self.max_pack_size = None
        self.topic_alias = None
        self.request_response = False
        self.request_problem = False
        self.user_property = {}

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

        if self.will_flag != 0:
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
            #TODO
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
            self.prop_len = self.message[index]
            for i in range(index + 1,index + self.prop_len):
                self.properties += bytes([self.message[i]])
            self.__extract_property()
            return index + self.prop_len + 1

    def __extract_property(self):
        cnt = 0
        idx = 0
        for id in self.properties:
            idx += 1
            if id == SESSION_EXPIRY_INTERVAL:
                self.expiry_interval = int.from_bytes(self.properties[idx:idx + 4], "big",
                                                      signed=False)
                print(f'expiry : {self.expiry_interval}')
            elif id == RECEIVE_MAXIMUM:
                self.recv_max = int.from_bytes(self.properties[idx:idx + 2], "big",
                                                      signed=False)
                print(f'recv max : {self.recv_max}')
            elif id == MAXIMUM_PACKET_SIZE:
                self.max_pack_size = int.from_bytes(self.properties[idx:idx + 4], "big",
                                               signed=False)
                print(f'max pack size : {self.max_pack_size}')
            elif id == TOPIC_ALIAS_MAXIMUM:
                self.topic_alias = int.from_bytes(self.properties[idx:idx + 2], "big",
                                                    signed=False)
                print(f'topic alias : {self.topic_alias}')
            elif id == REQUEST_RESPONSE_INFORMATION:
                self.request_response = self.properties[idx]
                print(f'request response : {self.request_response}')
            elif id == REQUEST_PROBLEM_INFORMATION:
                self.max_pack_size = self.properties[idx]
                print(f'request problem : {self.max_pack_size}')
            elif id == USER_PROPERTY:
                key, val = self.__get_user(idx)
                self.user_property[key] = val
                pass

    def __get_user(self,idx):
        key_len = int.from_bytes(self.properties[idx:idx + 2], "big", signed=False)
        key = self.properties[idx + 2:idx + key_len + 2].decode('utf-8')
        val_len = int.from_bytes(self.properties[idx + key_len + 2:idx + key_len + 4], "big", signed=False)
        val = 20 #TODO
        return key, val

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
        len = int.from_bytes(self.message[index:index + 2], "big", signed=False)
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



