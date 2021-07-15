import pytest
import json
import requests

from services.ecs import EcsFargate
from unittest.mock import patch


@patch("requests.get")
def test_get_container_metadata_v4_successful(requests_get_function):
    requests_get_function.return_value = type(
        "fake_request", (), {"json": lambda: json.dumps({"A": "B"}), "status_code": 200}
    )
    result = EcsFargate().get_container_metadata_v4()
    assert result == {"A": "B"}


@patch("requests.get")
def test_get_container_metadata_v4_failed_bad_json_raise_errors(requests_get_function):
    requests_get_function.return_value = type(
        "fake_request", (), {"json": lambda: "abc", "status_code": 200}
    )
    with pytest.raises(json.decoder.JSONDecodeError):
        EcsFargate(raise_errors=True).get_container_metadata_v4()


@patch("requests.get")
def test_get_container_metadata_v4_failed_bad_json_swallow_errors(
    requests_get_function,
):
    requests_get_function.return_value = type(
        "fake_request", (), {"json": lambda: "abc", "status_code": 200}
    )
    result = EcsFargate(raise_errors=False).get_container_metadata_v4()
    assert result == {}


@patch("requests.get")
def test_get_container_metadata_v4_raises_invalid_status_code(requests_get_function):
    requests_get_function.return_value = type(
        "fake_request",
        (),
        {"json": lambda: "abc", "status_code": 401, "text": lambda: "abc"},
    )
    with pytest.raises(RuntimeError):
        EcsFargate(raise_errors=True).get_container_metadata_v4()


@pytest.mark.parametrize(
    "exception",
    [
        requests.exceptions.BaseHTTPError,
        requests.exceptions.ReadTimeout,
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ],
)
@patch("requests.get")
def test_get_container_metadata_v4_handles_http_exceptions(
    requests_get_function, exception
):
    requests_get_function.side_effect = exception
    with pytest.raises(exception):
        EcsFargate(raise_errors=True).get_container_metadata_v4()

    result_no_raise = EcsFargate(raise_errors=False).get_container_metadata_v4()
    assert result_no_raise == {}
