from turtle import clear
from analyzer_socket import AnalyzerCmd, PreampPorts, MultiPreampInput, Channels
from time import sleep


def bla(response):
    print("I did it")


# 38
with AnalyzerCmd("192.168.1.132", debug_mode=True) as opti:
    opti.import_patterns("/home/Downloads/pattern_cr1")
