import argparse
import hashlib
import json
import shutil
import statistics
import subprocess
import sys

from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

# evaluate.py:
# codingAgentProj/evaluation/evaluate.py
#
# parent        -> evaluation/
# parent.parent -> codingAgentProj/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# Add codingAgentProj/ to Python's module search path
# BEFORE importing anything from src.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# ---------------------------------------------------------
# Project imports
# ---------------------------------------------------------

from src.agent import CodingAgent
from src.sandbox import DockerSandbox
from src.errors import ProviderInfrastructureError


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

EVALUATION_ROOT = PROJECT_ROOT / "evaluation"
TASKS_DIR = EVALUATION_ROOT / "tasks"
RESULTS_DIR = EVALUATION_ROOT / "results"

WORKSPACE_ROOT = PROJECT_ROOT / "workspace"

ACTIVE_REPO = (
    WORKSPACE_ROOT / "sample_repo"
)

BACKUP_REPO = (
    WORKSPACE_ROOT
    / "_sample_repo_before_evaluation"
)

# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def load_metadata(task_dir: Path) -> dict:
    metadata_path = task_dir / "metadata.json"

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Missing metadata.json in {task_dir}"
        )

    return json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )


def copy_task_to_workspace(
    task_dir: Path,
) -> None:
    """
    Copy a fresh task into workspace/sample_repo.

    metadata.json and TASK.md are evaluator metadata, not part
    of the repository presented to the coding agent.
    """

    if ACTIVE_REPO.exists():
        shutil.rmtree(ACTIVE_REPO)

    shutil.copytree(
        task_dir,
        ACTIVE_REPO,
        ignore=shutil.ignore_patterns(
            "metadata.json",
            "TASK.md",
            "__pycache__",
            ".pytest_cache",
        ),
    )

    # Ignore runtime artifacts so they do not pollute git_diff.
    gitignore = ACTIVE_REPO / ".gitignore"

    gitignore.write_text(
        "__pycache__/\n"
        "*.py[cod]\n"
        ".pytest_cache/\n",
        encoding="utf-8",
    )


def run_git(
    *args: str,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ACTIVE_REPO,
        capture_output=True,
        text=True,
    )


def create_git_baseline() -> None:
    """
    Each evaluation task gets its OWN nested Git repository.

    This means git_diff() compares against the buggy task
    baseline rather than against your coding-agent project's
    outer Git repository.
    """

    result = run_git("init", "-q")

    if result.returncode != 0:
        raise RuntimeError(
            "Failed to initialize task Git repository:\n"
            + result.stderr
        )

    run_git(
        "config",
        "user.name",
        "Coding Agent Evaluator",
    )

    run_git(
        "config",
        "user.email",
        "evaluator@local",
    )

    result = run_git("add", ".")

    if result.returncode != 0:
        raise RuntimeError(
            "Failed to stage task baseline:\n"
            + result.stderr
        )

    result = run_git(
        "commit",
        "-q",
        "-m",
        "evaluation baseline",
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Failed to commit task baseline:\n"
            + result.stderr
        )


def get_changed_files() -> list[str]:
    """
    Return files changed by the agent relative to the
    per-task baseline.
    """

    result = run_git(
        "status",
        "--porcelain",
    )

    if result.returncode != 0:
        return []

    files = []

    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue

        path = line[3:].strip()

        # Rename output can look like:
        # old.py -> new.py
        if " -> " in path:
            path = path.split(
                " -> ",
                1,
            )[1]

        files.append(path)

    return sorted(set(files))


# ---------------------------------------------------------
# Protected-path integrity
# ---------------------------------------------------------

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def snapshot_paths(
    repo: Path,
    protected_paths: list[str],
) -> dict[str, str]:
    """
    Hash all files under protected paths.

    This detects:
    - modified tests
    - deleted tests
    - newly-created test files
    """

    snapshot = {}

    for protected in protected_paths:

        target = repo / protected

        if not target.exists():
            continue

        if target.is_file():

            relative = str(
                target.relative_to(repo)
            )

            snapshot[relative] = (
                sha256_file(target)
            )

            continue

        for path in sorted(
            target.rglob("*")
        ):
            if not path.is_file():
                continue

            if "__pycache__" in path.parts:
                continue

            relative = str(
                path.relative_to(repo)
            )

            snapshot[relative] = (
                sha256_file(path)
            )

    return snapshot


