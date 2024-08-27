import time
from qass.tools.networking.analyzer_socket import AnalyzerRemote, Channels, Amplitudes

######## Example 1 ############
""" Simple example how to intialize a socket connection to the optimizer and have access to analyzer functions."""
with AnalyzerRemote(ip="ip") as opti:
    opti.set_multiplexer(channel=Channels.CHANNEL_1)
    info = opti.get_project_info()
    print(info)
    opti.set_multiplexer(gain=800)

    proc = opti.get_process_number()

    opti.set_process_comment(proc, "Hello World")

    opti.start_measuring()
    opti.start_sineGenerator(frequency=500, amplitude=Amplitudes.AMP_191_mV)
    time.sleep(2)
    opti.stop_sineGenerator()
    opti.stop_measuring()

######## Example 2 ############
""" Example two shows an easy way to debug system in case you need some more detailed information how to process incomming responses"""
with AnalyzerRemote(ip="ip", debug_mode=True) as opti:
    info = opti.get_project_info()
    print(info)

######## Example 3 ############
""" Example to show how to use report function with an easy callback"""

def own_callback_example(result):
    """Function that prints "I/O state changed" everytime it does.

    Callback function always has response as argument. In this case response is used as event.
    Evertime the event happens, print command is going to be executed.
    """
    if result:
        print("I/O state changed")

with AnalyzerRemote(ip="ip") as opti:
    # Start report
    opti.add_io_report_callback(own_callback_example)
    # Do something
    #
    # stop report automatically without active callback
    opti.remove_io_report_callback(own_callback_example)
