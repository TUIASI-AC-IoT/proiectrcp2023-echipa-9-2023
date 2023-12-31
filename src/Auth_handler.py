import Fixed_header

class AUTH_packet(Fixed_header):
    def __init__(self, message):
        super().__init__(message)
        self.variable_header = {
            'auth_reason_code': None,
            'prop_len': 0,
            'properties': b''
        }
        self.extract_info()

    def extract_info(self):
        self.read_fixed_field()
        self.read_var_header()

    def read_var_header(self):
        self.variable_header['auth_reason_code'] = self.message[self.index]
        self.index += 1

        self.index = self.__get_properties(self.index)

    def __get_properties(self, index):
        if self.message[index] == 0:
            print("Properties field is NULL")
            return index + 1
        else:
            properties = b''
            prop_len = self.decode_variable_byte_integer(self.message[index:])
            index += prop_len[1]
            for i in range(index, index + prop_len[0]):
                properties += bytes([self.message[i]])
            self.variable_header['prop_len'] = prop_len[0]
            self.variable_header['properties'] = properties

            self.__extract_property(properties, index)
            return index + prop_len[0]

    def __extract_property(self, properties, index):
        while index < len(properties):
            property_identifier = properties[index]
            index += 1
            if property_identifier == AUTHENTICATION_METHOD:
                length = properties[index]
                index += 1
                value = properties[index:index + length].decode('utf-8')
                index += length
                self.variable_header['authentication_method'] = value

    def print_all(self):
        print(f'Packet Type: {self.pack_type}')
        print(f'Remaining Length: {self.remaining_len}')
        print(f'Authenticate Reason Code: {self.variable_header["auth_reason_code"]}')

        print('Properties:')
        for key, value in self.variable_header.items():
            if key != 'properties':
                print(f'  {key}: {value}')

        print(f'Raw Properties: {self.variable_header["properties"]}')