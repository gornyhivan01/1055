import pytest
import socket
import requests.exceptions
from unittest.mock import patch, MagicMock
from tasks import check_availability


def test_check_availability_success():
    with patch('tasks.requests.get') as mock_get, \
         patch('tasks.socket.gethostbyname') as mock_gethostbyname:

        mock_gethostbyname.return_value = "8.8.8.8"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = check_availability("http://example.com")

        assert result["url"] == "http://example.com"
        assert result["status"] == 200
        assert result["online"] is True
        assert result["ip"] == "8.8.8.8"
        mock_get.assert_called_once_with("http://example.com", timeout=10)


def test_check_availability_dns_failure():
    with patch('tasks.socket.gethostbyname') as mock_gethostbyname:
        mock_gethostbyname.side_effect = socket.gaierror("Name or service not known")

        result = check_availability("http://invalid-host.xyz")

        assert result["url"] == "http://invalid-host.xyz"
        assert result["online"] is False
        assert "Could not resolve IP" in result["error"]


def test_check_availability_request_failure():
    with patch('tasks.socket.gethostbyname') as mock_gethostbyname, \
         patch('tasks.requests.get') as mock_get:

        mock_gethostbyname.return_value = "192.0.2.1"
        mock_get.side_effect = requests.exceptions.RequestException("Connection refused")

        result = check_availability("http://timeout.test")

        assert result["url"] == "http://timeout.test"
        assert result["online"] is False
        assert "error" in result