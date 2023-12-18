"""This module defines the JsonWriter abstract base class."""
from __future__ import annotations

import abc

from ..entities import artefact


class JsonWriter(abc.ABC):
    """Abstract base class for writing manifest to a destination."""

    @abc.abstractmethod
    def write_manifest(self, manifest: artefact.Manifest) -> None:
        """Write manfest to a destination."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_manifest(self) -> artefact.Manifest | None:
        """Read manifest from a destination."""
        raise NotImplementedError
