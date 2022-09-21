from analyzer_socket import AnalyzerCmd, PreampPorts
from time import sleep


def bla(response):
    print("I did it")


with AnalyzerCmd("192.168.1.233", debug_mode=False) as opti:
    print(opti.get_preamp_hardware_info(PreampPorts.PREAMP_PORT_1))
