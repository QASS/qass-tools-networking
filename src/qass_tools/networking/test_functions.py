from analyzer_socket import AnalyzerCmd
from time import sleep


def bla(response):
    print("I did it")


with AnalyzerCmd("192.168.1.50", debug_mode=False) as opti:
    opti.set_preamp()
