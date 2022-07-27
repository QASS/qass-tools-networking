import time
import queue
from qass_tools.networking.analyzer_socket import AnalyzerCmd

######## Example 1 ############
""" Simple example how to intialize a socket connection to the optimizer and have access to analyzer functions.
"""
with AnalyzerCmd(ip="192.168.2.67") as opti:
    opti.set_preamp(channel=3)
    info = opti.get_info()
    print(info)
    opti.set_preamp(gain=800)

    proc = opti.get_process_number()

    opti.set_process_comment("Hey ich bims, eins Kommentar")

    opti.start_measuring()
    opti.start_sineGenerator(500, 191)
    time.sleep(2)
    opti.stop_sineGenerator()
    opti.stop_measuring()

######## Example 2 ############
""" Example two shows an easy way to debug system in case you need some more detailed information how to process incomming responses
"""
with AnalyzerCmd(ip="192.168.2.67", debug_mode=True) as opti:
    info = opti.get_info()
    print(info)

######## Example 3 ############
""" Example to show how to use report function with an easy callback
"""


def own_callback_example(result):
    """Function that prints "I/O state changed" everytime it does.

    Callback function always becomes response as arg. In this case response is used as event.
    Evertime this event happens print command will happen.
    """
    if result:
        print("I/O state changed")


with AnalyzerCmd(ip="192.168.2.67") as opti:
    opti.set_io_report(own_callback_example, mode="enable")

######## Example 4 ############
""" Example to show how to use report function with an easy callback
"""
q = queue.Queue()


def getter(queue_obj):
    """ Helper tp get queur content. If you want to check your command for failure, use the check_response function.
    """
    resp = q.get()
    AnalyzerCmd.check_response(resp)
    return resp


def own_callback_example_return(result, queue_var=q):
    """Function that prints a state change everytime it does and returns analyzer repsonse.

    Callback function always becomes response as arg. To parse inforamtion betweenthe threads,
    use a queue object.
    """
    print("Proces number changend")
    # do something more

    return queue_var.put(result)


with AnalyzerCmd(ip="192.168.2.67") as opti:
    opti.set_process_number_report(
        own_callback_example_return, mode="enable")
    result = getter(q)
