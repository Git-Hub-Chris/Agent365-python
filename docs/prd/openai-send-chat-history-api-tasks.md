# Task Breakdown: OpenAI `send_chat_history_messages_async` API

| **Document Information** |                                              |
|--------------------------|----------------------------------------------|
| **PRD Reference**        | [openai-send-chat-history-api.md](openai-send-chat-history-api.md) |
| **Created**              | January 21, 2026                             |
| **Target Package**       | `microsoft-agents-a365-tooling-extensions-openai` |
| **Estimated Total Effort** | 40-56 hours                                |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Impact Analysis](#2-architecture-impact-analysis)
3. [Task Breakdown by Phase](#3-task-breakdown-by-phase)
4. [Task Dependencies](#4-task-dependencies)
5. [Testing Strategy Overview](#5-testing-strategy-overview)
6. [Risks and Considerations](#6-risks-and-considerations)
7. [Appendix: Task Checklist](#appendix-task-checklist)

---

## 1. Executive Summary

### 1.1 Overview

This task breakdown covers the implementation of two new async APIs for the OpenAI orchestrator extension:

1. **`send_chat_history_async(turn_context, session, limit, options)`** - Extracts messages from an OpenAI `Session` object and delegates to `send_chat_history_messages_async`. This is the primary/most common use case.

2. **`send_chat_history_messages_async(turn_context, messages, options)`** - Accepts a list of OpenAI `TResponseInputItem` messages and converts them to `ChatHistoryMessage` format before sending to the MCP platform.

### 1.2 Key Implementation Points

| Aspect | Details |
|--------|---------|
| **Target File** | `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Delegation Target** | `McpToolServerConfigurationService.send_chat_history()` in `microsoft-agents-a365-tooling` |
| **Return Type** | `OperationResult` (success/failure pattern) |
| **Error Handling** | `ValueError` for validation, `OperationResult.failed()` for runtime errors |

### 1.3 Scope Summary

- **In Scope**: Two new public methods, message conversion logic, comprehensive unit/integration tests
- **Out of Scope**: Changes to core `McpToolServerConfigurationService`, synchronous wrappers, other orchestrator extensions

### 1.4 Effort Estimation

| Phase | Estimated Hours |
|-------|-----------------|
| Phase 1: Foundation & Infrastructure | 6-8 hours |
| Phase 2: Core Implementation | 12-16 hours |
| Phase 3: Testing | 14-20 hours |
| Phase 4: Documentation & Finalization | 8-12 hours |
| **Total** | **40-56 hours** |

---

## 2. Architecture Impact Analysis

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Developer Application                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  microsoft-agents-a365-tooling-extensions-openai                            │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                   McpToolRegistrationService                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  NEW: send_chat_history_async()                                 │  │  │
│  │  │  NEW: send_chat_history_messages_async()                        │  │  │
│  │  │  NEW: _convert_openai_messages_to_chat_history()                │  │  │
│  │  │  NEW: _convert_single_message()                                 │  │  │
│  │  │  NEW: _extract_role() / _extract_content() / _extract_id()      │  │  │
│  │  │  EXISTING: add_tool_servers_to_agent()                          │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ delegates to
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  microsoft-agents-a365-tooling (core package)                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                McpToolServerConfigurationService                      │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  EXISTING: send_chat_history()                                  │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP Platform                                       │
│                    /real-time-threat-protection/chat-message                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Files Impacted

| File | Impact Type | Changes |
|------|-------------|---------|
| `mcp_tool_registration_service.py` | **Modified** | Add 2 public methods, 5+ private helper methods |
| `__init__.py` (openai extension) | **Modified** | Ensure exports are correct |
| `pyproject.toml` (openai extension) | **Modified** | Add `openai-agents` dependency if not present |
| `tests/tooling/extensions/openai/test_send_chat_history_async.py` | **New** | Main API unit tests |
| `tests/tooling/extensions/openai/test_message_conversion.py` | **New** | Conversion logic tests |
| `tests/tooling/extensions/openai/conftest.py` | **New** | Shared pytest fixtures |
| `README.md` (openai extension) | **Modified** | Add usage documentation |

### 2.3 Dependency Analysis

| Dependency | Type | Purpose | Risk |
|------------|------|---------|------|
| `openai-agents` | External (new) | OpenAI SDK types (`TResponseInputItem`, `Session`) | Medium - API stability |
| `microsoft-agents-a365-tooling` | Internal (existing) | Core `McpToolServerConfigurationService` | Low |
| `microsoft-agents-a365-runtime` | Internal (existing) | `OperationResult`, `OperationError` | Low |
| `microsoft-agents-hosting-core` | External (existing) | `TurnContext` | Low |

### 2.4 Breaking Changes

**None** - This is a purely additive change. All existing methods remain unchanged.

---

## 3. Task Breakdown by Phase

---

### Phase 1: Foundation & Infrastructure (6-8 hours)

#### Task 1.1: Analyze OpenAI SDK Types and Create Type Stubs

| Attribute | Details |
|-----------|---------|
| **Title** | Analyze OpenAI SDK Types and Create Type Stubs |
| **Estimate** | 3-4 hours |
| **Description** | Research the OpenAI Agents SDK to understand the `TResponseInputItem` union type, `Session` protocol, and message types. Create type stubs or protocols for testing if needed. |
| **Acceptance Criteria** | - Document all message types in `TResponseInputItem` union<br>- Identify attributes for role, content, id, timestamp extraction<br>- Create mock classes for unit testing<br>- Verify `Session.get_items()` method signature |
| **Files to Create/Modify** | - `tests/tooling/extensions/openai/conftest.py` (fixtures and mocks) |
| **Dependencies** | None |
| **Testing Requirements** | N/A (research task) |

---

#### Task 1.2: Add openai-agents Dependency

| Attribute | Details |
|-----------|---------|
| **Title** | Add openai-agents Dependency to pyproject.toml |
| **Estimate** | 1 hour |
| **Description** | Add the `openai-agents` package dependency to the OpenAI extension's `pyproject.toml` with appropriate version constraints. |
| **Acceptance Criteria** | - `openai-agents` added to `[project.dependencies]`<br>- Version constraint allows flexibility for minor updates<br>- `pip install` succeeds with new dependency<br>- No conflicts with existing dependencies |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/pyproject.toml` |
| **Dependencies** | None |
| **Testing Requirements** | Run `pip install -e .` and verify installation |

---

#### Task 1.3: Create Test Directory Structure and Fixtures

| Attribute | Details |
|-----------|---------|
| **Title** | Create Test Directory Structure and Shared Fixtures |
| **Estimate** | 2-3 hours |
| **Description** | Create the test directory structure for the OpenAI extension and define shared pytest fixtures for mocking OpenAI types, TurnContext, and common test data. |
| **Acceptance Criteria** | - Test directory structure created: `tests/tooling/extensions/openai/`<br>- `conftest.py` with fixtures for mock TurnContext, mock OpenAI messages, mock Session<br>- `__init__.py` files in place<br>- Fixtures are reusable across test files |
| **Files to Create/Modify** | - `tests/tooling/extensions/openai/__init__.py` (new)<br>- `tests/tooling/extensions/openai/conftest.py` (new)<br>- `tests/tooling/extensions/__init__.py` (new if needed) |
| **Dependencies** | Task 1.1 |
| **Testing Requirements** | Verify fixtures work with `pytest --collect-only` |

---

### Phase 2: Core Implementation (12-16 hours)

#### Task 2.1: Implement Role Extraction Helper

| Attribute | Details |
|-----------|---------|
| **Title** | Implement `_extract_role()` Private Method |
| **Estimate** | 2 hours |
| **Description** | Implement the private `_extract_role()` method that maps OpenAI message types to `ChatHistoryMessage` roles ("user", "assistant", "system"). Handle unknown types with a warning log and default to "user". |
| **Acceptance Criteria** | - Maps `UserMessage` → "user"<br>- Maps `AssistantMessage` → "assistant"<br>- Maps `SystemMessage` → "system"<br>- Maps `ResponseOutputMessage` with role="assistant" → "assistant"<br>- Unknown types default to "user" with warning log<br>- Method is type-hinted |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Dependencies** | Task 1.1, Task 1.2 |
| **Testing Requirements** | Unit tests in Task 3.2 |

---

#### Task 2.2: Implement Content Extraction Helper

| Attribute | Details |
|-----------|---------|
| **Title** | Implement `_extract_content()` Private Method |
| **Estimate** | 2-3 hours |
| **Description** | Implement the private `_extract_content()` method that extracts text content from OpenAI messages. Handle string content, list content (concatenate text parts), `.text` attribute, and empty/None content with warning log. |
| **Acceptance Criteria** | - String `.content` used directly<br>- List `.content` concatenates all text parts<br>- Falls back to `.text` attribute if present<br>- Returns empty string with warning for empty/None content<br>- Method is type-hinted |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Dependencies** | Task 1.1, Task 1.2 |
| **Testing Requirements** | Unit tests in Task 3.2 |

---

#### Task 2.3: Implement ID and Timestamp Extraction Helpers

| Attribute | Details |
|-----------|---------|
| **Title** | Implement `_extract_id()` and `_extract_timestamp()` Private Methods |
| **Estimate** | 2 hours |
| **Description** | Implement helper methods to extract or generate message IDs (UUID if missing) and timestamps (current UTC if missing). |
| **Acceptance Criteria** | - `_extract_id()`: Returns existing ID if present, generates UUID if missing<br>- `_extract_timestamp()`: Returns existing timestamp if present, uses `datetime.now(timezone.utc)` if missing<br>- Debug logging for generated values<br>- Methods are type-hinted |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Dependencies** | Task 1.1 |
| **Testing Requirements** | Unit tests in Task 3.2 |

---

#### Task 2.4: Implement Single Message Conversion

| Attribute | Details |
|-----------|---------|
| **Title** | Implement `_convert_single_message()` Private Method |
| **Estimate** | 2 hours |
| **Description** | Implement the private method that converts a single `TResponseInputItem` to a `ChatHistoryMessage` using the extraction helpers. |
| **Acceptance Criteria** | - Calls all extraction helpers<br>- Returns `ChatHistoryMessage` with role, content, id, timestamp<br>- Returns `None` for unconvertible messages with error log<br>- Method is type-hinted |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Dependencies** | Task 2.1, Task 2.2, Task 2.3 |
| **Testing Requirements** | Unit tests in Task 3.2 |

---

#### Task 2.5: Implement Batch Message Conversion

| Attribute | Details |
|-----------|---------|
| **Title** | Implement `_convert_openai_messages_to_chat_history()` Private Method |
| **Estimate** | 1-2 hours |
| **Description** | Implement the private method that converts a list of `TResponseInputItem` messages to a list of `ChatHistoryMessage` objects. Filter out `None` results from unconvertible messages. |
| **Acceptance Criteria** | - Iterates through all messages<br>- Calls `_convert_single_message()` for each<br>- Filters out `None` results<br>- Returns `List[ChatHistoryMessage]`<br>- Info logging with count of converted messages<br>- Method is type-hinted |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Dependencies** | Task 2.4 |
| **Testing Requirements** | Unit tests in Task 3.2 |

---

#### Task 2.6: Implement send_chat_history_messages_async Method

| Attribute | Details |
|-----------|---------|
| **Title** | Implement `send_chat_history_messages_async()` Public Method |
| **Estimate** | 3-4 hours |
| **Description** | Implement the public API method that validates inputs, converts OpenAI messages, and delegates to `McpToolServerConfigurationService.send_chat_history()`. |
| **Acceptance Criteria** | - Validates `turn_context` is not None (raises `ValueError`)<br>- Validates `messages` is not None (raises `ValueError`)<br>- Empty list returns `OperationResult.success()` (no-op)<br>- Sets default `ToolOptions` with orchestrator_name="OpenAI"<br>- Converts messages using `_convert_openai_messages_to_chat_history()`<br>- Delegates to `self.config_service.send_chat_history()`<br>- Returns `OperationResult`<br>- Catches exceptions and returns `OperationResult.failed()`<br>- Complete docstring with Args/Returns/Raises |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Dependencies** | Task 2.5 |
| **Testing Requirements** | Unit tests in Task 3.3, Task 3.4 |

---

#### Task 2.7: Implement send_chat_history_async Method

| Attribute | Details |
|-----------|---------|
| **Title** | Implement `send_chat_history_async()` Public Method |
| **Estimate** | 2 hours |
| **Description** | Implement the session-based public API method that extracts messages from an OpenAI `Session` and delegates to `send_chat_history_messages_async()`. |
| **Acceptance Criteria** | - Validates `turn_context` is not None (raises `ValueError`)<br>- Validates `session` is not None (raises `ValueError`)<br>- Calls `session.get_items(limit=limit)` to extract messages<br>- Delegates to `send_chat_history_messages_async()`<br>- Returns `OperationResult`<br>- Catches exceptions and returns `OperationResult.failed()`<br>- Complete docstring with Args/Returns/Raises |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Dependencies** | Task 2.6 |
| **Testing Requirements** | Unit tests in Task 3.3, Task 3.4 |

---

### Phase 3: Testing (14-20 hours)

#### Task 3.1: Implement Input Validation Unit Tests

| Attribute | Details |
|-----------|---------|
| **Title** | Implement Input Validation Unit Tests (UV-01 to UV-09) |
| **Estimate** | 3-4 hours |
| **Description** | Implement unit tests for all input validation scenarios as specified in PRD section 9.2.1. |
| **Acceptance Criteria** | - UV-01: `test_send_chat_history_messages_async_validates_turn_context_none`<br>- UV-02: `test_send_chat_history_messages_async_validates_messages_none`<br>- UV-03: `test_send_chat_history_messages_async_empty_list_returns_success`<br>- UV-04: `test_send_chat_history_messages_async_validates_activity_none`<br>- UV-05: `test_send_chat_history_messages_async_validates_conversation_id`<br>- UV-06: `test_send_chat_history_messages_async_validates_message_id`<br>- UV-07: `test_send_chat_history_messages_async_validates_user_message`<br>- UV-08: `test_send_chat_history_async_validates_turn_context_none`<br>- UV-09: `test_send_chat_history_async_validates_session_none`<br>- All tests pass |
| **Files to Create/Modify** | - `tests/tooling/extensions/openai/test_send_chat_history_async.py` (new) |
| **Dependencies** | Task 2.6, Task 2.7, Task 1.3 |
| **Testing Requirements** | `pytest tests/tooling/extensions/openai/test_send_chat_history_async.py -v` |

---

#### Task 3.2: Implement Conversion Logic Unit Tests

| Attribute | Details |
|-----------|---------|
| **Title** | Implement Conversion Logic Unit Tests (CV-01 to CV-12) |
| **Estimate** | 4-5 hours |
| **Description** | Implement unit tests for all message conversion scenarios as specified in PRD section 9.2.2. |
| **Acceptance Criteria** | - CV-01: `test_convert_user_message_to_chat_history`<br>- CV-02: `test_convert_assistant_message_to_chat_history`<br>- CV-03: `test_convert_system_message_to_chat_history`<br>- CV-04: `test_convert_message_with_string_content`<br>- CV-05: `test_convert_message_with_list_content`<br>- CV-06: `test_convert_message_generates_uuid_when_id_missing`<br>- CV-07: `test_convert_message_uses_utc_when_timestamp_missing`<br>- CV-08: `test_convert_message_preserves_existing_id`<br>- CV-09: `test_convert_message_preserves_existing_timestamp`<br>- CV-10: `test_convert_unknown_message_type_defaults_to_user`<br>- CV-11: `test_convert_empty_content_uses_empty_string`<br>- CV-12: `test_convert_multiple_messages`<br>- All tests pass |
| **Files to Create/Modify** | - `tests/tooling/extensions/openai/test_message_conversion.py` (new) |
| **Dependencies** | Task 2.1, Task 2.2, Task 2.3, Task 2.4, Task 2.5, Task 1.3 |
| **Testing Requirements** | `pytest tests/tooling/extensions/openai/test_message_conversion.py -v` |

---

#### Task 3.3: Implement Success Path Unit Tests

| Attribute | Details |
|-----------|---------|
| **Title** | Implement Success Path Unit Tests (SP-01 to SP-07) |
| **Estimate** | 3-4 hours |
| **Description** | Implement unit tests for all success path scenarios as specified in PRD section 9.2.3. |
| **Acceptance Criteria** | - SP-01: `test_send_chat_history_messages_async_success`<br>- SP-02: `test_send_chat_history_messages_async_with_options`<br>- SP-03: `test_send_chat_history_messages_async_default_orchestrator_name`<br>- SP-04: `test_send_chat_history_messages_async_delegates_to_config_service`<br>- SP-05: `test_send_chat_history_async_success`<br>- SP-06: `test_send_chat_history_async_with_limit`<br>- SP-07: `test_send_chat_history_async_delegates_to_send_chat_history_messages`<br>- All tests pass |
| **Files to Create/Modify** | - `tests/tooling/extensions/openai/test_send_chat_history_async.py` |
| **Dependencies** | Task 2.6, Task 2.7, Task 1.3 |
| **Testing Requirements** | `pytest tests/tooling/extensions/openai/test_send_chat_history_async.py -v` |

---

#### Task 3.4: Implement Error Handling Unit Tests

| Attribute | Details |
|-----------|---------|
| **Title** | Implement Error Handling Unit Tests (EH-01 to EH-05) |
| **Estimate** | 2-3 hours |
| **Description** | Implement unit tests for all error handling scenarios as specified in PRD section 9.2.4. |
| **Acceptance Criteria** | - EH-01: `test_send_chat_history_messages_async_http_error`<br>- EH-02: `test_send_chat_history_messages_async_timeout_error`<br>- EH-03: `test_send_chat_history_messages_async_client_error`<br>- EH-04: `test_send_chat_history_messages_async_conversion_error`<br>- EH-05: `test_send_chat_history_async_get_items_error`<br>- All tests pass |
| **Files to Create/Modify** | - `tests/tooling/extensions/openai/test_send_chat_history_async.py` |
| **Dependencies** | Task 2.6, Task 2.7, Task 1.3 |
| **Testing Requirements** | `pytest tests/tooling/extensions/openai/test_send_chat_history_async.py -v` |

---

#### Task 3.5: Implement Integration Tests

| Attribute | Details |
|-----------|---------|
| **Title** | Implement Integration Tests (IT-01 to IT-03) |
| **Estimate** | 3-4 hours |
| **Description** | Implement integration tests that verify end-to-end flow with mocked HTTP as specified in PRD section 9.3. |
| **Acceptance Criteria** | - IT-01: `test_send_chat_history_async_end_to_end_success`<br>- IT-02: `test_send_chat_history_async_end_to_end_server_error`<br>- IT-03: `test_send_chat_history_async_payload_format`<br>- Tests use real OpenAI SDK types where possible<br>- Tests verify full conversion and delegation chain<br>- All tests pass |
| **Files to Create/Modify** | - `tests/tooling/extensions/openai/test_integration.py` (new) |
| **Dependencies** | Task 2.6, Task 2.7, Task 1.3 |
| **Testing Requirements** | `pytest tests/tooling/extensions/openai/test_integration.py -v` |

---

#### Task 3.6: Verify Test Coverage and Add Performance Benchmarks

| Attribute | Details |
|-----------|---------|
| **Title** | Verify Test Coverage Targets and Add Performance Benchmarks |
| **Estimate** | 2-3 hours |
| **Description** | Run coverage analysis to ensure ≥95% line coverage and ≥90% branch coverage. Add performance benchmark tests for CI regression detection. |
| **Acceptance Criteria** | - Line coverage ≥95%<br>- Branch coverage ≥90%<br>- Performance benchmark: <10ms for 100 messages conversion<br>- Performance benchmark: <1MB memory for 1000 messages<br>- Coverage report generated |
| **Files to Create/Modify** | - `tests/tooling/extensions/openai/test_performance.py` (new)<br>- `pyproject.toml` (add coverage config if needed) |
| **Dependencies** | Task 3.1, Task 3.2, Task 3.3, Task 3.4, Task 3.5 |
| **Testing Requirements** | `pytest tests/tooling/extensions/openai/ --cov --cov-report=html` |

---

### Phase 4: Documentation & Finalization (8-12 hours)

#### Task 4.1: Add Method Docstrings and Type Hints

| Attribute | Details |
|-----------|---------|
| **Title** | Complete Method Docstrings and Type Hints |
| **Estimate** | 2-3 hours |
| **Description** | Ensure all public and private methods have complete docstrings following project conventions and full type annotations. |
| **Acceptance Criteria** | - All public methods have docstrings with Args/Returns/Raises<br>- All private methods have docstrings<br>- All parameters and return types are type-hinted<br>- Type checker (`mypy` or `pyright`) passes<br>- Follows existing project docstring style |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/microsoft_agents_a365/tooling/extensions/openai/mcp_tool_registration_service.py` |
| **Dependencies** | Task 2.6, Task 2.7 |
| **Testing Requirements** | `mypy` or `pyright` check |

---

#### Task 4.2: Update Package README with Usage Examples

| Attribute | Details |
|-----------|---------|
| **Title** | Update README.md with Usage Examples |
| **Estimate** | 2-3 hours |
| **Description** | Update the OpenAI extension's README.md with documentation and usage examples for both new methods. |
| **Acceptance Criteria** | - `send_chat_history_async()` documented with code example<br>- `send_chat_history_messages_async()` documented with code example<br>- Error handling best practices documented<br>- Prerequisites and installation instructions updated<br>- API reference section added |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/README.md` |
| **Dependencies** | Task 2.6, Task 2.7 |
| **Testing Requirements** | Code examples are syntactically correct |

---

#### Task 4.3: Update Package CHANGELOG

| Attribute | Details |
|-----------|---------|
| **Title** | Update CHANGELOG.md |
| **Estimate** | 1 hour |
| **Description** | Add changelog entry for the new API methods following the project's changelog format. |
| **Acceptance Criteria** | - New version entry added<br>- `send_chat_history_async()` listed as new feature<br>- `send_chat_history_messages_async()` listed as new feature<br>- Breaking changes section confirms none<br>- Follows existing changelog format |
| **Files to Create/Modify** | - `libraries/microsoft-agents-a365-tooling-extensions-openai/CHANGELOG.md` (create if not exists) |
| **Dependencies** | Task 2.6, Task 2.7 |
| **Testing Requirements** | N/A |

---

#### Task 4.4: Code Review and Linting

| Attribute | Details |
|-----------|---------|
| **Title** | Final Code Review and Linting Compliance |
| **Estimate** | 2-3 hours |
| **Description** | Run all linting tools, address any issues, and perform final code review to ensure code quality and consistency with existing patterns. |
| **Acceptance Criteria** | - `ruff check` passes with no errors<br>- `ruff format` applied<br>- No new security vulnerabilities<br>- Code follows existing project patterns<br>- Self-review completed<br>- Ready for PR |
| **Files to Create/Modify** | - All modified files |
| **Dependencies** | All previous tasks |
| **Testing Requirements** | `ruff check .` and `ruff format --check .` |

---

#### Task 4.5: Final Integration Verification

| Attribute | Details |
|-----------|---------|
| **Title** | Final Integration Verification |
| **Estimate** | 1-2 hours |
| **Description** | Perform final end-to-end verification that all tests pass, documentation is complete, and the implementation meets all PRD requirements. |
| **Acceptance Criteria** | - All 33+ unit tests pass<br>- All 3 integration tests pass<br>- Coverage targets met<br>- Documentation complete<br>- PR checklist completed<br>- All functional requirements (FR-01 to FR-14) verified<br>- All acceptance criteria (AC-01 to AC-16) verified |
| **Files to Create/Modify** | N/A |
| **Dependencies** | All previous tasks |
| **Testing Requirements** | Full test suite run |

---

## 4. Task Dependencies

### 4.1 Dependency Diagram

```
                    ┌──────────────────────┐
                    │   Task 1.1           │
                    │   Analyze OpenAI     │
                    │   SDK Types          │
                    └──────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Task 1.2    │  │  Task 1.3    │  │  Task 2.3    │
    │  Add Deps    │  │  Test Setup  │  │  ID/Time     │
    └──────────────┘  └──────────────┘  │  Helpers     │
              │               │          └──────────────┘
              │               │                 │
              ▼               │                 │
    ┌──────────────┐         │                 │
    │  Task 2.1    │◄────────┘                 │
    │  Role        │                           │
    │  Extraction  │                           │
    └──────────────┘                           │
              │                                │
              ▼                                │
    ┌──────────────┐                          │
    │  Task 2.2    │                          │
    │  Content     │                          │
    │  Extraction  │                          │
    └──────────────┘                          │
              │                                │
              └────────────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Task 2.4           │
                    │   Single Message     │
                    │   Conversion         │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Task 2.5           │
                    │   Batch Conversion   │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Task 2.6           │
                    │   send_chat_history  │
                    │   _messages_async    │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Task 2.7           │
                    │   send_chat_history  │
                    │   _async             │
                    └──────────────────────┘
                               │
       ┌───────────────┬───────┴───────┬───────────────┐
       │               │               │               │
       ▼               ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│Task 3.1  │    │Task 3.2  │    │Task 3.3  │    │Task 3.4  │
│Input     │    │Conversion│    │Success   │    │Error     │
│Validation│    │Tests     │    │Path Tests│    │Handling  │
│Tests     │    │          │    │          │    │Tests     │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
       │               │               │               │
       └───────────────┴───────┬───────┴───────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Task 3.5           │
                    │   Integration Tests  │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Task 3.6           │
                    │   Coverage &         │
                    │   Performance        │
                    └──────────────────────┘
                               │
       ┌───────────────┬───────┴───────┬───────────────┐
       │               │               │               │
       ▼               ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│Task 4.1  │    │Task 4.2  │    │Task 4.3  │    │Task 4.4  │
│Docstrings│    │README    │    │CHANGELOG │    │Linting   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
       │               │               │               │
       └───────────────┴───────┬───────┴───────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Task 4.5           │
                    │   Final Verification │
                    └──────────────────────┘
```

### 4.2 Critical Path

The critical path for this implementation is:

```
Task 1.1 → Task 1.2 → Task 2.1 → Task 2.2 → Task 2.4 → Task 2.5 → Task 2.6 → Task 2.7 → Task 3.3 → Task 3.6 → Task 4.5
```

**Estimated Critical Path Duration**: 24-32 hours

### 4.3 Parallelization Opportunities

The following tasks can be done in parallel:

| Parallel Group | Tasks | Notes |
|----------------|-------|-------|
| After Task 1.1 | Task 1.2, Task 1.3, Task 2.3 | Infrastructure setup |
| After Task 2.7 | Task 3.1, Task 3.2, Task 3.3, Task 3.4 | Unit test implementation |
| After Task 3.6 | Task 4.1, Task 4.2, Task 4.3, Task 4.4 | Documentation and finalization |

---

## 5. Testing Strategy Overview

### 5.1 Test Categories Summary

| Category | Test Count | Coverage Target | Priority |
|----------|------------|-----------------|----------|
| Input Validation (UV) | 9 tests | 100% validation paths | P0 |
| Conversion Logic (CV) | 12 tests | 100% conversion scenarios | P0 |
| Success Path (SP) | 7 tests | All happy paths | P0 |
| Error Handling (EH) | 5 tests | All error conditions | P0 |
| Integration (IT) | 3 tests | End-to-end flows | P0 |
| Performance | 2+ tests | Regression detection | P1 |
| **Total** | **38+ tests** | **≥95% lines, ≥90% branches** | |

### 5.2 Test File Structure

```
tests/
└── tooling/
    └── extensions/
        └── openai/
            ├── __init__.py
            ├── conftest.py                      # Shared fixtures
            ├── test_send_chat_history_async.py  # UV, SP, EH tests (both methods)
            ├── test_message_conversion.py       # CV tests
            ├── test_integration.py              # IT tests
            └── test_performance.py              # Performance benchmarks
```

### 5.3 Mocking Strategy

| Component | Mock Approach |
|-----------|---------------|
| OpenAI Message Types | Use `Mock` objects with role/content attributes |
| OpenAI Session | Use `Mock` with `get_items()` returning mock messages |
| TurnContext | Use `Mock(spec=TurnContext)` for interface compliance |
| McpToolServerConfigurationService | Use `AsyncMock` for `send_chat_history()` |
| HTTP Layer | Mock `aiohttp.ClientSession` for integration tests |

### 5.4 Coverage Requirements

```python
# pyproject.toml coverage configuration
[tool.pytest.ini_options]
addopts = "--cov=microsoft_agents_a365.tooling.extensions.openai --cov-report=html --cov-fail-under=95"
```

---

## 6. Risks and Considerations

### 6.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **OpenAI SDK Breaking Changes** | Medium | High | Pin version, use duck typing, create adapter layer |
| **Type Union Complexity** | Medium | Medium | Comprehensive type checking, runtime isinstance checks |
| **Performance Regression** | Low | Medium | Add benchmark tests in CI |
| **Thread Safety Issues** | Low | High | Stateless design, no shared mutable state |

### 6.2 Schedule Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **OpenAI SDK Research Takes Longer** | Medium | Medium | Time-box research to 4 hours max |
| **Test Coverage Gap Discovery** | Low | Medium | Continuous coverage monitoring |
| **Code Review Delays** | Low | Low | Early reviewer engagement |

### 6.3 Integration Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Core Service API Changes** | Low | High | No planned changes to core service |
| **Dependency Version Conflicts** | Low | Medium | Use flexible version constraints |

### 6.4 Open Questions to Resolve

| Question | Resolution Needed By | Impact if Unresolved |
|----------|---------------------|---------------------|
| Full enumeration of `TResponseInputItem` types | Task 1.1 | May miss some message types |
| Session.get_items() async vs sync | Task 1.1 | Implementation approach |
| Content validation (empty string allowed?) | Task 2.2 | May need to relax ChatHistoryMessage validator |

### 6.5 Assumptions

1. The `openai-agents` package is available and stable
2. `Session.get_items()` method exists and returns `List[TResponseInputItem]`
3. The core `McpToolServerConfigurationService.send_chat_history()` remains unchanged
4. Empty content strings should be handled gracefully (may require relaxing `ChatHistoryMessage.content` validator)

---

## Appendix: Task Checklist

### Phase 1: Foundation & Infrastructure
- [ ] Task 1.1: Analyze OpenAI SDK Types and Create Type Stubs
- [ ] Task 1.2: Add openai-agents Dependency
- [ ] Task 1.3: Create Test Directory Structure and Fixtures

### Phase 2: Core Implementation
- [ ] Task 2.1: Implement `_extract_role()` Private Method
- [ ] Task 2.2: Implement `_extract_content()` Private Method
- [ ] Task 2.3: Implement `_extract_id()` and `_extract_timestamp()` Private Methods
- [ ] Task 2.4: Implement `_convert_single_message()` Private Method
- [ ] Task 2.5: Implement `_convert_openai_messages_to_chat_history()` Private Method
- [ ] Task 2.6: Implement `send_chat_history_messages_async()` Public Method
- [ ] Task 2.7: Implement `send_chat_history_async()` Public Method

### Phase 3: Testing
- [ ] Task 3.1: Implement Input Validation Unit Tests (UV-01 to UV-09)
- [ ] Task 3.2: Implement Conversion Logic Unit Tests (CV-01 to CV-12)
- [ ] Task 3.3: Implement Success Path Unit Tests (SP-01 to SP-07)
- [ ] Task 3.4: Implement Error Handling Unit Tests (EH-01 to EH-05)
- [ ] Task 3.5: Implement Integration Tests (IT-01 to IT-03)
- [ ] Task 3.6: Verify Test Coverage and Add Performance Benchmarks

### Phase 4: Documentation & Finalization
- [ ] Task 4.1: Complete Method Docstrings and Type Hints
- [ ] Task 4.2: Update README.md with Usage Examples
- [ ] Task 4.3: Update CHANGELOG.md
- [ ] Task 4.4: Final Code Review and Linting Compliance
- [ ] Task 4.5: Final Integration Verification

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | January 21, 2026 | PRD Task Generator Agent | Initial task breakdown |
