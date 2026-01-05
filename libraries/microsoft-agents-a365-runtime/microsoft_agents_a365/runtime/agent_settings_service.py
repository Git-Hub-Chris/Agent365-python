# Copyright (c) Microsoft. All rights reserved.

"""Service for managing agent settings templates and instance-specific settings."""

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from .power_platform_api_discovery import PowerPlatformApiDiscovery


@dataclass
class AgentSettingTemplate:
    """Represents an agent setting template.
    
    Attributes:
        agent_type: The agent type identifier.
        settings: The settings template as a key-value dictionary.
        metadata: Optional metadata about the template.
    """
    
    agent_type: str
    settings: dict[str, Any]
    metadata: dict[str, Any] | None = None


@dataclass
class AgentSettings:
    """Represents agent settings for a specific instance.
    
    Attributes:
        agent_instance_id: The agent instance identifier.
        agent_type: The agent type identifier.
        settings: The settings as a key-value dictionary.
        metadata: Optional metadata about the settings.
    """
    
    agent_instance_id: str
    agent_type: str
    settings: dict[str, Any]
    metadata: dict[str, Any] | None = None


class AgentSettingsService:
    """Service for managing agent settings templates and instance-specific settings."""

    def __init__(self, api_discovery: PowerPlatformApiDiscovery, tenant_id: str) -> None:
        """Creates a new instance of AgentSettingsService.
        
        Args:
            api_discovery: The Power Platform API discovery service.
            tenant_id: The tenant identifier.
        """
        self.api_discovery = api_discovery
        self.tenant_id = tenant_id

    def _get_base_endpoint(self) -> str:
        """Gets the base endpoint for agent settings API.
        
        Returns:
            The base endpoint URL.
        """
        tenant_endpoint = self.api_discovery.get_tenant_endpoint(self.tenant_id)
        return f"https://{tenant_endpoint}/agents/v1.0"

    def get_agent_setting_template_endpoint(self, agent_type: str) -> str:
        """Gets the endpoint for agent setting templates.
        
        Args:
            agent_type: The agent type identifier.
            
        Returns:
            The endpoint URL for the agent type template.
        """
        return f"{self._get_base_endpoint()}/settings/templates/{quote(agent_type, safe='')}"

    def get_agent_settings_endpoint(self, agent_instance_id: str) -> str:
        """Gets the endpoint for agent instance settings.
        
        Args:
            agent_instance_id: The agent instance identifier.
            
        Returns:
            The endpoint URL for the agent instance settings.
        """
        return f"{self._get_base_endpoint()}/settings/instances/{quote(agent_instance_id, safe='')}"

    async def get_agent_setting_template(
        self, agent_type: str, access_token: str
    ) -> AgentSettingTemplate:
        """Retrieves an agent setting template by agent type.
        
        Args:
            agent_type: The agent type identifier.
            access_token: The access token for authentication.
            
        Returns:
            The agent setting template.
            
        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        endpoint = self.get_agent_setting_template_endpoint(agent_type)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )
            
            if not response.is_success:
                raise httpx.HTTPStatusError(
                    f"Failed to get agent setting template for type '{agent_type}': "
                    f"{response.status_code} {response.reason_phrase}",
                    request=response.request,
                    response=response,
                )
            
            data = response.json()
            return AgentSettingTemplate(
                agent_type=data["agentType"],
                settings=data["settings"],
                metadata=data.get("metadata"),
            )

    async def set_agent_setting_template(
        self, template: AgentSettingTemplate, access_token: str
    ) -> AgentSettingTemplate:
        """Sets an agent setting template for a specific agent type.
        
        Args:
            template: The agent setting template to set.
            access_token: The access token for authentication.
            
        Returns:
            The updated agent setting template.
            
        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        endpoint = self.get_agent_setting_template_endpoint(template.agent_type)
        
        payload = {
            "agentType": template.agent_type,
            "settings": template.settings,
        }
        if template.metadata is not None:
            payload["metadata"] = template.metadata
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            
            if not response.is_success:
                raise httpx.HTTPStatusError(
                    f"Failed to set agent setting template for type '{template.agent_type}': "
                    f"{response.status_code} {response.reason_phrase}",
                    request=response.request,
                    response=response,
                )
            
            data = response.json()
            return AgentSettingTemplate(
                agent_type=data["agentType"],
                settings=data["settings"],
                metadata=data.get("metadata"),
            )

    async def get_agent_settings(
        self, agent_instance_id: str, access_token: str
    ) -> AgentSettings:
        """Retrieves agent settings for a specific agent instance.
        
        Args:
            agent_instance_id: The agent instance identifier.
            access_token: The access token for authentication.
            
        Returns:
            The agent settings.
            
        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        endpoint = self.get_agent_settings_endpoint(agent_instance_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )
            
            if not response.is_success:
                raise httpx.HTTPStatusError(
                    f"Failed to get agent settings for instance '{agent_instance_id}': "
                    f"{response.status_code} {response.reason_phrase}",
                    request=response.request,
                    response=response,
                )
            
            data = response.json()
            return AgentSettings(
                agent_instance_id=data["agentInstanceId"],
                agent_type=data["agentType"],
                settings=data["settings"],
                metadata=data.get("metadata"),
            )

    async def set_agent_settings(
        self, settings: AgentSettings, access_token: str
    ) -> AgentSettings:
        """Sets agent settings for a specific agent instance.
        
        Args:
            settings: The agent settings to set.
            access_token: The access token for authentication.
            
        Returns:
            The updated agent settings.
            
        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        endpoint = self.get_agent_settings_endpoint(settings.agent_instance_id)
        
        payload = {
            "agentInstanceId": settings.agent_instance_id,
            "agentType": settings.agent_type,
            "settings": settings.settings,
        }
        if settings.metadata is not None:
            payload["metadata"] = settings.metadata
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            
            if not response.is_success:
                raise httpx.HTTPStatusError(
                    f"Failed to set agent settings for instance '{settings.agent_instance_id}': "
                    f"{response.status_code} {response.reason_phrase}",
                    request=response.request,
                    response=response,
                )
            
            data = response.json()
            return AgentSettings(
                agent_instance_id=data["agentInstanceId"],
                agent_type=data["agentType"],
                settings=data["settings"],
                metadata=data.get("metadata"),
            )
