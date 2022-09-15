from analyzer_socket import AnalyzerCmd
from time import sleep


def bla(response):
    print("I did it")


with AnalyzerCmd("192.168.1.50", debug_mode=False) as opti:
    opti.start_operator(
        "Test_PY", "loop from 0 to - 1 simulation 2", user_callback=bla)
    opti.get_heartbeat()
