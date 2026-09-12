from pathlib import Path
import subprocess

from src.workspace import get_repo_path
from src.sandbox import DockerSandbox


SANDBOX = DockerSandbox()


def _safe_path(path: str) -> Path:
    """
    Convert a repository-relative path into an absolute path
    while preventing access outside the active repository.
    """

    repo = get_repo_path()

    target = (repo / path).resolve()

    if target != repo and repo not in target.parents:
        raise ValueError(
            "Access outside the active repository is not allowed"
        )

    return target


def read_file(path: str) -> str:
    file_path = _safe_path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Not a file: {path}"
        )

    return file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def write_file(path: str, content: str) -> str:
    file_path = _safe_path(path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return f"Wrote file: {path}"


def list_files(path: str = ".") -> list[str]:
    directory = _safe_path(path)

    if not directory.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {path}"
        )

    if not directory.is_dir():
        raise ValueError(
            f"Not a directory: {path}"
        )

    repo = get_repo_path()

    entries = []

    for item in sorted(directory.iterdir()):
        relative = item.relative_to(repo)

        if item.is_dir():
            entries.append(f"{relative}/")
        else:
            entries.append(str(relative))

    return entries


def get_tree(
    path: str = ".",
    max_depth: int = 4,
) -> str:
    root = _safe_path(path)

    if not root.exists():
        raise FileNotFoundError(
            f"Path does not exist: {path}"
        )

    if not root.is_dir():
        raise ValueError(
            f"Not a directory: {path}"
        )

    repo = get_repo_path()
    lines = []

    ignored_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
        "node_modules",
    }

    def walk(
        directory: Path,
        depth: int,
    ):
        if depth > max_depth:
            return

        items = sorted(
            directory.iterdir(),
            key=lambda item: (
                not item.is_dir(),
                item.name.lower(),
            ),
        )

        for item in items:
            if (
                item.is_dir()
                and item.name in ignored_dirs
            ):
                continue

            relative = item.relative_to(repo)

            indent = "    " * depth

            if item.is_dir():
                lines.append(
                    f"{indent}{relative.name}/"
                )

                if depth < max_depth:
                    walk(
                        item,
                        depth + 1,
                    )

            else:
                lines.append(
                    f"{indent}{relative.name}"
                )

    if root == repo:
        lines.append(".")
    else:
        lines.append(
            str(root.relative_to(repo))
        )

    walk(root, 1)

    return "\n".join(lines)


def run_command(command: str) -> str:
    """
    Execute a repository command inside the Docker sandbox.

    The agent receives a human-readable representation of
    the structured sandbox result.
    """

    result = SANDBOX.run(command)

    return result.to_text()

def git_diff() -> str:
    """
    Return the current Git diff for the active repository.

    This is a fixed, read-only Git operation. It runs on the host
    because the Docker sandbox only mounts the active repository
    and does not contain the parent project's .git directory.

    Untracked files are listed separately because normal
    `git diff` does not include them.
    """

    repo = get_repo_path()

    # First check that the active repository is somewhere inside
    # a Git working tree.
    check = subprocess.run(
        [
            "git",
            "rev-parse",
            "--is-inside-work-tree",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )

    if check.returncode != 0:
        return (
            "Git diff unavailable: the active repository "
            "is not inside a Git working tree.\n\n"
            f"STDERR:\n{check.stderr}"
        )

    # Diff tracked files relative to the current Git baseline.
    diff_result = subprocess.run(
        [
            "git",
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--",
            ".",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )

    if diff_result.returncode != 0:
        return (
            "Git diff failed.\n\n"
            f"STDERR:\n{diff_result.stderr}"
        )

    # `git diff` does not show newly-created untracked files,
    # so list those separately.
    untracked_result = subprocess.run(
        [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            ".",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )

    output_parts = []

    if diff_result.stdout.strip():
        output_parts.append(
            "Tracked file changes:\n\n"
            + diff_result.stdout
        )
    else:
        output_parts.append(
            "Tracked file changes:\n\n"
            "No tracked file changes."
        )

    if (
        untracked_result.returncode == 0
        and untracked_result.stdout.strip()
    ):
        output_parts.append(
            "Untracked files:\n\n"
            + untracked_result.stdout
        )
    else:
        output_parts.append(
            "Untracked files:\n\nNone."
        )

    return "\n\n".join(output_parts)

TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "get_tree": get_tree,
    "run_command": run_command,
    "git_diff": git_diff,
}