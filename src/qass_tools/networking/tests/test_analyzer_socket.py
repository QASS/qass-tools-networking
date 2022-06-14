import pytest
from networking.analyzer_socket import AnalyzerCmd

def test_get_info(monkeypatch):
    def send(command):
        return command
    
    def handle_response(response):
        return response
    
    #monkeypatch.setattr(AnalyzerCmd, "_send", send)
    #monkeypatch.setattr(AnalyzerCmd, "_handle_commserver_response", handle_response)
    
    opti = AnalyzerCmd(ip="192.168.2.67")
    sended_command = opti.get_info()
    assert sended_command['cmd'] == "getinfo"
