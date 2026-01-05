# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Unit tests for AgentSettingsService class."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from microsoft_agents_a365.runtime.agent_settings_service import (
    AgentSettings,
    AgentSettingsService,
    AgentSettingTemplate,
)
from microsoft_agents_a365.runtime.power_platform_api_discovery import (
    PowerPlatformApiDiscovery,
)


@pytest.fixture
def test_tenant_id():
    return "e3064512-cc6d-4703-be71-a2ecaecaa98a"


@pytest.fixture
def test_access_token():
    return "test-access-token-123"


@pytest.fixture
def test_agent_type():
    return "test-agent-type"


@pytest.fixture
def test_agent_instance_id():
    return "test-agent-instance-123"


@pytest.fixture
def api_discovery():
    return PowerPlatformApiDiscovery("prod")


@pytest.fixture
def service(api_discovery, test_tenant_id):
    return AgentSettingsService(api_discovery, test_tenant_id)


class TestAgentSettingsService:
    """Tests for AgentSettingsService class."""

    def test_get_agent_setting_template_endpoint(self, service, test_agent_type):
        """Test get_agent_setting_template_endpoint returns correct endpoint."""
        endpoint = service.get_agent_setting_template_endpoint(test_agent_type)
        assert "/agents/v1.0/settings/templates/" in endpoint
        assert test_agent_type in endpoint
        assert endpoint.startswith("https://")

    def test_get_agent_setting_template_endpoint_with_special_chars(self, service):
        """Test endpoint encoding with special characters in agent type."""
        agent_type_with_special_chars = "agent/type with spaces"
        endpoint = service.get_agent_setting_template_endpoint(agent_type_with_special_chars)
        # URL encoding: spaces -> %20, / -> %2F
        assert "agent%2Ftype%20with%20spaces" in endpoint

    def test_get_agent_settings_endpoint(self, service, test_agent_instance_id):
        """Test get_agent_settings_endpoint returns correct endpoint."""
        endpoint = service.get_agent_settings_endpoint(test_agent_instance_id)
        assert "/agents/v1.0/settings/instances/" in endpoint
        assert test_agent_instance_id in endpoint
        assert endpoint.startswith("https://")

    def test_get_agent_settings_endpoint_with_special_chars(self, service):
        """Test endpoint encoding with special characters in agent instance id."""
        instance_id_with_special_chars = "instance/id with spaces"
        endpoint = service.get_agent_settings_endpoint(instance_id_with_special_chars)
        # URL encoding: spaces -> %20, / -> %2F
        assert "instance%2Fid%20with%20spaces" in endpoint

    @pytest.mark.asyncio
    async def test_get_agent_setting_template_success(
        self, service, test_agent_type, test_access_token
    ):
        """Test successfully retrieving agent setting template."""
        mock_template_data = {
            "agentType": test_agent_type,
            "settings": {"setting1": "value1", "setting2": 42},
            "metadata": {"version": "1.0"},
        }

        mock_response = Mock(spec=httpx.Response)
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = mock_template_data

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await service.get_agent_setting_template(test_agent_type, test_access_token)

            assert result.agent_type == test_agent_type
            assert result.settings == {"setting1": "value1", "setting2": 42}
            assert result.metadata == {"version": "1.0"}

            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert f"/settings/templates/{test_agent_type}" in call_args[0][0]
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {test_access_token}"

    @pytest.mark.asyncio
    async def test_get_agent_setting_template_failure(
        self, service, test_agent_type, test_access_token
    ):
        """Test error handling when API returns non-ok status."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"
        mock_response.request = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError, match="Failed to get agent setting template"):
                await service.get_agent_setting_template(test_agent_type, test_access_token)

    @pytest.mark.asyncio
    async def test_set_agent_setting_template_success(
        self, service, test_agent_type, test_access_token
    ):
        """Test successfully setting agent setting template."""
        template = AgentSettingTemplate(
            agent_type=test_agent_type,
            settings={"setting1": "value1", "setting2": 42},
            metadata={"version": "1.0"},
        )

        mock_response_data = {
            "agentType": test_agent_type,
            "settings": {"setting1": "value1", "setting2": 42},
            "metadata": {"version": "1.1"},
        }

        mock_response = Mock(spec=httpx.Response)
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.put.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await service.set_agent_setting_template(template, test_access_token)

            assert result.agent_type == test_agent_type
            assert result.settings == {"setting1": "value1", "setting2": 42}
            assert result.metadata == {"version": "1.1"}

            mock_client.put.assert_called_once()
            call_args = mock_client.put.call_args
            assert f"/settings/templates/{test_agent_type}" in call_args[0][0]
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {test_access_token}"
            assert call_args[1]["json"]["agentType"] == test_agent_type

    @pytest.mark.asyncio
    async def test_set_agent_setting_template_failure(
        self, service, test_agent_type, test_access_token
    ):
        """Test error handling when setting template fails."""
        template = AgentSettingTemplate(
            agent_type=test_agent_type,
            settings={"setting1": "value1"},
        )

        mock_response = Mock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.reason_phrase = "Bad Request"
        mock_response.request = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.put.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError, match="Failed to set agent setting template"):
                await service.set_agent_setting_template(template, test_access_token)

    @pytest.mark.asyncio
    async def test_get_agent_settings_success(
        self, service, test_agent_instance_id, test_agent_type, test_access_token
    ):
        """Test successfully retrieving agent settings."""
        mock_settings_data = {
            "agentInstanceId": test_agent_instance_id,
            "agentType": test_agent_type,
            "settings": {"instanceSetting1": "value1", "instanceSetting2": 100},
            "metadata": {"lastUpdated": "2024-01-01T00:00:00Z"},
        }

        mock_response = Mock(spec=httpx.Response)
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = mock_settings_data

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await service.get_agent_settings(test_agent_instance_id, test_access_token)

            assert result.agent_instance_id == test_agent_instance_id
            assert result.agent_type == test_agent_type
            assert result.settings == {"instanceSetting1": "value1", "instanceSetting2": 100}
            assert result.metadata == {"lastUpdated": "2024-01-01T00:00:00Z"}

            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert f"/settings/instances/{test_agent_instance_id}" in call_args[0][0]
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {test_access_token}"

    @pytest.mark.asyncio
    async def test_get_agent_settings_failure(
        self, service, test_agent_instance_id, test_access_token
    ):
        """Test error handling when getting agent settings fails."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 403
        mock_response.reason_phrase = "Forbidden"
        mock_response.request = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError, match="Failed to get agent settings"):
                await service.get_agent_settings(test_agent_instance_id, test_access_token)

    @pytest.mark.asyncio
    async def test_set_agent_settings_success(
        self, service, test_agent_instance_id, test_agent_type, test_access_token
    ):
        """Test successfully setting agent settings."""
        settings = AgentSettings(
            agent_instance_id=test_agent_instance_id,
            agent_type=test_agent_type,
            settings={"instanceSetting1": "value1", "instanceSetting2": 100},
            metadata={"lastUpdated": "2024-01-01T00:00:00Z"},
        )

        mock_response_data = {
            "agentInstanceId": test_agent_instance_id,
            "agentType": test_agent_type,
            "settings": {"instanceSetting1": "value1", "instanceSetting2": 100, "newSetting": True},
            "metadata": {"lastUpdated": "2024-01-02T00:00:00Z"},
        }

        mock_response = Mock(spec=httpx.Response)
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.put.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await service.set_agent_settings(settings, test_access_token)

            assert result.agent_instance_id == test_agent_instance_id
            assert result.agent_type == test_agent_type
            assert result.settings["newSetting"] is True

            mock_client.put.assert_called_once()
            call_args = mock_client.put.call_args
            assert f"/settings/instances/{test_agent_instance_id}" in call_args[0][0]
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {test_access_token}"
            assert call_args[1]["json"]["agentInstanceId"] == test_agent_instance_id

    @pytest.mark.asyncio
    async def test_set_agent_settings_failure(
        self, service, test_agent_instance_id, test_agent_type, test_access_token
    ):
        """Test error handling when setting agent settings fails."""
        settings = AgentSettings(
            agent_instance_id=test_agent_instance_id,
            agent_type=test_agent_type,
            settings={"instanceSetting1": "value1"},
        )

        mock_response = Mock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.reason_phrase = "Internal Server Error"
        mock_response.request = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.put.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(
                httpx.HTTPStatusError, match="Failed to set agent settings for instance"
            ):
                await service.set_agent_settings(settings, test_access_token)

    @pytest.mark.parametrize(
        "cluster,expected_domain",
        [
            ("prod", "api.powerplatform.com"),
            ("gov", "api.gov.powerplatform.microsoft.us"),
            ("high", "api.high.powerplatform.microsoft.us"),
        ],
    )
    def test_different_cluster_categories(
        self, test_tenant_id, test_agent_type, cluster, expected_domain
    ):
        """Test endpoint construction with different cluster categories."""
        discovery = PowerPlatformApiDiscovery(cluster)
        test_service = AgentSettingsService(discovery, test_tenant_id)

        endpoint = test_service.get_agent_setting_template_endpoint(test_agent_type)

        assert expected_domain in endpoint
        assert "/agents/v1.0/settings/templates/" in endpoint