# ---------------------------------------------------------
# Task execution
# ---------------------------------------------------------

def evaluate_task(
    task_dir: Path,
) -> dict:

    metadata = load_metadata(
        task_dir
    )

    task_id = metadata["id"]
    prompt = metadata["prompt"]

    validation_command = metadata.get(
        "validation_command",
        "python -m pytest -q",
    )

    protected_paths = metadata.get(
        "protected_paths",
        ["tests/"],
    )

    editable_paths = metadata.get(
        "editable_paths",
        [],
    )

    print()
    print("=" * 70)
    print(f"EVALUATING: {task_id}")
    print("=" * 70)

    print(f"Category:   {metadata.get('category', 'unknown')}")
    print(f"Difficulty: {metadata.get('difficulty', 'unknown')}")
    print(f"Task:       {prompt}")
    print()

    # -----------------------------------------------------
    # Fresh task copy
    # -----------------------------------------------------

    copy_task_to_workspace(
        task_dir
    )

    create_git_baseline()

    protected_before = snapshot_paths(
        ACTIVE_REPO,
        protected_paths,
    )

    sandbox = DockerSandbox()

    # -----------------------------------------------------
    # Verify benchmark baseline actually FAILS.
    # -----------------------------------------------------

    print(
        "Checking buggy baseline..."
    )

    baseline_result = sandbox.run(
        validation_command
    )

    baseline_fails = (
        not baseline_result.success
        and baseline_result.infrastructure_error
        is None
    )

    print(
        f"Baseline exit code: "
        f"{baseline_result.exit_code}"
    )

    if not baseline_fails:

        print(
            "WARNING: Benchmark baseline did not "
            "produce an ordinary validation failure."
        )

        return {
            "task_id": task_id,
            "category": metadata.get(
                "category"
            ),
            "difficulty": metadata.get(
                "difficulty"
            ),
            "benchmark_valid": False,
            "evaluation_success": False,
            "error": (
                "Buggy baseline did not fail "
                "validation as expected."
            ),
            "baseline_exit_code":
                baseline_result.exit_code,
        }

    # -----------------------------------------------------
    # Run coding agent
    # -----------------------------------------------------

    agent = CodingAgent()

    # Future-proof: metadata can choose a different test
    # command even though all current tasks use pytest.
    agent.validator.command = (
        validation_command
    )

    agent_answer = None
    agent_error = None
    infrastructure_failure = None


    try:
        agent_answer = agent.run(
            prompt
        )


    except ProviderInfrastructureError as error:

        infrastructure_failure = (
            error.to_dict()
        )

        print(
            "\nInfrastructure failure:"
        )

        print(
            json.dumps(
                infrastructure_failure,
                indent=2,
            )
        )


    except Exception as error:

        agent_error = (
            f"{type(error).__name__}: "
            f"{error}"
        )

        print(
            "\nAgent failure:"
        )

        print(
            agent_error
        )
        print(
            f"\nAgent raised an exception: "
            f"{agent_error}"
        )

    # -----------------------------------------------------
    # Independent evaluator verification
    #
    # Do not rely only on the agent's own validator.
    # -----------------------------------------------------

    print(
        "\nRunning evaluator-owned final validation..."
    )

    final_result = sandbox.run(
        validation_command
    )

    # -----------------------------------------------------
    # Ensure protected tests were not changed.
    # -----------------------------------------------------

    protected_after = snapshot_paths(
        ACTIVE_REPO,
        protected_paths,
    )

    tests_unchanged = (
        protected_before
        == protected_after
    )

    # -----------------------------------------------------
    # Inspect changed files.
    # -----------------------------------------------------

    changed_files = (
        get_changed_files()
    )

    unexpected_changed_files = []

    if editable_paths:

        for changed in changed_files:

            # Ignore runtime .gitignore created by evaluator.
            if changed == ".gitignore":
                continue

            allowed = False

            for editable in editable_paths:

                editable = (
                    editable.rstrip("/")
                )

                if (
                    changed == editable
                    or changed.startswith(
                        editable + "/"
                    )
                ):
                    allowed = True
                    break

            # tests are separately protected, so any test
            # change will also fail integrity.
            if not allowed:
                unexpected_changed_files.append(
                    changed
                )

    # -----------------------------------------------------
    # Strong evaluation success criterion
    # -----------------------------------------------------

    evaluation_success = (
        final_result.success
        and tests_unchanged
        and agent_error is None
        and infrastructure_failure is None
    )

    if infrastructure_failure is not None:

        outcome = (
            "infrastructure_failure"
        )

    elif evaluation_success:

        outcome = "solved"

    else:

        outcome = "task_failure"    

    metrics = {}

    if agent.last_metrics is not None:
        metrics = (
            agent.last_metrics.to_dict()
        )

    result = {
        "task_id": task_id,

        "category": metadata.get(
            "category"
        ),

        "difficulty": metadata.get(
            "difficulty"
        ),

        "prompt": prompt,

        "benchmark_valid": True,

        "outcome": outcome,

        # Strict evaluator result.
        "evaluation_success":
            evaluation_success,

        # What the internal V6 metrics thought.
        "agent_reported_success":
            metrics.get(
                "task_success",
                False,
            ),

        "tests_unchanged":
            tests_unchanged,

        "changed_files":
            changed_files,

        "unexpected_changed_files":
            unexpected_changed_files,

        "baseline_exit_code":
            baseline_result.exit_code,

        "final_exit_code":
            final_result.exit_code,

        "agent_answer":
            agent_answer,

        "agent_error":
            agent_error,

        "trace_path":
            agent.last_trace_path,

        "metrics":
            metrics,
    }

    print()
    print(
        "Evaluation result: "
        + (
            "PASS"
            if evaluation_success
            else "FAIL"
        )
    )

    print(
        f"Tests unchanged: "
        f"{tests_unchanged}"
    )

    print(
        f"Changed files: "
        f"{changed_files}"
    )

    if unexpected_changed_files:
        print(
            "Unexpected changed files: "
            f"{unexpected_changed_files}"
        )

    return result


