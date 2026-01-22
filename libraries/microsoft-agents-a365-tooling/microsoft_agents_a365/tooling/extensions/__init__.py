# Copyright (c) Microsoft. All rights reserved.

"""
Microsoft Agent 365 Tooling Extensions.

This is a namespace package that allows extension packages to contribute
their modules under the microsoft_agents_a365.tooling.extensions namespace.
"""

import sys
from pkgutil import extend_path

# First, try standard pkgutil-style namespace extension
__path__ = extend_path(__path__, __name__)

# For editable installs with custom finders, we need to manually discover
# extension paths by checking meta_path finders
for finder in sys.meta_path:
    # Check if this is an editable finder with namespace support
    if hasattr(finder, "find_spec"):
        try:
            spec = finder.find_spec(__name__, None)
            if spec is not None and spec.submodule_search_locations:
                for path in spec.submodule_search_locations:
                    if path not in __path__ and not path.endswith(".__path_hook__"):
                        __path__.append(path)
        except (ImportError, TypeError):
            pass
