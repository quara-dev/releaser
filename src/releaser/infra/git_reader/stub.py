from __future__ import annotations

from releaser.hexagon.ports import GitReader


class GitReaderStub(GitReader):
    def __init__(self) -> None:
        self._sha: str | None = None
        self._history: list[str] | None = None
        self._is_dirty: bool | None = None

    def is_dirty(self) -> bool:
        if self._is_dirty is None:
            raise RuntimeError("is_dirty not set in stub git reader")
        return self._is_dirty

    def read_most_recent_commit_sha(self) -> str:
        if self._sha is None:
            raise RuntimeError("sha not set in stub git reader")
        return self._sha

    def read_commit_message_history(self, depth: int) -> list[str]:
        if self._history is None:
            raise RuntimeError("history not set in stub git reader")
        return list(self._history)

    def set_sha(self, sha: str) -> None:
        self._sha = sha

    def set_history(self, history: list[str]) -> None:
        self._history = history

    def set_is_dirty(self, is_dirty: bool) -> None:
        self._is_dirty = is_dirty
