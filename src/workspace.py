from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

WORKSPACE_ROOT = PROJECT_ROOT / "workspace"

ACTIVE_REPO = WORKSPACE_ROOT / "sample_repo"


def get_repo_path() -> Path:
    repo = ACTIVE_REPO.resolve()

    if not repo.exists():
        raise FileNotFoundError(
            f"Active repository does not exist: {repo}"
        )

    if not repo.is_dir():
        raise ValueError(
            f"Active repository is not a directory: {repo}"
        )

    return repo