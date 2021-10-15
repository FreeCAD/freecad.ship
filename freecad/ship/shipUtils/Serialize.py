import pickle


# The number of bytes of each integer. 32 bits integers are considered for the
# time being
INT_SIZE = 4


def serialize(obj):
    """Create an integers list that can be stored in a App::PropertyIntegerList

    Position arguments:
    obj -- Any object to be serialized

    Returns:
    The list of integers. The first integer is the length of the bytes array
    """
    b = pickle.dumps(obj)
    # Get the length of the original bytes, and extend them to be multiple of
    # the integer size
    ints = [len(b)]
    while len(b) % INT_SIZE:
        b += b'\x00'
    # Convert the object in a list of integers
    for i in range(len(b) // INT_SIZE):
        i0 = i * INT_SIZE
        ints.append(int.from_bytes(b[i0:i0 + INT_SIZE], "little"))
    return ints


def unserialize(data):
    """Recover back the information serialized with serialize()

    Position arguments:
    data -- The list of integers obtained with serialize()

    Returns:
    The original object
    """
    l = data[0]
    # Convert everything in bytes again
    b = b''
    for i in data[1:]:
        b += i.to_bytes(INT_SIZE, byteorder='little')
    # Truncate to the original size and unpickle
    return pickle.loads(b[:l])
