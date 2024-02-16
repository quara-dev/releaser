"""This module defines the GitReader abstract base class."""
from __future__ import annotations

import abc
import re


class GitReader(abc.ABC):
    @abc.abstractmethod
    def is_dirty(self) -> bool:
        """Check if the repository has uncommitted changes."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_current_branch(self) -> str:
        """Read the name of the current branch."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_most_recent_commit_sha(self) -> str:
        """Read the SHA of the latest commit."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_commit_message_history(self, depth: int) -> list[str]:
        """Read the message of the latest commit."""
        raise NotImplementedError

    def read_last_commit_message(self, depth: int, filter: str | None) -> str | None:
        """Extract the last commit message from a commit history."""
        history = self.read_commit_message_history(depth)
        if not history:
            return None
        if filter:
            regexp = re.compile(filter)
            for commit_msg in history:
                if regexp.match(commit_msg):
                    return commit_msg
            return None
        return history[0]

    def current_reference_matches(self, ref: list[str]) -> bool:
        """Check if the current reference matches the given ref."""
        if not ref:
            return True
        return self.read_current_branch() in ref
