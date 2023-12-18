from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class VersionTag:
    """A version tag is a tag with a version number."""

    file: str | None = None
    """The file to read the version number from."""

    prefix: str | None = None
    """A prefix to prepend to the version number."""

    suffix: str | None = None
    """A suffix to append to the version number."""

    minor: bool = False
    """Whether to truncate version to minor version."""

    major: bool = False
    """Whether to truncate version to major version."""

    type: Literal["version"] = "version"
    """The type of the tag source."""

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "VersionTag":
        """Parse a version tag from a dictionary."""
        return cls(
            file=data.get("file"),
            prefix=data.get("prefix"),
            suffix=data.get("suffix"),
            minor=data.get("minor", False),
            major=data.get("major", False),
        )


@dataclass
class GitCommitShaTag:
    """A Git commit SHA tag may be used to identify a commit."""

    size: int = 7
    """The number of characters to include in the tag."""

    type: Literal["git_commit_sha"] = "git_commit_sha"
    """The type of the tag source."""

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "GitCommitShaTag":
        """Parse a Git commit SHA tag from a dictionary."""
        return cls(size=data.get("size", 7))


@dataclass
class LiteralTag:
    """A literal tag is a tag with a fixed value."""

    value: str
    """The value of the tag."""

    type: Literal["literal"] = "literal"
    """The type of the tag source."""

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "LiteralTag":
        """Parse a literal tag from a dictionary."""
        return cls(value=data["value"])


@dataclass
class CommitMsgMatchPolicy:
    """A match policy describes how to match a commit message
    to one or more tags."""

    match: list[str]
    """A list of regular expressions to match against the latest commit message."""

    tags: list[VersionTag | GitCommitShaTag | LiteralTag]
    """A list of tags to apply if the commit message match."""

    filter: str | None = None
    """A filter to apply to the commit message history."""

    depth: int = 20
    """The number of commit messages to read."""

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "CommitMsgMatchPolicy":
        """Parse a match policy from a dictionary."""
        return cls(
            match=_aslist(data["match"]),
            tags=[
                VersionTag.parse_dict(tag)
                if tag.get("type") == "version"
                else GitCommitShaTag.parse_dict(tag)
                if tag.get("type") == "git_commit_sha"
                else LiteralTag.parse_dict(tag)
                for tag in data["tags"]
            ],
            filter=data.get("filter"),
            depth=data.get("depth", 20),
        )


def _aslist(any: Any) -> list[Any]:
    """Convert a value to a list."""
    if any is None:
        return []
    if not isinstance(any, list):
        return [any]
    return any  # type: ignore