# ---------------------------------------------------------
# Aggregation
# ---------------------------------------------------------

def mean(
    values: list[float],
) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def build_summary(
    results: list[dict],
) -> dict:

    valid_results = [
        result
        for result in results
        if result.get(
            "benchmark_valid",
            False,
        )
    ]

    infrastructure_results = [
        result
        for result in valid_results
        if result.get("outcome")
        == "infrastructure_failure"
    ]

    completed_results = [
        result
        for result in valid_results
        if result.get("outcome")
        in {"solved", "task_failure"}
    ]

    solved_results = [
        result
        for result in completed_results
        if result.get("outcome")
        == "solved"
    ]

    task_failure_results = [
        result
        for result in completed_results
        if result.get("outcome")
        == "task_failure"
    ]

    total = len(valid_results)
    completed = len(completed_results)
    solved = len(solved_results)

    infrastructure_failures = len(
        infrastructure_results
    )

    task_failures = len(
        task_failure_results
    )

    first_attempt_successes = 0

    validation_failure_tasks = 0
    validation_recoveries = 0

    steps = []
    tool_calls = []
    llm_calls = []
    tokens = []
    runtimes = []
    sandbox_executions = []

    # IMPORTANT:
    # Efficiency/recovery metrics should only describe
    # completed agent runs, not API/infrastructure failures.
    for result in completed_results:

        metrics = result.get(
            "metrics",
            {},
        )

        strict_success = result.get(
            "evaluation_success",
            False,
        )

        if (
            strict_success
            and metrics.get(
                "first_attempt_success",
                False,
            )
        ):
            first_attempt_successes += 1

        failed_validations = metrics.get(
            "failed_validations",
            0,
        )

        if failed_validations > 0:

            validation_failure_tasks += 1

            if (
                strict_success
                and metrics.get(
                    "recovered_from_validation_failure",
                    False,
                )
            ):
                validation_recoveries += 1

        if "steps" in metrics:
            steps.append(
                metrics["steps"]
            )

        if "tool_calls" in metrics:
            tool_calls.append(
                metrics["tool_calls"]
            )

        if "llm_calls" in metrics:
            llm_calls.append(
                metrics["llm_calls"]
            )

        if "total_tokens" in metrics:
            tokens.append(
                metrics["total_tokens"]
            )

        if "runtime_seconds" in metrics:
            runtimes.append(
                metrics["runtime_seconds"]
            )

        if (
            "total_sandbox_executions"
            in metrics
        ):
            sandbox_executions.append(
                metrics[
                    "total_sandbox_executions"
                ]
            )

    # Of runs that actually reached agent execution,
    # how many were solved?
    resolution_rate = (
        solved / completed
        if completed
        else 0.0
    )

    # Of ALL valid benchmark attempts, how many
    # completed successfully end-to-end?
    end_to_end_completion_rate = (
        solved / total
        if total
        else 0.0
    )

    # Of completed agent runs, how many passed
    # their first final validation?
    first_attempt_rate = (
        first_attempt_successes / completed
        if completed
        else 0.0
    )

    # Of tasks that failed final validation at least once,
    # how many eventually recovered?
    if validation_failure_tasks:
        recovery_rate = (
            validation_recoveries
            / validation_failure_tasks
        )
    else:
        recovery_rate = None

    summary = {
        "tasks_discovered": len(results),

        "valid_tasks": total,

        "completed_task_runs": completed,

        "solved": solved,

        "task_failures": task_failures,

        "infrastructure_failures":
            infrastructure_failures,

        "resolution_rate":
            resolution_rate,

        "end_to_end_completion_rate":
            end_to_end_completion_rate,

        "first_validation_successes":
            first_attempt_successes,

        "first_validation_success_rate":
            first_attempt_rate,

        "tasks_with_validation_failure":
            validation_failure_tasks,

        "validation_recoveries":
            validation_recoveries,

        "validation_recovery_rate":
            recovery_rate,

        "average_steps":
            mean(steps),

        "average_llm_calls":
            mean(llm_calls),

        "average_tool_calls":
            mean(tool_calls),

        "average_total_tokens":
            mean(tokens),

        "average_runtime_seconds":
            mean(runtimes),

        "median_runtime_seconds": (
            statistics.median(runtimes)
            if runtimes
            else 0.0
        ),

        "average_sandbox_executions":
            mean(sandbox_executions),
    }

    return summary


