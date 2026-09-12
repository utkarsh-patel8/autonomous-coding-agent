import os
import subprocess
import uuid

from dataclasses import dataclass
from pathlib import Path

from src.workspace import get_repo_path


@dataclass
class ExecutionResult:
    command: str
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool = False
    infrastructure_error: str | None = None

    @property
    def success(self) -> bool:
        return (
            self.exit_code == 0
            and not self.timed_out
            and self.infrastructure_error is None
        )

    def to_text(self) -> str:
        parts = [
            "Execution environment: Docker sandbox",
            f"Command: {self.command}",
        ]

        if self.infrastructure_error:
            parts.append(
                f"Infrastructure error: {self.infrastructure_error}"
            )

        if self.timed_out:
            parts.append("Timed out: yes")

        if self.exit_code is not None:
            parts.append(
                f"Exit code: {self.exit_code}"
            )

        if self.stdout:
            parts.append(
                f"STDOUT:\n{self.stdout}"
            )

        if self.stderr:
            parts.append(
                f"STDERR:\n{self.stderr}"
            )

        return "\n\n".join(parts)


class DockerSandbox:
    def __init__(
        self,
        image_name: str = "coding-agent-sandbox:latest",
        timeout: int = 30,
        memory_limit: str = "512m",
        cpu_limit: str = "1.0",
        pids_limit: int = 128,
    ):
        self.image_name = image_name
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.pids_limit = pids_limit

    def _user_arguments(self) -> list[str]:
        if (
            hasattr(os, "getuid")
            and hasattr(os, "getgid")
        ):
            return [
                "--user",
                f"{os.getuid()}:{os.getgid()}",
            ]

        return []

    def run(
        self,
        command: str,
        repo_path: Path | None = None,
    ) -> ExecutionResult:

        if repo_path is None:
            repo_path = get_repo_path()

        repo = repo_path.resolve()

        if not repo.exists():
            return ExecutionResult(
                command=command,
                exit_code=None,
                stdout="",
                stderr="",
                infrastructure_error=(
                    f"Repository does not exist: {repo}"
                ),
            )

        container_name = (
            f"coding-agent-{uuid.uuid4().hex[:12]}"
        )

        docker_command = [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "--pull",
            "never",
            "--network",
            "none",
            "--memory",
            self.memory_limit,
            "--cpus",
            self.cpu_limit,
            "--pids-limit",
            str(self.pids_limit),
            "--security-opt",
            "no-new-privileges",
            "--cap-drop",
            "ALL",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=64m",
            "-e",
            "PYTHONPATH=/workspace",
            "-e",
            "HOME=/tmp",
            "-v",
            f"{repo}:/workspace:rw",
            "-w",
            "/workspace",
        ]

        docker_command.extend(
            self._user_arguments()
        )

        docker_command.extend(
            [
                self.image_name,
                "sh",
                "-lc",
                command,
            ]
        )

        try:
            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

        except FileNotFoundError:
            return ExecutionResult(
                command=command,
                exit_code=None,
                stdout="",
                stderr="",
                infrastructure_error=(
                    "Docker executable was not found."
                ),
            )

        except subprocess.TimeoutExpired:

            subprocess.run(
                [
                    "docker",
                    "rm",
                    "-f",
                    container_name,
                ],
                capture_output=True,
                text=True,
            )

            return ExecutionResult(
                command=command,
                exit_code=None,
                stdout="",
                stderr="",
                timed_out=True,
            )

        infrastructure_error = None

        # Docker uses exit code 125 when docker run itself fails,
        # for example if the daemon/image is unavailable.
        if result.returncode == 125:
            infrastructure_error = (
                "Docker failed to start the sandbox command."
            )

        return ExecutionResult(
            command=command,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            infrastructure_error=infrastructure_error,
        )