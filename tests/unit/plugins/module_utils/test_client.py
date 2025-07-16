from __future__ import absolute_import, division, print_function

__metaclass__ = type

import mock
from unittest.mock import Mock, patch

from ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.client import (
    Client,
)


class TestClient:
    def setup_method(self):
        self.api_key = "test_api_key_12345"
        self.client = Client(self.api_key)
        self.base_url = "https://api.deadmanssnitch.com/v1"

    def test_init(self):
        client = Client("test_key")
        assert client.api_key == "test_key"
        assert client._url_base == "https://api.deadmanssnitch.com/v1"

    @patch("requests.request")
    def test_list_snitches_no_tags(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"snitches": [{"id": "1", "name": "test"}]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.list_snitches()

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches",
            method="GET",
            headers={},
            auth=mock.ANY,
        )
        assert result == {"snitches": [{"id": "1", "name": "test"}]}

    @patch("requests.request")
    def test_list_snitches_with_tags(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"snitches": [{"id": "1", "name": "test"}]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        tags = ["tag1", "tag2", "tag3"]
        result = self.client.list_snitches(tags=tags)

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches?tags=tag1,tag2,tag3",
            method="GET",
            headers={},
            auth=mock.ANY,
        )
        assert result == {"snitches": [{"id": "1", "name": "test"}]}

    @patch("requests.request")
    def test_get_snitch(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "name": "test_snitch"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.get_snitch("123")

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123",
            method="GET",
            headers={},
            auth=mock.ANY,
        )
        assert result == {"id": "123", "name": "test_snitch"}

    @patch("requests.request")
    def test_create_snitch_minimal(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new_id", "name": "new_snitch"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.create_snitch(name="new_snitch", interval="hourly")

        expected_data = {
            "name": "new_snitch",
            "interval": "hourly"
        }

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches",
            method="POST",
            headers={"Content-Type": "application/json"},
            auth=mock.ANY,
            json=expected_data,
        )
        assert result == {"id": "new_id", "name": "new_snitch"}

    @patch("requests.request")
    def test_create_snitch_full(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new_id", "name": "full_snitch"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.create_snitch(
            name="full_snitch",
            interval="daily",
            alert_type="smart",
            alert_email=["test@example.com", "admin@example.com"],
            notes="Test snitch for monitoring",
            tags=["production", "critical"],
        )

        expected_data = {
            "name": "full_snitch",
            "interval": "daily",
            "alert_type": "smart",
            "alert_email": ["test@example.com", "admin@example.com"],
            "notes": "Test snitch for monitoring",
            "tags": ["production", "critical"],
        }

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches",
            method="POST",
            headers={"Content-Type": "application/json"},
            auth=mock.ANY,
            json=expected_data,
        )
        assert result == {"id": "new_id", "name": "full_snitch"}

    @patch("requests.request")
    def test_update_snitch_no_changes(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "name": "updated_snitch"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.update_snitch("123")

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123",
            method="PATCH",
            headers={"Content-Type": "application/json"},
            auth=mock.ANY
        )
        assert result == {"id": "123", "name": "updated_snitch"}

    @patch("requests.request")
    def test_update_snitch_with_changes(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "name": "updated_snitch"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.update_snitch(
            snitch_id="123",
            name="updated_snitch",
            interval="weekly",
            alert_type="basic",
            alert_email=["new@example.com"],
            notes="Updated notes",
            tags=["updated", "tags"],
        )

        expected_data = {
            "name": "updated_snitch",
            "interval": "weekly",
            "alert_type": "basic",
            "alert_email": ["new@example.com"],
            "notes": "Updated notes",
            "tags": ["updated", "tags"],
        }

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123",
            method="PATCH",
            headers={"Content-Type": "application/json"},
            auth=mock.ANY,
            json=expected_data,
        )
        assert result == {"id": "123", "name": "updated_snitch"}

    @patch("requests.request")
    def test_remove_snitch_tag(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "tags": []}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.remove_snitch_tag("123", "old_tag")

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123/tags/old_tag",
            method="DELETE",
            headers={"Content-Type": "application/json"},
            auth=mock.ANY,
        )
        assert result == {"id": "123", "tags": []}

    @patch("requests.request")
    def test_append_snitch_tags(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "tags": ["existing", "new_tag"]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        tags_to_add = ["new_tag", "important"]
        result = self.client.append_snitch_tags("123", tags_to_add)

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123/tags",
            method="POST",
            headers={"Content-Type": "application/json"},
            auth=mock.ANY,
            json=tags_to_add,
        )
        assert result == {"id": "123", "tags": ["existing", "new_tag"]}

    @patch("requests.request")
    def test_replace_snitch_tags(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "tags": ["tag1", "tag2"]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        tags_to_replace = ["tag1", "tag2"]
        result = self.client.replace_snitch_tags("123", tags_to_replace)

        expected_data = {"tags": tags_to_replace}
        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123",
            method="PATCH",
            headers={"Content-Type": "application/json"},
            auth=mock.ANY,
            json=expected_data,
        )
        assert result == {"id": "123", "tags": ["tag1", "tag2"]}

    @patch("requests.request")
    def test_delete_snitch(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"deleted": True}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.delete_snitch("123")

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123",
            method="DELETE",
            headers={},
            auth=mock.ANY,
        )
        assert result == {"deleted": True}

    @patch("requests.request")
    def test_pause_snitch(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "status": "paused"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.pause_snitch("123")

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123/pause",
            method="POST",
            headers={},
            auth=mock.ANY,
        )
        assert result == {"id": "123", "status": "paused"}

    @patch("requests.request")
    def test_unpause_snitch(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "status": "active"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.unpause_snitch("123")

        mock_request.assert_called_once_with(
            url=f"{self.base_url}/snitches/123/unpause",
            method="POST",
            headers={},
            auth=mock.ANY,
        )
        assert result == {"id": "123", "status": "active"}

    @patch("requests.request")
    def test_content_type_header_for_post_patch(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        self.client.create_snitch(name="test", interval="hourly")
        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"

        self.client.update_snitch(snitch_id="123", name="updated")
        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
