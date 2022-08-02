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


callbacks["2"].append("nice")
callbacks["3"].append("nein")
callbacks["2"].append("nice")
print(callbacks)


def shift_binary(original_bin: int) -> int:
    """Helper to invert incomming binaries.
    :param original_bin: Incomming binary
    :type original_bin: int
    :return: Inversed binary
    :rtype: int
    """
    new_val = 0
    new_binary = ""
    for i in range(16):
        bit_state = (original_bin & (1 << i) >> i)
        print(bit_state)
        new_val = new_val | (bit_state << (16-i))

    return str(new_val)


def binary_to_hexa(binary: str):
    deci_num = int(binary, 2)
    print(binary)
    print(hex(deci_num))
    return hex(deci_num)


#b = "00100000 00000000"
# b = b.replace(" ", "")  # delete space
#b_shifted = shift_binary(int(b))
# binary_to_hexa(b_shifted)
