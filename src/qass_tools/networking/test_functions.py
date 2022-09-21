from analyzer_socket import AnalyzerCmd
from time import sleep


def bla(response):
    print("I did it")


with AnalyzerCmd("192.168.1.233", debug_mode=False) as opti:
    opti.set_preamp(gain=900)
