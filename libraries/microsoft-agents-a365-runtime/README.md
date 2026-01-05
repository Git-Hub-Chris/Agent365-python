# microsoft-agents-a365-runtime

[![PyPI](https://img.shields.io/pypi/v/microsoft-agents-a365-runtime?label=PyPI&logo=pypi)](https://pypi.org/project/microsoft-agents-a365-runtime)
[![PyPI Downloads](https://img.shields.io/pypi/dm/microsoft-agents-a365-runtime?label=Downloads&logo=pypi)](https://pypi.org/project/microsoft-agents-a365-runtime)

Core runtime utilities and environment management for AI agent applications. This package provides essential Power Platform API discovery, environment configuration, and authentication scope resolution.

## Installation

```bash
pip install microsoft-agents-a365-runtime
```

## Usage

### Agent Settings Service

The Agent Settings Service provides methods to manage agent settings templates and instance-specific settings:

```python
import asyncio
from microsoft_agents_a365.runtime import (
    AgentSettingsService,
    AgentSettingTemplate,
    AgentSettings,
    PowerPlatformApiDiscovery,
)

# Initialize the service
api_discovery = PowerPlatformApiDiscovery("prod")
tenant_id = "your-tenant-id"
service = AgentSettingsService(api_discovery, tenant_id)

async def main():
    access_token = "your-access-token"
    
    # Get agent setting template by agent type
    template = await service.get_agent_setting_template(
        "my-agent-type",
        access_token
    )
    
    # Set agent setting template
    new_template = AgentSettingTemplate(
        agent_type="my-agent-type",
        settings={"key1": "value1", "key2": "value2"}
    )
    await service.set_agent_setting_template(new_template, access_token)
    
    # Get agent settings by instance
    settings = await service.get_agent_settings(
        "agent-instance-id",
        access_token
    )
    
    # Set agent settings by instance
    new_settings = AgentSettings(
        agent_instance_id="agent-instance-id",
        agent_type="my-agent-type",
        settings={"instanceKey": "instanceValue"}
    )
    await service.set_agent_settings(new_settings, access_token)

asyncio.run(main())
```

For more usage examples and detailed documentation, see the [Microsoft Agent 365 Developer documentation](https://learn.microsoft.com/microsoft-agent-365/developer/?tabs=python) on Microsoft Learn.

## Support

For issues, questions, or feedback:

- File issues in the [GitHub Issues](https://github.com/microsoft/Agent365-python/issues) section
- See the [main documentation](../../README.md) for more information
 
## Trademarks
 
*Microsoft, Windows, Microsoft Azure and/or other Microsoft products and services referenced in the documentation may be either trademarks or registered trademarks of Microsoft in the United States and/or other countries. The licenses for this project do not grant you rights to use any Microsoft names, logos, or trademarks. Microsoft's general trademark guidelines can be found at http://go.microsoft.com/fwlink/?LinkID=254653.*

## License

Copyright (c) Microsoft Corporation. All rights reserved.

Licensed under the MIT License - see the [LICENSE](../../LICENSE.md) file for details.
