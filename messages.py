

def serialize_message(message):
    return [ord(character) for character in message]

def deserialize_message(ascii_list):
    return "".join([chr(num) for num in ascii_list])