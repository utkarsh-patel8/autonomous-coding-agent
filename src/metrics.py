from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter


@dataclass
class AgentMetrics:
    task: str

    steps: int = 0

    llm_calls: int = 0
    tool_calls: int = 0

    file_read_calls: int = 0
    file_write_calls: int = 0
    agent_command_calls: int = 0

    validation_attempts: int = 0
    failed_validations: int = 0

    input_tokens: int = 0
    output_tokens: int = 0

    task_success: bool = False

    tool_usage: dict[str, int] = field(
        default_factory=dict
    )

    files_read: set[str] = field(
        default_factory=set
    )

    files_written: set[str] = field(
        default_factory=set
    )

    started_at: str | None = None
    finished_at: str | None = None

    _start_time: float | None = field(
        default=None,
        repr=False,
    )

    _runtime_seconds: float = field(
        default=0.0,
        repr=False,
    )

    def start(self):
        self.started_at = (
            datetime.now(timezone.utc).isoformat()
        )

        self._start_time = perf_counter()

    def finish(self, success: bool):
        self.task_success = success

        self.finished_at = (
            datetime.now(timezone.utc).isoformat()
        )

        if self._start_time is not None:
            self._runtime_seconds = (
                perf_counter() - self._start_time
            )

    def record_step(self, step: int):
        self.steps = max(
            self.steps,
            step,
        )

    def record_llm_call(
        self,
        input_tokens: int,
        output_tokens: int,
    ):
        self.llm_calls += 1

        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def record_tool_call(
        self,
        tool_name: str,
        arguments: dict,
    ):
        self.tool_calls += 1

        self.tool_usage[tool_name] = (
            self.tool_usage.get(tool_name, 0)
            + 1
        )

        if tool_name == "read_file":
            self.file_read_calls += 1

            path = arguments.get("path")

            if path:
                self.files_read.add(path)

        elif tool_name == "write_file":
            self.file_write_calls += 1

            path = arguments.get("path")

            if path:
                self.files_written.add(path)

        elif tool_name == "run_command":
            self.agent_command_calls += 1

    def record_validation(
        self,
        success: bool,
    ):
        self.validation_attempts += 1

        if not success:
            self.failed_validations += 1

    @property
    def runtime_seconds(self) -> float:
        return self._runtime_seconds

    @property
    def total_tokens(self) -> int:
        return (
            self.input_tokens
            + self.output_tokens
        )

    @property
    def first_attempt_success(self) -> bool:
        return (
            self.task_success
            and self.validation_attempts == 1
        )

    @property
    def recovered_from_validation_failure(
        self,
    ) -> bool:
        return (
            self.task_success
            and self.failed_validations > 0
        )

    @property
    def total_sandbox_executions(self) -> int:
        return (
            self.agent_command_calls
            + self.validation_attempts
        )

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "task_success": self.task_success,

            "steps": self.steps,

            "llm_calls": self.llm_calls,
            "tool_calls": self.tool_calls,

            "file_read_calls": (
                self.file_read_calls
            ),
            "file_write_calls": (
                self.file_write_calls
            ),
            "agent_command_calls": (
                self.agent_command_calls
            ),

            "validation_executions": (
                self.validation_attempts
            ),

            "total_sandbox_executions": (
                self.total_sandbox_executions
            ),
            "unique_files_read": (
                len(self.files_read)
            ),
            "unique_files_written": (
                len(self.files_written)
            ),

            "files_read": sorted(
                self.files_read
            ),
            "files_written": sorted(
                self.files_written
            ),

            "tool_usage": dict(
                sorted(
                    self.tool_usage.items()
                )
            ),

            "validation_attempts": (
                self.validation_attempts
            ),
            "failed_validations": (
                self.failed_validations
            ),

            "first_attempt_success": (
                self.first_attempt_success
            ),

            "recovered_from_validation_failure":
                self.recovered_from_validation_failure,

            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,

            "runtime_seconds": round(
                self.runtime_seconds,
                3,
            ),

            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }

    def format_report(
        self,
        trace_path: str | None = None,
    ) -> str:

        success = (
            "YES"
            if self.task_success
            else "NO"
        )

        first_attempt = (
            "YES"
            if self.first_attempt_success
            else "NO"
        )

        recovery = (
            "YES"
            if self.recovered_from_validation_failure
            else "NO"
        )

        lines = [
            "",
            "========== AGENT REPORT ==========",
            "",
            f"Task solved:              {success}",
            f"Steps:                    {self.steps}",
            f"LLM calls:                {self.llm_calls}",
            f"Tool calls:               {self.tool_calls}",
            "",
            f"Unique files read:        {len(self.files_read)}",
            f"Unique files written:     {len(self.files_written)}",
            f"File read calls:          {self.file_read_calls}",
            f"File write calls:         {self.file_write_calls}",
            f"Agent command calls:      {self.agent_command_calls}",
            f"Validation executions:    {self.validation_attempts}",
            f"Total sandbox executions: {self.total_sandbox_executions}",
            "",
            f"Validation attempts:      {self.validation_attempts}",
            f"Failed validations:       {self.failed_validations}",
            f"First-attempt success:    {first_attempt}",
            f"Validation Recovery:      {recovery}",
            "",
            f"Input tokens:             {self.input_tokens}",
            f"Output tokens:            {self.output_tokens}",
            f"Total tokens:             {self.total_tokens}",
            "",
            (
                "Runtime:                  "
                f"{self.runtime_seconds:.2f} sec"
            ),
        ]

        if trace_path:
            lines.extend(
                [
                    "",
                    f"Trace:                    {trace_path}",
                ]
            )

        lines.extend(
            [
                "",
                "Tool usage:",
            ]
        )

        for tool_name, count in sorted(
            self.tool_usage.items()
        ):
            lines.append(
                f"  {tool_name:<22} {count}"
            )

        lines.extend(
            [
                "",
                "==================================",
            ]
        )

        return "\n".join(lines)