def print_summary(
    summary: dict,
) -> None:

    print()
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    # -----------------------------------------------------
    # Task outcomes
    # -----------------------------------------------------

    print(
        f"Tasks discovered:                 "
        f"{summary['tasks_discovered']}"
    )

    print(
        f"Valid benchmark tasks:            "
        f"{summary['valid_tasks']}"
    )

    print(
        f"Completed agent runs:             "
        f"{summary['completed_task_runs']}"
    )

    print()

    print(
        f"Solved:                           "
        f"{summary['solved']}"
    )

    print(
        f"Task failures:                    "
        f"{summary['task_failures']}"
    )

    print(
        f"Infrastructure failures:          "
        f"{summary['infrastructure_failures']}"
    )

    # -----------------------------------------------------
    # Success rates
    # -----------------------------------------------------

    print()

    print(
        f"Resolution rate:                  "
        f"{summary['resolution_rate'] * 100:.1f}%"
    )

    print(
        f"End-to-end completion rate:       "
        f"{summary['end_to_end_completion_rate'] * 100:.1f}%"
    )

    print(
        f"First-validation success rate:    "
        f"{summary['first_validation_success_rate'] * 100:.1f}%"
    )

    recovery_rate = summary[
        "validation_recovery_rate"
    ]

    if recovery_rate is None:
        recovery_text = "N/A"
    else:
        recovery_text = (
            f"{recovery_rate * 100:.1f}%"
        )

    print(
        f"Validation recovery rate:         "
        f"{recovery_text}"
    )

    # -----------------------------------------------------
    # Agent efficiency metrics
    # -----------------------------------------------------

    print()

    print(
        f"Average steps/task:               "
        f"{summary['average_steps']:.2f}"
    )

    print(
        f"Average LLM calls/task:           "
        f"{summary['average_llm_calls']:.2f}"
    )

    print(
        f"Average tool calls/task:          "
        f"{summary['average_tool_calls']:.2f}"
    )

    print(
        f"Average tokens/task:              "
        f"{summary['average_total_tokens']:.0f}"
    )

    print(
        f"Average runtime/task:             "
        f"{summary['average_runtime_seconds']:.2f}s"
    )

    print(
        f"Median runtime/task:              "
        f"{summary['median_runtime_seconds']:.2f}s"
    )

    print(
        f"Average sandbox executions/task:  "
        f"{summary['average_sandbox_executions']:.2f}"
    )

    print("=" * 70)


