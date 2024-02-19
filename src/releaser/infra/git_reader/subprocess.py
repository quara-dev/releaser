from __future__ import annotations

import subprocess

from releaser.hexagon.ports import GitReader


class GitSubprocessReader(GitReader):
    """A git reader that uses subprocesses to read git information."""

    def __init__(self) -> None:
        # FIXME: Check if git is installed
        # FIXME: Check if directory is a git repository
        # Let the CLI handle these errors
        pass

    def is_dirty(self) -> bool:
        process = subprocess.run(["git", "diff-index", "--quiet", "HEAD", "--"])
        return process.returncode != 0

    def read_current_branch(self) -> str:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return branch.decode().strip()

    def read_most_recent_commit_sha(self) -> str:
        long_sha = (
            subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        )
        return long_sha

    def read_commit_message_history(self, depth: int) -> list[str]:
        history = (
            subprocess.check_output(["git", "log", f"-{depth}", "--pretty=%s"])
            .decode()
            .strip()
            .splitlines()
        )
        return [line.strip() for line in history]
