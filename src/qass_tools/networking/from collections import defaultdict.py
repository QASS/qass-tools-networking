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


append(recognition, print)
append(recognition, print_two)

print(len(callbacks[recognition]))
print(callbacks[recognition].index(print))
callbacks[recognition][1]("bam")
for c in range(0, len(callbacks[recognition])):
    print(c)
# for x in callbacks[recognition]:
#    callbacks[recognition][x]("bam")
#
