from dataclasses import dataclass

from src.sandbox import (
    DockerSandbox,
    ExecutionResult,
)


@dataclass
class ValidationResult:
    success: bool
    command: str
    execution: ExecutionResult
    failure_type: str | None = None

    def to_feedback(self) -> str:
        """
        Format validation information for the LLM.
        """

        if self.success:
            return (
                "Automated validation passed.\n\n"
                + self.execution.to_text()
            )

        return (
            "Automated validation failed.\n\n"
            f"Failure type: {self.failure_type}\n\n"
            + self.execution.to_text()
        )


class RepositoryValidator:
    def __init__(
        self,
        command: str = "python -m pytest -q",
    ):
        self.command = command
        self.sandbox = DockerSandbox()

    def validate(self) -> ValidationResult:

        execution = self.sandbox.run(
            self.command
        )

        if execution.infrastructure_error:
            return ValidationResult(
                success=False,
                command=self.command,
                execution=execution,
                failure_type="infrastructure_error",
            )

        if execution.timed_out:
            return ValidationResult(
                success=False,
                command=self.command,
                execution=execution,
                failure_type="timeout",
            )

        if execution.exit_code != 0:
            return ValidationResult(
                success=False,
                command=self.command,
                execution=execution,
                failure_type="test_failure",
            )

        return ValidationResult(
            success=True,
            command=self.command,
            execution=execution,
        )