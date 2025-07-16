from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.mikemorency.deadmanssnitch.plugins.modules.snitch_info import (
    main as module_main
)
from ...common.utils import run_module, ModuleTestCase


class TestSnitchInfo(ModuleTestCase):

    def __prepare(self, mocker):
        # Mock the entire Client class where it's imported in module_base
        self.mock_client_class = mocker.patch(
            "ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.module_base.Client"
        )
        # Create a mock instance
        self.mock_client_instance = mocker.MagicMock()
        self.mock_client_class.return_value = self.mock_client_instance

    def test_no_match(self, mocker):
        self.__prepare(mocker)
        self.mock_client_instance.list_snitches.return_value = []
        self.mock_client_instance.get_snitch.return_value = None

        module_args = dict(name="test-snitch")
        result = run_module(module_entry=module_main, module_args=module_args)
        assert result["changed"] is False
        assert result["snitches"] == []
        self.mock_client_instance.list_snitches.assert_called_once()

        module_args = dict(id="test-snitch")
        result = run_module(module_entry=module_main, module_args=module_args)
        assert result["changed"] is False
        assert result["snitches"] == []
        self.mock_client_instance.get_snitch.assert_called_once()

        self.mock_client_instance.list_snitches.reset_mock()
        module_args = dict()
        result = run_module(module_entry=module_main, module_args=module_args)
        assert result["changed"] is False
        assert result["snitches"] == []
        self.mock_client_instance.list_snitches.assert_called_once()

    def test_snitch_by_name_success(self, mocker):
        self.__prepare(mocker)
        mock_snitch = {
            "token": "123456",
            "name": "test-snitch",
            "interval": "1_minute",
            "alert_type": "basic",
            "alert_email": ["test1@example.com"],
            "notes": "First test snitch",
            "tags": ["test"],
            "status": "active",
            "created_at": "2021-01-01T00:00:00Z",
            "updated_at": "2021-01-01T00:00:00Z",
        }
        self.mock_client_instance.list_snitches.return_value = [mock_snitch]

        module_args = dict(name="test-snitch")
        result = run_module(module_entry=module_main, module_args=module_args)

        assert result["changed"] is False
        assert result["snitches"] == [mock_snitch]
        self.mock_client_instance.list_snitches.assert_called_once()

    def test_snitch_by_id_success(self, mocker):
        self.__prepare(mocker)
        mock_snitch = {
            "token": "123456",
            "name": "test-snitch",
            "interval": "1_minute",
            "alert_type": "basic",
            "alert_email": ["test1@example.com"],
            "notes": "First test snitch",
            "tags": ["test"],
            "status": "active",
            "created_at": "2021-01-01T00:00:00Z",
            "updated_at": "2021-01-01T00:00:00Z",
        }
        self.mock_client_instance.get_snitch.return_value = mock_snitch

        module_args = dict(id="123456")
        result = run_module(module_entry=module_main, module_args=module_args)

        assert result["changed"] is False
        assert result["snitches"] == [mock_snitch]
        self.mock_client_instance.get_snitch.assert_called_once_with(snitch_id="123456")

    def test_snitches_by_tags_success(self, mocker):
        self.__prepare(mocker)
        mock_snitches = [
            {
                "token": "123456",
                "name": "test-snitch",
                "interval": "1_minute",
                "alert_type": "basic",
                "alert_email": ["test1@example.com"],
                "notes": "First test snitch",
                "tags": ["test"],
                "status": "active",
                "created_at": "2021-01-01T00:00:00Z",
                "updated_at": "2021-01-01T00:00:00Z",
            },
            {
                "token": "789012",
                "name": "snitch-2",
                "interval": "1_minute",
                "alert_type": "basic",
                "alert_email": [],
                "notes": "Second snitch",
                "tags": ["production"],
                "status": "active",
                "created_at": "2021-01-02T00:00:00Z",
                "updated_at": "2021-01-02T00:00:00Z",
            },
        ]
        self.mock_client_instance.list_snitches.return_value = mock_snitches

        module_args = dict(tags=["test"])
        result = run_module(module_entry=module_main, module_args=module_args)

        assert result["changed"] is False
        assert result["snitches"] == mock_snitches
        self.mock_client_instance.list_snitches.assert_called_once_with(tags=["test"])

    def test_get_all_snitches_success(self, mocker):
        self.__prepare(mocker)
        mock_snitches = [
            {
                "token": "123456",
                "name": "test-snitch",
                "interval": "1_minute",
                "alert_type": "basic",
                "alert_email": ["test1@example.com"],
                "notes": "First test snitch",
                "tags": ["test"],
                "status": "active",
                "created_at": "2021-01-01T00:00:00Z",
                "updated_at": "2021-01-01T00:00:00Z",
            },
            {
                "token": "789012",
                "name": "snitch-2",
                "interval": "1_minute",
                "alert_type": "basic",
                "alert_email": [],
                "notes": "Second snitch",
                "tags": ["production"],
                "status": "active",
                "created_at": "2021-01-02T00:00:00Z",
                "updated_at": "2021-01-02T00:00:00Z",
            },
            {
                "token": "345678",
                "name": "snitch-3",
                "interval": "1_minute",
                "alert_type": "basic",
                "alert_email": ["test3@example.com"],
                "notes": "Third snitch",
                "tags": ["development"],
                "status": "active",
                "created_at": "2021-01-03T00:00:00Z",
                "updated_at": "2021-01-03T00:00:00Z",
            },
        ]
        self.mock_client_instance.list_snitches.return_value = mock_snitches

        module_args = dict()
        result = run_module(module_entry=module_main, module_args=module_args)

        assert result["changed"] is False
        assert result["snitches"] == mock_snitches
        self.mock_client_instance.list_snitches.assert_called_once()

    def test_client_exception_handling(self, mocker):
        self.__prepare(mocker)
        self.mock_client_instance.list_snitches.side_effect = Exception("API Error")

        module_args = dict(name="test-snitch")
        result = run_module(
            module_entry=module_main, module_args=module_args, expect_success=False
        )

        assert result["failed"] is True
        assert "Failed to get snitches: API Error" in result["msg"]

    def test_get_snitch_by_id_exception(self, mocker):
        self.__prepare(mocker)
        self.mock_client_instance.get_snitch.side_effect = Exception("Snitch not found")

        module_args = dict(id="invalid-id")
        result = run_module(
            module_entry=module_main, module_args=module_args, expect_success=False
        )

        assert result["failed"] is True
        assert "Failed to get snitches: Snitch not found" in result["msg"]

    def test_multiple_tags_filtering(self, mocker):
        self.__prepare(mocker)
        mock_snitches = [
            {
                "token": "123456",
                "name": "test-snitch",
                "interval": "1_minute",
                "alert_type": "basic",
                "alert_email": ["test1@example.com"],
                "notes": "First test snitch",
                "tags": ["test"],
                "status": "active",
                "created_at": "2021-01-01T00:00:00Z",
                "updated_at": "2021-01-01T00:00:00Z",
            }
        ]
        self.mock_client_instance.list_snitches.return_value = mock_snitches

        module_args = dict(tags=["test", "critical"])
        result = run_module(module_entry=module_main, module_args=module_args)

        assert result["changed"] is False
        assert result["snitches"] == mock_snitches
        self.mock_client_instance.list_snitches.assert_called_once_with(
            tags=["test", "critical"]
        )

    def test_snitch_by_name_multiple_matches(self, mocker):
        self.__prepare(mocker)
        mock_snitches = [
            {
                "token": "123456",
                "name": "test-snitch",
                "interval": "1_minute",
                "alert_type": "basic",
                "alert_email": ["test1@example.com"],
                "notes": "First test snitch",
                "tags": ["test"],
                "status": "active",
                "created_at": "2021-01-01T00:00:00Z",
                "updated_at": "2021-01-01T00:00:00Z",
            },
            {
                "token": "789012",
                "name": "test-snitch",
                "interval": "5_minute",
                "alert_type": "smart",
                "alert_email": [],
                "notes": "Second test snitch",
                "tags": ["test"],
                "status": "active",
                "created_at": "2021-01-02T00:00:00Z",
                "updated_at": "2021-01-02T00:00:00Z",
            },
        ]
        self.mock_client_instance.list_snitches.return_value = mock_snitches

        module_args = dict(name="test-snitch")
        result = run_module(module_entry=module_main, module_args=module_args)

        assert result["changed"] is False
        # Should only return the first match due to break statement in get_snitch_by_name
        assert result["snitches"] == [mock_snitches[0]]
        self.mock_client_instance.list_snitches.assert_called_once()

    def test_empty_tags_list(self, mocker):
        self.__prepare(mocker)
        self.mock_client_instance.list_snitches.return_value = []

        module_args = dict(tags=[])
        result = run_module(module_entry=module_main, module_args=module_args)

        assert result["changed"] is False
        assert result["snitches"] == []
        self.mock_client_instance.list_snitches.assert_called_once_with()
