# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from ..agent_details import AgentDetails
from ..constants import (
    GEN_AI_EXECUTION_SOURCE_DESCRIPTION_KEY,
    GEN_AI_EXECUTION_SOURCE_NAME_KEY,
    GEN_AI_EXECUTION_TYPE_KEY,
    GEN_AI_INPUT_MESSAGES_KEY,
)
from ..opentelemetry_scope import OpenTelemetryScope
from ..request import Request
from ..tenant_details import TenantDetails
from ..utils import safe_json_dumps

INPUT_OPERATION_NAME = "input_messages"


class InputScope(OpenTelemetryScope):
    """Provides OpenTelemetry tracing scope for input messages."""

    @staticmethod
    def start(
        agent_details: AgentDetails,
        tenant_details: TenantDetails,
        request: Request,
    ) -> "InputScope":
        """Creates and starts a new scope for input tracing.

        Args:
            agent_details: The details of the agent
            tenant_details: The details of the tenant
            request: The request details which invokes the agent

        Returns:
            A new InputScope instance
        """
        return InputScope(agent_details, tenant_details, request)

    def __init__(
        self,
        agent_details: AgentDetails,
        tenant_details: TenantDetails,
        request: Request,
    ):
        """Initialize the input scope.

        Args:
            agent_details: The details of the agent
            tenant_details: The details of the tenant
            request: The request details which invokes the agent
        """
        super().__init__(
            kind="Client",
            operation_name=INPUT_OPERATION_NAME,
            activity_name=(f"{INPUT_OPERATION_NAME} {agent_details.agent_id}"),
            agent_details=agent_details,
            tenant_details=tenant_details,
        )

        # Set request metadata
        if request.source_metadata:
            self.set_tag_maybe(GEN_AI_EXECUTION_SOURCE_NAME_KEY, request.source_metadata.name)
            self.set_tag_maybe(
                GEN_AI_EXECUTION_SOURCE_DESCRIPTION_KEY, request.source_metadata.description
            )

        self.set_tag_maybe(
            GEN_AI_EXECUTION_TYPE_KEY,
            request.execution_type.value if request.execution_type else None,
        )
        self.set_tag_maybe(GEN_AI_INPUT_MESSAGES_KEY, safe_json_dumps([request.content]))

    def record_input_messages(self, messages: list[str]) -> None:
        """Records the input messages for telemetry tracking.

        Args:
            messages: List of input messages
        """
        self.set_tag_maybe(GEN_AI_INPUT_MESSAGES_KEY, safe_json_dumps(messages))
