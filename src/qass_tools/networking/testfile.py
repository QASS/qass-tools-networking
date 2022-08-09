from collections import defaultdict

recognition = "cmd"
callbacks = defaultdict(list)


def append(key, value):
    callbacks[key].append(value)


def print_two(result):
    print(result)
    print("No way")


def kill_callback(callback):
    callbacks[recognition].remove(callback)


def shift_binary(original_bin) -> int:
    """Helper to invert incomming binaries.
    :param original_bin: Incomming binary
    :type original_bin: str
    :return: Inversed binary
    :rtype: str
    """
    # Elias Version didn't worked
    #new_val = 0
    # for i in range(16):
    #    bit_state = (original_bin & (1 << i) >> i)
    #    print("bit state", bit_state)
    #    new_val = new_val | (bit_state << (16-i))

    # return new_val

    new_val = [0] * len(original_bin)
    for (i, bit) in enumerate(original_bin):
        new_val[len(new_val)-1-i] = bit

    return "".join(new_val)


def binary_to_hexa(binary: str):
    #deci_num = int(binary, 2)
    print(binary)
    #hexa = hex(deci_num)


b = "10110000 00000000"
b = b.replace(" ", "")  # delete space

b_shifted = shift_binary(b)
binary_to_hexa(b_shifted)
