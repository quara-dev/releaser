"""This module defines the VersionReader abstract base class."""
from __future__ import annotations

import abc


class VersionReader(abc.ABC):
    """Abstract base class for reading the version of a project.

    This class is used to abstract away how the version of a project
    is read.
    """

    @abc.abstractmethod
    def read_version(self) -> str | None:
        """Read the version of a project."""
        raise NotImplementedError
