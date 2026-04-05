from .llm import mock_llm
from .logger import get_logger
from .schemas import AgentResult, ToolExecutionRecord
from .state import AgentState
from .tools import get_tool_map, validate_tool_arguments


class MinimalAgent:
    def __init__(
        self,
        max_loops: int = 5,
        max_tool_failures: int = 2,
        max_tool_retries: int = 1,
    ):
        self.max_loops = max_loops
        self.max_tool_failures = max_tool_failures
        self.max_tool_retries = max_tool_retries
        self.tool_map = get_tool_map()
        self.logger = get_logger()

    def run(self, user_input: str) -> AgentResult:
        state = AgentState(user_input=user_input)

        while True:
            if state.loop_count >= self.max_loops:
                end_reason = "max_loops_reached"
                final = (
                    state.final_answer
                    or "Stopped because max loop count was reached before final answer."
                )
                self.logger.info("Stop: %s", end_reason)
                return AgentResult(False, final, end_reason, state.loop_count)

            if state.tool_failures > self.max_tool_failures:
                end_reason = "max_tool_failures_reached"
                final = "Stopped because tool failures exceeded limit."
                self.logger.info("Stop: %s", end_reason)
                return AgentResult(False, final, end_reason, state.loop_count)

            state.loop_count += 1
            self.logger.info("Loop %s", state.loop_count)

            model_output = mock_llm(state)
            state.add_step(f"loop_{state.loop_count}_action={model_output.action}")
            self.logger.info("Model action: %s", model_output.action)

            if model_output.action == "final_answer":
                state.final_answer = model_output.final_answer or ""
                end_reason = "final_answer"
                self.logger.info("Stop: %s", end_reason)
                return AgentResult(True, state.final_answer, end_reason, state.loop_count)

            if model_output.action != "tool_call" or not model_output.tool_call:
                state.tool_failures += 1
                self.logger.error("Invalid model output for tool call")
                continue

            tool_name = model_output.tool_call.tool_name
            arguments = model_output.tool_call.arguments
            self.logger.info("Tool call: %s args=%s", tool_name, arguments)

            if tool_name not in self.tool_map:
                state.tool_failures += 1
                record = ToolExecutionRecord(
                    tool_name=tool_name,
                    arguments=arguments,
                    success=False,
                    result="Unknown tool",
                )
                state.tool_history.append(record)
                state.add_step(f"tool_error={tool_name}:unknown_tool")
                self.logger.error("Unknown tool: %s", tool_name)
                continue

            try:
                validate_tool_arguments(tool_name, arguments)
            except Exception as exc:
                state.tool_failures += 1
                record = ToolExecutionRecord(
                    tool_name=tool_name,
                    arguments=arguments,
                    success=False,
                    result=f"{type(exc).__name__}: {exc}",
                )
                state.tool_history.append(record)
                state.add_step(f"tool_error={tool_name}:{exc}")
                self.logger.error("Tool argument validation error: %s", exc)
                continue

            last_exception: Exception | None = None
            for attempt in range(1, self.max_tool_retries + 2):
                try:
                    result = self.tool_map[tool_name].func(**arguments)
                    record = ToolExecutionRecord(
                        tool_name=tool_name,
                        arguments=arguments,
                        success=True,
                        result=result,
                    )
                    state.tool_history.append(record)
                    state.scratchpad["last_tool_result"] = result
                    state.add_step(f"tool_success={tool_name}:{result}")
                    self.logger.info("Tool result: %s", result)
                    break
                except Exception as exc:
                    last_exception = exc
                    self.logger.error(
                        "Tool execution error on attempt %s: %s",
                        attempt,
                        exc,
                    )
                    if attempt <= self.max_tool_retries:
                        self.logger.info("Retrying tool: %s", tool_name)
                        continue

                    state.tool_failures += 1
                    record = ToolExecutionRecord(
                        tool_name=tool_name,
                        arguments=arguments,
                        success=False,
                        result=f"{type(exc).__name__}: {exc}",
                    )
                    state.tool_history.append(record)
                    state.add_step(f"tool_error={tool_name}:{last_exception}")
