from turtle import clear
from analyzer_socket import AnalyzerCmd, PreampPorts, MultiPreampInput, Channels
from time import sleep


def bla(response):
    print("I did it")


# 38
with AnalyzerCmd("192.168.1.38", debug_mode=True) as opti:
    # opti.change_preamp_input(PreampPorts.PREAMP_PORT_1,
    #                         MultiPreampInput.MULTI_INPUT_4)
   # opti.flash_preamp_software(preampport=PreampPorts.PREAMP_PORT_1,
   #                            filepath="/home/opti/Downloads/preamp_V2.0.2.9_pulse.hex")
  #  sleep(15)
