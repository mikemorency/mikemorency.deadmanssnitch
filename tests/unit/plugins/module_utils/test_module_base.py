from __future__ import absolute_import, division, print_function

__metaclass__ = type

import mock
from unittest.mock import Mock, patch

from ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.module_base import (
    ModuleBase,
)
from ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.client import (
    RequestError
)
from ansible.module_utils.basic import env_fallback


class DummyRequest:
    def __init__(self, url="http://example.com", method="GET", headers=None, body="body"):
        self.url = url
        self.method = method
        if headers is None:
            self.headers = {"h": "v"}
        else:
            self.headers = headers
        self.body = body


class DummyResponse:
    def __init__(self, status_code=404, reason="Not Found"):
        self.status_code = status_code
        self.reason = reason

    def json(self):
        return {"error": "not found"}


class DummyHTTPError(Exception):
    def __init__(self, request=DummyRequest(), response=DummyResponse()):
        self.request = request
        self.response = response


class TestModuleBase:
    def test_init(self):
        mock_module = Mock(params={"api_key": "test_key"})
        module = ModuleBase(mock_module)
        assert module.module == mock_module
        assert module.params == mock_module.params
        assert module.client is not None

    def test_base_argument_spec(self):
        assert ModuleBase.base_argument_spec() == {
            "api_key": dict(
                type="str", required=True, fallback=(env_fallback, ["DMS_API_KEY"]), no_log=True
            ),
        }

    def test_handle_missing_lib_calls_fail_json(self):
        mock_module = Mock(params={"api_key": "test_key"})
        module = ModuleBase(mock_module)
        module.module.fail_json = Mock()
        module.handle_missing_lib("requests", "some exception")
        module.module.fail_json.assert_called_once()
        args, kwargs = module.module.fail_json.call_args
        assert "requests" in kwargs["msg"]
        assert kwargs["exception"] == "some exception"

    def test_handle_exception_calls_handle_http_error_for_http_error(self):
        mock_module = Mock(params={"api_key": "test_key"})
        module = ModuleBase(mock_module)
        module.handle_http_error = Mock()
        # Patch isinstance to return True for HTTPError
        error = RequestError(exception=DummyHTTPError())
        module.handle_exception(error)
        module.handle_http_error.assert_called_once_with(error.exception)

    def test_handle_exception_calls_fail_json_for_other_errors(self):
        mock_module = Mock(params={"api_key": "test_key"})
        module = ModuleBase(mock_module)
        module.module.fail_json = Mock()
        error = Exception("fail")
        module.handle_exception(error)
        module.module.fail_json.assert_called_once()
        args, kwargs = module.module.fail_json.call_args
        assert "fail" in kwargs["msg"]

    def test_handle_http_error_calls_fail_json_with_fields(self):
        mock_module = Mock(params={"api_key": "test_key"})
        module = ModuleBase(mock_module)
        module.module.fail_json = Mock()
        error = DummyHTTPError(
            request=DummyRequest(),
            response=DummyResponse()
        )
        module.handle_http_error(error)
        module.module.fail_json.assert_called_once()
        args, kwargs = module.module.fail_json.call_args
        assert "HTTP error" in kwargs["msg"]
        assert kwargs["request_url"] == "http://example.com"
        assert kwargs["request_method"] == "GET"
        assert kwargs["request_headers"] == {"h": "v"}
        assert kwargs["request_body"] == "body"
        assert kwargs["code"] == 404
        assert kwargs["response"] == {"error": "not found"}

    def test_fail_unable_to_find_snitch_id(self):
        mock_module = Mock(params={"api_key": "test_key", "id": "foo", "name": None})
        module = ModuleBase(mock_module)
        module.module.fail_json = Mock()
        module.fail_unable_to_find_snitch()
        module.module.fail_json.assert_called_once()
        args, kwargs = module.module.fail_json.call_args
        assert "Unable to find snitch" in kwargs["msg"]
        assert kwargs["searched"]["param"] == "id"
        assert kwargs["searched"]["value"] == "foo"

    def test_fail_unable_to_find_snitch_name(self):
        mock_module = Mock(params={"api_key": "test_key", "id": None, "name": "bar"})
        module = ModuleBase(mock_module)
        module.module.fail_json = Mock()
        module.fail_unable_to_find_snitch()
        module.module.fail_json.assert_called_once()
        args, kwargs = module.module.fail_json.call_args
        assert "Unable to find snitch" in kwargs["msg"]
        assert kwargs["searched"]["param"] == "name"
        assert kwargs["searched"]["value"] == "bar"

    def test_init_calls_handle_missing_lib_if_requests_missing(self):
        # Patch HAS_REQUESTS to False and check handle_missing_lib is called
        with patch("ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.module_base.HAS_REQUESTS", False):
            with patch.object(ModuleBase, "handle_missing_lib") as mock_handle_missing_lib:
                mock_module = Mock(params={"api_key": "test_key"})
                ModuleBase(mock_module)
                mock_handle_missing_lib.assert_called_once_with("requests", mock.ANY)
