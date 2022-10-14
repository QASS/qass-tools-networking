from turtle import clear
from analyzer_socket import AnalyzerCmd, PreampPorts, MultiPreampInput
from time import sleep


def bla(response):
    print("I did it")


with AnalyzerCmd("192.168.1.38", debug_mode=True) as opti:
    # opti.import_trigger_list(
    #    "/home/opti/2021_09_16_template_Triggerlist_Straightening_V_2.0.ini", append=True)
    opti.change_preamp_input(PreampPorts.PREAMP_PORT_1,
                             MultiPreampInput.MULTI_INPUT_4)
