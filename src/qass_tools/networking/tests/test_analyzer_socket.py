import pytest
import mock
from analyzer_socket import AnalyzerCmd
import socket

@pytest.fixture
def create_instance_helper():
    with mock.patch('socket.socket') as socket_mock:
        obj = AnalyzerCmd(ip="192.168.2.67")
        return obj
@

def test_start_measuring(monkeypatch, create_instance_helper):
    # Arrange
    monkeypatch.setattr(socket, "recv", rec_mock)
    # Act
    response = create_instance_helper.start_measuring()
    # Assert
    create_instance_helper.tcp_socket.connect.asssert_called_with(ip="192.168.2.67")    