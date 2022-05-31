import pytest
from networking.analyzer_socket import AnalyzerCmd

opti = AnalyzerCmd(ip="192.168.1.50")
def test_get_info():
    info = opti.get_info()
    assert type(info) is dict

def test_get_process_number():
    proc = opti.get_process_number()
    assert type(proc) is int


