import pytest
import mock
from analyzer_socket import AnalyzerCmd
import socket
from unittest.mock import Mock

@pytest.fixture
def create_instance_helper():
    with mock.patch('socket.socket') as socket_mock:
        obj = AnalyzerCmd(ip="192.168.2.67")
        return obj
@pytest.fixture
def send_helper(monkeypatch):
    def send_wrapper(self,some_command):
        pass
    monkeypatch.setattr(socket,"sendall", send_wrapper)

def test_start_measuring(monkeypatch, create_instance_helper):
    # Arrange
    expected_response = bytes(b'\x00B{"cmd":"responseappcmd","ok":true,"p1":"startMeasuring","v":"2.7"}')
    recv_mock = Mock(return_value=expected_response)
    monkeypatch.setattr(socket,"recv", recv_mock)
    # Act
    create_instance_helper.start_measuring()
    # Assert
    #create_instance_helper.tcp_socket.connect.asssert_called_with(ip="192.168.2.67")    