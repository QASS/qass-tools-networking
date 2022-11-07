from turtle import clear
from analyzer_socket import AnalyzerCmd, PreampPorts, MultiPreampInput, Channels
from time import sleep


def bla(response):
    print("I did it")


# 38
with AnalyzerCmd("192.168.1.132", debug_mode=True) as opti:
    # opti.flash_preamp_software(preampport=PreampPorts.PREAMP_PORT_1,
    #                           filepath="/home/opti/Downloads/preamp_V2.0.2.9_pulse.hex")
    opti.import_patterns("/home/opti/testing_bitch/")
