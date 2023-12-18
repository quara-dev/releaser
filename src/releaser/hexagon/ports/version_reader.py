"""This module defines the VersionReader abstract base class."""
from __future__ import annotations

import abc

from releaser.hexagon.entities import strategy


class VersionReader(abc.ABC):
    """Abstract base class for reading the version of a project.

    This class is used to abstract away how the version of a project
    is read.
    """

    @abc.abstractmethod
    def read_version(self, version_file: str | None) -> str | None:
        """Read the version of a project."""
        raise NotImplementedError

    def read_version_tag(self, tag: strategy.VersionTag) -> str | None:
        """Read the version from a version tag."""
        version = self.read_version(tag.file)
        if not version:
            return None
        if tag.minor:
            version = ".".join(version.split(".")[:2])
        elif tag.major:
            version = version.split(".")[0]
        if tag.prefix:
            version = f"{tag.prefix}{version}"
        if tag.suffix:
            version = f"{version}{tag.suffix}"
        return version
