# Product Requirements Document (PRD)

## OpenAI `send_chat_history_async` API for Agent365-python SDK

| **Document Information** |                                              |
|--------------------------|----------------------------------------------|
| **Version**              | 1.0                                          |
| **Status**               | Draft                                        |
| **Author**               | Agent365 Python SDK Team                     |
| **Created**              | January 21, 2026                             |
| **Last Updated**         | January 21, 2026                             |
| **Target Package**       | `microsoft-agents-a365-tooling-extensions-openai` |

---

## Table of Contents

1. [Overview and Business Justification](#1-overview-and-business-justification)
2. [Objectives](#2-objectives)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
5. [Technical Requirements](#5-technical-requirements)
6. [Package Impact Analysis](#6-package-impact-analysis)
7. [API Design](#7-api-design)
8. [Observability Requirements](#8-observability-requirements)
9. [Testing Strategy](#9-testing-strategy)
10. [Acceptance Criteria](#10-acceptance-criteria)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Dependencies](#12-dependencies)
13. [Risks and Mitigations](#13-risks-and-mitigations)
14. [Open Questions](#14-open-questions)

---

## 1. Overview and Business Justification

### 1.1 Problem Statement

The Agent365-python SDK currently provides a core `send_chat_history` method in `McpToolServerConfigurationService` that sends conversation history to the MCP platform for real-time threat protection. However, this method requires developers using the OpenAI Agents SDK to manually convert OpenAI-native types (such as `Session`, `TResponseInputItem`, `UserMessage`, `AssistantMessage`, etc.) to the SDK's `ChatHistoryMessage` format.

This manual conversion creates:
- **Developer friction**: Extra boilerplate code to transform OpenAI types
- **Inconsistency risk**: Different developers may implement conversion logic differently
- **Error-prone integrations**: Missing ID or timestamp handling may vary
- **Feature parity gap**: The .NET SDK already provides framework-specific `SendChatHistoryAsync` methods for Agent Framework (PR #171) and Semantic Kernel (PR #173)

### 1.2.1 Method Naming Convention

This PRD defines two methods with the following naming convention:
- **`send_chat_history_messages_async`**: Accepts a list of OpenAI `TResponseInputItem` messages directly
- **`send_chat_history_async`**: Extracts messages from an OpenAI `Session` object (the more common use case)

### 1.2 Proposed Solution

Implement OpenAI-specific chat history APIs in the `microsoft-agents-a365-tooling-extensions-openai` package that:
- Accepts OpenAI SDK native types directly (Session protocol items, message types)
- Handles all conversion logic internally
- Provides a seamless developer experience for OpenAI Agents SDK users
- Maintains feature parity with the .NET SDK

### 1.3 Business Value

| Value Driver | Description |
|--------------|-------------|
| **Developer Experience** | Reduces integration effort from ~20 lines of conversion code to a single method call |
| **Adoption** | Lowers barrier to entry for OpenAI SDK developers adopting Agent365 |
| **Consistency** | Ensures standardized handling of missing IDs, timestamps, and role mapping |
| **Feature Parity** | Aligns Python SDK capabilities with .NET SDK |
| **Enterprise Readiness** | Enables real-time threat protection for OpenAI-based agents with minimal effort |

### 1.4 Success Metrics

| Metric | Target |
|--------|--------|
| API adoption rate | 80% of OpenAI extension users use `send_chat_history_async` or `send_chat_history_messages_async` within 3 months |
| Code reduction | Average 15+ lines of boilerplate eliminated per integration |
| Test coverage | ≥95% line coverage, ≥90% branch coverage |
| Documentation completeness | 100% of public APIs documented with examples |

---

## 2. Objectives

### 2.1 Primary Objectives

1. **O1**: Provide OpenAI-native API for sending chat history to the MCP platform
2. **O2**: Support OpenAI Session protocol items (`TResponseInputItem` types)
3. **O3**: Support direct list of OpenAI message types
4. **O4**: Maintain backward compatibility with existing `McpToolServerConfigurationService`
5. **O5**: Achieve feature parity with .NET SDK implementation

### 2.2 Secondary Objectives

1. **O6**: Provide extensible design for future OpenAI SDK version support
2. **O7**: Enable observability integration for tracing chat history operations
3. **O8**: Support both synchronous and asynchronous usage patterns

### 2.3 Out of Scope

- Modifications to the core `McpToolServerConfigurationService`
- Support for other orchestrator SDKs (covered by separate extensions)
- Persistent storage of chat history (handled by MCP platform)
- Chat history retrieval APIs (read operations)

---

## 3. User Stories

### 3.1 Primary User Stories

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| **US-01** | As an OpenAI agent developer, I want to send my agent's Session history to the MCP platform so that my conversations are protected by real-time threat detection | P0 | Session items are converted and sent successfully |
| **US-02** | As an OpenAI agent developer, I want to send a list of messages to the MCP platform without manual conversion so that I can focus on agent logic | P0 | List of OpenAI messages converts and sends correctly |
| **US-03** | As an OpenAI agent developer, I want missing message IDs to be auto-generated so that I don't need to track IDs manually | P0 | UUIDs generated for messages without IDs |
| **US-04** | As an OpenAI agent developer, I want missing timestamps to use current UTC time so that all messages have valid timestamps | P0 | Current UTC timestamp used when not provided |
| **US-05** | As an OpenAI agent developer, I want to receive clear success/failure results so that I can handle errors appropriately | P0 | `OperationResult` returned with error details on failure |
| **US-05a** | As an OpenAI agent developer, I want to send my Session's conversation history directly so that I don't need to extract messages manually | P0 | `send_chat_history_async` extracts and sends Session items |

### 3.2 Secondary User Stories

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| **US-06** | As an OpenAI agent developer, I want to pass custom `ToolOptions` so that I can customize orchestrator identification | P1 | ToolOptions parameter accepted and applied |
| **US-07** | As an OpenAI agent developer, I want detailed logging of conversion operations so that I can debug issues | P1 | Debug-level logs for conversion operations |
| **US-08** | As an OpenAI agent developer, I want support for all standard OpenAI message roles so that system, user, and assistant messages are handled | P1 | All roles mapped correctly |

---

## 4. Functional Requirements

### 4.1 Core Functional Requirements

| ID | Requirement | Priority | Verification Method |
|----|-------------|----------|---------------------|
| **FR-01** | The API SHALL accept OpenAI `TResponseInputItem` types and convert them to `ChatHistoryMessage` | P0 | Unit tests |
| **FR-02** | The API SHALL support `UserMessage`, `AssistantMessage`, and `SystemMessage` OpenAI types | P0 | Unit tests |
| **FR-03** | The API SHALL generate a UUID for messages without an ID | P0 | Unit tests |
| **FR-04** | The API SHALL use `datetime.now(timezone.utc)` for messages without a timestamp | P0 | Unit tests |
| **FR-05** | The API SHALL delegate to `McpToolServerConfigurationService.send_chat_history` | P0 | Integration tests |
| **FR-06** | The API SHALL return `OperationResult` indicating success or failure | P0 | Unit tests |
| **FR-07** | The API SHALL validate that `turn_context` is not None | P0 | Unit tests |
| **FR-08** | The API SHALL allow empty message lists (no-op, return success) | P0 | Unit tests |
| **FR-09** | The API SHALL map OpenAI roles to `ChatHistoryMessage` roles ("user", "assistant", "system") | P0 | Unit tests |
| **FR-10** | The API SHALL extract text content from OpenAI message content arrays | P0 | Unit tests |
| **FR-11** | The API SHALL provide a `send_chat_history_async` method that accepts an OpenAI Session | P0 | Unit tests |
| **FR-12** | The `send_chat_history_async` method SHALL call `session.get_items()` to retrieve messages | P0 | Unit tests |
| **FR-13** | The `send_chat_history_async` method SHALL support an optional `limit` parameter for `get_items()` | P1 | Unit tests |
| **FR-14** | The API SHALL include all item types from the session without filtering | P0 | Unit tests |

### 4.2 Method Signatures

The implementation SHALL provide the following method overloads:

```python
# Primary method - extracts messages from OpenAI Session (most common use case)
async def send_chat_history_async(
    self,
    turn_context: TurnContext,
    session: Session,
    limit: Optional[int] = None,
    options: Optional[ToolOptions] = None,
) -> OperationResult:
    """
    Extracts chat history from an OpenAI Session and sends it to the MCP platform.

    Args:
        turn_context: TurnContext from the Agents SDK containing conversation info.
        session: OpenAI Session instance to extract messages from.
        limit: Optional maximum number of items to retrieve from session.
                If None, retrieves all items.
        options: Optional ToolOptions for customization.

    Returns:
        OperationResult indicating success or failure.
    """

# Secondary method - accepts list of OpenAI message types directly
async def send_chat_history_messages_async(
    self,
    turn_context: TurnContext,
    messages: List[TResponseInputItem],
    options: Optional[ToolOptions] = None,
) -> OperationResult:
    """
    Sends OpenAI chat history to the MCP platform for threat protection.

    Args:
        turn_context: TurnContext from the Agents SDK containing conversation info.
        messages: List of OpenAI TResponseInputItem messages to send.
        options: Optional ToolOptions for customization.

    Returns:
        OperationResult indicating success or failure.
    """
```

### 4.3 Role Mapping

| OpenAI Type | ChatHistoryMessage Role |
|-------------|------------------------|
| `UserMessage` | `"user"` |
| `AssistantMessage` | `"assistant"` |
| `SystemMessage` | `"system"` |
| `ResponseOutputMessage` with role="assistant" | `"assistant"` |
| Other/Unknown | `"user"` (default fallback with warning log) |

### 4.4 Content Extraction

The API SHALL extract text content following this priority:
1. If message has `.content` as string → use directly
2. If message has `.content` as list → concatenate all text parts
3. If message has `.text` attribute → use directly
4. If content is empty/None → use empty string with warning log

---

## 5. Technical Requirements

### 5.1 Language and Runtime

| Requirement | Specification |
|-------------|---------------|
| Python version | ≥3.10 |
| Async support | Full `async/await` pattern |
| Type hints | Complete type annotations (PEP 484) |
| Pydantic version | ≥2.0 (for model validation) |

### 5.1.1 Type Hints - NEVER Use `Any`

**CRITICAL**: The use of `typing.Any` is **strictly forbidden** in this codebase. Using `Any` defeats the purpose of type checking and can hide bugs.

**Required alternatives (in order of preference):**

| Instead of `Any` | Use |
|------------------|-----|
| External SDK types | Import and use actual types from the SDK (e.g., `Session`, `TResponseInputItem`) |
| Multiple known types | `Union[Type1, Type2, ...]` |
| Pass-through data | `object` |
| Dictionary values | `Dict[str, object]` or specific types |
| Unknown external types (last resort) | `Protocol` - but confirm with developer first |

**Preferred approach - Use actual SDK types:**

```python
from agents.memory import Session
from agents.items import TResponseInputItem

async def send_chat_history_async(
    self,
    turn_context: TurnContext,
    session: Session,  # Use actual SDK type
) -> OperationResult:
    ...

async def send_chat_history_messages_async(
    self,
    turn_context: TurnContext,
    messages: List[TResponseInputItem],  # Use actual SDK type
) -> OperationResult:
    ...
```

**Why actual SDK types are preferred:**
- Better IDE support (autocomplete, type checking)
- Ensures compatibility with the external SDK
- Less maintenance burden (no custom protocols to keep in sync)
- Clearer intent for developers reading the code

**When to use Protocol (last resort only):**
If external types cannot be found or imported, a `Protocol` may be defined. However, this should be rare and requires confirmation with the developer before proceeding, as it may indicate a missing dependency or incorrect understanding of the external API.

This requirement applies to both production code AND test files.

### 5.2 OpenAI SDK Compatibility

| Requirement | Specification |
|-------------|---------------|
| OpenAI Agents SDK | Compatible with `openai-agents` package |
| Message types | Support `TResponseInputItem` union type |
| Session protocol | Support items from `Session.get_items()` |

### 5.3 Error Handling

| Error Condition | Expected Behavior |
|-----------------|-------------------|
| `turn_context` is None | Raise `ValueError` with descriptive message |
| `messages` is None | Raise `ValueError` with descriptive message |
| `messages` is empty list | Return `OperationResult.success()` (no-op) |
| `turn_context.activity` is None | Raise `ValueError` with descriptive message |
| Missing conversation ID | Raise `ValueError` with field path |
| Missing message ID | Raise `ValueError` with field path |
| Missing user message text | Raise `ValueError` with field path |
| HTTP error from MCP platform | Return `OperationResult.failed()` with error |
| Network timeout | Return `OperationResult.failed()` with error |
| Conversion error | Return `OperationResult.failed()` with error |

### 5.4 Thread Safety

- The service class SHALL be thread-safe for concurrent calls
- State SHALL NOT be shared between method invocations
- Logger instance SHALL be initialized per instance

---

## 6. Package Impact Analysis

### 6.1 Modified Package

**Package**: `microsoft-agents-a365-tooling-extensions-openai`

| File | Change Type | Description |
|------|-------------|-------------|
| `mcp_tool_registration_service.py` | Modified | Add `send_chat_history_async` method |
| `__init__.py` | Modified | Export new types if needed |

### 6.2 New Files

| File | Purpose |
|------|---------|
| `tests/tooling/extensions/openai/test_send_chat_history_async.py` | Unit tests |
| `tests/tooling/extensions/openai/test_message_conversion.py` | Conversion logic tests |

### 6.3 Dependency Changes

**New Dependencies (in `pyproject.toml`)**:

```toml
[project.dependencies]
# Existing dependencies...
openai-agents = ">=0.1.0"  # For type definitions
```

### 6.4 Package Exports

Update `__init__.py` to export:
- `McpToolRegistrationService` (already exported, method added)

---

## 7. API Design

### 7.1 Class Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     McpToolRegistrationService                       │
├─────────────────────────────────────────────────────────────────────┤
│ - _orchestrator_name: str = "OpenAI"                                │
│ - _logger: logging.Logger                                           │
│ - config_service: McpToolServerConfigurationService                 │
├─────────────────────────────────────────────────────────────────────┤
│ + __init__(logger: Optional[Logger])                                │
│ + add_tool_servers_to_agent(...) -> Agent                          │
│ + send_chat_history_async(                                          │
│     turn_context: TurnContext,                                      │
│     session: Session,                                               │
│     limit: Optional[int],                                           │
│     options: Optional[ToolOptions]                                  │
│   ) -> OperationResult                                              │
│ + send_chat_history_messages_async(                                 │
│     turn_context: TurnContext,                                      │
│     messages: List[TResponseInputItem],                             │
│     options: Optional[ToolOptions]                                  │
│   ) -> OperationResult                                              │
│ - _convert_openai_messages_to_chat_history(                         │
│     messages: List[TResponseInputItem]                              │
│   ) -> List[ChatHistoryMessage]                                     │
│ - _convert_single_message(                                          │
│     message: TResponseInputItem                                     │
│   ) -> Optional[ChatHistoryMessage]                                 │
│ - _extract_role(message: TResponseInputItem) -> str                 │
│ - _extract_content(message: TResponseInputItem) -> str              │
│ - _extract_id(message: TResponseInputItem) -> str                   │
│ - _extract_timestamp(message: TResponseInputItem) -> datetime       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ delegates to
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                McpToolServerConfigurationService                     │
├─────────────────────────────────────────────────────────────────────┤
│ + send_chat_history(                                                │
│     turn_context: TurnContext,                                      │
│     chat_history_messages: List[ChatHistoryMessage],                │
│     options: Optional[ToolOptions]                                  │
│   ) -> OperationResult                                              │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Sequence Diagram

```
Developer          McpToolRegistrationService     McpToolServerConfigurationService     MCP Platform
    │                        │                              │                               │
    │ send_chat_history_     │                              │                               │
    │ messages_async         │                              │                               │
    │──────────────────────>│                               │                               │
    │                        │                              │                               │
    │                        │ validate inputs              │                               │
    │                        │──────────────┐               │                               │
    │                        │              │               │                               │
    │                        │<─────────────┘               │                               │
    │                        │                              │                               │
    │                        │ _convert_openai_messages_to_chat_history                     │
    │                        │──────────────┐               │                               │
    │                        │              │ for each message:                             │
    │                        │              │ - extract role                                │
    │                        │              │ - extract content                             │
    │                        │              │ - extract/generate ID                         │
    │                        │              │ - extract/generate timestamp                  │
    │                        │<─────────────┘               │                               │
    │                        │                              │                               │
    │                        │ send_chat_history            │                               │
    │                        │─────────────────────────────>│                               │
    │                        │                              │                               │
    │                        │                              │ POST /chat-message            │
    │                        │                              │──────────────────────────────>│
    │                        │                              │                               │
    │                        │                              │              HTTP 200 / Error │
    │                        │                              │<──────────────────────────────│
    │                        │                              │                               │
    │                        │           OperationResult    │                               │
    │                        │<─────────────────────────────│                               │
    │                        │                              │                               │
    │   OperationResult      │                              │                               │
    │<──────────────────────│                               │                               │
    │                        │                              │                               │
```

### 7.3 Data Models

#### 7.3.1 Existing Models (No Changes)

```python
# From microsoft_agents_a365.tooling.models

class ChatHistoryMessage(BaseModel):
    """Represents a single message in the chat history."""
    
    id: Optional[str] = Field(default=None)
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = Field(default=None)


class ToolOptions:
    """Configuration options for tooling operations."""
    
    orchestrator_name: Optional[str]
```

#### 7.3.2 OpenAI Types (External, for reference)

```python
# From openai-agents SDK (external types for reference)

TResponseInputItem = Union[
    EasyInputMessage,
    ResponseOutputMessage,
    ResponseFileSearchToolCall,
    ResponseFunctionWebSearch,
    ResponseComputerToolCall,
    ResponseFunctionToolCall,
    ResponseFunctionToolCallOutput,
    ResponseReasoningItem,
    ItemReference,
    # ... other types
]

class UserMessage:
    role: Literal["user"]
    content: Union[str, List[ContentPart]]

class AssistantMessage:
    role: Literal["assistant"]
    content: Union[str, List[ContentPart]]

class SystemMessage:
    role: Literal["system"]
    content: Union[str, List[ContentPart]]
```

### 7.4 Method Implementation Pseudocode

```python
async def send_chat_history_async(
    self,
    turn_context: TurnContext,
    session: Session,
    limit: Optional[int] = None,
    options: Optional[ToolOptions] = None,
) -> OperationResult:
    """
    Extracts chat history from an OpenAI Session and sends it to the MCP platform.
    """
    # Validate inputs
    if turn_context is None:
        raise ValueError("turn_context cannot be None")
    if session is None:
        raise ValueError("session cannot be None")

    try:
        # Extract messages from session
        messages = await session.get_items(limit=limit)

        # Delegate to the list-based method
        return await self.send_chat_history_messages_async(
            turn_context=turn_context,
            messages=messages,
            options=options,
        )
    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as ex:
        self._logger.error(f"Failed to send chat history: {ex}")
        return OperationResult.failed(OperationError(ex))


async def send_chat_history_messages_async(
    self,
    turn_context: TurnContext,
    messages: List[TResponseInputItem],
    options: Optional[ToolOptions] = None,
) -> OperationResult:
    """
    Sends OpenAI chat history to the MCP platform for threat protection.
    """
    # Validate inputs
    if turn_context is None:
        raise ValueError("turn_context cannot be None")
    if messages is None:
        raise ValueError("messages cannot be None")

    # Handle empty list as no-op
    if len(messages) == 0:
        self._logger.info("Empty message list provided, returning success")
        return OperationResult.success()

    # Set default options
    if options is None:
        options = ToolOptions(orchestrator_name=self._orchestrator_name)
    elif options.orchestrator_name is None:
        options.orchestrator_name = self._orchestrator_name

    try:
        # Convert OpenAI messages to ChatHistoryMessage format
        chat_history_messages = self._convert_openai_messages_to_chat_history(messages)

        # Delegate to core service
        return await self.config_service.send_chat_history(
            turn_context=turn_context,
            chat_history_messages=chat_history_messages,
            options=options,
        )
    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as ex:
        self._logger.error(f"Failed to send chat history messages: {ex}")
        return OperationResult.failed(OperationError(ex))
```

---

## 8. Observability Requirements

### 8.1 Logging Requirements

| Level | When | Message Template |
|-------|------|------------------|
| INFO | Method entry | `"Sending {count} OpenAI messages as chat history"` |
| INFO | Success | `"Successfully sent chat history with {count} messages"` |
| DEBUG | Per-message conversion | `"Converting message: role={role}, has_id={has_id}, has_timestamp={has_ts}"` |
| DEBUG | ID generation | `"Generated UUID {id} for message without ID"` |
| DEBUG | Timestamp generation | `"Using current UTC time for message without timestamp"` |
| WARNING | Unknown role | `"Unknown message type {type}, defaulting to 'user' role"` |
| WARNING | Empty content | `"Message has empty content, using empty string"` |
| ERROR | Conversion failure | `"Failed to convert message: {error}"` |
| ERROR | Send failure | `"Failed to send chat history: {error}"` |

### 8.2 Metrics (Future Enhancement)

| Metric Name | Type | Description |
|-------------|------|-------------|
| `a365.tooling.openai.send_chat_history.count` | Counter | Total number of send operations |
| `a365.tooling.openai.send_chat_history.success` | Counter | Successful send operations |
| `a365.tooling.openai.send_chat_history.failure` | Counter | Failed send operations |
| `a365.tooling.openai.send_chat_history.messages` | Histogram | Messages per batch |
| `a365.tooling.openai.send_chat_history.duration_ms` | Histogram | Operation duration |

### 8.3 Tracing Integration

The method SHOULD integrate with the existing observability framework:

```python
# Future enhancement - integrate with ExecuteToolScope
from microsoft_agents_a365.observability.core import ExecuteToolScope, ToolCallDetails

with ExecuteToolScope.start(
    tool_call_details=ToolCallDetails(
        tool_name="send_chat_history",
        tool_arguments={"message_count": len(messages)},
    )
) as scope:
    result = await self._send_internal(...)
    scope.record_response(str(result))
```

---

## 9. Testing Strategy

### 9.1 Test Categories

| Category | Coverage Target | Focus |
|----------|-----------------|-------|
| Unit Tests | ≥95% lines | Method logic, conversion, validation |
| Integration Tests | Key flows | End-to-end with mocked HTTP |
| Edge Case Tests | 100% identified cases | Null handling, empty content, unknown types |

### 9.2 Unit Test Cases

#### 9.2.1 Input Validation Tests

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| UV-01 | `test_send_chat_history_messages_async_validates_turn_context_none` | Verify ValueError when turn_context is None |
| UV-02 | `test_send_chat_history_messages_async_validates_messages_none` | Verify ValueError when messages is None |
| UV-03 | `test_send_chat_history_messages_async_empty_list_returns_success` | Verify empty list returns success (no-op) |
| UV-04 | `test_send_chat_history_messages_async_validates_activity_none` | Verify ValueError when activity is None |
| UV-05 | `test_send_chat_history_messages_async_validates_conversation_id` | Verify ValueError when conversation.id missing |
| UV-06 | `test_send_chat_history_messages_async_validates_message_id` | Verify ValueError when activity.id missing |
| UV-07 | `test_send_chat_history_messages_async_validates_user_message` | Verify ValueError when activity.text missing |
| UV-08 | `test_send_chat_history_async_validates_turn_context_none` | Verify ValueError when turn_context is None |
| UV-09 | `test_send_chat_history_async_validates_session_none` | Verify ValueError when session is None |

#### 9.2.2 Conversion Tests

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| CV-01 | `test_convert_user_message_to_chat_history` | UserMessage converts with role="user" |
| CV-02 | `test_convert_assistant_message_to_chat_history` | AssistantMessage converts with role="assistant" |
| CV-03 | `test_convert_system_message_to_chat_history` | SystemMessage converts with role="system" |
| CV-04 | `test_convert_message_with_string_content` | String content extracted directly |
| CV-05 | `test_convert_message_with_list_content` | List content concatenated |
| CV-06 | `test_convert_message_generates_uuid_when_id_missing` | UUID generated for missing ID |
| CV-07 | `test_convert_message_uses_utc_when_timestamp_missing` | UTC timestamp used when missing |
| CV-08 | `test_convert_message_preserves_existing_id` | Existing ID preserved |
| CV-09 | `test_convert_message_preserves_existing_timestamp` | Existing timestamp preserved |
| CV-10 | `test_convert_unknown_message_type_defaults_to_user` | Unknown type defaults to user role |
| CV-11 | `test_convert_empty_content_uses_empty_string` | Empty content handled gracefully |
| CV-12 | `test_convert_multiple_messages` | Multiple messages converted correctly |

#### 9.2.3 Success Path Tests

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| SP-01 | `test_send_chat_history_messages_async_success` | Successful send returns succeeded=True |
| SP-02 | `test_send_chat_history_messages_async_with_options` | Custom ToolOptions applied |
| SP-03 | `test_send_chat_history_messages_async_default_orchestrator_name` | Default orchestrator name set |
| SP-04 | `test_send_chat_history_messages_async_delegates_to_config_service` | Delegation verified |
| SP-05 | `test_send_chat_history_async_success` | Session messages extracted and sent |
| SP-06 | `test_send_chat_history_async_with_limit` | Limit parameter passed to get_items |
| SP-07 | `test_send_chat_history_async_delegates_to_send_chat_history_messages` | Delegation verified |

#### 9.2.4 Error Handling Tests

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| EH-01 | `test_send_chat_history_messages_async_http_error` | HTTP error returns failed result |
| EH-02 | `test_send_chat_history_messages_async_timeout_error` | Timeout returns failed result |
| EH-03 | `test_send_chat_history_messages_async_client_error` | Network error returns failed result |
| EH-04 | `test_send_chat_history_messages_async_conversion_error` | Conversion error returns failed result |
| EH-05 | `test_send_chat_history_async_get_items_error` | Session get_items error returns failed result |

### 9.3 Integration Test Cases

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| IT-01 | `test_send_chat_history_async_end_to_end_success` | Full flow with mocked HTTP |
| IT-02 | `test_send_chat_history_async_end_to_end_server_error` | Full flow with HTTP 500 |
| IT-03 | `test_send_chat_history_async_payload_format` | Verify JSON payload structure |

### 9.4 Test File Structure

```
tests/
└── tooling/
    └── extensions/
        └── openai/
            ├── __init__.py
            ├── test_send_chat_history_async.py      # Main API tests
            ├── test_message_conversion.py           # Conversion logic tests
            └── conftest.py                          # Shared fixtures
```

### 9.5 Sample Test Code

```python
# tests/tooling/extensions/openai/test_send_chat_history_async.py

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
import uuid

from microsoft_agents.hosting.core import TurnContext
from microsoft_agents_a365.tooling.extensions.openai import McpToolRegistrationService
from microsoft_agents_a365.runtime import OperationResult


class TestSendChatHistoryMessagesAsync:
    """Tests for send_chat_history_messages_async method."""

    @pytest.fixture
    def service(self):
        """Create McpToolRegistrationService instance."""
        return McpToolRegistrationService()

    @pytest.fixture
    def mock_turn_context(self):
        """Create a mock TurnContext."""
        mock_context = Mock(spec=TurnContext)
        mock_activity = Mock()
        mock_conversation = Mock()
        mock_conversation.id = "conv-123"
        mock_activity.conversation = mock_conversation
        mock_activity.id = "msg-456"
        mock_activity.text = "Hello, how are you?"
        mock_context.activity = mock_activity
        return mock_context

    @pytest.fixture
    def sample_openai_messages(self):
        """Create sample OpenAI messages."""
        # Mock OpenAI message types
        user_msg = Mock()
        user_msg.role = "user"
        user_msg.content = "Hello"

        assistant_msg = Mock()
        assistant_msg.role = "assistant"
        assistant_msg.content = "Hi there!"

        return [user_msg, assistant_msg]

    @pytest.mark.asyncio
    async def test_send_chat_history_messages_async_validates_turn_context_none(
        self, service, sample_openai_messages
    ):
        """Test that send_chat_history_messages_async validates turn_context."""
        with pytest.raises(ValueError, match="turn_context cannot be None"):
            await service.send_chat_history_messages_async(None, sample_openai_messages)

    @pytest.mark.asyncio
    async def test_send_chat_history_messages_async_success(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test successful send_chat_history_messages_async call."""
        with patch.object(
            service.config_service,
            'send_chat_history',
            new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            result = await service.send_chat_history_messages_async(
                mock_turn_context,
                sample_openai_messages
            )

            assert result.succeeded is True
            mock_send.assert_called_once()
```

---

## 10. Acceptance Criteria

### 10.1 Functional Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-01 | `send_chat_history_async` method exists in `McpToolRegistrationService` | Code review |
| AC-01a | `send_chat_history_messages_async` method exists in `McpToolRegistrationService` | Code review |
| AC-02 | Method accepts `List[TResponseInputItem]` parameter | Type checker passes |
| AC-03 | Method returns `OperationResult` | Unit tests pass |
| AC-04 | Missing message IDs are generated as UUIDs | Unit tests pass |
| AC-05 | Missing timestamps use current UTC time | Unit tests pass |
| AC-06 | All OpenAI role types map correctly | Unit tests pass |
| AC-07 | Validation errors raise `ValueError` with descriptive messages | Unit tests pass |
| AC-07a | Empty message list returns `OperationResult.success()` | Unit tests pass |
| AC-08 | HTTP errors return `OperationResult.failed()` | Unit tests pass |
| AC-08a | `send_chat_history_async` calls `session.get_items()` correctly | Unit tests pass |

### 10.2 Non-Functional Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-09 | Unit test coverage ≥95% | Coverage report |
| AC-10 | All public methods have docstrings | Code review |
| AC-11 | Type hints on all parameters and returns | Type checker passes |
| AC-12 | No new linting errors | `ruff check` passes |
| AC-13 | Code follows existing patterns | Code review |

### 10.3 Documentation Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-14 | Method has complete docstring with Args/Returns/Raises | Code review |
| AC-15 | README.md updated with usage example | Documentation review |
| AC-16 | CHANGELOG.md updated | Documentation review |

---

## 11. Non-Functional Requirements

### 11.1 Performance

| Requirement | Target |
|-------------|--------|
| Conversion overhead | <10ms for 100 messages |
| Memory overhead | <1MB for 1000 messages |
| No blocking calls | All I/O is async |
| Batch size | No limit - endpoint assumed to handle unlimited size |
| Performance benchmarks | Required in CI for regression detection |

### 11.2 Reliability

| Requirement | Target |
|-------------|--------|
| Graceful degradation | Return `OperationResult.failed()` on errors |
| No data loss | Messages not modified in place |
| Idempotent IDs | Same message without ID gets different UUID each call |

### 11.3 Maintainability

| Requirement | Target |
|-------------|--------|
| Cyclomatic complexity | <10 per method |
| Method length | <50 lines |
| Single responsibility | One public method, helper methods for conversion |

### 11.4 Security

| Requirement | Description |
|-------------|-------------|
| No credential logging | Auth tokens never logged |
| Input sanitization | Content not modified, passed through |
| Secure defaults | HTTPS enforced by underlying service |

---

## 12. Dependencies

### 12.1 Internal Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `microsoft-agents-a365-tooling` | ≥1.0.0 | Core `McpToolServerConfigurationService` |
| `microsoft-agents-a365-runtime` | ≥1.0.0 | `OperationResult`, `OperationError` |

### 12.2 External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai-agents` | ≥0.1.0 | OpenAI message types (`TResponseInputItem`) |
| `microsoft-agents-hosting-core` | ≥0.1.0 | `TurnContext`, `Authorization` |
| `pydantic` | ≥2.0.0 | Model validation |

### 12.3 Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | ≥7.0.0 | Test framework |
| `pytest-asyncio` | ≥0.21.0 | Async test support |
| `pytest-cov` | ≥4.0.0 | Coverage reporting |

---

## 13. Risks and Mitigations

### 13.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenAI SDK type changes | Medium | High | Use duck typing, version pin, adapter pattern |
| Performance regression | Low | Medium | Benchmark tests, lazy evaluation |
| Thread safety issues | Low | High | Stateless design, no shared state |

### 13.2 Schedule Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | Medium | Medium | Clear scope definition, change control |
| Testing delays | Medium | Medium | Parallel test development |
| Review delays | Low | Medium | Early reviewer engagement |

### 13.3 Integration Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing API | Low | High | No changes to existing methods |
| Dependency conflicts | Low | Medium | Version ranges, compatibility testing |

---

## 14. Open Questions

### 14.1 Design Questions

| ID | Question | Status | Decision |
|----|----------|--------|----------|
| OQ-01 | Should we support OpenAI Session protocol directly in addition to message lists? | **Resolved** | **Yes** - `send_chat_history_async` extracts messages from Session, `send_chat_history_messages_async` accepts message list directly |
| OQ-02 | Should we add a synchronous wrapper `send_chat_history` for convenience? | **Deferred** | Skip for now - evaluate in future iteration |
| OQ-03 | Should empty message lists be allowed (no-op) vs. raising ValueError? | **Resolved** | **Empty list allowed** - Return success with no-op |
| OQ-04 | Should we support custom ID generators (injectable)? | **Resolved** | **No** - Use UUID by default for simplicity |

### 14.2 Implementation Questions

| ID | Question | Status | Decision |
|----|----------|--------|----------|
| OQ-05 | Which specific OpenAI message types need support beyond User/Assistant/System? | Open | Need to enumerate `TResponseInputItem` union |
| OQ-06 | Should tool call/result messages be included in chat history? | **Resolved** | **Yes** - Include all items retrieved, no filtering required |
| OQ-07 | What is the maximum batch size for messages? | **Resolved** | **No limit assumed** - Assume endpoint handles unlimited size, no batching required |

### 14.3 Testing Questions

| ID | Question | Status | Decision |
|----|----------|--------|----------|
| OQ-08 | Should we add performance benchmarks to CI? | **Resolved** | **Yes** - Add performance benchmarks for regression detection |
| OQ-09 | Should we mock OpenAI types or use real SDK types in tests? | **Resolved** | **Yes** - Mock for unit tests, real SDK types for integration tests |

---

## Appendix A: .NET SDK Reference

### A.1 Agent Framework Implementation (PR #171)

The .NET implementation provides four method overloads:

```csharp
// Method 1: IEnumerable<ChatMessage>
Task<OperationResult> SendChatHistoryAsync(
    TurnContext turnContext,
    IEnumerable<ChatMessage> chatMessages,
    ToolOptions? options = null,
    CancellationToken cancellationToken = default);

// Method 2: ChatMessageStore
Task<OperationResult> SendChatHistoryAsync(
    TurnContext turnContext,
    ChatMessageStore chatMessageStore,
    ToolOptions? options = null,
    CancellationToken cancellationToken = default);
```

Key implementation details:
- Generates `Guid.NewGuid()` for missing IDs
- Uses `DateTime.UtcNow` for missing timestamps
- Converts to `ChatHistoryMessage[]` array for the core API

### A.2 Semantic Kernel Implementation (PR #173)

```csharp
// Method 1: ChatHistory
Task<OperationResult> SendChatHistoryAsync(
    TurnContext turnContext,
    ChatHistory chatHistory,
    ToolOptions? options = null,
    CancellationToken cancellationToken = default);

// Method 2: IEnumerable<ChatMessageContent>
Task<OperationResult> SendChatHistoryAsync(
    TurnContext turnContext,
    IEnumerable<ChatMessageContent> chatHistory,
    ToolOptions? options = null,
    CancellationToken cancellationToken = default);
```

---

## Appendix B: OpenAI SDK Type Reference

### B.1 TResponseInputItem Union Type

The `TResponseInputItem` is a union type in the OpenAI Agents SDK that includes:

```python
TResponseInputItem = Union[
    EasyInputMessage,           # Simple input message
    ResponseOutputMessage,      # Response from agent
    ResponseFileSearchToolCall, # File search tool call
    ResponseFunctionWebSearch,  # Web search function
    ResponseComputerToolCall,   # Computer use tool call
    ResponseFunctionToolCall,   # Function tool call
    ResponseFunctionToolCallOutput,  # Tool call output
    ResponseReasoningItem,      # Reasoning step
    ItemReference,              # Reference to another item
    # ... potentially more types
]
```

### B.2 Message Content Types

```python
# Content can be string or list of parts
ContentPart = Union[
    TextContentPart,
    ImageContentPart,
    AudioContentPart,
]

class TextContentPart:
    type: Literal["text"]
    text: str
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Agent365 Python SDK Team | Initial draft |
