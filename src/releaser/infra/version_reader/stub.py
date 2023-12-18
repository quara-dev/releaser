from __future__ import annotations

from releaser.hexagon.ports import VersionReader


class VersionReaderStub(VersionReader):
    """A stub version reader that can be used for testing."""

    def __init__(self) -> None:
        self.version: str | None = None
        self.path: str | None = None
        self._version_files_read: list[str | None] = []

    def read(self, version_file: str | None) -> str | None:
        self._version_files_read.append(version_file)
        return self.version

    def set_version(self, version: str) -> None:
        """Test helper: set the version to be returned by read_version()."""
        self.version = version

    def did_read_version_file(self, version_file: str | None) -> bool:
        """Test helper: check if the version file was read."""
        return version_file in self._version_files_read
