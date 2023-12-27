class Fixed_header():
    def __init__(self, message):
        self.message = message
        self.index = 0
        self.pack_type = None
        self.pack_flags = None
        self.remaining_len = 0

    def read_fixed_field(self):
        self.pack_type = self.message[0] >> 4
        self.pack_flags = self.message[0] & 0x0f
        self.remaining_len, self.index = self.variable_byte_integer(1)

    def variable_byte_integer(self, i):
        ret = b''
        while self.message[i] >> 7 == 1:
            ret += bytes([self.message[i]])
            i += 1
        ret += bytes([self.message[i]])
        decoded_value, index = self.decode_variable_byte_integer(ret)
        return decoded_value, i + 1

    def print_fixed_field(self):
        print(f'Pack Type : {self.pack_type}\n'
              f'Pack Flags : {self.pack_flags}\n'
              f'Remaining Length : {self.remaining_len}')

    def decode_variable_byte_integer(self,encoded_bytes):
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
