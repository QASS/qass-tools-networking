import time
from qass_tools.networking.analyzer_socket import AnalyzerCmd, Channels, Amplitudes, PreampPorts

######## Example 1 ############
""" Simple example how to intialize a socket connection to the optimizer and have access to analyzer functions."""
with AnalyzerCmd(ip="192.168.2.67") as opti:
    opti.set_preamp(channel=Channels.CHANNEL_1)
    info = opti.get_info()
    print(info)
    opti.set_preamp(gain=800)

    proc = opti.get_process_number()

    opti.set_process_comment("Hey ich bims, eins Kommentar")

    opti.start_measuring()
    opti.start_sineGenerator(frequency=500, amplitude=Amplitudes.AMP_191_mV)
    time.sleep(2)
    opti.stop_sineGenerator()
    opti.stop_measuring()

######## Example 2 ############
""" Example two shows an easy way to debug system in case you need some more detailed information how to process incomming responses"""
with AnalyzerCmd(ip="192.168.2.67", debug_mode=True) as opti:
    info = opti.get_info()
    print(info)

######## Example 3 ############
""" Example to show how to use report function with an easy callback"""


def own_callback_example(result):
    """Function that prints "I/O state changed" everytime it does.

    Callback function always becomes response as arg. In this case response is used as event.
    Evertime this event happens print command will happen.
    """
    if result:
        print("I/O state changed")


with AnalyzerCmd(ip="192.168.2.67") as opti:
    # Start report
    opti.add_io_report_callback(own_callback_example)
    # Do something
    #
    # stop report automatically without active callback
    opti.remove_io_report_callback(own_callback_example)


######## Example 4 ############
""" Possible first start for optimizer script"""
with AnalyzerCmd(ip="192.168.2.67") as opti:
    project_dict = opti.get_project_info()
    current_state = opti.get_service_parameter("pFPGAVersion")
    if current_state is not 2:
        opti.set_service_parameter("pFPGAVersion", 2)
    opti.pulsetest_port(PreampPorts.PREAMP_PORT_1)
    opti.import_patterns("/home/opti/patterns/")
