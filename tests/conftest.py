import os
import sys


def _ensure_repo_on_path() -> None:
    # Add project root to sys.path so tests can import top-level modules like `main` and `tools`
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


_ensure_repo_on_path()


