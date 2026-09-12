import json

from src.llm import LLMClient
from src.tools import TOOLS, git_diff
from src.validator import RepositoryValidator
from src.metrics import AgentMetrics
from src.tracing import RunTracer
from src.errors import ProviderInfrastructureError


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_tree",
            "description": (
                "Inspect the recursive directory structure "
                "of the active repository. Use this near the "
                "start of repository-level tasks to understand "
                "the project layout."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Directory relative to the repository root. "
                            "Use '.' for the whole repository."
                        ),
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": (
                            "Maximum recursion depth for the tree. "
                            "Usually 3 or 4 is sufficient."
                        ),
                    },
                },
                "required": [],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List files and directories directly inside "
                "a directory in the active repository."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Directory relative to repository root. "
                            "Use '.' for the root."
                        ),
                    }
                },
                "required": [],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the complete contents of a text file "
                "inside the repository."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "File path relative to repository root."
                        ),
                    }
                },
                "required": ["path"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create or overwrite a text file inside "
                "the repository. Prefer making the smallest "
                "correct modification required by the task."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "File path relative to repository root."
                        ),
                    },
                    "content": {
                        "type": "string",
                        "description": (
                            "Complete contents that should replace "
                            "the file."
                        ),
                    },
                },
                "required": [
                    "path",
                    "content",
                ],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a shell command from the active repository root. "
                "The repository root is configured as the working directory. "
                "Use this for running tests, scripts, linters, or other "
                "repository commands. For Python pytest projects, prefer "
                "'python -m pytest' over running test files directly."
            ),            
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Shell command to execute from "
                            "the repository root."
                        ),
                    }
                },
                "required": ["command"],
            },
        },
    },

    {
    "type": "function",
    "function": {
        "name": "git_diff",
        "description": (
                "Show the changes currently made to the active repository "
                "relative to its Git baseline. Use this to review exactly "
                "what files and lines were changed before completing a task. "
                "Also reports newly-created untracked files."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


SYSTEM_PROMPT = """
You are an autonomous software engineering agent working on an
existing code repository.

Your goal is to solve the user's coding task correctly while making
the smallest reasonable changes to the repository.

Repository workflow:

1. Inspect the repository structure before making assumptions.
2. Identify the files that are relevant to the user's task.
3. Read existing source code and tests before modifying code.
4. Do not invent repository contents. Use tools to inspect them.
5. Preserve the project's existing coding style and architecture.
6. Avoid modifying files unrelated to the task.
7. After changing code, run the most relevant tests or commands.
8. For Python pytest projects, prefer "python -m pytest".
9. Inspect command output and exit codes carefully.
10. If a command or validation fails, use the failure output to
    diagnose the problem before trying again.
11. Do not simply repeat the same failing command unless the
    repository state has changed or there is a clear reason to
    expect a different result.
12. Do not claim that something works merely because the code
    appears correct.
13. Stop when you believe the user's task has been completed.
14. In the final response, briefly explain:
    - what was wrong,
    - what you changed,
    - how you verified it.

Important:
When you believe the task is complete, an external validator will
independently run the repository test suite. If validation fails,
you will receive the failure output and must continue working.
"""

class CodingAgent:
    def __init__(
        self,
        max_steps: int = 20,
        max_validation_retries: int = 3,
    ):
        self.llm = LLMClient()

        self.max_steps = max_steps

        self.max_validation_retries = (
            max_validation_retries
        )

        self.validator = RepositoryValidator()

        # Exposed after each run so main.py can
        # display the report.
        self.last_metrics = None
        self.last_trace_path = None

        self.metrics = None
        self.tracer = None

    def execute_tool(
        self,
        tool_name: str,
        arguments: dict,
    ) -> str:

        if tool_name not in TOOLS:
            return (
                f"Error: Unknown tool '{tool_name}'"
            )

        try:
            result = TOOLS[tool_name](
                **arguments
            )

            if isinstance(result, str):
                return result

            return json.dumps(
                result,
                indent=2,
            )

        except Exception as error:
            return (
                f"Tool error: "
                f"{type(error).__name__}: "
                f"{error}"
            )

    def _finish_run(
        self,
        success: bool,
    ):
        """
        Finish metrics and save the trace.
        """

        self.metrics.finish(
            success=success
        )

        self.tracer.log(
            "run_finished",
            success=success,
        )

        self.last_metrics = self.metrics

        self.last_trace_path = (
            self.tracer.save(
                metrics=self.metrics.to_dict()
            )
        )

    def run(
        self,
        task: str,
    ) -> str:

        # Fresh observability state for every task.
        self.metrics = AgentMetrics(
            task=task
        )

        self.metrics.start()

        self.tracer = RunTracer(
            task=task
        )

        self.last_metrics = None
        self.last_trace_path = None

        self.tracer.log(
            "run_started"
        )

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": task,
            },
        ]

        validation_failures = 0

        try:

            for step in range(
                1,
                self.max_steps + 1,
            ):

                self.metrics.record_step(
                    step
                )

                print(
                    f"\n========== STEP {step} =========="
                )

                # -----------------------------------------
                # LLM call
                # -----------------------------------------

                llm_result = self.llm.generate(
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                )

                self.metrics.record_llm_call(
                    input_tokens=(
                        llm_result.input_tokens
                    ),
                    output_tokens=(
                        llm_result.output_tokens
                    ),
                )

                response = llm_result.message

                tool_calls = getattr(
                    response,
                    "tool_calls",
                    None,
                )

                self.tracer.log(
                    "llm_response",
                    step=step,
                    input_tokens=(
                        llm_result.input_tokens
                    ),
                    output_tokens=(
                        llm_result.output_tokens
                    ),
                    has_tool_calls=bool(
                        tool_calls
                    ),
                    content=(
                        response.content
                        if not tool_calls
                        else None
                    ),
                )

                messages.append(response)

                # -----------------------------------------
                # Model believes task is complete.
                # Validate independently.
                # -----------------------------------------

                if not tool_calls:

                    proposed_final_answer = (
                        response.content
                        or "Task completed."
                    )

                    self.tracer.log(
                        "completion_proposed",
                        step=step,
                        response=proposed_final_answer,
                    )

                    print(
                        "\n========== VALIDATION =========="
                    )

                    validation = (
                        self.validator.validate()
                    )

                    self.metrics.record_validation(
                        success=validation.success
                    )

                    execution = (
                        validation.execution
                    )

                    self.tracer.log(
                        "validation",
                        step=step,
                        success=validation.success,
                        failure_type=(
                            validation.failure_type
                        ),
                        command=(
                            validation.command
                        ),
                        exit_code=(
                            execution.exit_code
                        ),
                        timed_out=(
                            execution.timed_out
                        ),
                        infrastructure_error=(
                            execution.infrastructure_error
                        ),
                        stdout=(
                            execution.stdout
                        ),
                        stderr=(
                            execution.stderr
                        ),
                    )

                    print(
                        execution.to_text()
                    )

                    # ------------------------------
                    # Validation passed.
                    # ------------------------------

                    if validation.success:
                        print("\nValidation: PASSED")

                        final_diff = git_diff()

                        print("\n========== FINAL GIT DIFF ==========")
                        print(final_diff)

                        self.tracer.log(
                            "final_git_diff",
                            step=step,
                            diff=final_diff,
                        )

                        self._finish_run(
                            success=True
                        )

                        return proposed_final_answer

                    # ------------------------------
                    # Infrastructure failure.
                    # ------------------------------

                    if (
                        validation.failure_type
                        == "infrastructure_error"
                    ):

                        self._finish_run(
                            success=False
                        )

                        return (
                            "Agent stopped because "
                            "the validation environment "
                            "failed.\n\n"
                            + validation.to_feedback()
                        )

                    # ------------------------------
                    # Validation failed.
                    # ------------------------------

                    validation_failures += 1

                    print(
                        "\nValidation: FAILED "
                        f"({validation_failures}/"
                        f"{self.max_validation_retries})"
                    )

                    if (
                        validation_failures
                        >= self.max_validation_retries
                    ):

                        self._finish_run(
                            success=False
                        )

                        return (
                            "Agent could not produce "
                            "a validated solution within "
                            "the allowed number of "
                            "validation retries.\n\n"
                            + validation.to_feedback()
                        )

                    feedback = (
                        "[AUTOMATED VALIDATION FEEDBACK]\n\n"
                        "You attempted to finish the task, "
                        "but the repository did not pass "
                        "automated validation.\n\n"
                        f"{validation.to_feedback()}\n\n"
                        "Continue working on the original "
                        "task. Diagnose this failure before "
                        "making another change. Do not simply "
                        "repeat the same unsuccessful action."
                    )

                    self.tracer.log(
                        "validation_feedback",
                        step=step,
                        feedback=feedback,
                    )

                    messages.append(
                        {
                            "role": "user",
                            "content": feedback,
                        }
                    )

                    continue

                # -----------------------------------------
                # Execute requested tools.
                # -----------------------------------------

                for tool_call in tool_calls:

                    tool_name = (
                        tool_call.function.name
                    )

                    arguments = {}

                    try:
                        arguments = json.loads(
                            tool_call.function.arguments
                        )

                    except json.JSONDecodeError as error:

                        tool_result = (
                            "Error: Model produced "
                            "invalid JSON arguments: "
                            f"{error}"
                        )

                        # It was still a requested
                        # tool call, so count it.
                        self.metrics.record_tool_call(
                            tool_name=tool_name,
                            arguments={},
                        )

                        self.tracer.log(
                            "tool_call",
                            step=step,
                            tool=tool_name,
                            arguments_raw=(
                                tool_call.function.arguments
                            ),
                            success=False,
                            result=tool_result,
                        )

                    else:

                        self.metrics.record_tool_call(
                            tool_name=tool_name,
                            arguments=arguments,
                        )

                        print(
                            f"Tool: {tool_name}"
                        )

                        print(
                            f"Arguments: {arguments}"
                        )

                        tool_result = (
                            self.execute_tool(
                                tool_name,
                                arguments,
                            )
                        )

                        self.tracer.log(
                            "tool_call",
                            step=step,
                            tool=tool_name,
                            arguments=arguments,
                            result=tool_result,
                        )

                    print(
                        f"\nResult:\n{tool_result}"
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": (
                                tool_call.id
                            ),
                            "name": tool_name,
                            "content": tool_result,
                        }
                    )

            # ---------------------------------------------
            # MAX_STEPS reached.
            # ---------------------------------------------

            self.tracer.log(
                "max_steps_reached",
                step=self.max_steps,
            )

            self._finish_run(
                success=False
            )

            return (
                "Agent stopped because it reached "
                f"the maximum of {self.max_steps} "
                "steps before producing a "
                "validated solution."
            )

        except ProviderInfrastructureError as error:

            self.tracer.log(
                "infrastructure_failure",
                provider=error.provider,
                failure_type=(
                    error.failure_type
                ),
                status_code=(
                    error.status_code
                ),
                error_message=str(error),
            )

            self._finish_run(
                success=False
            )

            raise


        except Exception as error:

            self.tracer.log(
                "run_error",
                error_type=(
                    type(error).__name__
                ),
                error_message=str(error),
            )

            self._finish_run(
                success=False
            )

            raise