from analyzer_socket import AnalyzerCmd
import json

with AnalyzerCmd("192.168.1.50", debug_mode=True) as opti:
    opti.create_project("test")
