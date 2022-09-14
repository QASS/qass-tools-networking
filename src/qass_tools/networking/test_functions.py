from analyzer_socket import AnalyzerCmd
from time import sleep

with AnalyzerCmd("192.168.1.50", debug_mode=True) as opti:
    opti.load_test_project()
