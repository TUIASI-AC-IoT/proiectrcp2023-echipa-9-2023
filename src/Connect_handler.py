from Fixed_header import *

class CONNECT_packet(Fixed_header):
    def __init__(self, message):
        Fixed_header.__init__(self, message)
        self.variable_header = {
            'name_len': None,
            'name': b'',
            'version': None,
            'username_flag': None,
            'password_flag': None,
            'will_retain': None,
            'qos_level': None,
            'will_flag': None,
            'clean_session': None,
            'reserved': None,
            'keep_alive': None,
            'prop_len': 0,
            'properties': b'',
            'expiry_interval': None,
            'recv_max': None,
            'max_pack_size': None,
            'topic_alias': None,
            'request_response': False,
            'request_problem': False
        }
        self.user_property = {}
        self.payload = {
            'id_len': None,
            'id': b'',
            'will_prop_len': None,
            'will_prop': b'',
            'will_topic_len': 0,
            'will_topic': b'',
            'will_message_len': None,
            'will_message': b'',
            'username_len': None,
            'username': b'',
            'password_len': None,
            'password': b''
        }
        self.extract_info()

    def extract_info(self):
        self.read_fixed_field()
        self.read_var_field()
        self.read_payload_field()

    def read_payload_field(self):
        id_len,self.index = self.get_len_field(self.index)
        if id_len != 0:
            id = self.message[self.index:self.index + id_len].decode('utf-8')
            self.index += id_len
            self.payload['id_len'] = id_len
            self.payload['id'] = id

        if self.variable_header['will_flag'] != 0:
            self.index = self.read_will_properties(self.index)
            will_topic_len, self.index = self.get_len_field(self.index)
            if will_topic_len != 0:
                will_topic = self.message[self.index:self.index+will_topic_len].decode('utf-8')
                self.index += will_topic_len
                self.payload['will_topic_len'] = will_topic_len
                self.payload['will_topic'] = will_topic

            will_message_len, self.index = self.get_len_field(self.index)
            if will_message_len != 0:
                will_message = self.message[self.index:self.index+will_message_len].decode('utf-8')
                self.index += will_message_len
                self.payload['will_message_len'] = will_message_len
                self.payload['will_mesage'] = will_message

        username_len, self.index = self.get_len_field(self.index)
        if username_len != 0:
            username = self.message[self.index:self.index+username_len].decode('utf-8')
            self.index += username_len
            self.payload['username_len'] = username_len
            self.payload['username'] = username

        password_len, self.index = self.get_len_field(self.index)
        if password_len != 0:
            password = self.message[self.index:self.index + password_len].decode('utf-8')
            self.index += password_len
            self.payload['password_len'] = password_len
            self.payload['password'] = password

    def read_will_properties(self,index):
        if self.message[index] == 0:
            print("Will properties field is NULL")
            return index + 1
        else:
            will_prop = b''
            will_prop_len = self.message[index]
            for i in range(self.index,self.index + will_prop_len + 1):
                will_prop += bytes([self.message[i]])

            self.payload['will_prop_len'] = will_prop_len
            self.payload['will_prop'] = will_prop

            return index + will_prop_len + 1

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
            properties = b''
            prop_len = self.message[index]
            for i in range(index + 1,index + prop_len + 1):
                properties += bytes([self.message[i]])
            self.variable_header['prop_len'] = prop_len
            self.variable_header['properties'] = properties
            self.__extract_property(properties)
            return index + prop_len + 1

    def __extract_property(self,properties):
        idx = 0
        for id in properties:
            idx += 1
            if id == SESSION_EXPIRY_INTERVAL:
                expiry_interval = int.from_bytes(properties[idx:idx + 4], "big",
                                                    signed=False)
                self.variable_header['expiry_interval'] = expiry_interval
            elif id == RECEIVE_MAXIMUM:
                recv_max = int.from_bytes(properties[idx:idx + 2], "big",
                                                    signed=False)
                self.variable_header['recv_max'] = recv_max
            elif id == MAXIMUM_PACKET_SIZE:
                max_pack_size = int.from_bytes(properties[idx:idx + 4], "big",
                                                    signed=False)
                self.variable_header['max_pack_size'] = max_pack_size
            elif id == TOPIC_ALIAS_MAXIMUM:
                topic_alias = int.from_bytes(properties[idx:idx + 2], "big",
                                                    signed=False)
                self.variable_header['topic_alias'] = topic_alias
            elif id == REQUEST_RESPONSE_INFORMATION:
                request_response = properties[idx]
                self.variable_header['request_response'] = request_response
            elif id == REQUEST_PROBLEM_INFORMATION:
                max_pack_size = properties[idx]
                self.variable_header['max_pack_size'] = max_pack_size
            elif id == USER_PROPERTY:
                key, val = self.__get_user_field(idx, properties)
                self.user_property[key] = val

    def __get_user_field(self,idx,properties):
        key_len = int.from_bytes(properties[idx:idx + 2], "big", signed=False)
        key = properties[idx + 2:idx + key_len + 2].decode('utf-8')
        val_len = int.from_bytes(properties[idx + key_len + 2:idx + key_len + 4], "big", signed=False)
        val = properties[idx + key_len + 4:idx + key_len + val_len + 4].decode('utf-8')
        return key, val

    def __get_name(self, index):
        name = b''
        name_len = int.from_bytes(self.message[index:index + 2], "big", signed=False)
        index += 2
        for i in range(index, index + name_len):
            name += bytes([self.message[i]])
        index += name_len
        version = self.message[index]

        self.variable_header['name_len'] = name_len
        self.variable_header['name'] = name
        self.variable_header['version'] = version

        return index + 1

    def __get_keep_alive(self,index):
        keep_alive = int.from_bytes(self.message[index:index + 2], "big", signed=False)
        self.variable_header['keep_alive'] = keep_alive
        return index + 2

    def __get_flags(self, index):
        flags = self.message[index]
        self.variable_header['username_flag'] = (flags & 0b10000000) >> 7
        self.variable_header['password_flag'] = (flags & 0b01000000) >> 6
        self.variable_header['will_retain'] = (flags & 0b00100000) >> 5
        self.variable_header['qos_level'] = (flags & 0b00011000) >> 3
        self.variable_header['will_flag'] = (flags & 0b00000100) >> 2
        self.variable_header['clean_session'] = (flags & 0b00000010) >> 1
        self.variable_header['reserved'] = (flags & 0b00000001)
        return index + 1

    def get_len_field(self,index):
        len = int.from_bytes(self.message[index:index + 2], "big", signed=False)
        return len, index + 2

    def print_all(self):
        print(f'Message = {self.message}\n'
              f'Type = {self.pack_type}\n'
              f'Message length = {self.remaining_len}\n'
              f'Protocol name length = {self.variable_header["name_len"]}\n'
              f'Protocol name = {self.variable_header["name"]}\n'
              f'Protocol version = {self.variable_header["version"]}\n'
              )

        print("Protocol flags : ")
        self.print_flags()

        print(f'Keep alive  = {self.variable_header["keep_alive"]}\n'
              f'Id length = {self.payload["id_len"]}\n'
              f'Id = {self.payload["id"]}\n'
              f'Will topic length = {self.payload["will_topic_len"]}\n'
              f'Will topic = {self.payload["will_topic"]}\n'
              f'Will message length = {self.payload["will_message_len"]}\n'
              f'Will message = {self.payload["will_message"]}\n'
              f'Username length = {self.payload["username_len"]}\n'
              f'Username = {self.payload["username"]}\n'
              f'Password length = {self.payload["password_len"]}\n'
              f'Password = {self.payload["password"]}\n')

    def print_flags(self):
        print(f'Username flag = {self.variable_header["username_flag"]}\n'
              f'Password flag = {self.variable_header["password_flag"]}\n'
              f'Will retain = {self.variable_header["will_retain"]}\n'
              f'QoS level = {self.variable_header["qos_level"]}\n'
              f'Will flag = {self.variable_header["will_flag"]}\n'
              f'Clean Session = {self.variable_header["clean_session"]}\n'
              f'Reserved = {self.variable_header["reserved"]}\n')



