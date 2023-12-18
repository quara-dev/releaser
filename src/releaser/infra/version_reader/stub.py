from __future__ import annotations

from releaser.hexagon.ports import VersionReader


class VersionReaderStub(VersionReader):
    def __init__(self) -> None:
        self.version: str | None = None
        self.path: str | None = None

    def read_version(self, version_file: str | None) -> str | None:
        self.path = version_file
        return self.version

    def set_version(self, version: str) -> None:
        self.version = version