# ---------------------------------------------------------
# Main evaluation runner
# ---------------------------------------------------------

def discover_tasks() -> list[Path]:

    if not TASKS_DIR.exists():
        raise FileNotFoundError(
            f"Evaluation task directory not found: "
            f"{TASKS_DIR}"
        )

    tasks = sorted(
        path
        for path in TASKS_DIR.iterdir()
        if (
            path.is_dir()
            and (
                path / "metadata.json"
            ).exists()
        )
    )

    if not tasks:
        raise RuntimeError(
            "No evaluation tasks found."
        )

    return tasks


def save_results(
    results: list[dict],
    summary: dict,
) -> Path:

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S"
    )

    path = (
        RESULTS_DIR
        / f"evaluation_{timestamp}.json"
    )

    payload = {
        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "summary": summary,
        "tasks": results,
    }

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the autonomous coding agent "
            "on the V7 benchmark suite."
        )
    )

    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help=(
            "Run only one task by directory/id, "
            "for example task01_calculator_subtract."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Evaluate only the first N tasks. "
            "Useful for testing the evaluator."
        ),
    )

    parser.add_argument(
        "--start",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--end",
        type=int,
        default=None,
    )

    args = parser.parse_args()

    tasks = discover_tasks()

    if args.start is not None or args.end is not None:

        start = args.start or 1
        end = args.end or len(tasks)

        tasks = [
            task
            for task in tasks
            if start <= int(
                task.name.split("_")[0].replace("task", "")
            ) <= end
        ]

    if args.task is not None:
        tasks = [
            task
            for task in tasks
            if (
                task.name == args.task
                or load_metadata(
                    task
                ).get("id")
                == args.task
            )
        ]

        if not tasks:
            raise ValueError(
                f"Task not found: "
                f"{args.task}"
            )

    if args.limit is not None:
        tasks = tasks[
            :args.limit
        ]

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # Preserve your normal sample repo.
    # -----------------------------------------------------

    if BACKUP_REPO.exists():
        raise RuntimeError(
            f"Backup workspace already exists: "
            f"{BACKUP_REPO}\n"
            "Remove/restore it before running evaluation."
        )

    had_original_repo = (
        ACTIVE_REPO.exists()
    )

    if had_original_repo:
        ACTIVE_REPO.rename(
            BACKUP_REPO
        )

    results = []

    try:

        for index, task_dir in enumerate(
            tasks,
            start=1,
        ):

            print()
            print(
                f"\n[{index}/{len(tasks)}]"
            )

            try:
                result = evaluate_task(
                    task_dir
                )

            except Exception as error:

                print(
                    f"Evaluation task crashed: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

                result = {
                    "task_id":
                        task_dir.name,

                    "benchmark_valid":
                        False,

                    "evaluation_success":
                        False,

                    "error": (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                }

            results.append(result)

    finally:

        # Delete final evaluation task.
        if ACTIVE_REPO.exists():
            shutil.rmtree(
                ACTIVE_REPO
            )

        # Restore the user's original sample repo.
        if (
            had_original_repo
            and BACKUP_REPO.exists()
        ):
            BACKUP_REPO.rename(
                ACTIVE_REPO
            )

    summary = build_summary(
        results
    )

    print_summary(
        summary
    )

    output_path = save_results(
        results,
        summary,
    )

    print()
    print(
        f"Evaluation results saved to:"
    )

    try:
        relative = output_path.relative_to(
            PROJECT_ROOT
        )

        print(relative)

    except ValueError:
        print(output_path)


if __name__ == "__main__":
    main()