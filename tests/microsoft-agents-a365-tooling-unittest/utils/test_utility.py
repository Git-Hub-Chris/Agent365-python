# Copyright (c) Microsoft. All rights reserved.

"""
Unit tests for utility functions in the tooling package.
"""

import os
from unittest.mock import patch

from microsoft_agents_a365.tooling.utils.utility import (
    get_tooling_gateway_for_digital_worker,
    get_mcp_base_url,
    build_mcp_server_url,
    _get_current_environment,
    _get_mcp_platform_base_url,
    get_mcp_platform_authentication_scope,
    MCP_PLATFORM_PROD_BASE_URL,
    PPAPI_TOKEN_SCOPE,
    PROD_MCP_PLATFORM_AUTHENTICATION_SCOPE,
)


class TestUtilityFunctions:
    """Test class for utility functions."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Store original environment variables to restore after tests
        self.original_env = {
            key: os.environ.get(key)
            for key in [
                "ENVIRONMENT",
                "MCP_PLATFORM_ENDPOINT",
                "MCP_PLATFORM_AUTHENTICATION_SCOPE",
            ]
        }

    def teardown_method(self):
        """Clean up after each test method."""
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_get_tooling_gateway_for_digital_worker(self):
        """Test get_tooling_gateway_for_digital_worker function."""
        # Arrange
        agent_user_id = "test-agent-123"

        # Act
        result = get_tooling_gateway_for_digital_worker(agent_user_id)

        # Assert
        expected = f"{MCP_PLATFORM_PROD_BASE_URL}/agents/{agent_user_id}/mcpServers"
        assert result == expected

    @patch.dict(os.environ, {"MCP_PLATFORM_ENDPOINT": "https://custom.endpoint.com"}, clear=False)
    def test_get_tooling_gateway_with_custom_endpoint(self):
        """Test get_tooling_gateway_for_digital_worker with custom MCP platform endpoint."""
        # Arrange
        agent_user_id = "test-agent-456"

        # Act
        result = get_tooling_gateway_for_digital_worker(agent_user_id)

        # Assert
        expected = "https://custom.endpoint.com/agents/test-agent-456/mcpServers"
        assert result == expected

    def test_get_mcp_base_url_production(self):
        """Test get_mcp_base_url in production environment."""
        # Arrange - Set production environment
        os.environ.pop("ENVIRONMENT", None)

        # Act
        result = get_mcp_base_url()

        # Assert
        expected = f"{MCP_PLATFORM_PROD_BASE_URL}/agents/servers"
        assert result == expected

    @patch.dict(os.environ, {"MCP_PLATFORM_ENDPOINT": "https://custom.endpoint.com"}, clear=False)
    def test_get_mcp_base_url_with_custom_endpoint(self):
        """Test get_mcp_base_url with custom MCP platform endpoint."""
        # Act
        result = get_mcp_base_url()

        # Assert
        expected = "https://custom.endpoint.com/agents/servers"
        assert result == expected

    def test_build_mcp_server_url_production(self):
        """Test build_mcp_server_url in production environment."""
        # Arrange
        server_name = "mail_server"

        # Act
        result = build_mcp_server_url(server_name)

        # Assert
        expected = f"{MCP_PLATFORM_PROD_BASE_URL}/agents/servers/{server_name}"
        assert result == expected

    def test_get_current_environment_default(self):
        """Test _get_current_environment returns default when no env vars set."""
        # Arrange - Clear environment variables
        os.environ.pop("ENVIRONMENT", None)

        # Act
        result = _get_current_environment()

        # Assert
        assert result == "Development"

    @patch.dict(os.environ, {"ENVIRONMENT": "Production"}, clear=False)
    def test_get_current_environment_set(self):
        """Test _get_current_environment returns ENVIRONMENT value."""
        # Act
        result = _get_current_environment()

        # Assert
        assert result == "Production"

    def test_get_mcp_platform_base_url_default(self):
        """Test _get_mcp_platform_base_url returns default production URL."""
        # Arrange
        os.environ.pop("MCP_PLATFORM_ENDPOINT", None)

        # Act
        result = _get_mcp_platform_base_url()

        # Assert
        assert result == MCP_PLATFORM_PROD_BASE_URL

    @patch.dict(os.environ, {"MCP_PLATFORM_ENDPOINT": "https://test.platform.com"}, clear=False)
    def test_get_mcp_platform_base_url_custom(self):
        """Test _get_mcp_platform_base_url returns custom endpoint."""
        # Act
        result = _get_mcp_platform_base_url()

        # Assert
        assert result == "https://test.platform.com"

    def test_get_mcp_platform_authentication_scope_production(self):
        """Test get_mcp_platform_authentication_scope returns production scope."""
        # Arrange - Clear environment variable to use default
        os.environ.pop("MCP_PLATFORM_AUTHENTICATION_SCOPE", None)

        # Act
        result = get_mcp_platform_authentication_scope()

        # Assert
        expected = [PROD_MCP_PLATFORM_AUTHENTICATION_SCOPE]
        assert result == expected

    @patch.dict(
        os.environ, {"MCP_PLATFORM_AUTHENTICATION_SCOPE": "custom-scope/.default"}, clear=False
    )
    def test_get_mcp_platform_authentication_scope_custom(self):
        """Test get_mcp_platform_authentication_scope returns custom scope from environment."""
        # Act
        result = get_mcp_platform_authentication_scope()

        # Assert
        expected = ["custom-scope/.default"]
        assert result == expected

    def test_constants_values(self):
        """Test that constants have expected values."""
        # Assert
        assert MCP_PLATFORM_PROD_BASE_URL == "https://agent365.svc.cloud.microsoft"
        assert PPAPI_TOKEN_SCOPE == "https://api.powerplatform.com"
        assert (
            PROD_MCP_PLATFORM_AUTHENTICATION_SCOPE
            == "ea9ffc3e-8a23-4a7d-836d-234d7c7565c1/.default"
        )

    def test_get_tooling_gateway_empty_agent_id(self):
        """Test get_tooling_gateway_for_digital_worker with empty agent ID."""
        # Arrange
        agent_user_id = ""

        # Act
        result = get_tooling_gateway_for_digital_worker(agent_user_id)

        # Assert - Function should still work but produce invalid URL
        expected = f"{MCP_PLATFORM_PROD_BASE_URL}/agents//mcpServers"
        assert result == expected

    def test_build_mcp_server_url_empty_params(self):
        """Test build_mcp_server_url with empty parameters."""
        # Arrange
        server_name = ""

        # Act
        result = build_mcp_server_url(server_name)

        # Assert
        expected = f"{MCP_PLATFORM_PROD_BASE_URL}/agents/servers/"
        assert result == expected
